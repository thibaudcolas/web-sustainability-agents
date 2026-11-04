#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = []
# [tool.uv]
# required-version = ">=0.12.20,<0.13"
# ///
"""Prepare or run an optional GreenFrame client-only scenario with provenance."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import re
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

JSON = dict[str, Any]
CLI_VERSION = "2.0.1"


def clean_environment() -> dict[str, str]:
    """Avoid inheriting optional GreenFrame cloud upload credentials/configuration."""
    return {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("GREENFRAME_")
    }


def scenario(phase: str, consent_selector: str | None) -> str:
    """Generate the JavaScript bridge required by GreenFrame's Playwright runner."""
    lines = [
        "module.exports = async (page) => {",
        "  await page.setViewportSize({width: 1280, height: 800});",
        "  await page.goto('', {waitUntil: 'load', timeout: 45000});",
        "  await page.waitForTimeout(3000);",
        "  await page.addMilestone('initial: no interaction');",
    ]
    if phase != "initial":
        if consent_selector:
            lines.append(
                f"  await page.locator({json.dumps(consent_selector)}).click({{timeout: 10000}});"
            )
        lines.extend(
            [
                "  await page.waitForTimeout(3000);",
                "  await page.addMilestone('after consent action or declared no-banner state');",
            ]
        )
    if phase == "after_scroll":
        lines.extend(
            [
                "  for (let step = 0; step < 40; step += 1) {",
                "    const bottom = await page.evaluate(() => {",
                "      window.scrollBy(0, window.innerHeight * 0.8);",
                "      return window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 2;",
                "    });",
                "    await page.waitForTimeout(250);",
                "    if (bottom) break;",
                "    if (step === 39) throw new Error('Scroll bound reached before page bottom');",
                "  }",
                "  await page.waitForTimeout(3000);",
                "  await page.addMilestone('after bounded scroll to bottom');",
            ]
        )
    return "\n".join([*lines, "};", ""])


def prepare(
    url: str,
    work: Path,
    phase: str,
    consent_selector: str | None,
    samples: int,
    no_banner: bool = False,
) -> JSON:
    """Write an isolated config that includes the browser and no server containers."""
    parts = urlsplit(url)
    if (
        parts.scheme not in {"http", "https"}
        or not parts.hostname
        or parts.username
        or parts.password
    ):
        raise ValueError("Use an HTTP(S) URL without credentials")
    if parts.query or parts.fragment:
        raise ValueError("Use a public URL without query identifiers or fragments")
    if (
        phase not in {"initial", "after_consent", "after_scroll"}
        or not 2 <= samples <= 10
    ):
        raise ValueError("Use a supported phase and 2–10 samples")
    if phase != "initial" and not consent_selector and not no_banner:
        raise ValueError(
            "Specify a consent selector or explicitly declare --no-banner for later phases"
        )
    if consent_selector and no_banner:
        raise ValueError("A consent selector conflicts with --no-banner")
    if work.exists() and any(work.iterdir()):
        raise ValueError("Use an empty output directory to preserve prior runs")
    work.mkdir(parents=True, exist_ok=True)
    script = work / "scenario.js"
    script.write_text(scenario(phase, consent_selector))
    config: JSON = {
        "baseURL": url,
        "scenarios": [{"path": str(script.resolve()), "name": phase}],
        "projectName": "web-sustainability-agents-client",
        "samples": samples,
        "distant": False,
        "useAdblock": False,
        "ignoreHTTPSErrors": False,
        "containers": [],
        "databaseContainers": [],
    }
    # JSON is valid YAML and avoids introducing another configuration serializer.
    config_path = work / ".greenframe.yml"
    config_path.write_text(json.dumps(config, indent=2) + "\n")
    return {
        "schemaVersion": "greenframe-client-v1",
        "preparedAt": datetime.now(UTC).isoformat(),
        "url": url,
        "phase": phase,
        "consentSelector": consent_selector,
        "noBannerDeclared": no_banner,
        "samples": samples,
        "status": "prepared_not_measured",
        "requiredCliVersion": CLI_VERSION,
        "configSHA256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
        "scenarioSHA256": hashlib.sha256(script.read_bytes()).hexdigest(),
        "wrapperSHA256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "system": {"platform": platform.platform(), "machine": platform.machine()},
        "measurementBoundary": "GreenFrame browser container resource counters converted by its energy/carbon model; remote servers excluded",
        "comparisonRule": "Independent complete scenarios, not incremental phase energy; retain first-load result as headline and compare matched repeated scenarios",
        "limitations": "Modeled Wh and gCO2e, not RAPL or wall-meter energy; never add to SWDM or infer annual site footprint directly. Runner image/browser versions require separate verification before comparing runs.",
        "metrics": None,
    }


