#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = []
# [tool.uv]
# required-version = ">=0.12.20,<0.13"
# ///
"""Aggregate skill-authored scoped judgments without inventing conformance."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

JSON = dict[str, Any]
ROOT = Path(__file__).resolve().parent.parent
OUTCOMES = {"pass", "fail", "cantTell", "inapplicable", "untested"}


def grouped_outcome(values: list[str]) -> str:
    """Count each guideline once, retaining untested expectations within a group."""
    if "fail" in values:
        return "fail"
    if "cantTell" in values or ("untested" in values and "pass" in values):
        return "cantTell"
    if "untested" in values or not values:
        return "untested"
    return "pass" if "pass" in values else "inapplicable"


def assess(review: JSON, rubric: JSON, weights: JSON) -> JSON:
    """Calculate scoped pass counts and weights, keeping every guideline visible."""
    catalog = {row["number"]: row for row in rubric["guidelines"]}
    if len(catalog) != len(rubric["guidelines"]):
        raise ValueError("Duplicate rubric guideline")
    groups: dict[str, list[JSON]] = {}
    for row in review["rows"]:
        number = row["guideline"]
        if number not in catalog or not catalog[number]["expectation"]:
            raise ValueError("Judgment outside the supported rubric")
        if row["outcome"] not in OUTCOMES:
            raise ValueError("Invalid judgment outcome")
        if (
            not isinstance(row.get("rationale"), str)
            or len(row["rationale"].strip()) < 20
        ):
            raise ValueError("Judgment requires a substantive rationale")
        ids = row.get("evidenceIds")
        if not isinstance(ids, list) or any(
            not isinstance(i, str) or not i for i in ids
        ):
            raise ValueError("Invalid evidence identifiers")
        if row["outcome"] in {"pass", "fail"} and not ids:
            raise ValueError("A decisive judgment requires evidence")
        index = review.get("evidenceIndex", {})
        for identifier in ids:
            resolved = index.get(identifier)
            if not isinstance(resolved, dict) or not all(
                isinstance(resolved.get(key), str) and resolved[key]
                for key in ["artifact", "jsonPointer", "sourceSHA256"]
            ):
                raise ValueError(
                    "Every cited identifier needs resolved evidence provenance"
                )
        groups.setdefault(number, []).append(row)
    rows: list[JSON] = []
    for number, rule in catalog.items():
        weight = weights["weights"][number]
        if (
            isinstance(weight, bool)
            or not isinstance(weight, (int, float))
            or not math.isfinite(weight)
            or weight < 0
        ):
            raise ValueError("Impact weights must be finite and nonnegative")
        judgments = groups.get(number, [])
        rows.append(
            {
                **rule,
                "outcome": grouped_outcome([row["outcome"] for row in judgments]),
                "impactWeight": weight,
                "judgments": judgments,
                "conformance": "not_determined",
            }
        )
    counts = Counter(row["outcome"] for row in rows)
    checked = counts["pass"] + counts["fail"] + counts["cantTell"]
    checked_weight = sum(
        row["impactWeight"]
        for row in rows
        if row["outcome"] in {"pass", "fail", "cantTell"}
    )
    passed_weight = sum(row["impactWeight"] for row in rows if row["outcome"] == "pass")
    return {
        "site": review["site"],
        "rubricVersion": rubric["rubricVersion"],
        "label": "Scoped WSG audit score",
        "value": 100 * counts["pass"] / checked if checked else None,
        "unit": "percent",
        "formula": "100 * passed / (passed + failed + cantTell), grouped once per guideline",
        "counts": {key: counts[key] for key in sorted(OUTCOMES)},
        "checkedGuidelines": checked,
        "totalGuidelines": len(rows),
        "checkedCoveragePercent": 100 * checked / len(rows) if rows else None,
        "supportedByMethod": sum(bool(row["expectation"]) for row in rows),
        "fullGuidelinesVerified": 0,
        "impactWeighted": {
            "value": 100 * passed_weight / checked_weight if checked_weight else None,
            "passedWeight": passed_weight,
            "checkedWeight": checked_weight,
            "status": "Experimental project convention using WSG impact priority points; not a W3C site score",
        },
        "interpretation": "Passes satisfy only the declared scoped expectations; unknowns earn no points but are not defects. Compare only matching rubric, sample, and evidence profiles.",
        "guidelines": rows,
    }


def main() -> None:
    """Publish reproducible scores from explicit reviewer output and pinned rubric."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reviews",
        type=Path,
        default=ROOT / "docs/initial-implementation/assets/skill-reviews.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "docs/initial-implementation/assets/scored-audits.json",
    )
    parser.add_argument("--rubric", type=Path, default=ROOT / "audit/rubric.json")
    parser.add_argument(
        "--weights", type=Path, default=ROOT / "audit/impact-weights.json"
    )
    parser.add_argument(
        "--assets", type=Path, default=ROOT / "docs/initial-implementation/assets"
    )
    args = parser.parse_args()
    paths = {
        "reviews": args.reviews,
        "rubric": args.rubric,
        "impactWeights": args.weights,
    }
    raw = {key: path.read_bytes() for key, path in paths.items()}
    data = {key: json.loads(value) for key, value in raw.items()}
    validate_provenance(data["reviews"], raw["rubric"], args.assets)
    sites = [review["site"] for review in data["reviews"]["reviews"]]
    if len(set(sites)) != len(sites):
        raise ValueError("Each site needs one reconciled review")
    result = {
        "schemaVersion": "0.1.0",
        "sourceSHA256": {
            key: hashlib.sha256(value).hexdigest() for key, value in raw.items()
        },
        "scores": [
            assess(review, data["rubric"], data["impactWeights"])
            for review in data["reviews"]["reviews"]
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")


def validate_provenance(reviews: JSON, rubric_raw: bytes, assets: Path) -> None:
    """Reject stale rubrics, changed evidence, and fabricated indexed locations."""
    if reviews.get("rubricSHA256") != hashlib.sha256(rubric_raw).hexdigest():
        raise ValueError("Reviews were made against a different rubric")
    sources = {}
    for name, expected in reviews["sourceSHA256"].items():
        if Path(name).name != name:
            raise ValueError("Invalid source artifact name")
        raw = (assets / name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError("Review source provenance changed")
        sources[name] = json.loads(raw)
    for review in reviews["reviews"]:
        for entry in review["evidenceIndex"].values():
            name = entry["artifact"]
            if (
                name not in sources
                or entry["sourceSHA256"] != reviews["sourceSHA256"][name]
            ):
                raise ValueError("Indexed source provenance changed")
            value = sources[name]
            pointer = entry["jsonPointer"]
            if not isinstance(pointer, str) or not pointer.startswith("/"):
                raise ValueError("Invalid indexed JSON Pointer")
            try:
                for part in pointer[1:].split("/"):
                    key = part.replace("~1", "/").replace("~0", "~")
                    if isinstance(value, list):
                        if not key.isdecimal():
                            raise ValueError("Invalid array pointer")
                        value = value[int(key)]
                    else:
                        value = value[key]
            except (KeyError, IndexError, TypeError) as error:
                raise ValueError("Indexed evidence does not exist") from error


if __name__ == "__main__":
    main()
