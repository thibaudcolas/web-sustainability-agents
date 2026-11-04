#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = ["playwright==1.64.1"]
# [tool.uv]
# required-version = ">=0.12.20,<0.13"
# ///
"""Collect bounded interaction evidence for skill-led WSG interpretation."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlsplit

from playwright.async_api import Browser, CDPSession, Page, async_playwright
from playwright.async_api import Error as BrowserError

JSON = dict[str, Any]
CHECKS: list[JSON] = json.loads(
    Path(__file__).with_name("probe-checks.json").read_text()
)["checks"]

DOM = r"""() => {
 const cap = (items, limit) => ({items: items.slice(0, limit), total: items.length, truncated: items.length > limit});
 const visible = e => { const r=e.getBoundingClientRect(), s=getComputedStyle(e); return r.width>0 && r.height>0 && s.visibility!=='hidden' && s.display!=='none'; };
 const label = e => ({text:(e.innerText||e.textContent||'').trim().slice(0,300), ariaLabel:e.getAttribute('aria-label'), labelledBy:e.getAttribute('aria-labelledby'), title:e.getAttribute('title')});
 const box = e => {const r=e.getBoundingClientRect(); return {x:r.x,y:r.y,width:r.width,height:r.height,visible:visible(e)};};
 const text=document.body?.innerText || '';
 const links=[...document.querySelectorAll('a[href]')].map(e=>({url:e.href,...label(e),...box(e),download:e.getAttribute('download'),type:e.type}));
 return {
  url:location.href,title:document.title,lang:document.documentElement.lang,
  viewport:{width:innerWidth,height:innerHeight,deviceScaleFactor:devicePixelRatio},
  documentSize:{width:document.documentElement.scrollWidth,height:document.documentElement.scrollHeight},
  horizontalOverflow:document.documentElement.scrollWidth>innerWidth+1,
  text:{value:text.slice(0,20000),characters:text.length,truncated:text.length>20000},
  headings:cap([...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].map(e=>({level:e.tagName,...label(e),...box(e)})),100),
  navigation:cap([...document.querySelectorAll('nav,[role="navigation"]')].map(e=>({...label(e),...box(e)})),20),
  links:cap(links,300),
  downloads:cap(links.filter(e=>e.download!==null || /\.(pdf|docx?|xlsx?|pptx?|odt|zip)([?#]|$)/i.test(e.url)),100),
  controls:cap([...document.querySelectorAll('button,input,select,textarea,[role="button"],[role="switch"]')].map(e=>({tag:e.tagName,type:e.type||null,id:e.id,...label(e),...box(e),labels:[...(e.labels||[])].map(l=>l.textContent.trim()),required:e.required||false,disabled:e.disabled||false,checked:typeof e.checked==='boolean'?e.checked:null,autocomplete:e.autocomplete||null})),150),
  overlays:cap([...document.querySelectorAll('dialog,[role="dialog"],[role="alert"],[aria-live]')].map(e=>({...label(e),role:e.getAttribute('role'),live:e.getAttribute('aria-live'),...box(e)})),40),
  images:cap([...document.images].map(e=>({url:e.currentSrc||e.src,alt:e.getAttribute('alt'),loading:e.loading,naturalWidth:e.naturalWidth,naturalHeight:e.naturalHeight,...box(e)})),150),
  media:cap([...document.querySelectorAll('video,audio')].map(e=>({tag:e.tagName,url:e.currentSrc,autoplay:e.autoplay,controls:e.controls,loop:e.loop,muted:e.muted,paused:e.paused,preload:e.preload,...box(e)})),50),
  animations:cap(document.getAnimations().map(a=>({playState:a.playState,currentTime:a.currentTime,iterations:a.effect?.getTiming().iterations===Infinity?'Infinity':a.effect?.getTiming().iterations,target:a.effect?.target?.tagName||null})),100),
  fonts:cap([...document.fonts].map(f=>({family:f.family,status:f.status,weight:f.weight,style:f.style,display:f.display})),100),
  bodyFont:document.body?{family:getComputedStyle(document.body).fontFamily,size:getComputedStyle(document.body).fontSize,lineHeight:getComputedStyle(document.body).lineHeight}:null,
  print:{matches:matchMedia('print').matches,visibleNavigation:[...document.querySelectorAll('nav')].filter(visible).length,visibleImages:[...document.images].filter(visible).length},
  preferences:{reducedMotion:matchMedia('(prefers-reduced-motion: reduce)').matches},
  notification:{apiAvailable:'Notification' in window,permission:'Notification' in window?Notification.permission:null,requestCalls:window.__wsgNotificationRequests||0},
  resources:cap(performance.getEntriesByType('resource').map(r=>({url:r.name,initiatorType:r.initiatorType,startTimeMs:r.startTime,durationMs:r.duration,transferSize:r.transferSize,encodedBodySize:r.encodedBodySize,decodedBodySize:r.decodedBodySize})),300)
 };
}"""
NOTIFICATIONS = """(() => { window.__wsgNotificationRequests=0;
 if ('Notification' in window) { const original=Notification.requestPermission;
 Notification.requestPermission=function(...args) {window.__wsgNotificationRequests++; return original.apply(this,args);}; }
})();"""


def timestamp() -> str:
    """Record collection time for evidence provenance."""
    return datetime.now(UTC).isoformat()


def validate_plan(plan: JSON) -> None:
    """Bound entry points and avoid silently expanding beyond the supplied origin."""
    origin = urlsplit(plan["origin"])
    if origin.scheme not in {"http", "https"} or not origin.netloc or origin.username:
        raise ValueError("Plan requires an HTTP(S) origin without credentials")
    if origin.path not in {"", "/"} or origin.query or origin.fragment:
        raise ValueError("Plan origin cannot contain a path, query or fragment")
    pages = plan.get("pages", [])
    journeys = plan.get("journeys", [])
    if not pages or len(pages) > 20 or len(journeys) > 10:
        raise ValueError("Plan requires 1–20 pages and at most 10 journeys")
    for entry in [*pages, *journeys]:
        parsed = urlsplit(entry["url"])
        if (parsed.scheme, parsed.netloc) != (origin.scheme, origin.netloc):
            raise ValueError("All entry URLs must match the plan origin")
        if not isinstance(entry.get("id"), str) or not entry["id"]:
            raise ValueError("Each page and journey requires an ID")
    for entries in [pages, journeys]:
        if len({entry["id"] for entry in entries}) != len(entries):
            raise ValueError("Duplicate entry IDs")
    for journey in journeys:
        if len(journey.get("actions", [])) > 20:
            raise ValueError("Journeys are limited to 20 actions")
        for action in journey.get("actions", []):
            if action.get("type") not in {"click", "fill", "press"}:
                raise ValueError(
                    "Journey supports only explicit click/fill/press actions"
                )
            if not isinstance(action.get("selector"), str) or not action["selector"]:
                raise ValueError("Every action requires a selector")
            required = {"fill": "value", "press": "key"}.get(action["type"])
            if required and not isinstance(action.get(required), str):
                raise ValueError(f"Action requires {required}")


async def snapshot(page: Page) -> JSON:
    """Capture bounded observable facts, leaving qualitative decisions to reviewers."""
    return cast(JSON, await page.evaluate(DOM))


async def start_coverage(cdp: CDPSession) -> None:
    """Enable initial-load code observations in a separate measurement context."""
    await cdp.send("Profiler.enable")
    await cdp.send(
        "Profiler.startPreciseCoverage", {"callCount": False, "detailed": True}
    )
    await cdp.send("DOM.enable")
    await cdp.send("CSS.enable")
    await cdp.send("CSS.startRuleUsageTracking")


async def finish_coverage(cdp: CDPSession) -> JSON:
    """Keep raw offset observations rather than misreporting them as removable bytes."""
    javascript = await cdp.send("Profiler.takePreciseCoverage")
    css = await cdp.send("CSS.stopRuleUsageTracking")
    await cdp.send("Profiler.stopPreciseCoverage")
    scripts = javascript.get("result", [])
    bounded = []
    for script in scripts[:100]:
        functions = script.get("functions", [])
        bounded.append(
            {
                "url": script.get("url"),
                "scriptId": script["scriptId"],
                "functions": [
                    {
                        "ranges": function["ranges"][:100],
                        "rangesTruncated": len(function["ranges"]) > 100,
                    }
                    for function in functions[:200]
                ],
                "functionsTruncated": len(functions) > 200,
            }
        )
    return {
        "scope": "Initial load plus 500 ms; main CDP target only; offsets are source positions, not network bytes; unexecuted code may be needed later",
        "javascript": bounded,
        "scriptsTruncated": len(scripts) > 100,
        "cssRuleUsage": css.get("ruleUsage", [])[:2000],
        "cssRulesTruncated": len(css.get("ruleUsage", [])) > 2000,
    }


async def inspect_page(browser: Browser, target: JSON) -> JSON:
    """Observe initial, resized, reduced-motion and print states without user actions."""
    result: JSON = {
        "id": target["id"],
        "url": target["url"],
        "task": target.get("task"),
        "startedAt": timestamp(),
        "states": [],
        "errors": [],
    }
    context = await browser.new_context(
        viewport={"width": 1280, "height": 800},
        device_scale_factor=1,
        locale="en-GB",
        timezone_id="Europe/London",
        service_workers="block",
    )
    try:
        async with asyncio.timeout(50):
            page = await context.new_page()
            await page.add_init_script(NOTIFICATIONS)
            cdp = await context.new_cdp_session(page)
            try:
                await start_coverage(cdp)
            except BrowserError as error:
                result["errors"].append(
                    {"phase": "coverage_start", "error": str(error)}
                )
            response = await page.goto(target["url"], wait_until="load", timeout=25000)
            result["documentStatus"] = response.status if response else None
            await page.wait_for_timeout(500)
            try:
                result["codeCoverage"] = await finish_coverage(cdp)
            except BrowserError as error:
                result["errors"].append(
                    {"phase": "coverage_finish", "error": str(error)}
                )
            result["states"].append(
                {
                    "name": "desktop",
                    "capturedAt": timestamp(),
                    "observations": await snapshot(page),
                }
            )
            await page.set_viewport_size({"width": 360, "height": 800})
            await page.wait_for_timeout(250)
            result["states"].append(
                {
                    "name": "narrow",
                    "capturedAt": timestamp(),
                    "observations": await snapshot(page),
                }
            )
            await page.set_viewport_size({"width": 1280, "height": 800})
            await page.emulate_media(reduced_motion="reduce")
            await page.wait_for_timeout(250)
            result["states"].append(
                {
                    "name": "reduced_motion",
                    "capturedAt": timestamp(),
                    "observations": await snapshot(page),
                }
            )
            await page.emulate_media(media="print")
            await page.wait_for_timeout(250)
            result["states"].append(
                {
                    "name": "print",
                    "capturedAt": timestamp(),
                    "observations": await snapshot(page),
                }
            )
            result["frames"] = [frame.url for frame in page.frames]
    except (BrowserError, TimeoutError) as error:
        result["errors"].append(
            {"phase": "page", "error": str(error) or type(error).__name__}
        )
    finally:
        try:
            async with asyncio.timeout(5):
                await context.close()
        except (BrowserError, TimeoutError) as error:
            result["errors"].append(
                {"phase": "cleanup", "error": str(error) or type(error).__name__}
            )
    nojs = await inspect_nojs(browser, target["url"])
    result["states"].append(nojs)
    if nojs.get("error"):
        result["errors"].append({"phase": "no_javascript", "error": nojs["error"]})
    result["status"] = "completed_with_errors" if result["errors"] else "completed"
    return result


async def inspect_nojs(browser: Browser, url: str) -> JSON:
    """Observe a separate fresh no-JavaScript context without claiming task completion."""
    result: JSON = {"name": "no_javascript", "capturedAt": timestamp()}
    context = await browser.new_context(
        viewport={"width": 1280, "height": 800},
        java_script_enabled=False,
        locale="en-GB",
        service_workers="block",
    )
    try:
        async with asyncio.timeout(30):
            page = await context.new_page()
            response = await page.goto(url, wait_until="load", timeout=25000)
            result["documentStatus"] = response.status if response else None
            result["observations"] = await snapshot(page)
    except (BrowserError, TimeoutError) as error:
        result["error"] = str(error) or type(error).__name__
    finally:
        try:
            async with asyncio.timeout(5):
                await context.close()
        except (BrowserError, TimeoutError) as error:
            result["error"] = str(error) or type(error).__name__
    return result


async def inspect_journey(browser: Browser, journey: JSON) -> JSON:
    """Run only supplied actions, recording missing controls and completion separately."""
    result: JSON = {
        "id": journey["id"],
        "url": journey["url"],
        "task": journey.get("task"),
        "actions": [],
        "errors": [],
        "successSelectorVisible": None,
    }
    context = await browser.new_context(
        viewport={"width": 1280, "height": 800}, locale="en-GB", service_workers="block"
    )
    try:
        async with asyncio.timeout(90):
            page = await context.new_page()
            await page.add_init_script(NOTIFICATIONS)
            response = await page.goto(journey["url"], wait_until="load", timeout=25000)
            result["documentStatus"] = response.status if response else None
            result["before"] = await snapshot(page)
            for action in journey.get("actions", []):
                event: JSON = {"action": action, "startedAt": timestamp()}
                result["actions"].append(event)
                try:
                    locator = page.locator(action["selector"])
                    if action.get("optional") and not await locator.count():
                        event["status"] = "not_present"
                        continue
                    if action["type"] == "click":
                        await locator.click(timeout=5000)
                    elif action["type"] == "fill":
                        await locator.fill(action["value"], timeout=5000)
                    else:
                        await locator.press(action["key"], timeout=5000)
                    event["status"] = "completed"
                except BrowserError as error:
                    event.update(status="failed", error=str(error))
                    break
            await page.wait_for_timeout(500)
            result["after"] = await snapshot(page)
            if selector := journey.get("successSelector"):
                result["successSelectorVisible"] = await page.locator(
                    selector
                ).first.is_visible()
    except (BrowserError, TimeoutError) as error:
        result["errors"].append(str(error) or type(error).__name__)
    finally:
        try:
            async with asyncio.timeout(5):
                await context.close()
        except (BrowserError, TimeoutError) as error:
            result["errors"].append(str(error) or type(error).__name__)
    result["status"] = (
        "completed_with_errors"
        if result["errors"] or any(a["status"] == "failed" for a in result["actions"])
        else "completed"
    )
    return result


def write_private(path: Path, result: JSON) -> None:
    """Checkpoint evidence privately; page text and configured inputs need publication review."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(mode=0o600, exist_ok=True)
    path.chmod(0o600)
    path.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")


async def collect(plan: JSON, output: Path) -> JSON:
    """Collect evidence from any bounded one-origin plan without hardcoded site knowledge."""
    validate_plan(plan)
    result: JSON = {
        "schemaVersion": "0.1.0",
        "site": plan["origin"],
        "startedAt": timestamp(),
        "purpose": plan.get("purpose"),
        "planSHA256": hashlib.sha256(
            json.dumps(plan, sort_keys=True).encode()
        ).hexdigest(),
        "protocol": {
            "pageDeadlineSeconds": 50,
            "additionalNoJavaScriptDeadlineSeconds": 30,
            "journeyDeadlineSeconds": 90,
            "observationMs": 500,
            "states": "Initial desktop, then same document resized to 360 CSS px, live reduced-motion change, print emulation; separate fresh no-JavaScript context. Resized and emulated states are not independent cold loads or real-device tests.",
            "measurementPurpose": "Qualitative review and bounded interaction evidence, not headline bytes or energy",
            "limitations": [
                "Main document observations; embedded frames are not traversed",
                "No scrolling or interaction in page probes; journey actions must be explicit",
                "Resource Timing zeros may reflect timing restrictions or cache, not zero traffic",
                "Notification requestPermission calls counted with a delegating wrapper",
                "Print emulation is not PDF pagination or document accessibility testing",
            ],
        },
        "checkDefinitions": CHECKS,
        "pages": [],
        "journeys": [],
        "executionStatus": "running",
    }
    write_private(output, result)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        result["browser"] = browser.version
        try:
            for target in plan["pages"]:
                result["pages"].append(await inspect_page(browser, target))
                write_private(output, result)
            for journey in plan.get("journeys", []):
                result["journeys"].append(await inspect_journey(browser, journey))
                write_private(output, result)
        finally:
            await browser.close()
    result["finishedAt"] = timestamp()
    result["executionStatus"] = (
        "completed_with_errors"
        if any(
            item["status"] != "completed"
            for item in [*result["pages"], *result["journeys"]]
        )
        else "completed"
    )
    write_private(output, result)
    return result


def main() -> None:
    """Run a private evidence capture for later skill-led interpretation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    asyncio.run(collect(json.loads(args.plan.read_text()), args.output))


if __name__ == "__main__":
    main()
