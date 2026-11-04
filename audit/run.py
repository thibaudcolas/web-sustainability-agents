#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = [
#   "playwright==1.64.1",
#   "httpx==0.28.1",
#   "wappalyzer==2.0.4",
#   "dnspython==2.9.2",
# ]
# [tool.uv]
# required-version = ">=0.12.20,<0.13"
# ///
"""Measure bounded page states, discover disclosures, and identify technologies.

Run ``./audit/run.py --help``. Network measurements never share a context with
Wappalyzer. Outputs are private by default; use --publish for sanitized evidence.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.metadata
import json
import logging
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, cast
from urllib.parse import urljoin, urlsplit, urlunsplit

import dns.asyncresolver
import dns.exception
import httpx
from playwright.async_api import Browser, FrameLocator, Page, async_playwright
from playwright.async_api import Error as BrowserError

JSON = dict[str, Any]
ROOT = Path(__file__).resolve().parent.parent
LOG = logging.getLogger(__name__)
PROTOCOL: JSON = {
    "version": "0.2.0",
    "viewport": {"width": 1280, "height": 800},
    "deviceScaleFactor": 1,
    "locale": "en-GB",
    "timezoneId": "Europe/London",
    "observationMs": 3000,
    "byteDefinition": "CDP received network bytes including reported overhead; failed/unfinished transfers remain explicitly unresolved",
    "scope": "Main CDP session; service workers blocked; child-frame coverage incomplete; no network interception or request blocking",
    "headlinePhase": "initial",
    "phaseMeaning": "Cumulative totals in one context; deltas are additional bytes since the preceding checkpoint, not independent page loads",
}


def timestamp() -> str:
    """Return an evidence timestamp, not an editorial dateline."""
    return datetime.now(UTC).isoformat()


def read_json(path: Path) -> JSON:
    """Read an object-shaped JSON document."""
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def safe_url(value: str) -> str:
    """Remove URL credentials, query identifiers, and fragments for publication."""
    try:
        parts = urlsplit(value)
        port = parts.port
    except ValueError:
        return "[invalid URL removed]"
    if parts.scheme not in {"http", "https"}:
        return value
    host = parts.hostname or ""
    if ":" in host:
        host = f"[{host}]"
    if port:
        host += f":{port}"
    return urlunsplit((parts.scheme, host, parts.path, "", ""))


def sanitize(value: Any) -> Any:
    """Sanitize URL-shaped values recursively without publishing credentials."""
    if isinstance(value, dict):
        return {sanitize(key): sanitize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if isinstance(value, str):
        return re.sub(r"https?://[^\s<>\"']+", lambda match: safe_url(match[0]), value)
    return value


def is_http_url(value: str) -> bool:
    """Reject malformed and non-HTTP discovery URLs without aborting a scan."""
    try:
        parsed = urlsplit(value)
        _ = parsed.port
        return parsed.scheme in {"http", "https"} and bool(parsed.hostname)
    except ValueError:
        return False


def resolve_link(base: str, link: str) -> str:
    """Resolve links while retaining malformed candidates for error reporting."""
    try:
        return urljoin(base, link)
    except ValueError:
        return link


def save_private(path: Path | None, result: JSON) -> None:
    """Checkpoint private results so later failures do not discard completed work."""
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.touch(mode=0o600, exist_ok=True)
    temporary.chmod(0o600)
    temporary.write_text(json.dumps(result, indent=2, default=str) + "\n")
    temporary.replace(path)


class NetworkLedger:
    """Retain all observed requests across phases without attributing errors as defects."""

    def __init__(self) -> None:
        """Initialize the request journal."""
        self.requests: dict[str, JSON] = {}
        self.redirects: list[JSON] = []
        self.phase = "initial"
        self.coverage_gaps: set[str] = set()

    def child_frame(self, _: Any) -> None:
        """Keep a sticky coverage gap even when a child frame later disappears."""
        self.coverage_gaps.add(
            "Child frame observed; subframe traffic may be incomplete"
        )

    def websocket(self, _: JSON) -> None:
        """Record unsupported streaming traffic rather than silently missing bytes."""
        self.coverage_gaps.add(
            "WebSocket observed; frames are outside this byte ledger"
        )

    def requested(self, event: JSON) -> None:
        """Start a request and preserve redirect responses before ID reuse."""
        request_id = event["requestId"]
        if event.get("redirectResponse") and request_id in self.requests:
            previous = self.requests[request_id]
            response = event["redirectResponse"]
            previous.update(
                status=response["status"],
                receivedBytes=response.get("encodedDataLength"),
                finished=True,
            )
            self.redirects.append(previous)
        self.requests[request_id] = {
            "id": request_id,
            "url": event["request"]["url"],
            "type": event.get("type"),
            "requestedInPhase": self.phase,
            "finished": False,
            "receivedBytes": None,
            "fromCache": False,
            "partialBodyBytes": 0,
        }

    def response(self, event: JSON) -> None:
        """Record selected response metadata, excluding cookies and credentials."""
        if entry := self.requests.get(event["requestId"]):
            response = event["response"]
            if response.get("fromServiceWorker"):
                self.coverage_gaps.add("Unexpected service-worker response")
            selected = {
                "cache-control",
                "content-encoding",
                "content-length",
                "content-type",
                "etag",
                "vary",
            }
            entry.update(
                status=response["status"],
                mimeType=response.get("mimeType"),
                fromCache=entry["fromCache"] or response.get("fromDiskCache", False),
                fromServiceWorker=response.get("fromServiceWorker", False),
                headers={
                    key.lower(): value
                    for key, value in response["headers"].items()
                    if key.lower() in selected
                },
            )

    def data(self, event: JSON) -> None:
        """Keep partial encoded body observations without inventing missing overhead."""
        if entry := self.requests.get(event["requestId"]):
            entry["partialBodyBytes"] += event.get("encodedDataLength", 0)

    def finished(self, event: JSON) -> None:
        """Record the authoritative received total for a completed request."""
        if entry := self.requests.get(event["requestId"]):
            entry.update(finished=True, receivedBytes=event["encodedDataLength"])

    def failed(self, event: JSON) -> None:
        """Keep a failed request visible; missing bytes are not inferred to be zero."""
        if entry := self.requests.get(event["requestId"]):
            entry.update(finished=True, error=event["errorText"])

    def cached(self, event: JSON) -> None:
        """Mark cache reuse without disabling the browser cache."""
        if entry := self.requests.get(event["requestId"]):
            entry["fromCache"] = True

    def snapshot(self, previous_bytes: int = 0) -> JSON:
        """Freeze cumulative bytes and independent accounting and resource-error states."""
        resources = json.loads(json.dumps([*self.redirects, *self.requests.values()]))
        unresolved = [
            entry["id"]
            for entry in resources
            if not entry["finished"] or entry["receivedBytes"] is None
        ]
        received = sum(
            entry["receivedBytes"]
            if entry["receivedBytes"] is not None
            else entry["partialBodyBytes"]
            for entry in resources
        )
        return {
            "receivedBytes": received,
            "additionalBytes": received - previous_bytes,
            "requestCount": len(resources),
            "unresolvedRequestIds": unresolved,
            "accountingStatus": "partial"
            if unresolved or self.coverage_gaps or received < previous_bytes
            else "complete_within_protocol",
            "coverageGaps": sorted(self.coverage_gaps),
            "nonMonotonicBytes": received < previous_bytes,
            "resourceErrors": [
                {
                    "id": entry["id"],
                    "url": entry["url"],
                    "status": entry.get("status"),
                    "error": entry.get("error"),
                }
                for entry in resources
                if entry.get("error") or entry.get("status", 0) >= 400
            ],
            "resources": resources,
        }


async def _perform_action(page: Page, action: JSON) -> JSON:
    """Execute a configured bounded interaction, never guess a consent choice."""
    scope: Page | FrameLocator = (
        page.frame_locator(action["frameSelector"])
        if action.get("frameSelector")
        else page
    )
    locator = scope.locator(action["selector"])
    result: JSON = {"action": action, "startedAt": timestamp()}
    try:
        if await locator.count() == 0 or not await locator.first.is_visible():
            result["status"] = (
                "not_present" if action.get("optional", False) else "failed"
            )
            return result
        kind = action["type"]
        if kind == "click":
            await locator.click(timeout=5000)
        elif kind == "fill":
            await locator.fill(action["value"], timeout=5000)
        elif kind == "press":
            await locator.press(action["key"], timeout=5000)
        elif kind == "check":
            await locator.check(timeout=5000)
        elif kind == "select":
            await locator.select_option(action["value"], timeout=5000)
        else:
            raise ValueError(f"Unsupported interaction: {kind}")
        result["status"] = "completed"
    except BrowserError as error:
        result.update(status="failed", error=str(error))
    return result


async def perform_action(page: Page, action: JSON) -> JSON:
    """Bound the complete action, including iframe resolution and selector lookup."""
    try:
        async with asyncio.timeout(10):
            return await _perform_action(page, action)
    except TimeoutError:
        return {
            "action": action,
            "status": "failed",
            "error": "Interaction deadline exceeded",
            "capturedAt": timestamp(),
        }


async def checkpoint(page: Page, ledger: NetworkLedger, previous: int) -> JSON:
    """Combine a frozen network snapshot with the current page state."""
    state = cast(
        JSON,
        await page.evaluate("""() => ({
      viewport: {width: innerWidth, height: innerHeight, deviceScaleFactor: devicePixelRatio},
      scrollY, documentHeight: document.documentElement.scrollHeight,
      title: document.title,
      links: [...document.querySelectorAll('a[href]')].map(a => ({url: a.href, text: a.textContent.trim().slice(0,160)})),
      images: [...document.images].map(img => ({url: img.currentSrc || img.src, loading: img.loading, naturalWidth: img.naturalWidth, renderedWidth: img.getBoundingClientRect().width, top: img.getBoundingClientRect().top + scrollY}))
    })"""),
    )
    snapshot = ledger.snapshot(previous)
    frames = [frame.url for frame in page.frames]
    if len(frames) > 1:
        snapshot["accountingStatus"] = "partial"
    snapshot.update(
        phase=ledger.phase,
        capturedAt=timestamp(),
        finalUrl=page.url,
        frames=frames,
        frameCoverage="partial"
        if len(frames) > 1 or any("Child frame" in gap for gap in ledger.coverage_gaps)
        else "main_frame",
        state=state,
    )
    return snapshot


async def collect(
    browser: Browser, target: JSON, branch: JSON, observation_ms: int = 3000
) -> JSON:
    """Measure initial, post-choice, and post-scroll totals in one fresh context."""
    result: JSON = {
        "id": f"{target['id']}-{branch['name']}",
        "url": target["url"],
        "branch": branch["name"],
        "startedAt": timestamp(),
        "browser": browser.version,
        "phases": [],
        "actions": [],
    }
    context = await browser.new_context(
        viewport=PROTOCOL["viewport"],
        device_scale_factor=1,
        locale="en-GB",
        timezone_id="Europe/London",
        service_workers="block",
    )
    try:
        page = await context.new_page()
        cdp = await context.new_cdp_session(page)
        ledger = NetworkLedger()
        page.on("frameattached", ledger.child_frame)
        await cdp.send("Network.enable")
        for event, handler in {
            "Network.requestWillBeSent": ledger.requested,
            "Network.responseReceived": ledger.response,
            "Network.dataReceived": ledger.data,
            "Network.loadingFinished": ledger.finished,
            "Network.loadingFailed": ledger.failed,
            "Network.requestServedFromCache": ledger.cached,
            "Network.webSocketCreated": ledger.websocket,
        }.items():
            cdp.on(event, handler)
        try:
            response = await page.goto(target["url"], wait_until="load", timeout=30000)
            result["documentStatus"] = response.status if response else None
        except BrowserError as error:
            result["navigationError"] = str(error)
        await page.wait_for_timeout(observation_ms)
        initial = await checkpoint(page, ledger, 0)
        result["phases"].append(initial)
        ledger.phase = "after_consent"
        for action in branch.get("actions", []):
            result["actions"].append(await perform_action(page, action))
        performed = any(action["status"] == "completed" for action in result["actions"])
        if performed:
            await page.wait_for_timeout(observation_ms)
        consent = await checkpoint(page, ledger, initial["receivedBytes"])
        consent["interactionStatus"] = (
            "failed"
            if any(a["status"] == "failed" for a in result["actions"])
            else "completed"
            if performed
            else "not_applicable_or_not_present"
        )
        result["phases"].append(consent)
        ledger.phase = "after_scroll"
        steps = 0
        at_bottom = False
        while steps < 60:
            await page.evaluate("window.scrollBy(0, innerHeight * 0.8)")
            await page.wait_for_timeout(200)
            steps += 1
            at_bottom = bool(
                await page.evaluate(
                    "scrollY + innerHeight >= document.documentElement.scrollHeight - 1"
                )
            )
            if at_bottom:
                # Allow intersection observers to append more content before deciding.
                await page.wait_for_timeout(500)
                at_bottom = bool(
                    await page.evaluate(
                        "scrollY + innerHeight >= document.documentElement.scrollHeight - 1"
                    )
                )
                if at_bottom:
                    break
        await page.wait_for_timeout(observation_ms)
        scrolled = await checkpoint(page, ledger, consent["receivedBytes"])
        scrolled.update(
            scrollSteps=steps,
            reachedBottom=bool(
                await page.evaluate(
                    "scrollY + innerHeight >= document.documentElement.scrollHeight - 1"
                )
            ),
        )
        result["phases"].append(scrolled)
        return result
    except BrowserError as error:
        result["collectionError"] = str(error)
        return result
    finally:
        await context.close()


class Document(HTMLParser):
    """Extract bounded text and links for disclosure discovery, not compliance verdicts."""

    def __init__(self) -> None:
        """Initialize bounded extraction state."""
        super().__init__()
        self.links: list[JSON] = []
        self.text: list[str] = []
        self.href: str | None = None
        self.label: list[str] = []
        self.ignored = 0
        self.main_depth = 0
        self.main_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Collect links and skip script/style bodies."""
        if tag in {"script", "style"}:
            self.ignored += 1
        if tag in {"main", "article"}:
            self.main_depth += 1
        if tag == "a":
            self.href = dict(attrs).get("href")
            self.label = []

    def handle_endtag(self, tag: str) -> None:
        """Finish a link or ignored text block."""
        if tag in {"script", "style"}:
            self.ignored = max(0, self.ignored - 1)
        if tag in {"main", "article"}:
            self.main_depth = max(0, self.main_depth - 1)
        if tag == "a" and self.href:
            self.links.append({"url": self.href, "text": " ".join(self.label)})
            self.href = None

    def handle_data(self, data: str) -> None:
        """Retain document text outside executable/style content."""
        if not self.ignored:
            self.text.append(data)
            if self.main_depth:
                self.main_text.append(data)
            if self.href:
                self.label.append(data)


