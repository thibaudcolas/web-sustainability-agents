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
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

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


def annual_scenario(site: str, pages: list[JSON], traffic: JSON) -> JSON:
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
            "pageMix": "Equal weights across sampled page URLs; repeated branches averaged within each page first",
            "realPageMix": "unknown",
            "visitMix": "100% first visits, 0% returning visits",
            "hosting": "unknown; model uses non-green scenario",
            "traffic": "Rank-bucket cohort estimate, not actual analytics",
            "sensitivity": "All views at the minimum/maximum sampled page intensity; not a confidence interval or bounds on true site emissions",
        },
    }
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


def model_pages(staged: JSON) -> dict[str, list[JSON]]:
    """Use pinned CO2.js without assigning ratings to partial traffic inputs."""
    samples = []
    for run in staged["runs"]:
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
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "docs/initial-implementation/assets/annual-footprints.json",
    )
    args = parser.parse_args()
    raw = {"staged": args.staged.read_bytes(), "traffic": args.traffic.read_bytes()}
    traffic = json.loads(raw["traffic"])
    pages = model_pages(json.loads(raw["staged"]))
    result = {
        "schemaVersion": "0.1.0",
        "sourceSHA256": {
            key: hashlib.sha256(value).hexdigest() for key, value in raw.items()
        },
        "calculatorSHA256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "dependencyLockSHA256": hashlib.sha256(
            (ROOT / "package-lock.json").read_bytes()
        ).hexdigest(),
        "model": "CO2.js 0.19.0 / SWDM v4, global model electricity factors, no DCR assigned by this scenario calculator",
        "trafficDatasetMonth": traffic["datasetMonth"],
        "scenarios": [
            annual_scenario(
                site,
                items,
                next((r for r in traffic["results"] if r["origin"] == site), {}),
            )
            for site, items in pages.items()
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
