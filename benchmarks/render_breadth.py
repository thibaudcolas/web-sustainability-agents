#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = []
# [tool.uv]
# required-version = ">=0.12.20,<0.13"
# ///
"""Render frozen breadth cases and both model outputs for owner review."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

JSON = dict[str, Any]
ROOT = Path(__file__).resolve().parent.parent
MODELS = {
    "openai/gpt-6.1-sol": "Sol/low",
    "neuralwatt/deepseek-v4.1-flash": "DeepSeek/high",
}


def cell(value: Any) -> str:
    """Escape a single Markdown table cell."""
    return str(value).replace("|", "\\|").replace("\n", " ")


def metric(row: JSON) -> str:
    """Preserve supplied numeric value, unit and evidence basis."""
    return (
        f"{json.dumps(row.get('value'))} {row.get('unit', '')} ({row.get('basis', '')})"
    )


def selected(results: JSON, ids: set[str]) -> dict[str, dict[str, JSON]]:
    """Select the one graded attempt per model/case; never choose a best prediction."""
    trials: dict[str, dict[str, JSON]] = {model: {} for model in MODELS}
    for campaign in results["campaigns"]:
        for trial in campaign["trials"]:
            model = trial["requestedModel"]
            if model not in trials or trial["exception"] is not None:
                continue
            if trial["case"] in trials[model]:
                raise ValueError(
                    "Multiple graded predictions; specify an explicit comparison protocol"
                )
            trials[model][trial["case"]] = trial
    if any(set(rows) != ids for rows in trials.values()):
        raise ValueError("Both models need one graded result for every case")
    return trials


def render(corpus: JSON, results: JSON, wsg: JSON) -> str:
    """Expose facts, expected judgments, outputs and explanations without changing grades."""
    trials = selected(results, {case["id"] for case in corpus["cases"]})
    links = {row["id"]: row["url"] for row in wsg["guidelines"]}
    lines = [
        "# Broader eval case review",
        "",
        "This page shows all sixteen frozen development cases and the two graded model outputs. Facts are synthetic; these are not additional measurements of either Wagtail site. Expected labels are author-created references for review, not independent ground truth. Setup failures are recorded in the [campaign results](breadth-benchmark.md#completed-model-comparison); this page shows the one graded prediction per model and case, including unchanged-input retries after setup failures.",
        "",
        "Review the facts, expected outcome and explanation together. A supported claim about uncertainty can require a different label from an unresolved site state. The dependency case exposes that distinction; the form case exposes a count-of-observations versus unavailable-measurement distinction. Original scores remain unchanged.",
        "",
        "| Case | Sol/low | DeepSeek/high |",
        "| --- | --- | --- |",
    ]
    for case in corpus["cases"]:
        outcomes = [
            "Accepted" if trials[model][case["id"]]["reward"] == 1 else "Rejected"
            for model in MODELS
        ]
        lines.append(f"| [{case['id']}](#{case['id']}) | {' | '.join(outcomes)} |")
    for case in corpus["cases"]:
        identifier = case["id"]
        reports = {model: trials[model][identifier]["report"] for model in MODELS}
        lines += [
            "",
            f"## {identifier.replace('-', ' ').capitalize()}",
            "",
            f"Case ID: `{identifier}`. WSG: "
            + ", ".join(f"[{number}]({links[number]})" for number in case["guidelines"])
            + ". "
            + (
                "A collection artifact is required."
                if case.get("requiresCollector")
                else "Evidence is provided directly."
            ),
            "",
            "### Supplied evidence",
            "",
            "```json",
            json.dumps(case["input"]["facts"], indent=2),
            "```",
            "",
            "### Claims and numeric request",
            "",
            "| ID / proposition | Expected | Sol/low | DeepSeek/high |",
            "| --- | --- | --- | --- |",
        ]
        for question in case["input"]["questions"]:
            expected = next(
                row
                for row in case["reference"]["answers"]
                if row["id"] == question["id"]
            )
            outcomes = [
                next(
                    (
                        row["outcome"]
                        for row in report["answers"]
                        if row["id"] == question["id"]
                    ),
                    "missing",
                )
                for report in reports.values()
            ]
            lines.append(
                f"| `{question['id']}`: {cell(question['text'])} | {expected['outcome']} | {' | '.join(outcomes)} |"
            )
        for request in case["input"]["metricRequests"]:
            expected = next(
                row
                for row in case["reference"]["metrics"]
                if row["id"] == request["id"]
            )
            outputs = [
                next(
                    (
                        metric(row)
                        for row in report["metrics"]
                        if row["id"] == request["id"]
                    ),
                    "missing",
                )
                for report in reports.values()
            ]
            lines.append(
                f"| `{request['id']}`: {cell(request['text'])} | {metric(expected)} | {' | '.join(outputs)} |"
            )
        lines += ["", "### Proposed operation and model explanations", ""]
        for request in case["input"]["recommendationRequests"]:
            expected = next(
                row
                for row in case["reference"]["recommendations"]
                if row["id"] == request["id"]
            )
            lines += [
                f"`{request['id']}`: {request['proposal']} **Expected action: `{expected['action']}`.**",
                "",
            ]
            for model, report in reports.items():
                row = next(
                    row
                    for row in report["recommendations"]
                    if row["id"] == request["id"]
                )
                lines += [
                    f"**{MODELS[model]} — `{row['action']}`:** {row['explanation']}",
                    "",
                ]
        for model, report in reports.items():
            errors = trials[model][identifier]["artifactRegrade"]["errors"]
            if errors:
                lines += [
                    f"**{MODELS[model]} strict diagnostics:** "
                    + "; ".join(errors)
                    + ".",
                    "",
                ]
                for error in errors:
                    parts = error.split(":", 1)[0].split("/")
                    if len(parts) == 2 and parts[0] in report:
                        row = next(
                            (row for row in report[parts[0]] if row["id"] == parts[1]),
                            {},
                        )
                        lines += [
                            row.get("explanation", "No explanation available."),
                            "",
                        ]
        if identifier == "dependency-declared-not-installed":
            lines += [
                "**Owner review needed:** Both models identify the deployed version as unknown and reject an unsupported upgrade, but return `inconclusive` for the proposition that the version is unresolved. The reference treats that proposition as a supported claim (`pass`). The instruction's exception for unresolved direct-state questions makes this distinction fragile. A future case version should declare question mode explicitly; this case and its scores remain frozen.",
                "",
            ]
        if identifier == "form-validation-task":
            lines += [
                "**Owner review needed:** The reference counts zero documented successful submissions; both models return null because valid submission was never tested. The input contains no explicit successful-submission counter. A future case should distinguish an observed-event count from an unmeasured success result, rather than inferring both from the same wording.",
                "",
            ]
    lines += [
        "## Feedback and reproduction",
        "",
        "For feedback, identify the case ID and whether the issue is a missing fact, reference label, question mode, recommendation operation or model interpretation. The [JSON case book](assets/breadth-benchmark-cases.json) preserves full inputs and references; [results](assets/breadth-benchmark-results.json) retain reports, diagnostics, hashes and setup errors. The [benchmark method](breadth-benchmark.md) describes controls and limits. Regenerate this page with `uv run --locked --script benchmarks/render_breadth.py`, then format Markdown with Prettier. No result is relabeled by this renderer.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    """Render completed, paired development results."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results",
        type=Path,
        default=ROOT
        / "docs/initial-implementation/assets/breadth-benchmark-results.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "docs/initial-implementation/breadth-review-cases.md",
    )
    args = parser.parse_args()
    corpus = json.loads((ROOT / "benchmarks/breadth-cases.json").read_text())
    results = json.loads(args.results.read_text())
    wsg = json.loads(
        (
            ROOT / ".agents/skills/sustainability-guideline-review/references/wsg.json"
        ).read_text()
    )
    args.output.write_text(render(corpus, results, wsg))


if __name__ == "__main__":
    main()