async def _fetch_document(client: httpx.AsyncClient, url: str) -> tuple[JSON, str]:
    """Retrieve a bounded public document and retain failures as discovery evidence."""
    record: JSON = {"url": url, "capturedAt": timestamp()}
    if not is_http_url(url):
        return {**record, "error": "Unsupported URL scheme"}, ""
    try:
        async with client.stream("GET", url) as response:
            body = bytearray()
            async for chunk in response.aiter_bytes():
                body.extend(chunk)
                if len(body) > 1_000_000:
                    record["truncated"] = True
                    break
            record.update(
                status=response.status_code,
                finalUrl=str(response.url),
                contentType=response.headers.get("content-type"),
                carbonLocation=response.headers.get("carbontxt-location"),
                sha256=hashlib.sha256(body).hexdigest(),
            )
            return record, body.decode("utf-8", errors="replace")
    except httpx.HTTPError as error:
        return {**record, "error": str(error)}, ""


async def fetch_document(
    client: httpx.AsyncClient, url: str, total_timeout: float = 20
) -> tuple[JSON, str]:
    """Enforce a total deadline as well as HTTP inactivity and body-size limits."""
    try:
        async with asyncio.timeout(total_timeout):
            return await _fetch_document(client, url)
    except (TimeoutError, ValueError, httpx.InvalidURL) as error:
        return {
            "url": url,
            "capturedAt": timestamp(),
            "error": type(error).__name__,
        }, ""


