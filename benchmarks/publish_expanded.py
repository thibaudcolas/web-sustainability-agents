#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = []
# [tool.uv]
# required-version = ">=0.12.20,<0.13"
# ///
"""Publish allowlisted Harbor results and verify paired frozen-input provenance."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

JSON = dict[str, Any]
# Resolve the repository-owned verifier from this standalone uv script.
grade = cast(
    Callable[[Any, JSON], JSON],
    importlib.import_module("benchmarks.grade_expanded").grade,
)


def digest(path: Path) -> str:
    """Hash exact evidence bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def campaign(directory: Path) -> JSON:
    """Read completed trials without publishing credentials or provider transcripts."""
    job = json.loads((directory / "result.json").read_text())
    if not job.get("finished_at"):
        raise ValueError(f"Campaign is unfinished: {directory.name}")
    trials = []
    for path in sorted(directory.glob("*/result.json")):
        trial = json.loads(path.read_text())
        task = Path(trial["config"]["task"]["path"])
        agent = trial["config"]["agent"]
        kwargs = agent.get("kwargs", {})
        report_path = path.parent / "artifacts/app/output/report.json"
        try:
            report = json.loads(report_path.read_text())
        except FileNotFoundError, UnicodeError, json.JSONDecodeError:
            report = None
        reference = json.loads((task / "tests/reference.json").read_text())
        if digest(task / "tests/grade.py") != digest(
            ROOT / "benchmarks/grade_expanded.py"
        ):
            raise ValueError("Refusing an implicit grader change")
        regrade = grade(report, reference)
        reward = (trial.get("verifier_result") or {}).get("rewards", {}).get("reward")
        if reward is not None and reward != regrade["reward"]:
            raise ValueError(
                f"Artifact regrade differs from Harbor: {trial['task_name']}"
            )
        usage = trial.get("agent_result") or {}
        trials.append(
            {
                "case": trial["task_name"],
                "agent": agent["name"],
                "requestedModel": agent.get("model_name"),
                "requestedReasoning": kwargs.get("reasoning_effort"),
                "codexVersion": kwargs.get("version"),
                "provider": kwargs.get("config", {}).get("model_provider"),
                "verifierMode": trial.get("verifier_environment_mode"),
                "taskChecksum": trial.get("task_checksum"),
                "hashes": {
                    "skillResources": {
                        str(p.relative_to(task / "environment/skills")): digest(p)
                        for p in sorted((task / "environment/skills").rglob("*"))
                        if p.is_file()
                    },
                    **{
                        key: digest(task / name)
                        for key, name in {
                            "input": "environment/input.json",
                            "instruction": "instruction.md",
                            "skill": "environment/skills/sustainability-evidence-review/SKILL.md",
                            "reference": "tests/reference.json",
                            "grader": "tests/grade.py",
                        }.items()
                    },
                },
                "reportSHA256": digest(report_path) if report_path.exists() else None,
                "reward": reward,
                "exception": (trial.get("exception_info") or {}).get("exception_type"),
                "startedAt": trial.get("started_at"),
                "finishedAt": trial.get("finished_at"),
                "usage": {
                    "inputTokens": usage.get("n_input_tokens"),
                    "cachedTokens": usage.get("n_cache_tokens"),
                    "outputTokens": usage.get("n_output_tokens"),
                    "harnessReportedCostUSD": usage.get("cost_usd"),
                    "inferenceEnergyJoules": None,
                    "energyStatus": "not reconciled for this campaign",
                },
                "artifactRegrade": regrade,
                "report": report,
            }
        )
    return {
        "name": directory.name,
        "harborVersion": "0.23.0",
        "startedAt": job["started_at"],
        "finishedAt": job["finished_at"],
        "trials": trials,
        "accepted": sum(t["reward"] == 1 for t in trials),
        "errors": sum(t["exception"] is not None for t in trials),
    }


def main() -> None:
    """Publish selected completed campaigns, verifying shared inputs across model arms."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jobs", nargs="+", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT
        / "docs/initial-implementation/assets/expanded-benchmark-results.json",
    )
    args = parser.parse_args()
    campaigns = [campaign(path) for path in args.jobs]
    paired: dict[str, JSON] = {}
    models = set()
    model_cases: dict[str, set[str]] = {}
    for item in campaigns:
        for trial in item["trials"]:
            if trial["agent"] != "codex":
                continue
            models.add(trial["requestedModel"])
            model_cases.setdefault(trial["requestedModel"], set()).add(trial["case"])
            previous = paired.setdefault(trial["case"], trial["hashes"])
            if previous != trial["hashes"]:
                raise ValueError(f"Paired model inputs differ for {trial['case']}")
    if len({frozenset(cases) for cases in model_cases.values()}) > 1:
        raise ValueError("Model arms have different case coverage")
    value = {
        "schemaVersion": "0.2.0",
        "status": "Public development comparison; no held-out accuracy claim",
        "pairedModels": sorted(models),
        "pairedInputHashesMatch": len(models) > 1,
        "costStatus": "Harness estimates, not reconciled invoices; missing cost/energy is unknown",
        "campaigns": campaigns,
    }
    output = json.dumps(value, indent=2) + "\n"
    for name in ["NEURALWATT_API_KEY", "OPENAI_API_KEY", "TYPESAFE_API_KEY"]:
        key = os.environ.get(name)
        if key and key in output:
            raise ValueError("Refusing to publish a credential")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output)


if __name__ == "__main__":
    main()
