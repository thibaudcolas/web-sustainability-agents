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
import statistics
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

JSON = dict[str, Any]
CLI_VERSION = "2.0.1"
RUNNER_IMAGE = "mcr.microsoft.com/playwright:v1.30.0-focal"
BOUNDARY = "GreenFrame modeled browser-container CPU, memory, disk and screen energy; network modeled separately; remote servers excluded"
# Keep the pinned upstream collector/model unchanged. Export raw counters and full
# precision component results through a narrow bridge instead of scraping stdout.
BRIDGE = r"""
const fs = require('node:fs');
const path = require('node:path');
const root = process.argv[2];
const {executeScenarioAndGetContainerStats} = require(path.join(root, 'dist/services/container'));
const {computeScenarioResult} = require(path.join(root, 'dist/services/computeScenarioResult'));
(async () => {
  const raw = await executeScenarioAndGetContainerStats({
    scenario: './scenario.js', url: process.argv[3], samples: Number(process.argv[4]),
    useAdblock: false, ignoreHTTPSErrors: false, containers: [], databaseContainers: []
  });
  fs.writeFileSync('raw-counters.json', JSON.stringify(raw));
  const aggregate = computeScenarioResult({allContainersStats: raw.allContainers, milestones: raw.allMilestones, name: 'initial'});
  const samples = raw.allContainers[0].dockerStats.map((item, index) =>
    computeScenarioResult({allContainersStats: [{...raw.allContainers[0], dockerStats: [item]}], milestones: [raw.allMilestones[index]], name: 'initial'}));
  fs.writeFileSync('model-results.json', JSON.stringify({aggregate, samples}));
})().catch(error => {console.error(error); process.exitCode = 1;});
"""


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
        "  const response = await page.goto('', {waitUntil: 'load', timeout: 45000});",
        "  if (!response || !response.ok()) throw new Error('Initial document did not return a successful response');",
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
        "scenarios": [{"path": "./scenario.js", "name": phase}],
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
        "measurementBoundary": BOUNDARY,
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


def preflight(binary_name: str, work: Path) -> JSON:
    """Check pinned tools and image without launching a browser or changing the host."""
    binary = shutil.which(binary_name)
    if binary:
        binary = str(Path(binary).resolve())
    docker = shutil.which("docker")
    cli = (
        probe([binary, "--version"], work)
        if binary
        else {"error": "greenframe executable not installed"}
    )
    daemon = (
        probe([docker, "version", "--format", "{{.Server.Version}}"], work)
        if docker
        else {"error": "docker executable not installed"}
    )
    image = (
        probe(
            [docker, "image", "inspect", RUNNER_IMAGE, "--format", "{{json .}}"], work
        )
        if docker
        else {"error": "docker executable not installed"}
    )
    root = Path(binary).resolve().parent.parent if binary else None
    library = bool(root and (root / "dist/services/container/index.js").is_file())
    version_ok = cli.get("returncode") == 0 and bool(
        re.search(
            rf"(?<![\d.]){re.escape(CLI_VERSION)}(?![\d.])", cli.get("output", "")
        )
    )
    # Do not retain verbose image metadata such as environment or build history.
    image_identity = None
    if image.get("returncode") == 0:
        data = json.loads(image["output"])
        image_identity = {
            key: data.get(key) for key in ("Id", "RepoDigests", "Architecture", "Os")
        }
    container = (
        probe(
            [
                docker,
                "ps",
                "-a",
                "--filter",
                "name=^/greenframe-runner$",
                "--format",
                "{{.Names}}",
            ],
            work,
        )
        if docker
        else {}
    )
    occupied = bool(container.get("output", "").strip())
    return {
        "ready": bool(
            version_ok
            and daemon.get("returncode") == 0
            and image_identity
            and library
            and not occupied
        ),
        "cli": cli,
        "docker": daemon,
        "image": image_identity,
        "libraryPresent": library,
        "runnerNameOccupied": occupied,
        "libraryRoot": str(root) if root else None,
        "requiredCliVersion": CLI_VERSION,
        "requiredImage": RUNNER_IMAGE,
        "browser": json.loads(
            (root / "node_modules/playwright-core/browsers.json").read_text()
        )["browsers"][0]
        if library and root
        else None,
        "remediation": "Install pinned GreenFrame CLI 2.0.1 locally and pull the required image; no host permission changes are performed",
    }