def disclosure_urls(parsed: JSON) -> list[str]:
    """Extract declared disclosure URLs without treating TOML parsing as validation."""
    org = parsed.get("org", {})
    if not isinstance(org, dict):
        return []
    records = org.get("disclosures", [])
    if not isinstance(records, list):
        return []
    return [
        entry["url"]
        for entry in records
        if isinstance(entry, dict)
        and isinstance(entry.get("url"), str)
        and is_http_url(entry["url"])
    ]


async def discover(
    client: httpx.AsyncClient,
    url: str,
    links: list[JSON],
    statement_urls: list[str] | None = None,
) -> JSON:
    """Try carbon.txt locations and bounded linked/common sustainability pages."""
    parts = urlsplit(url)
    origin = f"{parts.scheme}://{parts.netloc}"
    result: JSON = {
        "site": origin,
        "carbonAttempts": [],
        "documents": [],
        "dns": {},
        "scope": "DNS TXT, root, well-known, HTTP header; up to six linked, supplied, or common-path disclosures, with one-hop follow-up. Not an exhaustive search or verification of claims.",
    }
    locations = [f"{origin}/carbon.txt", f"{origin}/.well-known/carbon.txt"]
    try:
        answers = await dns.asyncresolver.resolve(
            parts.hostname or "", "TXT", lifetime=4
        )
        for answer in answers:
            text = b"".join(answer.strings).decode(errors="replace")
            if text.startswith("carbon-txt-location="):
                locations.insert(0, text.split("=", 1)[1])
        result["dns"]["status"] = "queried"
    except dns.exception.DNSException as error:
        result["dns"] = {
            "status": "unavailable_or_absent",
            "reason": type(error).__name__,
        }
    home_record, home_text = await fetch_document(client, url)
    result["homepage"] = home_record
    if home_record.get("carbonLocation"):
        locations.append(resolve_link(url, home_record["carbonLocation"]))
    document = Document()
    document.feed(home_text)
    candidates: list[tuple[str, str]] = []
    found_carbon = False
    for location in dict.fromkeys(locations):
        record, text = await fetch_document(client, location)
        if record.get("status") == 200 and not record.get("truncated"):
            try:
                parsed = tomllib.loads(text)
                urls = disclosure_urls(parsed)
                record.update(
                    parseStatus="parsed",
                    declaredVersion=parsed.get("version"),
                    schemaValidated=False,
                    disclosureUrls=urls,
                    declarations=parsed,
                )
                if urls:
                    found_carbon = True
                    candidates.extend((item, "carbon.txt disclosure") for item in urls)
            except tomllib.TOMLDecodeError:
                record["parseStatus"] = "not_toml"
        result["carbonAttempts"].append(record)
        if found_carbon:
            break
    candidates.extend(
        (item, "supplied statement hint; scope must be corroborated")
        for item in statement_urls or []
    )
    for link in [*links, *document.links]:
        candidate = resolve_link(url, link["url"])
        label = (link.get("text", "") + " " + candidate).lower()
        if any(
            word in label
            for word in (
                "sustainab",
                "carbon-footprint",
                "emissions",
                "environmental",
                "digital-footprint",
            )
        ):
            candidates.append((candidate, "linked sustainability or footprint page"))
    if not found_carbon:
        candidates.extend(
            (origin + path, "common-path fallback")
            for path in ("/sustainability/", "/sustainability-statement/")
        )
    visited: set[str] = set()
    for candidate, reason in candidates:
        candidate = candidate.split("#", 1)[0]
        if candidate in visited or len(visited) >= 6 or not is_http_url(candidate):
            continue
        visited.add(candidate)
        record, text = await fetch_document(client, candidate)
        record["discoveredVia"] = reason
        if record.get("status") == 200 and "html" in (record.get("contentType") or ""):
            doc = Document()
            doc.feed(text)
            record["textExcerpt"] = " ".join(
                " ".join(doc.main_text or doc.text).split()
            )[:3000]
            record["excerptScope"] = (
                "main/article text" if doc.main_text else "document text"
            )
            record["claimsVerified"] = False
            # Follow one relevant evidence link rather than crawling the site.
            if len(visited) == 1:
                for link in doc.links:
                    link_url = resolve_link(record["finalUrl"], link["url"])
                    if any(
                        word in (link.get("text", "") + " " + link_url).lower()
                        for word in ("footprint", "emissions", "measures up")
                    ):
                        candidates.insert(
                            1, (link_url, "linked from discovered statement")
                        )
                        break
        result["documents"].append(record)
    result["carbonStatus"] = (
        "disclosures_found" if found_carbon else "not_found_within_discovery_scope"
    )
    return result


