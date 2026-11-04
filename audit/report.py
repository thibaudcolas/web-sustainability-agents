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
        else f"{value / 1000:.1f} kB"
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
                    "reason": "No scoped review supplied to this export; calculate a versioned assessment with audit/assess.py.",
                },
                "headline": [],
                "observations": [],
                "ratings": [],
                "chartContracts": [
                    {
                        "id": "phase-traffic",
                        "metric": "received_bytes",
                        "unit": "B",
                        "displayUnit": "kB",
                        "x": "phase",
                        "series": ["pageUrl", "branch"],
                        "aggregation": "none",
                        "note": "Cumulative totals: never stack phases; partial observations must remain labeled.",
                    },
                    {
                        "id": "incremental-traffic",
                        "metric": "additional_bytes",
                        "unit": "B",
                        "displayUnit": "kB",
                        "x": "phase",
                        "series": ["pageUrl", "branch"],
                        "aggregation": "none",
                        "note": "Time-window increments, not causal savings. Keep independent branches separate.",
                    },
                    {
                        "id": "resource-composition",
                        "metric": "resource_bytes",
                        "unit": "B",
                        "displayUnit": "kB",
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


def enrich_reports(
    reports: dict[str, JSON],
    energy: JSON,
    traffic: JSON,
    energy_digest: str,
    traffic_digest: str,
) -> None:
    """Append independent energy and traffic series without combining incompatible metrics."""
    for run in energy.get("runs", []):
        parsed = urlsplit(run["url"])
        site = f"{parsed.scheme}://{parsed.netloc}"
        if site not in reports:
            continue
        measured = run["energy"]
        status = (
            measured["status"]
            if run.get("journeyStatus") == "completed"
            else "journey_failed"
        )
        if measured.get("allZero"):
            status = "sensor_plausibility_unknown"
        reports[site]["observations"].append(
            {
                "site": site,
                "runId": run["id"],
                "pageUrl": run["url"],
                "branch": "no_interaction",
                "phase": "whole_browser_session",
                "capturedAt": run["capturedAt"],
                "status": status,
                "basis": "observed",
                "sourceId": f"energy/{run['id']}",
                "sourceSHA256": energy_digest,
                "metric": "cpu_package_energy",
                "value": measured.get("joules"),
                "unit": "J",
                "category": "CPU package",
                "scope": measured.get("scope"),
                "protocolId": "co2-runner-firefox-session-v1",
                "durationMs": measured.get("sessionDurationMs"),
            }
        )
    for item in traffic.get("results", []):
        site = item["origin"]
        if site not in reports:
            continue
        scenario = item["traffic"]
        reports[site]["observations"].append(
            {
                "site": site,
                "runId": f"crux-{traffic.get('datasetMonth', 'unknown')}",
                "pageUrl": None,
                "branch": None,
                "phase": "annual_scenario",
                "capturedAt": traffic.get("capturedAt"),
                "status": scenario["status"],
                "basis": "scenario",
                "sourceId": f"traffic/{site}",
                "sourceSHA256": traffic_digest,
                "metric": "estimated_annual_pageviews",
                "value": scenario.get("annualPageviews"),
                "unit": "pageviews/year",
                "category": "rank bucket median",
                "scope": scenario.get("calibrationPopulation"),
                "datasetMonth": traffic.get("datasetMonth"),
                "rankBucket": item.get("rankBucket"),
            }
        )
    for report in reports.values():
        report["chartContracts"].extend(
            [
                {
                    "id": "session-energy",
                    "metric": "cpu_package_energy",
                    "unit": "J",
                    "x": "runId",
                    "series": ["pageUrl", "protocolId"],
                    "aggregation": "individual repetitions; median and range only for measured, completed, plausible counters",
                    "note": "Whole-system CPU package; different browser/viewport from traffic phases. Do not add to SWDM.",
                },
                {
                    "id": "traffic-scenario",
                    "metric": "estimated_annual_pageviews",
                    "unit": "pageviews/year",
                    "x": "datasetMonth",
                    "series": ["site"],
                    "aggregation": "none",
                    "note": "Scenario point, not actual analytics or a confidence interval. Missing values remain unknown.",
                },
            ]
        )


def report_stem(origin: str) -> str:
    """Use scheme and origin digest to avoid cross-site filename collisions."""
    parsed = urlsplit(origin)
    host = parsed.netloc.replace(".", "-").replace(":", "-")
    return f"{parsed.scheme}-{host}-{hashlib.sha256(origin.encode()).hexdigest()[:12]}"


def enrich_assessment(
    reports: dict[str, JSON],
    assessments: JSON,
    annual: JSON,
    assessment_digest: str,
    annual_digest: str,
) -> None:
    """Attach scoped scores and labeled annual scenarios as separate chart series."""
    for score in assessments.get("scores", []):
        site = score["site"]
        if site not in reports:
            continue
        report = reports[site]
        report["schemaVersion"] = "0.4.0"
        report["overallScore"] = {
            key: value for key, value in score.items() if key != "guidelines"
        }
        report["observations"].append(
            {
                "site": site,
                "metric": "scoped_audit_score",
                "value": score["value"],
                "unit": "percent",
                "phase": "evidence_review",
                "basis": "calculated",
                "status": "provisional_scoped_rubric",
                "sourceId": f"assessment/{site}",
                "sourceSHA256": assessment_digest,
                "rubricVersion": score["rubricVersion"],
                "checkedGuidelines": score["checkedGuidelines"],
                "totalGuidelines": score["totalGuidelines"],
            }
        )
        report["chartContracts"].append(
            {
                "id": "scoped-score",
                "metric": "scoped_audit_score",
                "unit": "percent",
                "x": "site",
                "series": ["rubricVersion"],
                "aggregation": "none",
                "note": "Display pass/fail/unknown counts and checked/total coverage; compare only matching rubric and sample. Not a conformance percentage.",
            }
        )
    for scenario in annual.get("scenarios", []):
        site = scenario["site"]
        if site not in reports:
            continue
        report = reports[site]
        report["annualFootprint"] = scenario
        sensitivity = scenario.get("sensitivityKgPerYear", {})
        report["observations"].append(
            {
                "site": site,
                "metric": "annual_browsing_footprint",
                "value": scenario["value"],
                "unit": "kgCO2e/year",
                "phase": "annual_scenario",
                "basis": "scenario",
                "status": scenario["status"],
                "transferInputs": scenario.get("transferInputs"),
                "sourceId": f"annual/{site}",
                "sourceSHA256": annual_digest,
                "sensitivityLow": sensitivity.get("lowestSampledPage"),
                "sensitivityHigh": sensitivity.get("highestSampledPage"),
            }
        )
        report["chartContracts"].append(
            {
                "id": "annual-footprint",
                "metric": "annual_browsing_footprint",
                "unit": "kgCO2e/year",
                "x": "site",
                "aggregation": "none",
                "note": "Assumed page mix and rank-derived traffic; show partial-input status. Sensitivity cases are not confidence intervals; never add measured package energy.",
            }
        )


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
    parser.add_argument(
        "--energy",
        type=Path,
        default=ROOT / "docs/initial-implementation/assets/energy-experiment.json",
    )
    parser.add_argument(
        "--traffic",
        type=Path,
        default=ROOT / "docs/initial-implementation/assets/traffic-scenarios.json",
    )
    parser.add_argument(
        "--assessments",
        type=Path,
        default=ROOT / "docs/initial-implementation/assets/scored-audits.json",
    )
    parser.add_argument(
        "--annual",
        type=Path,
        default=ROOT / "docs/initial-implementation/assets/annual-footprints.json",
    )
    args = parser.parse_args()
    raw = args.input.read_bytes()
    reports = export_reports(json.loads(raw), hashlib.sha256(raw).hexdigest())
    enrichments = []
    for path in [args.energy, args.traffic]:
        source = path.read_bytes() if path.exists() else b"{}"
        enrichments.append((json.loads(source), hashlib.sha256(source).hexdigest()))
    enrich_reports(
        reports,
        enrichments[0][0],
        enrichments[1][0],
        enrichments[0][1],
        enrichments[1][1],
    )
    optional = [
        path.read_bytes() if path.exists() else b"{}"
        for path in [args.assessments, args.annual]
    ]
    enrich_assessment(
        reports,
        json.loads(optional[0]),
        json.loads(optional[1]),
        hashlib.sha256(optional[0]).hexdigest(),
        hashlib.sha256(optional[1]).hexdigest(),
    )
    args.output.mkdir(parents=True, exist_ok=True)
    for origin, report in reports.items():
        name = report_stem(origin)
        (args.output / f"{name}.json").write_text(json.dumps(report, indent=2) + "\n")
        with (args.output / f"{name}.csv").open("w", newline="") as output:
            rows = report["observations"]
            if rows:
                writer = csv.DictWriter(
                    output,
                    fieldnames=list(dict.fromkeys(key for row in rows for key in row)),
                    lineterminator="\n",
                )
                writer.writeheader()
                writer.writerows(rows)


if __name__ == "__main__":
    main()
