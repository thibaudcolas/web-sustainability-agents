#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = []
# [tool.uv]
# required-version = ">=0.12.20,<0.13"
# ///
"""Render the frozen scope-v1 cases and single graded predictions for scrutiny."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
JSON = dict[str, Any]
MODELS = {
    "openai/gpt-6.1-sol": "GPT-6.1 Sol (high)",
    "neuralwatt/deepseek-v4.1-flash": "DeepSeek V4.1 Flash (high)",
}


def cell(value: Any) -> str:
    """Escape evidence and model text for a Markdown table cell."""
    return str(value).replace("|", "\\|").replace("\n", " ")


def selected(results: JSON, ids: set[str]) -> dict[str, dict[str, JSON]]:
    """Require one graded high-reasoning prediction per model and frozen case."""
    trials: dict[str, dict[str, JSON]] = {model: {} for model in MODELS}
    for campaign in results["campaigns"]:
        for trial in campaign["trials"]:
            model = trial["requestedModel"]
            if model not in trials or trial["exception"] is not None:
                continue
            if trial["case"] in trials[model]:
                raise ValueError("Multiple graded predictions for a model and case")
            if trial["requestedReasoning"] != "high":
                raise ValueError("Scope-v1 comparison requires high reasoning")
            if trial["reward"] not in (0, 1):
                raise ValueError("Missing verifier result for a graded prediction")
            trials[model][trial["case"]] = trial
    if any(set(rows) != ids for rows in trials.values()):
        raise ValueError("Both models need one graded result for every case")
    return trials


def metric(row: JSON) -> str:
    """Display numeric precision, units and evidence basis without relabeling."""
    value = json.dumps(row["value"]) if "value" in row else "missing"
    return f"{value} {row.get('unit', '')} ({row.get('basis', '')})"


def render(corpus: JSON, results: JSON) -> str:
    """Expose all facts, references and model explanations without changing grades."""
    trials = selected(results, {case["id"] for case in corpus["cases"]})
    lines = [
        "# Scope and qualitative case review",
        "",
        "These are public controlled development cases, not held-out accuracy labels or live-site findings. Both model arms requested high reasoning through Codex CLI. Read the [campaign method](scope-benchmark.md) for setup failures, controls, provenance and interpretation limits. Every reference is coordinator-authored; disagreement can identify a model error, an ambiguous task or a deficient reference.",
        "",
        "The verifier checks structured judgments and explanation presence. It does not grade the usefulness or truth of the prose below. References and rationale were withheld from model environments. No prediction was selected by its score.",
        "",
        "| Model | Accepted complete reports | Graded reports |",
        "| --- | --- | --- |",
    ]
    for model, label in MODELS.items():
        rows = trials[model]
        lines.append(
            f"| {label} | {sum(r['reward'] == 1 for r in rows.values())} | {len(rows)} |"
        )
    lines.extend(["", "## Cases", ""])
    for case in corpus["cases"]:
        name = case["id"]
        lines.extend(
            [
                f"### {name}",
                "",
                f"Review dimensions: {', '.join(case['dimensions'])}. Frozen collector handoff required: {'yes' if case['requiresCollector'] else 'no'}.",
                "",
                "Supplied evidence:",
                "",
                "```json",
                json.dumps(case["input"]["facts"], indent=2),
                "```",
                "",
                f"Reference rationale: {case['referenceRationale']}",
                "",
            ]
        )
        for section, request_key, request_field, label_field in [
            ("answers", "questions", "text", "outcome"),
            ("metrics", "metricRequests", "text", "value"),
            (
                "recommendations",
                "recommendationRequests",
                "proposal",
                "action",
            ),
        ]:
            requests = {r["id"]: r[request_field] for r in case["input"][request_key]}
            for expected in case["reference"][section]:
                display = (
                    metric(expected) if section == "metrics" else expected[label_field]
                )
                lines.extend(
                    [
                        f"**{expected['id']}: {requests[expected['id']]}**",
                        "",
                        f"Reference: {display}.",
                        "",
                        "| Model | Judgment | Explanation |",
                        "| --- | --- | --- |",
                    ]
                )
                for model, label in MODELS.items():
                    raw_report = trials[model][name]["report"]
                    report = raw_report if isinstance(raw_report, dict) else {}
                    section_rows = report.get(section)
                    actual = next(
                        (
                            r
                            for r in (
                                section_rows if isinstance(section_rows, list) else []
                            )
                            if isinstance(r, dict) and r.get("id") == expected["id"]
                        ),
                        {},
                    )
                    judgment = (
                        metric(actual)
                        if section == "metrics"
                        else actual.get(label_field, "missing")
                    )
                    explanation = str(actual.get("explanation", "Missing report item"))
                    evidence = actual.get("evidenceIds", [])
                    if isinstance(evidence, list) and evidence:
                        explanation += f" Evidence: {', '.join(map(str, evidence))}."
                    lines.append(
                        f"| {label} | {cell(judgment)} | {cell(explanation)} |"
                    )
                lines.append("")
        for model, label in MODELS.items():
            errors = trials[model][name]["artifactRegrade"]["errors"]
            if errors:
                lines.extend(
                    [f"{label} verifier diagnostics: {cell('; '.join(errors))}.", ""]
                )
    lines.extend(
        [
            "## Review and reproduction",
            "",
            "Identify the case ID and whether feedback concerns supplied facts, claim wording, numeric basis, reference labels, a proposed operation or model interpretation. The [case book](../initial-implementation/assets/scope-benchmark-cases.json) preserves all inputs, references and rationales. The [results](../initial-implementation/assets/scope-benchmark-results.json) retain complete reports, diagnostics and paired hashes. Regenerate with `uv run --locked --script benchmarks/render_scope.py`, then format the generated Markdown with Prettier.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    """Render only the independently inspectable published development artifacts."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cases",
        type=Path,
        default=ROOT / "docs/initial-implementation/assets/scope-benchmark-cases.json",
    )
    parser.add_argument(
        "--results",
        type=Path,
        default=ROOT
        / "docs/initial-implementation/assets/scope-benchmark-results.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "docs/evaluation/scope-review-cases.md",
    )
    args = parser.parse_args()
    args.output.write_text(
        render(json.loads(args.cases.read_text()), json.loads(args.results.read_text()))
    )


if __name__ == "__main__":
    main()