def technologies(urls: list[str]) -> JSON:
    """Run pinned PyPI Wappalyzer separately from network measurements."""
    package = importlib.metadata.distribution("wappalyzer")
    fingerprints = {
        str(path): hashlib.sha256(
            Path(str(package.locate_file(path))).read_bytes()
        ).hexdigest()
        for path in package.files or []
        if str(path).endswith((".zip", ".crx"))
    }
    result: JSON = {
        "package": "wappalyzer",
        "version": package.version,
        "mode": "full",
        "capturedAt": timestamp(),
        "fingerprintArchives": fingerprints,
        "interpretation": "Heuristic detections, not calibrated probabilities or proof of deployed versions. Missing detection is not absence. Separate browser and requests excluded from page-load totals.",
    }
    with tempfile.TemporaryDirectory() as directory:
        inputs = Path(directory) / "urls.txt"
        output = Path(directory) / "technologies.json"
        inputs.write_text("\n".join(urls))
        try:
            completed = subprocess.run(  # noqa: S603 - fixed module, argv array, no shell
                [
                    sys.executable,
                    "-m",
                    "wappalyzer",
                    "-i",
                    str(inputs),
                    "-w",
                    "1",
                    "-t",
                    "20",
                    "-oJ",
                    str(output),
                ],
                capture_output=True,
                text=True,
                timeout=90 * len(urls),
                check=False,
            )
            result["exitCode"] = completed.returncode
            result["scanErrors"] = [
                line
                for line in completed.stderr.splitlines()
                if "error" in line.lower()
            ]
            if output.exists():
                try:
                    result["detections"] = read_json(output)
                    result["reviewHints"] = technology_hints(result["detections"])
                except ValueError:
                    result["error"] = "Malformed technology output"
            else:
                result["error"] = completed.stderr[-1500:]
        except subprocess.TimeoutExpired:
            result["error"] = "Technology scan timed out"
    return result


