#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = ["playwright==1.64.1"]
# [tool.uv]
# required-version = ">=0.12.20,<0.13"
# ///
"""Capture bounded, independently timestamped illustrations for audit reports."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal, cast
from urllib.parse import urlsplit

from playwright.async_api import Browser, Route, async_playwright
from playwright.async_api import Error as BrowserError

JSON = dict[str, Any]


def timestamp() -> str:
    """Return a UTC capture timestamp."""
    return datetime.now(UTC).isoformat()


def origin_of(url: str) -> str:
    """Validate a public HTTP URL shape without embedded credentials."""
    parsed = urlsplit(url)
    _ = parsed.port
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username
        or parsed.password
    ):
        raise ValueError("Use an HTTP(S) URL without credentials")
    return f"{parsed.scheme}://{parsed.netloc}"


def validate_plan(plan: JSON) -> None:
    """Require explicit scope, useful captions and bounded passive captures."""
    origin = plan.get("origin", "")
    if origin_of(origin) != origin:
        raise ValueError("Use one exact origin")
    captures = plan.get("captures")
    if not isinstance(captures, list) or not 1 <= len(captures) <= 6:
        raise ValueError("Select between one and six illustrations")
    ids: set[str] = set()
    allowed = {
        "id",
        "url",
        "selector",
        "viewport",
        "colorScheme",
        "alt",
        "caption",
        "checkIds",
    }
    for capture in captures:
        if not isinstance(capture, dict) or set(capture) - allowed:
            raise ValueError(
                "Unsupported screenshot field; scripts and actions are not accepted"
            )
        identifier = capture.get("id", "")
        if (
            not isinstance(identifier, str)
            or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", identifier)
            or identifier in ids
        ):
            raise ValueError("Use unique filename-safe capture IDs")
        ids.add(identifier)
        if origin_of(capture.get("url", "")) != origin:
            raise ValueError("Every screenshot URL must match the origin")
        viewport = capture.get("viewport", {})
        for dimension, lower, upper in [("width", 320, 1920), ("height", 240, 1200)]:
            value = viewport.get(dimension)
            if type(value) is not int or not lower <= value <= upper:
                raise ValueError("Use a bounded explicit viewport")
        if capture.get("colorScheme") not in {"light", "dark"}:
            raise ValueError("Specify light or dark colorScheme")
        for field in ["alt", "caption"]:
            value = capture.get(field)
            if not isinstance(value, str) or not value.strip() or len(value) > 1000:
                raise ValueError(
                    "Provide concise, nonempty alternative text and caption"
                )
        if "selector" in capture and (
            not isinstance(capture["selector"], str) or not capture["selector"].strip()
        ):
            raise ValueError("A supplied selector must be nonempty")
        checks = capture.get("checkIds")
        if (
            not isinstance(checks, list)
            or not checks
            or any(
                not isinstance(item, str)
                or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", item)
                for item in checks
            )
        ):
            raise ValueError("Associate each illustration with check IDs")


async def capture_view(
    browser: Browser, origin: str, specification: JSON, output: Path
) -> JSON:
    """Capture one viewport, preserving failures without an illustrative image."""
    record: JSON = {
        **specification,
        "captureMode": "viewport",
        "status": "failed",
        "capturedAt": None,
    }
    filename = f"{specification['id']}.png"
    context = await browser.new_context(
        viewport=specification["viewport"],
        color_scheme=cast(Literal["dark", "light"], specification["colorScheme"]),
        device_scale_factor=1,
        reduced_motion="reduce",
    )
    page = await context.new_page()

    async def protect_navigation(route: Route) -> None:
        request = route.request
        if (
            request.is_navigation_request()
            and request.frame == page.main_frame
            and origin_of(request.url) != origin
        ):
            await route.abort()
        else:
            await route.continue_()

    await context.route("**/*", protect_navigation)
    page.set_default_timeout(8000)
    try:
        async with asyncio.timeout(35):
            response = await page.goto(
                specification["url"], wait_until="load", timeout=20000
            )
            if response is None or response.status >= 400:
                raise ValueError("The target did not return a successful document")
            if origin_of(page.url) != origin:
                raise ValueError("The final page is outside the declared origin")
            await page.wait_for_timeout(750)
            if specification.get("selector"):
                target = page.locator(specification["selector"])
                if await target.count() != 1:
                    raise ValueError(
                        "The illustration selector must match exactly one element"
                    )
                await target.scroll_into_view_if_needed()
                await page.wait_for_timeout(250)
            record["capturedAt"] = timestamp()
            await page.screenshot(
                path=str(output / filename),
                full_page=False,
                animations="disabled",
                timeout=8000,
            )
            if origin_of(page.url) != origin:
                raise ValueError("The page changed origin during capture")
            record.update(
                {
                    "status": "completed",
                    "finalUrl": page.url,
                    "documentStatus": response.status,
                    "pageTitle": await page.title(),
                    "file": filename,
                    "fileSHA256": hashlib.sha256(
                        (output / filename).read_bytes()
                    ).hexdigest(),
                }
            )
    except (BrowserError, TimeoutError, ValueError) as error:
        (output / filename).unlink(missing_ok=True)
        record["error"] = str(error)[:1500]
        record["finalUrl"] = page.url
        record["failedAt"] = timestamp()
    finally:
        await context.close()
    return record


def write(path: Path, value: JSON) -> None:
    """Save a small manifest or the exact parsed plan."""
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


async def collect(plan: JSON, output: Path) -> JSON:
    """Create a fresh illustration bundle without modifying audit evidence."""
    validate_plan(plan)
    if output.exists():
        raise ValueError(
            "Use a new output directory; prior illustrations are immutable"
        )
    output.mkdir(parents=True, mode=0o700)
    write(output / "plan.json", plan)
    manifest: JSON = {
        "schemaVersion": "1.0",
        "origin": plan["origin"],
        "startedAt": timestamp(),
        "status": "running",
        "planSHA256": hashlib.sha256((output / "plan.json").read_bytes()).hexdigest(),
        "collectorSHA256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "playwrightVersion": "1.64.1",
        "captures": [],
        "interpretation": "Supplemental visual illustrations captured separately from the scored audit. They do not establish historic appearance, transfer sizes, accessibility semantics, task completion or energy savings.",
        "protocol": {
            "captureMode": "viewport",
            "deviceScaleFactor": 1,
            "reducedMotion": "reduce",
            "animations": "disabled",
            "waitAfterLoadMs": 750,
            "waitAfterScrollMs": 250,
            "perCaptureDeadlineSeconds": 35,
            "freshContextPerCapture": True,
            "actions": "none",
        },
    }
    write(output / "manifest.json", manifest)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        manifest["browserVersion"] = browser.version
        try:
            for specification in plan["captures"]:
                manifest["captures"].append(
                    await capture_view(browser, plan["origin"], specification, output)
                )
                write(output / "manifest.json", manifest)
        finally:
            await browser.close()
    manifest["finishedAt"] = timestamp()
    manifest["status"] = (
        "completed"
        if all(item["status"] == "completed" for item in manifest["captures"])
        else "partial"
    )
    write(output / "manifest.json", manifest)
    return manifest


def main() -> None:
    """Capture only the views explicitly selected by the reporting agent."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text())
    result = asyncio.run(collect(plan, args.output))
    if result["status"] != "completed":
        raise SystemExit(
            "Some illustrations failed; inspect manifest.json and omit failed captures"
        )


if __name__ == "__main__":
    main()
