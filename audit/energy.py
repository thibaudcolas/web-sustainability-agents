#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = []
# [tool.uv]
# required-version = ">=0.12.20,<0.13"
# ///
"""Run local co2-runner journeys sequentially and validate Linux energy counters."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import logging
import math
import os
import platform
import shutil
import statistics
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

JSON = dict[str, Any]
ROOT = Path(__file__).resolve().parent.parent
LOG = logging.getLogger(__name__)


def read_profile(path: Path) -> JSON:
    """Read an uncompressed or gzip Firefox profile without publishing its contents."""
    raw = path.read_bytes()
    if raw.startswith(b"\x1f\x8b"):
        raw = gzip.decompress(raw)
    value: JSON = json.loads(raw)
    return value


def validate_profile(profile: JSON) -> JSON:
    """Validate one non-overlapping Linux CPU-package interval-energy series."""
    result: JSON = {
        "status": "unavailable",
        "joules": None,
        "mWh": None,
        "scope": "whole-system CPU package during Firefox session; excludes separate DRAM and other device energy",
    }
    counters = [
        c for c in profile.get("counters", []) if c.get("name") == "Power: CPU package"
    ]
    if len(counters) != 1:
        return {
            **result,
            "reason": "Expected exactly one top-level CPU-package counter",
        }
    samples = counters[0].get("samples", {})
    rows = samples.get("data", [])
    if samples.get("schema") != {"time": 0, "count": 1} or len(rows) < 2:
        return {
            **result,
            "reason": "Unsupported schema or insufficient counter samples",
        }
    previous = -1.0
    for row in rows:
        if (
            not isinstance(row, list)
            or len(row) != 2
            or any(
                isinstance(v, bool)
                or not isinstance(v, (int, float))
                or not math.isfinite(v)
                or v < 0
                for v in row
            )
            or row[0] <= previous
        ):
            return {
                **result,
                "status": "invalid",
                "reason": "Malformed, negative, nonfinite, or unordered counter samples",
            }
        previous = row[0]
    total = math.fsum(row[1] for row in rows)
    return {
        **result,
        "status": "measured",
        "joules": total * 3.6e-9,
        "mWh": total * 1e-9,
        "counter": counters[0]["name"],
        "sourceUnit": "pWh per interval",
        "sampleCount": len(rows),
        "firstSampleMs": rows[0][0],
        "lastSampleMs": rows[-1][0],
        "observedSpanSeconds": (rows[-1][0] - rows[0][0]) / 1000,
        "sessionDurationMs": profile.get("meta", {}).get("shutdownTime"),
        "configuredIntervalMs": profile.get("meta", {}).get("interval"),
        "allZero": total == 0,
        "firstSampleIncluded": True,
        "excludingFirstSampleJoules": (total - rows[0][1]) * 3.6e-9,
        "note": "Includes startup/shutdown and background work. First-sample exclusion is sensitivity data, not another measurement to add. Never add this to SWDM emissions.",
    }


def summarize(runs: list[JSON]) -> list[JSON]:
    """Summarize valid repetitions without hiding failures or implying confidence bounds."""
    summaries = []
    for url in dict.fromkeys(run["url"] for run in runs):
        selected = [run for run in runs if run["url"] == url]
        valid = [
            r["energy"]["joules"]
            for r in selected
            if r["energy"]["status"] == "measured"
            and r.get("journeyStatus") == "completed"
            and not r["energy"].get("allZero")
        ]
        summaries.append(
            {
                "url": url,
                "attempts": len(selected),
                "validRuns": len(valid),
                "medianJoules": statistics.median(valid) if valid else None,
                "minJoules": min(valid) if valid else None,
                "maxJoules": max(valid) if valid else None,
                "intervalMeaning": "observed range, not a confidence interval",
            }
        )
    return summaries


def execute(checkout: Path, journey: Path, work: Path) -> JSON:
    """Invoke the existing Node library with argument arrays and an isolated artifact root."""
    node = shutil.which("node")
    if node is None:
        raise FileNotFoundError("Node is required for the co2-runner library bridge")
    bridge = "import {pathToFileURL} from 'node:url'; const {runJourney}=await import(pathToFileURL(process.argv[1]).href); const result=await runJourney(process.argv[2]); console.log('AUDIT_RESULT='+JSON.stringify(result));"
    completed = subprocess.run(  # noqa: S603 - fixed library bridge, no shell
        [
            node,
            "--import",
            str(checkout / "node_modules/tsx/dist/loader.mjs"),
            "--input-type=module",
            "-e",
            bridge,
            str(checkout / "runner/run.ts"),
            str(journey),
        ],
        cwd=checkout,
        env={**os.environ, "CO2_RUNNER_HOME": str(work)},
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    (work / "runner.log").write_text(completed.stdout + completed.stderr)
    if completed.returncode:
        raise RuntimeError(
            f"co2-runner exited {completed.returncode}; private log retained"
        )
    lines = [
        line.removeprefix("AUDIT_RESULT=")
        for line in completed.stdout.splitlines()
        if line.startswith("AUDIT_RESULT=")
    ]
    if len(lines) != 1:
        raise ValueError("No unique structured co2-runner result")
    result: JSON = json.loads(lines[0])
    return result


def host_context() -> JSON:
    """Record read-only host metadata without claiming controlled experiment conditions."""
    cpuinfo = Path("/proc/cpuinfo")
    model = (
        next(
            (
                line.split(":", 1)[1].strip()
                for line in cpuinfo.read_text().splitlines()
                if line.startswith("model name")
            ),
            None,
        )
        if cpuinfo.exists()
        else None
    )
    paranoid = Path("/proc/sys/kernel/perf_event_paranoid")
    return {
        "observedAt": datetime.now(UTC).isoformat(),
        "cpuModel": model,
        "logicalCPUs": os.cpu_count(),
        "perfEventParanoid": paranoid.read_text().strip()
        if paranoid.exists()
        else None,
        "raplPackageEventPresent": Path(
            "/sys/bus/event_source/devices/power/events/energy-pkg"
        ).exists(),
    }


def main() -> None:
    """Measure short initial-load sessions without changing hardware permissions."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path, default=ROOT / "local/co2-runner")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "docs/initial-implementation/assets/energy-experiment.json",
    )
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument(
        "urls",
        nargs="*",
        default=["https://guide.wagtail.org/en/", "https://wagtail.org/"],
    )
    args = parser.parse_args()
    if not 1 <= args.repetitions <= 10 or any(
        urlsplit(url).scheme not in {"http", "https"} for url in args.urls
    ):
        parser.error("Use HTTP(S) targets and 1–10 repetitions")
    checkout = args.checkout.resolve()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%f")
    work = ROOT / ".audit-work/energy" / stamp
    work.mkdir(parents=True, mode=0o700)
    git = shutil.which("git")
    if git is None:
        raise FileNotFoundError("git is required to record source provenance")
    revision = subprocess.run(  # noqa: S603 - fixed read-only git command
        [git, "rev-parse", "HEAD"],
        cwd=checkout,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()  # noqa: S603
    dirty = (
        subprocess.run(  # noqa: S603 - fixed read-only git command
            [git, "status", "--porcelain"],
            cwd=checkout,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        != ""
    )  # noqa: S603
    result: JSON = {
        "schemaVersion": "0.1.0",
        "capturedAt": datetime.now(UTC).isoformat(),
        "platform": platform.platform(),
        "hostContext": host_context(),
        "tool": "co2-runner",
        "sourceRevision": revision,
        "sourceDirty": dirty,
        "sourceDigests": {
            name: hashlib.sha256((checkout / name).read_bytes()).hexdigest()
            for name in ["runner/run.ts", "runner/energy.ts", "package-lock.json"]
        },
        "protocol": {
            "browser": "Playwright Firefox",
            "playwrightVersion": json.loads(
                (checkout / "node_modules/playwright/package.json").read_text()
            )["version"],
            "viewport": {"width": 1280, "height": 720},
            "headless": False,
            "journey": "fresh page goto/load then wait 3000ms; no interaction or scrolling",
            "phase": "whole_browser_session",
            "baselineSubtracted": False,
            "execution": "sequential round-robin",
            "conditions": "Shared workstation; ambient activity, temperature and power state not experimentally controlled. No concurrent audit tests or model campaigns intentionally launched.",
        },
        "runs": [],
    }
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    for repetition in range(args.repetitions):
        for index, url in enumerate(args.urls):
            run_id = f"site-{index}-repeat-{repetition + 1}"
            run: JSON = {
                "id": run_id,
                "url": url,
                "repetition": repetition + 1,
                "capturedAt": datetime.now(UTC).isoformat(),
            }
            journey = work / f"{run_id}.yaml"
            # JSON is valid YAML; no new JavaScript journey or local checkout edit.
            journey.write_text(
                json.dumps(
                    {
                        "name": run_id,
                        "browser": "firefox",
                        "headless": False,
                        "steps": [
                            {"action": "goto", "url": url, "waitFor": "load"},
                            {"action": "wait", "ms": 3000},
                        ],
                    }
                )
            )
            try:
                raw = execute(checkout, journey, work)
                profile_path = Path(raw["profilePath"])
                profile = read_profile(profile_path)
                run["energy"] = validate_profile(profile)
                run["profileSHA256"] = hashlib.sha256(
                    profile_path.read_bytes()
                ).hexdigest()
                run["browserBuildId"] = profile.get("meta", {}).get("appBuildID")
                har_path = profile_path.with_name(f"{run_id}.har")
                har = json.loads(har_path.read_text())
                documents = [
                    entry
                    for entry in har["log"]["entries"]
                    if entry["request"]["url"].rstrip("/") == url.rstrip("/")
                ]
                status = documents[0]["response"]["status"] if documents else None
                run["documentStatus"] = status
                run["journeyStatus"] = (
                    "completed"
                    if status and 200 <= status < 300
                    else "unverified_or_failed"
                )
                run["harSHA256"] = hashlib.sha256(har_path.read_bytes()).hexdigest()
                run["upstreamJoules"] = raw["joules"]
            except (
                OSError,
                ValueError,
                RuntimeError,
                subprocess.TimeoutExpired,
            ) as error:
                run.update(
                    journeyStatus="failed",
                    error=type(error).__name__,
                    energy={
                        "status": "unavailable",
                        "joules": None,
                        "reason": str(error)[:250],
                    },
                )
            result["runs"].append(run)
            result["summary"] = summarize(result["runs"])
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, indent=2) + "\n")
            LOG.info(
                "%s: %s, %s", run_id, run["journeyStatus"], run["energy"]["status"]
            )


if __name__ == "__main__":
    main()
