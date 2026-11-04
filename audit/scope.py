#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = ["httpx==0.28.1", "playwright==1.64.1", "defusedxml==0.7.1"]
# [tool.uv]
# required-version = ">=0.12.20,<0.13"
# ///
"""Extend a bounded site inventory and collect evidence for additional WSG areas."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import logging
import re
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit
from urllib.robotparser import RobotFileParser

import httpx
from defusedxml import ElementTree
from defusedxml.common import DefusedXmlException
from playwright.async_api import Browser, async_playwright
from playwright.async_api import Error as BrowserError

JSON = dict[str, Any]
ROOT = Path(__file__).resolve().parent.parent
LOG = logging.getLogger(__name__)
SITES = {
    "https://guide.wagtail.org": [
        "/en/",
        "/en/how-to-guides/manage-images/",
        "/en/how-to-guides/manage-pages/",
        "/en/releases/new-in-wagtail-8-1/",
    ],
    "https://wagtail.org": [
        "/",
        "/sustainability/",
        "/digital-emissions/",
        "/privacy/",
        "/accessibility/",
    ],
}
FILES = [
    "/robots.txt",
    "/sitemap.xml",
    "/favicon.ico",
    "/site.webmanifest",
    "/opensearch.xml",
    "/.well-known/security.txt",
    "/carbon.txt",
]
DOM = """() => {
 const queries = [], blocked = [];
 function rules(list) { for (const r of list) { if (r.type === CSSRule.MEDIA_RULE) queries.push(r.conditionText); if (r.cssRules) rules(r.cssRules); } }
 for (const sheet of document.styleSheets) { try { rules(sheet.cssRules); } catch { blocked.push(sheet.href); } }
 const data = [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => { try { const value=JSON.parse(s.textContent); return {validJSON:true, types:[value['@type']].flat().filter(Boolean)}; } catch { return {validJSON:false}; } });
 return {
 title: document.title, lang: document.documentElement.lang,
 h1: [...document.querySelectorAll('h1')].map(x=>x.textContent.trim()),
 mainCount: document.querySelectorAll('main,[role="main"]').length,
 navCount: document.querySelectorAll('nav,[role="navigation"]').length,
 canonical: document.querySelector('link[rel="canonical"]')?.href ?? null,
 description: document.querySelector('meta[name="description"]')?.content ?? null,
 structuredData: data,
 manifestLinks: [...document.querySelectorAll('link[rel="manifest"]')].map(x=>x.href),
 searchDescriptionLinks: [...document.querySelectorAll('link[rel="search"]')].map(x=>x.href),
 iconLinks: [...document.querySelectorAll('link[rel~="icon"]')].map(x=>x.href),
 forms: [...document.forms].map(x=>({method:x.method,action:x.action})),
 images: {total:document.images.length,missingAlt:[...document.images].filter(x=>!x.hasAttribute('alt')).length},
 links: [...document.querySelectorAll('a[href]')].map(x=>({url:x.href,text:x.textContent.trim().slice(0,140)})),
 mediaQueries:[...new Set(queries)], inaccessibleStylesheets:blocked,
 autoplayMedia:document.querySelectorAll('video[autoplay],audio[autoplay]').length,
 activeAnimations:document.getAnimations().filter(x=>x.playState==='running').length,
 bodyColors:{color:getComputedStyle(document.body).color,background:getComputedStyle(document.body).backgroundColor},
 rootColors:{color:getComputedStyle(document.documentElement).color,background:getComputedStyle(document.documentElement).backgroundColor},
 preferences:{reducedMotion:matchMedia('(prefers-reduced-motion: reduce)').matches,dark:matchMedia('(prefers-color-scheme: dark)').matches}
 }; }"""


def sample_urls(urls: list[str], seed: str, count: int) -> list[str]:
    """Choose a reproducible hash-ordered pseudo-random subset without replacement."""
    return sorted(
        set(urls), key=lambda url: hashlib.sha256(f"{seed}\n{url}".encode()).digest()
    )[:count]


def same_origin(url: str, origin: str) -> bool:
    """Reject malformed or external sitemap and declared-file URLs."""
    try:
        parsed = urlsplit(url)
        return f"{parsed.scheme}://{parsed.netloc}" == origin
    except ValueError:
        return False


def parse_sitemap(text: str) -> tuple[str, list[str]]:
    """Parse sitemap URLs without resolving XML entities."""
    root = ElementTree.fromstring(text)
    kind = root.tag.rsplit("}", 1)[-1]
    if kind not in {"urlset", "sitemapindex"}:
        raise ValueError("Not a sitemap document")
    namespace = root.tag.rsplit("}", 1)[0] + "}" if "}" in root.tag else ""
    if namespace not in {"", "{http://www.sitemaps.org/schemas/sitemap/0.9}"}:
        raise ValueError("Unrecognized sitemap namespace")
    child = "url" if kind == "urlset" else "sitemap"
    return kind, [
        element.text.strip()
        for parent in root.findall(namespace + child)
        for element in parent.findall(namespace + "loc")
        if element.text
    ]


async def fetch(client: httpx.AsyncClient, url: str) -> tuple[JSON, str]:
    """Fetch bounded metadata documents and preserve errors rather than infer absence."""
    record: JSON = {"url": url, "capturedAt": datetime.now(UTC).isoformat()}
    try:
        async with asyncio.timeout(20):
            async with client.stream("GET", url) as response:
                body = bytearray()
                async for chunk in response.aiter_bytes():
                    body.extend(chunk)
                    if len(body) > 2_000_000:
                        record["truncated"] = True
                        break
                raw = bytes(body[:2_000_000])
                record.update(
                    status=response.status_code,
                    finalUrl=str(response.url),
                    contentType=response.headers.get("content-type"),
                    bodySHA256=hashlib.sha256(raw).hexdigest(),
                    observedBodyBytes=len(raw),
                )
                return record, raw.decode("utf-8", errors="replace")
    except (httpx.HTTPError, TimeoutError) as error:
        record["error"] = type(error).__name__
        return record, ""


async def inventory(client: httpx.AsyncClient, origin: str) -> JSON:
    """Collect advertised URL inventory, standard files, and a bounded sample plan."""
    result: JSON = {
        "site": origin,
        "files": [],
        "sitemaps": [],
        "urls": [],
        "limits": {"sitemaps": 4, "bytesPerFile": 2_000_000},
        "inventoryComplete": False,
    }
    documents: dict[str, str] = {}
    for path in FILES:
        record, body = await fetch(client, origin + path)
        record["id"] = f"file:{origin}{path}"
        # A successful HTML fallback is not proof of a working metadata file.
        record["htmlFallback"] = "text/html" in (record.get("contentType") or "")
        result["files"].append(record)
        if (
            record.get("status") == 200
            and not record.get("truncated")
            and not record["htmlFallback"]
        ):
            documents[path] = body
    robots = RobotFileParser()
    robots.parse(documents.get("/robots.txt", "").splitlines())
    pending = [origin + "/sitemap.xml"]
    pending += [
        line.split(":", 1)[1].strip()
        for line in documents.get("/robots.txt", "").splitlines()
        if line.lower().startswith("sitemap:")
    ]
    visited: set[str] = set()
    urls: set[str] = set()
    errors = False
    while pending and len(visited) < 4:
        url = pending.pop(0)
        if url in visited:
            continue
        if not same_origin(url, origin):
            errors = True
            result["sitemaps"].append(
                {"url": url, "status": "skipped_invalid_or_external_origin"}
            )
            continue
        visited.add(url)
        record, body = await fetch(client, url)
        try:
            if record.get("status") != 200 or record.get("truncated"):
                raise ValueError("Sitemap retrieval incomplete")
            kind, locations = parse_sitemap(body)
            record.update(kind=kind, locations=len(locations))
            if kind == "sitemapindex":
                pending.extend(locations)
            else:
                urls.update(value for value in locations if same_origin(value, origin))
        except (ValueError, ElementTree.ParseError, DefusedXmlException) as error:
            record["parseError"] = type(error).__name__
            errors = True
        result["sitemaps"].append(record)
    result["inventoryComplete"] = not errors and not set(pending) - visited
    result["inventoryMeaning"] = (
        "Advertised sitemap inventory only; not proof of all pages, states, templates, or processes"
    )
    result["urls"] = sorted(urls)
    result["advertisedURLCount"] = len(urls)
    purposeful = [origin + path for path in SITES[origin]]
    candidates = [
        url
        for url in urls
        if url not in purposeful and robots.can_fetch("WebSustainabilityAgents", url)
    ]
    seed = f"wsg-scope-development-v1:{origin}"
    random_urls = sample_urls(candidates, seed, 2)
    result["selection"] = {
        "purposeful": purposeful,
        "pseudoRandom": random_urls,
        "seed": seed,
        "algorithm": "SHA256(seed + newline + URL) ascending, first two unique allowed URLs excluding purposeful sample",
        "eligibleRandomCandidates": len(candidates),
        "departure": "Small development sample; not full evaluation below 1000 pages or STAR's 10–20% larger-site recommendation",
    }
    return result


async def inspect_page(browser: Browser, url: str, reason: str) -> JSON:
    """Observe DOM metadata and preference states without claiming accessibility conformance."""
    result: JSON = {
        "id": f"page:{url}",
        "url": url,
        "selectionReason": reason,
        "capturedAt": datetime.now(UTC).isoformat(),
        "browser": browser.version,
    }
    context = None
    try:
        async with asyncio.timeout(50):
            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                color_scheme="light",
                reduced_motion="no-preference",
            )
            page = await context.new_page()
            response = await page.goto(url, wait_until="load", timeout=30000)
            await page.wait_for_timeout(500)
            result.update(
                status=response.status if response else None, finalUrl=page.url
            )
            result["initial"] = await page.evaluate(DOM)
            await page.emulate_media(reduced_motion="reduce", color_scheme="dark")
            await page.wait_for_timeout(200)
            result["preferences"] = await page.evaluate(DOM)
            if url in {origin + paths[0] for origin, paths in SITES.items()}:
                await page.reload(wait_until="load", timeout=30000)
                await page.wait_for_timeout(300)
                result["preferencesAfterReload"] = await page.evaluate(DOM)

            result["bodyExcerpt"] = (
                (await page.locator("main").first.inner_text(timeout=1000))[:2000]
                if await page.locator("main").count()
                else ""
            )
            result["documentSHA256"] = hashlib.sha256(
                (await page.content()).encode()
            ).hexdigest()
    except (BrowserError, TimeoutError) as error:
        result["error"] = type(error).__name__
    finally:
        if context is not None:
            try:
                async with asyncio.timeout(5):
                    await context.close()
            except (BrowserError, TimeoutError) as error:
                result["cleanupError"] = type(error).__name__

    return result


def source_corroboration(origin: str) -> JSON:
    """Record bounded public-source candidates without asserting deployment identity."""
    folder, paths = (
        (
            "guide",
            [
                "apps/frontend/static_src/js/blocking.js",
                "apps/core/templates/base.html",
                "apps/core/templates/404.html",
                "public/robots.txt",
                "LICENSE",
                "CONTRIBUTING.md",
            ],
        )
        if "guide." in origin
        else (
            "wagtail.org",
            [
                "wagtailio/static/sass/base/_print.scss",
                "wagtailio/static/js/blocking.js",
                "wagtailio/utils/views.py",
                "wagtailio/project_styleguide/templates/patterns/pages/errors/404.html",
            ],
        )
    )
    checkout = ROOT / "local" / folder
    git = shutil.which("git")
    if not checkout.is_dir() or git is None:
        return {"status": "unavailable", "deploymentIdentity": "unknown"}
    revision = subprocess.run(  # noqa: S603 - fixed read-only command
        [git, "rev-parse", "HEAD"],
        cwd=checkout,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    dirty = (
        subprocess.run(  # noqa: S603 - fixed read-only command
            [git, "status", "--porcelain"],
            cwd=checkout,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        != ""
    )
    records = []
    for name in paths:
        path = checkout / name
        if path.exists():
            raw = path.read_bytes()
            lines = raw.decode().splitlines()
            matches = [
                {"line": i + 1, "text": line.strip()[:240]}
                for i, line in enumerate(lines)
                if any(
                    token in line.lower()
                    for token in [
                        "prefers-",
                        "matchmedia",
                        "@media",
                        "theme-dark",
                        "page not found",
                        "sitemap:",
                        "redistribution",
                        "disallow:",
                        "search",
                        "contribut",
                        "<html",
                        "get_current_language",
                    ]
                )
            ]
            records.append(
                {
                    "id": f"source:{folder}/{name}",
                    "path": name,
                    "SHA256": hashlib.sha256(raw).hexdigest(),
                    "selectedLines": matches[:15],
                }
            )
    return {
        "status": "inspected_candidates",
        "repository": folder,
        "revision": revision,
        "dirty": dirty,
        "deploymentIdentity": "unknown",
        "files": records,
    }


async def run(output: Path) -> None:
    """Collect both origin-specific scopes and checkpoint each completed observation."""
    result: JSON = {
        "schemaVersion": "0.1.0",
        "capturedAt": datetime.now(UTC).isoformat(),
        "protocol": {
            "collectorSHA256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "viewport": {"width": 1280, "height": 800},
            "observationMs": 500,
            "pageDeadlineSeconds": 50,
            "cleanupDeadlineSeconds": 5,
            "measurementPurpose": "metadata and preference-state evidence; not a byte or energy comparison",
            "interactionScope": "No form submissions or playback; dark/reduced-motion emulation only",
        },
        "sites": [],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    async with (
        httpx.AsyncClient(timeout=15, follow_redirects=True) as client,
        async_playwright() as playwright,
    ):
        browser = await playwright.chromium.launch()
        try:
            for origin in SITES:
                site = await inventory(client, origin)
                site["sourceCorroboration"] = source_corroboration(origin)
                site["pages"] = []
                result["sites"].append(site)
                selections = (
                    [(url, "purposeful") for url in site["selection"]["purposeful"]]
                    + [
                        (url, "pseudo_random")
                        for url in site["selection"]["pseudoRandom"]
                    ]
                    + [
                        (
                            origin + "/__sustainability_audit_missing_page__",
                            "error_recovery",
                        )
                    ]
                )
                for url, reason in selections:
                    site["pages"].append(await inspect_page(browser, url, reason))
                    if len(site["pages"]) == 1:
                        declared = site["pages"][0].get("initial", {})
                        site["declaredFileChecks"] = []
                        linked = (
                            declared.get("manifestLinks", [])
                            + declared.get("searchDescriptionLinks", [])
                            + declared.get("iconLinks", [])
                        )
                        for link in list(dict.fromkeys(linked))[:4]:
                            if same_origin(link, origin):
                                file_record, _ = await fetch(client, link)
                                site["declaredFileChecks"].append(file_record)
                    output.write_text(json.dumps(result, indent=2) + "\n")
                    LOG.info("Observed %s", url)
        finally:
            await browser.close()


def public_copy(value: Any) -> Any:
    """Remove URL credentials and query/fragment identifiers from the public artifact."""
    if isinstance(value, dict):
        return {public_copy(key): public_copy(item) for key, item in value.items()}
    if isinstance(value, list):
        return [public_copy(item) for item in value]
    if isinstance(value, str):

        def clean(match: re.Match[str]) -> str:
            try:
                parsed = urlsplit(match[0])
                host = parsed.hostname or ""
                if ":" in host:
                    host = f"[{host}]"
                if parsed.port:
                    host += f":{parsed.port}"
                return urlunsplit((parsed.scheme, host, parsed.path, "", ""))
            except ValueError:
                return "[invalid URL removed]"

        return re.sub(r"https?://[^\s<>\"']+", clean, value)
    return value


def main() -> None:
    """Run the bounded scope extension, retaining raw observations privately."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=ROOT / ".audit-work/scope-extension.json"
    )
    parser.add_argument("--publish", type=Path)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    asyncio.run(run(args.output))
    if args.publish:
        raw = args.output.read_bytes()
        result = public_copy(json.loads(raw))
        result["rawSHA256"] = hashlib.sha256(raw).hexdigest()
        result["publicationNote"] = (
            "URL userinfo, queries and fragments removed; public page excerpts retained as untrusted claims."
        )
        args.publish.parent.mkdir(parents=True, exist_ok=True)
        args.publish.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
