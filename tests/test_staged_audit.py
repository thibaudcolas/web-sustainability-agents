import asyncio
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import cast
from unittest.mock import AsyncMock, patch

import httpx
from playwright.async_api import Error as BrowserError
from playwright.async_api import Page, async_playwright

from audit.run import (
    Document,
    NetworkLedger,
    collect,
    disclosure_urls,
    discover,
    fetch_document,
    perform_action,
    sanitize,
    save_private,
    technology_hints,
)


class LedgerTests(unittest.TestCase):
    def request(self, ledger: NetworkLedger, request_id: str = "1") -> None:
        ledger.requested(
            {
                "requestId": request_id,
                "request": {"url": "https://site.test/asset"},
                "type": "Script",
            }
        )

    def test_failed_resource_is_separate_from_byte_accounting(self):
        ledger = NetworkLedger()
        self.request(ledger)
        ledger.response({"requestId": "1", "response": {"status": 404, "headers": {}}})
        ledger.finished({"requestId": "1", "encodedDataLength": 100})
        result = ledger.snapshot()
        self.assertEqual(result["receivedBytes"], 100)
        self.assertEqual(result["accountingStatus"], "complete_within_protocol")
        self.assertEqual(result["resourceErrors"][0]["status"], 404)

    def test_partial_bytes_are_replaced_not_double_counted(self):
        ledger = NetworkLedger()
        self.request(ledger)
        ledger.data({"requestId": "1", "encodedDataLength": 10})
        initial = ledger.snapshot()
        self.assertEqual(initial["accountingStatus"], "partial")
        ledger.phase = "after_consent"
        ledger.finished({"requestId": "1", "encodedDataLength": 15})
        result = ledger.snapshot(initial["receivedBytes"])
        self.assertEqual(result["receivedBytes"], 15)
        self.assertEqual(result["additionalBytes"], 5)
        self.assertEqual(initial["resources"][0]["receivedBytes"], None)
        self.assertEqual(result["resources"][0]["requestedInPhase"], "initial")

    def test_aborted_request_does_not_become_measured_zero(self):
        ledger = NetworkLedger()
        self.request(ledger)
        ledger.failed({"requestId": "1", "errorText": "net::ERR_ABORTED"})
        result = ledger.snapshot()
        self.assertEqual(result["receivedBytes"], 0)
        self.assertEqual(result["unresolvedRequestIds"], ["1"])
        self.assertEqual(result["accountingStatus"], "partial")

    def test_redirect_cache_and_sticky_frame_accounting(self):
        ledger = NetworkLedger()
        self.request(ledger)
        ledger.requested(
            {
                "requestId": "1",
                "request": {"url": "https://site.test/final"},
                "type": "Script",
                "redirectResponse": {"status": 302, "encodedDataLength": 50},
            }
        )
        ledger.cached({"requestId": "1"})
        ledger.finished({"requestId": "1", "encodedDataLength": 0})
        self.assertEqual(ledger.snapshot()["receivedBytes"], 50)
        ledger.child_frame(None)
        result = ledger.snapshot()
        self.assertEqual(result["accountingStatus"], "partial")
        ledger.websocket({})
        self.assertEqual(len(ledger.snapshot()["coverageGaps"]), 2)

    def test_publication_scrubs_keys_and_embedded_urls(self):
        secret_url = "https://person:password@site.test/?token=secret#fragment"
        result = json.dumps(
            sanitize({secret_url: {"error": f"Navigation failed at {secret_url}"}})
        )
        for secret in ["person", "password", "secret", "fragment"]:
            self.assertNotIn(secret, result)

    def test_private_checkpoint_survives_later_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "result.json"
            save_private(
                path, {"runs": [{"id": "completed"}], "executionStatus": "running"}
            )
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(json.loads(path.read_text())["runs"][0]["id"], "completed")

    def test_technology_hints_do_not_infer_green_hosting_or_working_pwa(self):
        hints = technology_hints(
            {
                "https://site.test": {
                    "Wagtail": {},
                    "Cloudflare": {},
                    "PWA": {},
                    "Plausible": {},
                }
            }
        )
        self.assertEqual(len(hints["https://site.test"]), 4)
        self.assertEqual(
            technology_hints({"https://unknown.test": {}}), {"https://unknown.test": []}
        )