def technology_hints(detections: JSON) -> JSON:
    """Adapt follow-up questions to detected technologies without inferring defects."""
    guidance = {
        "Wagtail": "Review Wagtail renditions, rich-text output, templates, and cache invalidation before proposing framework replacement or client-side rendering changes.",
        "Django": "Corroborate server-side caching and database work with runtime evidence; a framework fingerprint does not measure backend efficiency.",
        "Cloudflare": "Separate CDN delivery from origin hosting; a CDN detection does not establish low-carbon electricity or origin cache efficiency.",
        "Plausible": "Check observed request outcomes; detected script markup does not establish successful analytics execution or justify repairing the site before measuring it.",
        "Google Analytics": "Review observed loading phases and the owner's analytics needs before recommending removal.",
        "PWA": "Test offline behavior explicitly; a manifest or PWA fingerprint does not prove offline support or an active service worker.",
    }
    return {
        url: [
            {"technology": name, "followUp": guidance[name]}
            for name in values
            if name in guidance
        ]
        for url, values in detections.items()
    }


def rate_initial(run: JSON) -> JSON:
    """Call the existing pinned CO2.js library instead of duplicating SWDM formulas."""
    if not run["phases"]:
        return {"status": "not_calculated", "reason": "No initial capture"}
    initial = run["phases"][0]
    capture = {
        "complete": initial["accountingStatus"] == "complete_within_protocol"
        and 200 <= (run.get("documentStatus") or 0) < 400
        and not run.get("navigationError"),
        "cache": "cold",
        "receivedBytes": initial["receivedBytes"],
    }
    node = shutil.which("node")
    if node is None:
        return {
            "status": "not_calculated",
            "reason": "CO2.js bridge requires Node.js and npm ci",
        }
    # The sole JS interoperability bridge uses the repository's existing library adapter.
    bridge = "import {readFileSync} from 'node:fs'; import {rateCapture} from './audit/rating.js'; process.stdout.write(JSON.stringify(rateCapture(JSON.parse(readFileSync(0,'utf8')))));"
    completed = subprocess.run(  # noqa: S603 - fixed library bridge without shell
        [node, "--input-type=module", "-e", bridge],
        input=json.dumps(capture),
        text=True,
        capture_output=True,
        cwd=ROOT,
        timeout=15,
        check=False,
    )
    if completed.returncode:
        return {
            "status": "not_calculated",
            "reason": "CO2.js bridge failed; inspect dependency installation",
        }
    return cast(JSON, json.loads(completed.stdout))


