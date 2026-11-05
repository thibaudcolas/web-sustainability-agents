#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = []
# [tool.uv]
# required-version = ">=0.12.20,<0.13"
# ///
"""Estimate annual browsing emissions from declared page-mix and traffic proxies."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import statistics
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from audit.report_details import (  # noqa: E402 # ty: ignore[unresolved-import]
    energy_rows,
)

JSON = dict[str, Any]
ROOT = Path(__file__).resolve().parent.parent
BRIDGE = """import {readFileSync} from 'node:fs';
import {co2} from '@tgwf/co2';
const model = new co2({model:'swd',version:4});
const bytes = JSON.parse(readFileSync(0,'utf8'));
process.stdout.write(JSON.stringify(bytes.map(b=>model.perVisitTrace(b,false,{firstVisitPercentage:1,returnVisitPercentage:0,dataReloadRatio:0.02}))));
"""


def nonnegative(value: Any) -> bool:
    """Reject unknown, Boolean, nonfinite, negative, and oversized inputs."""
    try:
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(value)
            and value >= 0
        )
    except OverflowError:
        return False


def pageview_count(site: str, traffic: JSON) -> float | None:
    """Require the exact origin and an observed rank mapped to a finite count."""
    count = traffic.get("traffic", {}).get("annualPageviews")
    if (
        traffic.get("origin") != site
        or traffic.get("rankBucket") is None
        or not isinstance(traffic.get("rankBucket"), int)
        or isinstance(traffic.get("rankBucket"), bool)
        or traffic["rankBucket"] <= 0
        or traffic.get("traffic", {}).get("status") != "scenario"
        or not nonnegative(count)
    ):
        return None
    return float(count)


def annual_scenario(
    site: str, pages: list[JSON], traffic: JSON, selection: str = "branch-mean"
) -> JSON:
    """Apply an explicit equal-page proxy; never imply an observed site-wide mix."""
    result: JSON = {
        "site": site,
        "basis": "scenario",
        "unit": "kgCO2e/year",
        "status": "unavailable",
        "value": None,
        "functionalUnit": "One estimated year of page views at the audited origin, modeled operational and embodied browsing emissions",
        "notIncluded": "Not a complete organizational footprint; no site-specific backend/build/office inventory or remote inference energy",
        "assumptions": {
            "pageMix": "Equal weights across sampled page URLs",
            "visitSelection": "First recorded initial visit per URL"
            if selection == "first"
            else "Repeated branches averaged within each page first",
            "realPageMix": "unknown",
            "visitMix": "100% first visits, 0% returning visits",
            "hosting": "unknown; model uses non-green scenario",
            "traffic": "Rank-bucket cohort estimate, not actual analytics",
            "sensitivity": "All views at the minimum/maximum sampled page intensity; not a confidence interval or bounds on true site emissions",
        },
    }
    count = pageview_count(site, traffic)
    if count is None:
        result["reason"] = "Requires a matched-origin bucket and valid traffic scenario"
        return result
    if not pages or len({p["url"] for p in pages}) != len(pages):
        raise ValueError("Require unique page URLs before applying the page mix")
    for page in pages:
        url = urlsplit(page["url"])
        if f"{url.scheme}://{url.netloc}" != site or not nonnegative(
            page.get("gramsPerView")
        ):
            raise ValueError(
                "Page intensity must be valid and belong to this exact origin"
            )
    intensities = [p["gramsPerView"] for p in pages]
    central = statistics.mean(intensities)
    annual = count * (central / 1000)
    lower = count * (min(intensities) / 1000)
    upper = count * (max(intensities) / 1000)
    if not all(nonnegative(value) for value in [annual, lower, upper]):
        raise ValueError("Annual scenario exceeds finite numeric range")
    result.update(
        status="estimated",
        value=annual,
        annualPageviews=count,
        gramsPerViewProxy=central,
        rankBucket=traffic["rankBucket"],
        transferInputs="partial"
        if any(p["accountingStatus"] != "complete" for p in pages)
        else "complete_within_protocol",
        pages=[{**p, "pageWeight": 1 / len(pages)} for p in pages],
        sensitivityKgPerYear={
            "lowestSampledPage": lower,
            "highestSampledPage": upper,
        },
    )
    return result


def model_pages(staged: JSON, selection: str = "branch-mean") -> dict[str, list[JSON]]:
    """Use pinned CO2.js without assigning ratings to partial traffic inputs."""
    if selection not in {"first", "branch-mean"}:
        raise ValueError("Unsupported initial visit selection")
    samples = []
    seen = set()
    for run in staged["runs"]:
        if selection == "first" and run["url"] in seen:
            continue
        seen.add(run["url"])
        if (
            run.get("navigationError")
            or not 200 <= (run.get("documentStatus") or 0) < 400
        ):
            raise ValueError(
                "A failed document navigation cannot represent a normal annual page view"
            )
        phase = next(p for p in run["phases"] if p["phase"] == "initial")
        if not nonnegative(phase["receivedBytes"]) or phase["receivedBytes"] == 0:
            raise ValueError(
                "Annual page proxies require positive observed traffic; no bytes is not a zero-footprint site"
            )
        samples.append(
            {
                "url": run["url"],
                "runId": run["id"],
                "bytes": phase["receivedBytes"],
                "accountingStatus": phase["accountingStatus"],
            }
        )
    node = shutil.which("node")
    if node is None:
        raise RuntimeError("Install Node and run npm ci for the pinned CO2.js bridge")
    completed = subprocess.run(  # noqa: S603 - fixed library bridge, no shell
        [node, "--input-type=module", "-e", BRIDGE],
        cwd=ROOT,
        input=json.dumps([p["bytes"] for p in samples]),
        text=True,
        capture_output=True,
        check=True,
        timeout=30,
    )
    traces = json.loads(completed.stdout)
    if len(traces) != len(samples):
        raise ValueError("Unexpected model result count")
    grouped: dict[str, list[JSON]] = {}
    for sample, trace in zip(samples, traces, strict=True):
        grouped.setdefault(sample["url"], []).append({**sample, "trace": trace})
    sites: dict[str, list[JSON]] = {}
    for url, branches in grouped.items():
        parsed = urlsplit(url)
        site = f"{parsed.scheme}://{parsed.netloc}"
        sites.setdefault(site, []).append(
            {
                "url": url,
                "gramsPerView": statistics.mean(b["trace"]["co2"] for b in branches),
                "accountingStatus": "complete"
                if all(
                    b["accountingStatus"] == "complete_within_protocol"
                    for b in branches
                )
                else "partial",
                "branches": branches,
            }
        )
    return sites


def client_energy_scenario(
    site: str, energy: JSON | None, traffic: JSON, sampled_urls: set[str], grid: float
) -> JSON:
    """Scale explicit lab scenarios; never imply metered annual site electricity."""
    result: JSON = {
        "site": site,
        "status": "unavailable",
        "basis": "scenario",
        "value": None,
        "unit": "kWh/year",
        "kgCO2ePerYear": None,
        "gridIntensity": {
            "value": grid,
            "unit": "gCO2e/kWh",
            "basis": "Assumed comparison factor, not audience electricity data",
            "defaultFactorReference": "https://sustainablewebdesign.org/estimating-digital-emissions/",
        },
        "assumptions": {
            "pageMix": "Equal weights across energy-sampled URLs; median of three matching repetitions per URL",
            "visitMix": "Every estimated pageview repeats the recorded initial-load scenario on the tested device/browser",
            "boundary": "Modeled browser CPU, memory, disk and display operation only; excludes network, remote servers, embodied emissions and later reading/interaction",
            "measurement": "GreenFrame resource-counter model, not direct electricity metering",
            "improvement": "A proportional reduction is a sensitivity scenario, not demonstrated achievable savings",
            "additivity": "Overlaps SWDM device scope; do not add these estimates to SWDM",
        },
    }
    if not nonnegative(grid):
        raise ValueError("Grid intensity must be finite and nonnegative")
    if energy is None:
        return {**result, "reason": "No client-energy experiment supplied"}
    energy_rows(
        energy, site
    )  # Validate scope, three samples, units and recorded medians.
    urls = [page["url"] for page in energy["pages"]]
    if len(set(urls)) != len(urls) or not set(urls) <= sampled_urls:
        raise ValueError("Energy pages must be unique URLs within the audited sample")
    pages = [
        {"url": page["url"], "WhPerView": page["clientDeviceSummaryWh"]["median"]}
        for page in energy["pages"]
        if page["status"] == "completed"
    ]
    if not pages:
        return {**result, "reason": "No complete client-energy scenarios"}
    count = pageview_count(site, traffic)
    if count is None:
        return {
            **result,
            "reason": "Requires a matched-origin bucket and valid traffic scenario",
        }
    average = statistics.mean(page["WhPerView"] for page in pages)
    kwh = average * count / 1000
    kg = kwh * grid / 1000
    if not all(nonnegative(value) for value in (average, kwh, kg)):
        raise ValueError("Annual client-energy scenario exceeds finite numeric range")
    return {
        **result,
        "status": "estimated",
        "value": kwh,
        "kgCO2ePerYear": kg,
        "annualPageviews": count,
        "rankBucket": traffic["rankBucket"],
        "WhPerViewProxy": average,
        "sampledPageCount": len(pages),
        "auditedPageCount": len(sampled_urls),
        "pages": [{**page, "pageWeight": 1 / len(pages)} for page in pages],
    }


def annual_document(
    staged_raw: bytes,
    traffic_raw: bytes,
    energy_raw: bytes | None = None,
    selection: str = "first",
    grid: float = 494,
) -> JSON:
    """Bind both independent projections to exact inputs and calculation settings."""
    raw = {"staged": staged_raw, "traffic": traffic_raw}
    if energy_raw is not None:
        raw["energy"] = energy_raw
    traffic = json.loads(traffic_raw)
    energy = json.loads(energy_raw) if energy_raw is not None else None
    pages = model_pages(json.loads(staged_raw), selection)
    if energy and (len(pages) != 1 or energy.get("origin") not in pages):
        raise ValueError(
            "Client-energy enrichment requires one matching audited origin"
        )
    if len({r["origin"] for r in traffic["results"]}) != len(traffic["results"]):
        raise ValueError("Traffic lookup must contain unique origins")
    scenarios, client_scenarios = [], []
    for site, items in pages.items():
        record: JSON = next((r for r in traffic["results"] if r["origin"] == site), {})
        scenarios.append(annual_scenario(site, items, record, selection))
        client_scenarios.append(
            client_energy_scenario(
                site, energy, record, {p["url"] for p in items}, grid
            )
        )
    return {
        "schemaVersion": "0.2.0",
        "sourceSHA256": {
            key: hashlib.sha256(value).hexdigest() for key, value in raw.items()
        },
        "calculatorSHA256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "energyValidatorSHA256": hashlib.sha256(
            (ROOT / "audit/report_details.py").read_bytes()
        ).hexdigest(),
        "dependencyLockSHA256": hashlib.sha256(
            (ROOT / "package-lock.json").read_bytes()
        ).hexdigest(),
        "model": "CO2.js 0.19.0 / SWDM v4, global model electricity factors, no DCR assigned by this scenario calculator",
        "visitSelection": selection,
        "clientGridIntensity": grid,
        "trafficDatasetMonth": traffic.get("datasetMonth"),
        "scenarios": scenarios,
        "clientEnergyScenarios": client_scenarios,
        "sensitivity": {
            "reductionFraction": 0.1,
            "meaning": "Hypothetical 10% reduction in per-view intensity at unchanged traffic; not a forecast of achievable savings",
        },
    }


def main() -> None:
    """Publish annual scenarios separately from measured energy and DCR eligibility."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--staged",
        type=Path,
        default=ROOT / "docs/initial-implementation/assets/staged-audit.json",
    )
    parser.add_argument(
        "--traffic",
        type=Path,
        default=ROOT / "docs/initial-implementation/assets/traffic-scenarios.json",
    )
    parser.add_argument("--energy", type=Path)
    parser.add_argument(
        "--visit-selection", choices=["first", "branch-mean"], default="first"
    )
    parser.add_argument(
        "--client-grid-intensity",
        type=float,
        default=494,
        help="Assumed client electricity gCO2e/kWh; default SWDM v4 comparison factor, not measured audience mix",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "docs/initial-implementation/assets/annual-footprints.json",
    )
    args = parser.parse_args()
    result = annual_document(
        args.staged.read_bytes(),
        args.traffic.read_bytes(),
        args.energy.read_bytes() if args.energy else None,
        args.visit_selection,
        args.client_grid_intensity,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