class DiscoveryTests(unittest.IsolatedAsyncioTestCase):
    async def test_invalid_root_falls_back_to_well_known_toml_and_reads_disclosure(
        self,
    ):
        requests = []

        def handler(request):
            requests.append(request.url.path)
            if request.url.path == "/.well-known/carbon.txt":
                return httpx.Response(
                    200,
                    text='version = "0.6"\n[[org.disclosures]]\ndoc_type = "sustainability-page"\nurl = "https://site.test/disclosure"',
                )
            if request.url.path == "/disclosure":
                return httpx.Response(
                    200,
                    headers={"content-type": "text/html"},
                    text="<nav>Repeated navigation</nav><main>Our footprint is a modeled estimate.</main>",
                )
            return httpx.Response(200, text="<html>Not a carbon file</html>")

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            with patch(
                "audit.run.dns.asyncresolver.resolve", new=AsyncMock(return_value=[])
            ):
                result = await discover(client, "https://site.test/", [])
        self.assertEqual(result["carbonStatus"], "disclosures_found")
        self.assertEqual(result["carbonAttempts"][0]["parseStatus"], "not_toml")
        self.assertFalse(result["carbonAttempts"][1]["schemaValidated"])
        self.assertEqual(result["carbonAttempts"][1]["discoveredVia"], "well-known")
        self.assertEqual(result["carbonPresence"], "present")
        self.assertEqual(
            result["documents"][0]["textExcerpt"],
            "Our footprint is a modeled estimate.",
        )
        self.assertIn("/disclosure", requests)

    async def test_present_file_without_usable_disclosures_is_not_absent(self):
        def handler(request):
            if request.url.path == "/carbon.txt":
                return httpx.Response(
                    200, text='version = "0.6"\n[org]\ndisclosures = []'
                )
            return httpx.Response(404)

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            with patch(
                "audit.run.dns.asyncresolver.resolve", new=AsyncMock(return_value=[])
            ):
                result = await discover(client, "https://site.test/", [])
        self.assertEqual(result["carbonPresence"], "present")
        self.assertEqual(result["carbonStatus"], "not_found_within_discovery_scope")
        self.assertTrue(result["documents"])

    async def test_missing_carbon_uses_supplied_statement_and_retains_unknown_scope(
        self,
    ):
        def handler(request):
            if request.url.path == "/statement":
                return httpx.Response(
                    200,
                    headers={"content-type": "text/html"},
                    text="<main>Project statement</main>",
                )
            return httpx.Response(404)

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            with patch(
                "audit.run.dns.asyncresolver.resolve", new=AsyncMock(return_value=[])
            ):
                result = await discover(
                    client, "https://site.test/", [], ["https://parent.test/statement"]
                )
        self.assertEqual(result["carbonStatus"], "not_found_within_discovery_scope")
        self.assertEqual(result["documents"][0]["status"], 200)
        self.assertFalse(result["documents"][0]["claimsVerified"])

    async def test_malformed_urls_do_not_abort_discovery(self):
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(lambda _: httpx.Response(200))
        ) as client:
            for url in [
                "https://[broken",
                "https://site.test:bad/carbon.txt",
                "file:///etc/passwd",
            ]:
                record, _ = await fetch_document(client, url)
                self.assertIn("error", record)
        self.assertEqual(
            disclosure_urls({"org": {"disclosures": [{"url": "https://[broken"}]}}), []
        )

    async def test_slow_stream_has_overall_deadline(self):
        class SlowStream(httpx.AsyncByteStream):
            async def __aiter__(self):
                while True:
                    await asyncio.sleep(0.005)
                    yield b"a"

        async with httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda _: httpx.Response(200, stream=SlowStream())
            )
        ) as client:
            record, _ = await fetch_document(
                client, "https://site.test/", total_timeout=0.03
            )
            self.assertEqual(record["error"], "TimeoutError")

    async def test_action_lookup_error_is_recorded(self):
        class MissingFrame:
            def locator(self, _):
                return self

            async def count(self):
                raise BrowserError("Detached frame")

        result = await perform_action(
            cast(Page, MissingFrame()), {"type": "click", "selector": "button"}
        )
        self.assertEqual(result["status"], "failed")


class BrowserStageTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_interaction_adds_bytes_without_rewriting_initial_measurement(
        self,
    ):
        # Reuse the existing, accessibility-reviewed fixture; the active collector is Python.
        node = shutil.which("node")
        assert node is not None
        process = subprocess.Popen(  # noqa: S603 - fixed repository fixture without shell
            [
                node,
                "--input-type=module",
                "-e",
                "import {startFixture} from './audit/fixture.js'; const fixture = await startFixture(); console.log(fixture.url);",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            assert process.stdout is not None
            url = process.stdout.readline().strip()
            self.assertTrue(url.startswith("http://127.0.0.1:"))
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch()
                try:
                    result = await collect(
                        browser,
                        {"id": "fixture", "url": url},
                        {
                            "name": "activate",
                            "actions": [{"type": "click", "selector": "#show"}],
                        },
                        observation_ms=150,
                    )
                finally:
                    await browser.close()
            initial, after_action, after_scroll = result["phases"]
            self.assertFalse(
                any(
                    resource["url"].endswith("/illustration.svg")
                    for resource in initial["resources"]
                )
            )
            illustration = next(
                resource
                for resource in after_action["resources"]
                if resource["url"].endswith("/illustration.svg")
            )
            self.assertGreater(illustration["receivedBytes"], 0)
            self.assertGreater(after_action["receivedBytes"], initial["receivedBytes"])
            self.assertEqual(after_action["interactionStatus"], "completed")
            self.assertTrue(after_scroll["reachedBottom"])
            self.assertEqual(
                sum(phase["additionalBytes"] for phase in result["phases"]),
                after_scroll["receivedBytes"],
            )
        finally:
            process.terminate()
            process.communicate(timeout=5)


class TextTests(unittest.TestCase):
    def test_main_text_keeps_nested_article_once(self):
        parser = Document()
        parser.feed(
            "<nav>Navigation</nav><main>Start<article>Body</article>End</main><footer>Footer</footer>"
        )
        self.assertEqual(parser.main_text, ["Start", "Body", "End"])