async def run_audit(
    targets: list[JSON],
    observation_ms: int,
    include_technology: bool,
    output_path: Path | None = None,
) -> JSON:
    """Collect bounded states first, then enrichment in independent sessions."""
    result: JSON = {
        "schemaVersion": "0.2.0",
        "startedAt": timestamp(),
        "python": platform.python_version(),
        "protocol": {**PROTOCOL, "observationMs": observation_ms},
        "runs": [],
        "discovery": [],
        "executionStatus": "running",
    }
    sites: dict[str, JSON] = {}
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        try:
            for target in targets:
                for branch in target.get(
                    "branches", [{"name": "no_banner", "actions": []}]
                ):
                    run = await collect(browser, target, branch, observation_ms)
                    run["rating"] = rate_initial(run)
                    result["runs"].append(run)
                    save_private(output_path, result)
                    origin = urlsplit(target["url"]).netloc
                    site = sites.setdefault(
                        origin, {"url": target["url"], "links": [], "statementUrls": []}
                    )
                    site["statementUrls"].extend(target.get("statementUrls", []))
                    if run["phases"]:
                        site["links"].extend(run["phases"][0]["state"]["links"])
                    LOG.info("Collected %s", run["id"])
        finally:
            await browser.close()
    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=15,
        headers={
            "User-Agent": "WebSustainabilityAgents/0.2 (bounded disclosure discovery)"
        },
    ) as client:
        for site in sites.values():
            result["discovery"].append(
                await discover(
                    client, site["url"], site["links"], site["statementUrls"]
                )
            )
            save_private(output_path, result)
    if include_technology:
        result["technology"] = await asyncio.to_thread(
            technologies, [site["url"] for site in sites.values()]
        )
    result["finishedAt"] = timestamp()
    result["executionStatus"] = (
        "completed_with_errors"
        if any(
            run.get("collectionError") or run.get("navigationError")
            for run in result["runs"]
        )
        or result.get("technology", {}).get("error")
        else "completed"
    )
    save_private(output_path, result)
    return result