def component_metrics(result: JSON) -> JSON:
    """Validate modeled components and keep client device and network boundaries separate."""
    if result.get("status") != "finished":
        raise ValueError("GreenFrame scenario did not finish")
    components = result.get("score", {}).get("wh", {})
    for name in ("cpu", "mem", "disk", "screen", "network", "total"):
        value = components.get(name)
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or value < 0
        ):
            raise ValueError(
                "Missing, negative or nonfinite GreenFrame energy components"
            )
    device = math.fsum(components[name] for name in ("cpu", "mem", "disk", "screen"))
    if device <= 0 or components["cpu"] <= 0:
        raise ValueError(
            "Zero client or CPU energy cannot establish a working counter measurement"
        )
    if not math.isclose(
        device + components["network"], components["total"], rel_tol=1e-8, abs_tol=1e-12
    ):
        raise ValueError("GreenFrame component sum disagrees with total")
    return {
        "energy": {
            "value": components["total"],
            "unit": "Wh/scenario",
            "basis": "GreenFrame resource model",
        },
        "clientDeviceEnergy": {
            "value": device,
            "unit": "Wh/scenario",
            "basis": "GreenFrame resource model",
        },
        "networkEnergy": {
            "value": components["network"],
            "unit": "Wh/scenario",
            "basis": "GreenFrame resource model",
        },
        "componentsWh": components,
        "scenarioSeconds": result["score"]["s"]["totalTime"],
        "reportedPrecisionPercent": result.get("precision"),
    }


def measure_page(record: JSON, work: Path, checks: JSON) -> None:
    """Execute one pinned repeated scenario and retain raw counter/model provenance."""
    root = Path(checks["libraryRoot"])
    node = root / "bin/node"
    if not node.is_file():
        located = shutil.which("node")
        if located is None:
            raise ValueError("Node executable unavailable")
        node = Path(located)
    bridge = work / "bridge.cjs"
    bridge.write_text(BRIDGE)
    record["bridgeSHA256"] = hashlib.sha256(bridge.read_bytes()).hexdigest()
    record["sourceDigests"] = {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest()
        for name in (
            "package.json",
            "dist/services/container/index.js",
            "dist/services/container/execScenarioContainer.js",
            "dist/model/stat-tools/getConsumption.js",
            "dist/model/stat-tools/getWh.js",
        )
    }
    argv = [str(node), str(bridge), str(root), record["url"], str(record["samples"])]
    record["argv"] = argv
    record["startedAt"] = datetime.now(UTC).isoformat()
    with (work / "runner.log").open("w") as log:
        completed = subprocess.run(  # noqa: S603 - fixed bridge and validated URL
            argv,
            cwd=work,
            env=clean_environment(),
            stdout=log,
            stderr=subprocess.STDOUT,
            timeout=600,
            check=False,
        )  # noqa: S603
    record["finishedAt"] = datetime.now(UTC).isoformat()
    record["returncode"] = completed.returncode
    if completed.returncode:
        raise ValueError("GreenFrame runner failed; inspect private runner.log")
    raw = json.loads((work / "raw-counters.json").read_text())
    containers = raw["allContainers"]
    if len(containers) != 1 or containers[0].get("type") != "DEVICE":
        raise ValueError("Expected exactly one browser DEVICE container")
    samples = containers[0]["dockerStats"]
    if len(samples) != record["samples"] or any(
        len(item.get("stats", [])) < 2 for item in samples
    ):
        raise ValueError("Missing Docker counter samples")
    modeled = json.loads((work / "model-results.json").read_text())
    if len(modeled["samples"]) != record["samples"]:
        raise ValueError("Incomplete model repetitions")
    record["sampleMetrics"] = [component_metrics(item) for item in modeled["samples"]]
    record["metrics"] = component_metrics(modeled["aggregate"])
    for metric, summary in (
        ("clientDeviceEnergy", "clientDeviceSummaryWh"),
        ("networkEnergy", "networkSummaryWh"),
        ("energy", "totalSummaryWh"),
    ):
        values = [item[metric]["value"] for item in record["sampleMetrics"]]
        record[summary] = {
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "min": min(values),
            "max": max(values),
            "rangeMeaning": "Observed repetition range, not a confidence interval",
        }
    record["artifacts"] = {
        name: hashlib.sha256((work / name).read_bytes()).hexdigest()
        for name in (
            "raw-counters.json",
            "model-results.json",
            "runner.log",
            "scenario.js",
            "bridge.cjs",
        )
    }
    record["status"] = "completed"