def probe(argv: list[str], cwd: Path) -> JSON:
    """Run a bounded prerequisite command without a shell or inherited cloud token."""
    try:
        result = subprocess.run(  # noqa: S603
            argv,
            cwd=cwd,
            env=clean_environment(),
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        return {
            "argv": argv,
            "returncode": result.returncode,
            "output": (result.stdout + result.stderr)[-4000:],
        }
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"argv": argv, "returncode": None, "error": type(error).__name__}


def parse_metrics(output: str) -> JSON | None:
    """Read the documented summary while preserving unknown output as unavailable."""
    match = re.search(
        r"([\d.]+)\s*g eq\. co2\s*±\s*([\d.]+)%\s*\(([\d.]+)\s*Wh\)",
        output,
        re.IGNORECASE,
    )
    if not match:
        return None
    try:
        carbon, precision, energy = map(float, match.groups())
    except ValueError:
        return None
    if not all(
        math.isfinite(value) and value >= 0 for value in (carbon, precision, energy)
    ):
        return None
    return {
        "carbon": {
            "value": carbon,
            "unit": "gCO2e/scenario",
            "basis": "GreenFrame model",
        },
        "energy": {"value": energy, "unit": "Wh/scenario", "basis": "GreenFrame model"},
        "reportedPrecisionPercent": precision,
    }


def main() -> None:
    """Prepare by default; measure only when explicitly invoked with --run."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--phase",
        choices=["initial", "after_consent", "after_scroll"],
        default="initial",
    )
    parser.add_argument(
        "--consent-selector",
        help="Exact CSS selector for the agreed consent action; omit only for a declared no-banner journey",
    )
    parser.add_argument(
        "--no-banner",
        action="store_true",
        help="Explicitly declare the sampled journey has no consent banner",
    )
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--binary", default="greenframe")
    parser.add_argument(
        "--run",
        action="store_true",
        help="Run the prepared scenario after prerequisites pass; keep hardware workloads separate",
    )
    args = parser.parse_args()
    work = args.output_dir.resolve()
    record = prepare(
        args.url, work, args.phase, args.consent_selector, args.samples, args.no_banner
    )
    binary = shutil.which(args.binary)
    docker = shutil.which("docker")
    record["preflight"] = {
        "cli": probe([binary, "--version"], work)
        if binary
        else {"error": "greenframe executable not installed"},
        "docker": probe([docker, "version", "--format", "{{.Server.Version}}"], work)
        if docker
        else {"error": "docker executable not installed"},
    }
    cli = record["preflight"]["cli"]
    docker_probe = record["preflight"]["docker"]
    ready = bool(
        binary
        and cli.get("returncode") == 0
        and re.search(
            rf"(?<![\d.]){re.escape(CLI_VERSION)}(?![\d.])", cli.get("output", "")
        )
        and docker_probe.get("returncode") == 0
    )
    record["ready"] = ready
    record["argv"] = [
        binary or args.binary,
        "analyze",
        "--configFile",
        str(work / ".greenframe.yml"),
    ]
    if args.run and ready:
        record["startedAt"] = datetime.now(UTC).isoformat()
        with (work / "runner.log").open("w") as log:
            try:
                result = subprocess.run(  # noqa: S603
                    record["argv"],
                    cwd=work,
                    env=clean_environment(),
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    timeout=1200,
                    check=False,
                )
                record["returncode"] = result.returncode
                record["status"] = (
                    "completed" if result.returncode == 0 else "runner_failed"
                )
            except (OSError, subprocess.TimeoutExpired) as error:
                record["status"] = "runner_failed"
                record["error"] = type(error).__name__
        record["finishedAt"] = datetime.now(UTC).isoformat()
        output = (work / "runner.log").read_text(errors="replace")
        record["logSHA256"] = hashlib.sha256(
            (work / "runner.log").read_bytes()
        ).hexdigest()
        if record["status"] == "completed":
            record["metrics"] = parse_metrics(output)
            if record["metrics"] is None:
                record["status"] = "completed_summary_unrecognized"
    elif args.run:
        record["status"] = "unavailable_prerequisites"
    (work / "manifest.json").write_text(json.dumps(record, indent=2) + "\n")
    if args.run and record["status"] != "completed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
