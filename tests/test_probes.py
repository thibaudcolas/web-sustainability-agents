import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from playwright.async_api import async_playwright

from audit.probes import CHECKS, collect, inspect_journey, validate_plan

HTML = b"""<!doctype html><html lang="en"><meta charset="utf-8"><title>Probe fixture</title>
<style>main{width:700px}.moving{animation:spin 1s infinite linear}@keyframes spin{to{transform:rotate(360deg)}}
@media(prefers-reduced-motion:reduce){.moving{animation:none}}@media print{nav{display:none}}</style>
<nav><a href="/">Home</a></nav><main><h1>A useful task</h1><p>Read this accessible explanation.</p>
<label for="query">Search</label><input id="query"><button type="button" id="search">Find</button>
<div id="result" hidden>Matching result</div><span class="moving">Motion</span>
<a href="/report.pdf">Download report (PDF, 10 KB)</a><input type="checkbox" checked aria-label="Choice">
<video controls muted></video><div id="js-status">No JavaScript</div></main><script src="/app.js"></script></html>"""
SCRIPT = b"""function futureFeature(){return 42;}
document.querySelector('#js-status').textContent='JavaScript ran';
document.querySelector('#search').onclick=()=>{document.querySelector('#result').hidden=false;};"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/app.js":
            body, content_type = SCRIPT, "text/javascript"
        else:
            body, content_type = HTML, "text/html"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        pass


class PlanTests(unittest.TestCase):
    def test_rejects_external_pages_duplicate_ids_and_unknown_actions(self):
        plan: dict[str, Any] = {
            "origin": "https://example.com",
            "pages": [{"id": "home", "url": "https://other.example/"}],
        }
        with self.assertRaises(ValueError):
            validate_plan(plan)
        plan["pages"][0]["url"] = "https://example.com/"
        plan["pages"] *= 2
        with self.assertRaises(ValueError):
            validate_plan(plan)
        plan["pages"] = plan["pages"][:1]
        plan["journeys"] = [
            {
                "id": "bad",
                "url": "https://example.com/",
                "actions": [{"type": "execute", "selector": "body"}],
            }
        ]
        with self.assertRaises(ValueError):
            validate_plan(plan)

    def test_every_check_is_scoped_and_links_the_current_guideline(self):
        self.assertGreaterEqual(len(CHECKS), 10)
        self.assertEqual(len({check["id"] for check in CHECKS}), len(CHECKS))
        for check in CHECKS:
            self.assertFalse(check["fullGuidelineCoverage"])
            self.assertTrue(
                check["url"].startswith(
                    "https://www.w3.org/TR/web-sustainability-guidelines/#"
                )
            )
            self.assertIn("expectation", check)


class BrowserProbeTests(unittest.IsolatedAsyncioTestCase):
    server: ThreadingHTTPServer
    thread: threading.Thread
    origin: str

    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.origin = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    async def test_real_observations_and_explicit_journey(self):
        plan = {
            "origin": self.origin,
            "purpose": "Fixture behavior",
            "pages": [
                {"id": "home", "url": self.origin + "/", "task": "Read and search"}
            ],
            "journeys": [
                {
                    "id": "search",
                    "url": self.origin + "/",
                    "task": "Search",
                    "actions": [
                        {"type": "fill", "selector": "#query", "value": "bread"},
                        {"type": "click", "selector": "#search"},
                    ],
                    "successSelector": "#result",
                }
            ],
        }
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "probes.json"
            result = await collect(plan, output)
            self.assertEqual(
                result["executionStatus"], "completed", result["pages"][0]["errors"]
            )
            self.assertEqual(output.stat().st_mode & 0o777, 0o600)
            self.assertEqual(json.loads(output.read_text())["site"], self.origin)
        page = result["pages"][0]
        states = {state["name"]: state["observations"] for state in page["states"]}
        self.assertFalse(states["desktop"]["horizontalOverflow"])
        self.assertTrue(states["narrow"]["horizontalOverflow"])
        self.assertEqual(states["desktop"]["print"]["visibleNavigation"], 1)
        self.assertEqual(states["print"]["print"]["visibleNavigation"], 0)
        self.assertTrue(states["reduced_motion"]["preferences"]["reducedMotion"])
        self.assertEqual(states["reduced_motion"]["animations"]["total"], 0)
        self.assertIn("JavaScript ran", states["desktop"]["text"]["value"])
        self.assertIn("No JavaScript", states["no_javascript"]["text"]["value"])
        self.assertEqual(states["desktop"]["downloads"]["total"], 1)
        controls = states["desktop"]["controls"]["items"]
        self.assertEqual(
            next(item for item in controls if item["id"] == "query")["labels"],
            ["Search"],
        )
        scripts = page["codeCoverage"]["javascript"]
        application = next(
            script for script in scripts if script["url"].endswith("/app.js")
        )
        self.assertTrue(
            any(
                entry["count"] == 0
                for function in application["functions"]
                for entry in function["ranges"]
            )
        )
        journey = result["journeys"][0]
        self.assertEqual(
            [item["status"] for item in journey["actions"]], ["completed", "completed"]
        )
        self.assertTrue(journey["successSelectorVisible"])
        self.assertNotIn("Matching result", journey["before"]["text"]["value"])
        self.assertIn("Matching result", journey["after"]["text"]["value"])

    async def test_failed_action_does_not_claim_success_or_run_remaining_actions(self):
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch()
            try:
                result = await inspect_journey(
                    browser,
                    {
                        "id": "broken",
                        "url": self.origin + "/",
                        "actions": [
                            {"type": "click", "selector": "#missing"},
                            {"type": "click", "selector": "#search"},
                        ],
                        "successSelector": "#result",
                    },
                )
            finally:
                await browser.close()
        self.assertEqual(result["status"], "completed_with_errors")
        self.assertEqual(len(result["actions"]), 1)
        self.assertEqual(result["actions"][0]["status"], "failed")
        self.assertFalse(result["successSelectorVisible"])


if __name__ == "__main__":
    unittest.main()
