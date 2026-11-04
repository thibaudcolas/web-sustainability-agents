#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = []
# [tool.uv]
# required-version = ">=0.12.20,<0.13"
# ///
"""Export per-origin report data and long-form observations for future charts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

JSON = dict[str, Any]
ROOT = Path(__file__).resolve().parent.parent


def display_bytes(value: float) -> str:
    """Format decimal units while preserving base bytes in the data contract."""
    return (
        f"{value / 1_000_000:.2f} MB"
        if abs(value) >= 1_000_000
        else f"{value / 1000:.1f} KB"
    )


def export_reports(evidence: JSON, digest: str) -> dict[str, JSON]:
    """Separate origins and keep metric units, provenance, and phase semantics."""
    reports: dict[str, JSON] = {}
    for run in evidence["runs"]:
        url = urlsplit(run["url"])
        origin = f"{url.scheme}://{url.netloc}"
        report = reports.setdefault(
            origin,
            {
                "schemaVersion": "0.3.0",
                "site": origin,
                "sourceSHA256": digest,
                "protocol": evidence["protocol"],
                "overallScore": {
                    "value": None,
                    "status": "not_assessed",
                    "reason": "No validated aggregate WSG scoring model; bounded sample only.",
                },
                "headline": [],
                "observations": [],
                "ratings": [],
                "chartContracts": [
                    {
                        "id": "phase-traffic",
                        "metric": "received_bytes",
                        "unit": "B",
                        "displayUnit": "KB",
                        "x": "phase",
                        "series": ["pageUrl", "branch"],
                        "aggregation": "none",
                        "note": "Cumulative totals: never stack phases; partial observations must remain labeled.",
                    },
                    {
                        "id": "incremental-traffic",
                        "metric": "additional_bytes",
                        "unit": "B",
                        "displayUnit": "KB",
                        "x": "phase",
                        "series": ["pageUrl", "branch"],
                        "aggregation": "none",
                        "note": "Time-window increments, not causal savings. Keep independent branches separate.",
                    },
                    {
                        "id": "resource-composition",
                        "metric": "resource_bytes",
                        "unit": "B",
                        "displayUnit": "KB",
                        "x": "category",
                        "series": ["runId", "phase"],
                        "aggregation": "sum within a run and phase only",
                    },
                ],
            },
        )
        for phase in run["phases"]:
            common = {
                "site": origin,
                "runId": run["id"],
                "pageUrl": run["url"],
                "branch": run["branch"],
                "phase": phase["phase"],
                "capturedAt": phase["capturedAt"],
                "status": phase["accountingStatus"],
                "basis": "observed",
                "sourceId": f"{run['id']}/{phase['phase']}",
                "sourceSHA256": digest,
            }
            for metric, field in [
                ("received_bytes", "receivedBytes"),
                ("additional_bytes", "additionalBytes"),
            ]:
                report["observations"].append(
                    {
                        **common,
                        "metric": metric,
                        "value": phase[field],
                        "unit": "B",
                        "category": "all",
                    }
                )
            categories: dict[str, int] = {}
            for resource in phase["resources"]:
                category = resource.get("type") or "Other"
                value = resource.get("receivedBytes")
                categories[category] = categories.get(category, 0) + (
                    value if value is not None else resource.get("partialBodyBytes", 0)
                )
            for category, value in sorted(categories.items()):
                report["observations"].append(
                    {
                        **common,
                        "metric": "resource_bytes",
                        "value": value,
                        "unit": "B",
                        "category": category,
                    }
                )
            if phase["phase"] == "initial":
                report["headline"].append(
                    {
                        **common,
                        "receivedBytes": phase["receivedBytes"],
                        "display": display_bytes(phase["receivedBytes"]),
                        "requestCount": phase["requestCount"],
                    }
                )
        report["ratings"].append(
            {
                "runId": run["id"],
                "phase": "initial",
                "basis": "modeled",
                "rating": run["rating"],
            }
        )
    return reports


def main() -> None:
    """Write JSON envelopes and equivalent CSV metric rows for each audited origin."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "docs/initial-implementation/assets/staged-audit.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "docs/initial-implementation/assets/reports",
    )
    args = parser.parse_args()
    raw = args.input.read_bytes()
    reports = export_reports(json.loads(raw), hashlib.sha256(raw).hexdigest())
    args.output.mkdir(parents=True, exist_ok=True)
    for origin, report in reports.items():
        name = urlsplit(origin).netloc.replace(".", "-").replace(":", "-")
        (args.output / f"{name}.json").write_text(json.dumps(report, indent=2) + "\n")
        with (args.output / f"{name}.csv").open("w", newline="") as output:
            rows = report["observations"]
            if rows:
                writer = csv.DictWriter(output, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)


if __name__ == "__main__":
    main()
