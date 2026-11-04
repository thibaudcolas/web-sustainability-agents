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
import re
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


def invokes_collector(arguments: Any) -> bool:
    """Recognize an executed collector command, excluding source-file reads."""
    if not isinstance(arguments, dict):
        return False
    command = arguments.get("cmd")
    if isinstance(command, str) and re.search(
        r"(?:^|[;&\n])\s*python3?\s+/app/collect\.py(?:\s|$)", command
    ):
        return True
    code = arguments.get("input")
    return isinstance(code, str) and bool(
        re.search(
            r"(?:[\"']cmd[\"']|\bcmd)\s*:\s*[\"']python3?\s+/app/collect\.py\b",
            code,
        )
    )


def execution_evidence(directory: Path, agent: JSON) -> JSON:
    """Publish only runtime setting fields and hashes from private native traces."""
    contexts: list[JSON] = []
    for path in sorted(directory.glob("agent/sessions/**/*.jsonl")):
        values: list[JSON] = []
        for line in path.read_text().splitlines():
            entry = json.loads(line)
            if entry.get("type") == "turn_context":
                payload = entry.get("payload", {})
                values.append(
                    {
                        "model": payload.get("model"),
                        "reasoningEffort": payload.get("effort"),
                    }
                )
        contexts.append({"traceSHA256": digest(path), "turnContexts": values})
    calls: list[JSON] = []
    trajectory = directory / "agent/trajectory.json"
    recorded_agent: JSON = {}
    if trajectory.exists():
        trace = json.loads(trajectory.read_text())
        recorded_agent = trace.get("agent", {})
        for step in trace.get("steps", []):
            for call in step.get("tool_calls", []):
                arguments = call.get("arguments")
                if not invokes_collector(arguments):
                    continue
                observations = [
                    row
                    for row in (step.get("observation") or {}).get("results", [])
                    if row.get("source_call_id") == call.get("tool_call_id")
                ]
                calls.append(
                    {
                        "stepId": step.get("step_id"),
                        "function": call.get("function_name"),
                        "toolCallId": call.get("tool_call_id"),
                        "argumentsSHA256": hashlib.sha256(
                            json.dumps(arguments, sort_keys=True).encode()
                        ).hexdigest(),
                        "returnedObservationPresent": bool(observations),
                        "observationsSHA256": hashlib.sha256(
                            json.dumps(observations, sort_keys=True).encode()
                        ).hexdigest(),
                    }
                )
    observed = [row for trace in contexts for row in trace["turnContexts"]]
    model = agent.get("model_name", "").split("/")[-1]
    effort = agent.get("kwargs", {}).get("reasoning_effort")
    return {
        "scope": "Recorded native CLI settings and returned tool observations; not independent verification of provider computation or live browsing.",
        "nativeTraces": contexts,
        "recordedAgent": {
            "name": recorded_agent.get("name"),
            "version": recorded_agent.get("version"),
            "model": recorded_agent.get("model_name"),
        },
        "nativeSettingsMatchRequested": all(
            row["model"] == model and row["reasoningEffort"] == effort
            for row in observed
        )
        if observed
        else None,
        "trajectorySHA256": digest(trajectory) if trajectory.exists() else None,
        "collectorInvocations": calls,
    }


def campaign(directory: Path, breadth: bool = False, scope: bool = False) -> JSON:
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
            ROOT
            / "benchmarks"
            / ("grade_breadth.py" if breadth else "grade_expanded.py")
        ):
            raise ValueError("Refusing an implicit grader change")
        collection_path = path.parent / "artifacts/app/output/collection.json"
        collection = None
        if breadth:
            if digest(task / "tests/grade_expanded.py") != digest(
                ROOT / "benchmarks/grade_expanded.py"
            ):
                raise ValueError("Refusing an implicit base grader change")
            try:
                collection = json.loads(collection_path.read_text())
            except FileNotFoundError, UnicodeError, json.JSONDecodeError:
                pass
            breadth_grade = cast(
                Callable[[Any, JSON, Any], JSON],
                importlib.import_module("benchmarks.grade_breadth").grade,
            )
            regrade = breadth_grade(report, reference, collection)
        else:
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
                    **(
                        {
                            "extraResources": {
                                str(p.relative_to(task)): digest(p)
                                for p in [
                                    task / "environment/bundle.json",
                                    task / "environment/collect.py",
                                    task / "tests/grade_expanded.py",
                                ]
                                if p.exists()
                            }
                        }
                        if breadth
                        else {}
                    ),
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
                **(
                    {"executionEvidence": execution_evidence(path.parent, agent)}
                    if scope and agent["name"] == "codex"
                    else {}
                ),
                **(
                    {
                        "collectionRequired": "requiredCollection" in reference,
                        "collectionArtifactSHA256": digest(collection_path)
                        if collection_path.exists()
                        else None,
                        "collectionMatchesReference": collection
                        == reference.get("requiredCollection")
                        if "requiredCollection" in reference
                        else None,
                    }
                    if breadth
                    else {}
                ),
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
    families = parser.add_mutually_exclusive_group()
    families.add_argument("--breadth", action="store_true")
    families.add_argument("--scope", action="store_true")
    args = parser.parse_args()
    if (
        (args.breadth or args.scope)
        and args.output
        == ROOT / "docs/initial-implementation/assets/expanded-benchmark-results.json"
    ):
        args.output = ROOT / (
            "docs/initial-implementation/assets/scope-benchmark-results.json"
            if args.scope
            else "docs/initial-implementation/assets/breadth-benchmark-results.json"
        )
    campaigns = [
        campaign(path, args.breadth or args.scope, args.scope) for path in args.jobs
    ]
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