def collect_energy(
    plan: JSON, output: Path, mode: str = "readiness", binary: str = "greenframe"
) -> JSON:
    """Freeze explicit readiness, unavailable or measured per-origin energy evidence."""
    if mode not in {"readiness", "run", "skip"}:
        raise ValueError("Use energy mode readiness, run or skip")
    if output.exists() and any(output.iterdir()):
        raise ValueError(
            "Use an empty output directory to preserve prior energy evidence"
        )
    output.mkdir(parents=True, exist_ok=True)
    settings = plan.get("energy", {})
    wanted = settings.get("pageIds", [])
    pages = (
        [page for page in plan["pages"] if page["id"] in wanted]
        if wanted
        else plan["pages"][:1]
    )
    if not pages or len(pages) > 3 or len(pages) != (len(wanted) if wanted else 1):
        raise ValueError("Select 1–3 unique planned energy page IDs")
    if any(not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", page["id"]) for page in pages):
        raise ValueError("Use stable planned energy page IDs")
    origin = plan["origin"]
    if any(
        f"{urlsplit(page['url']).scheme}://{urlsplit(page['url']).netloc}" != origin
        for page in pages
    ):
        raise ValueError("Energy pages must match the exact audit origin")
    checks = preflight(binary, output) if mode != "skip" else {"ready": False}
    record: JSON = {
        "schemaVersion": "greenframe-energy-v2",
        "origin": origin,
        "capturedAt": datetime.now(UTC).isoformat(),
        "mode": mode,
        "tool": "GreenFrame",
        "toolVersion": CLI_VERSION,
        "preflight": checks,
        "measurementBoundary": BOUNDARY,
        "protocol": {
            "phase": "initial",
            "samples": settings.get("samples", 3),
            "viewport": {"width": 1280, "height": 800},
            "browser": "Chromium in pinned Playwright container",
            "journey": "Fresh browser context; initial navigation waits for load then 3000 ms; no consent action or scrolling",
            "baselineSubtracted": False,
            "measurementWindow": "Starts after browser/context startup and upstream 2000 ms warm-up; ends after scenario and browser close; fresh context per repetition, same browser container across repetitions",
            "execution": "Sequential; shared workstation, uncontrolled ambient activity",
            "upstreamBrowserFlags": ["--disable-web-security"],
            "userAgent": "GreenFrame fixed Chrome/89 user agent; not the actual browser version",
        },
        "limitations": [
            "Resource-counter model; not measured electricity, whole device energy or remote server energy",
            "Client-device headline excludes GreenFrame modeled network energy, which is listed separately",
            "Synthetic 45 W CPU and 14 W screen coefficients; CPU counters normalized by available host CPUs",
            "Never add to SWDM emissions or extrapolate directly to annual site impact",
            "Bounded energy sample may be smaller than the report's browser page sample",
        ],
        "pages": [],
    }
    for page in pages:
        work = output / page["id"]
        item = prepare(page["url"], work, "initial", None, settings.get("samples", 3))
        item["id"] = page["id"]
        item["status"] = (
            "skipped_explicitly"
            if mode == "skip"
            else "ready_not_measured"
            if checks["ready"]
            else "unavailable_prerequisites"
        )
        if mode == "run" and checks["ready"]:
            try:
                measure_page(item, work, checks)
            except (
                OSError,
                ValueError,
                KeyError,
                TypeError,
                subprocess.TimeoutExpired,
            ) as error:
                item.update(
                    status="unavailable_measurement",
                    metrics=None,
                    error=f"{type(error).__name__}: {error}"[:400],
                )
        (work / "manifest.json").write_text(
            json.dumps(item, indent=2, allow_nan=False) + "\n"
        )
        record["pages"].append(item)
        states = {row["status"] for row in record["pages"]}
        record["status"] = next(iter(states)) if len(states) == 1 else "partial"
        (output / "manifest.json").write_text(
            json.dumps(record, indent=2, allow_nan=False) + "\n"
        )
    return record


def main() -> None:
    """Prepare a bounded scenario or collect per-origin energy evidence explicitly."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--url")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--phase",
        choices=["initial", "after_consent", "after_scroll"],
        default="initial",
    )
    parser.add_argument("--consent-selector")
    parser.add_argument("--no-banner", action="store_true")
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--binary", default="greenframe")
    parser.add_argument(
        "--mode", choices=["readiness", "run", "skip"], default="readiness"
    )
    parser.add_argument("--run", action="store_true", help="Alias for --mode run")
    args = parser.parse_args()
    if bool(args.plan) == bool(args.url):
        parser.error("Specify exactly one of --plan or --url")
    if args.plan:
        plan = json.loads(args.plan.read_text())
    else:
        if args.phase != "initial" or args.consent_selector or args.no_banner:
            parser.error(
                "Energy collection currently supports initial load only; use prepare() for other scenario drafts"
            )
        parts = urlsplit(args.url)
        plan = {
            "origin": f"{parts.scheme}://{parts.netloc}",
            "pages": [{"id": "page-1", "url": args.url}],
            "energy": {"samples": args.samples},
        }
    result = collect_energy(
        plan, args.output_dir.resolve(), "run" if args.run else args.mode, args.binary
    )
    if (args.run or args.mode == "run") and result["status"] != "completed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