def main() -> None:
    """Run a configured audit, with explicit interaction choices and output paths."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--targets", type=Path, default=ROOT / "audit/targets.json")
    parser.add_argument(
        "--output", type=Path, default=ROOT / ".audit-work/staged-audit.json"
    )
    parser.add_argument(
        "--publish", type=Path, help="Optional sanitized evidence output"
    )
    parser.add_argument("--observation-ms", type=int, default=3000)
    parser.add_argument("--skip-technology", action="store_true")
    args = parser.parse_args()
    if args.observation_ms < 0:
        parser.error("--observation-ms must be nonnegative")
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    result = asyncio.run(
        run_audit(
            read_json(args.targets)["targets"],
            args.observation_ms,
            not args.skip_technology,
            args.output,
        )
    )
    save_private(args.output, result)
    if args.publish:
        published = sanitize(result)
        published["rawSHA256"] = hashlib.sha256(args.output.read_bytes()).hexdigest()
        published["publicationNote"] = (
            "URL query strings, fragments, and userinfo removed. Discovery excerpts are public claims, not verified emissions. Technology scans and discovery requests excluded from measured page traffic."
        )
        args.publish.parent.mkdir(parents=True, exist_ok=True)
        args.publish.write_text(json.dumps(published, indent=2, default=str) + "\n")
    LOG.info("Saved %s staged observations", len(result["runs"]))


if __name__ == "__main__":
    main()
