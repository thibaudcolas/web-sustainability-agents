#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = []
# [tool.uv]
# required-version = ">=0.12.20,<0.13"
# ///
"""Grade protected structured judgments, numeric claims, and recommendation decisions."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

JSON = dict[str, Any]


def grade(report: Any, reference: JSON) -> JSON:
    """Check semantic labels and units without pretending to score prose usefulness."""
    errors: list[str] = []
    if not isinstance(report, dict) or report.get("schemaVersion") != "0.2.0":
        return {"reward": 0, "errors": ["Invalid report structure"]}
    summary = report.get("summary")
    if (
        not isinstance(summary, dict)
        or summary.get("site") != reference["site"]
        or "overallScore" not in summary
        or summary["overallScore"] is not None
    ):
        errors.append("Invalid site scope or invented overall score")
    for section in ["answers", "metrics", "recommendations"]:
        rows = report.get(section)
        if not isinstance(rows, list) or any(
            not isinstance(r, dict) or not isinstance(r.get("id"), str) for r in rows
        ):
            errors.append(f"Invalid {section}")
            continue
        expected_rows = reference[section]
        if (
            len(rows) != len(expected_rows)
            or len({r["id"] for r in rows}) != len(rows)
            or {r["id"] for r in rows} != {r["id"] for r in expected_rows}
        ):
            errors.append(f"Wrong or duplicate {section} IDs")
        for expected in expected_rows:
            actual: JSON = next((r for r in rows if r["id"] == expected["id"]), {})
            key = f"{section}/{expected['id']}"
            if section == "metrics":
                value = actual.get("value")
                number = expected["value"]
                valid = (
                    value is None
                    if number is None
                    else isinstance(value, (float, int))
                    and not isinstance(value, bool)
                    and math.isfinite(value)
                    and math.isclose(value, number, rel_tol=1e-6, abs_tol=1e-6)
                )
                if (
                    "value" not in actual
                    or not valid
                    or actual.get("unit") != expected["unit"]
                    or actual.get("basis") != expected["basis"]
                ):
                    errors.append(f"{key}: incorrect value, unit, or basis")
            else:
                field = "outcome" if section == "answers" else "action"
                if actual.get(field) != expected[field]:
                    errors.append(f"{key}: incorrect {field}")
                ids = actual.get("evidenceIds")
                if (
                    not isinstance(ids, list)
                    or not all(isinstance(v, str) for v in ids)
                    or not set(expected["evidenceIds"]) <= set(ids)
                    or not set(ids) <= set(reference["allowedEvidenceIds"])
                ):
                    errors.append(f"{key}: missing or fabricated evidence")
            if (
                not isinstance(actual.get("explanation"), str)
                or len(actual["explanation"].strip()) < 20
            ):
                errors.append(f"{key}: missing explanation")
    return {"reward": int(not errors), "errors": errors}


def main() -> None:
    """Run inside Harbor's separate verifier; malformed reports fail without hiding infrastructure errors."""
    reference = json.loads(Path("/tests/reference.json").read_text())
    try:
        raw = Path("/app/output/report.json").read_text()
        report = json.loads(raw) if len(raw) <= 100_000 else None
    except FileNotFoundError, json.JSONDecodeError:
        report = None
    result = grade(report, reference)
    output = Path("/logs/verifier")
    output.mkdir(parents=True, exist_ok=True)
    (output / "reward.txt").write_text(str(result["reward"]))
    (output / "diagnostics.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
