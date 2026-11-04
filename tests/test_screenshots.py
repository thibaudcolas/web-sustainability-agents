import copy
import hashlib
import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from audit.screenshots import collect, validate_plan


def plan(origin: str = "https://example.com") -> dict[str, Any]:
    return {
        "origin": origin,
        "captures": [
            {
                "id": "article",
                "url": origin + "/",
                "viewport": {"width": 360, "height": 640},
                "colorScheme": "light",
                "alt": "A short article headed Fixture.",
                "caption": "A separate visual illustration of the article.",
                "checkIds": ["layout"],
            }
        ],
    }


class ScreenshotPlanTests(unittest.TestCase):
    def test_rejects_scope_filename_caption_and_unbounded_capture_inputs(self):
        valid = plan()
        validate_plan(valid)
        for changed in [
            {"url": "https://elsewhere.example/"},
            {"url": "https://user:password@example.com/"},
            {"id": "../article"},
            {"alt": ""},
            {"viewport": {"width": 100000, "height": 640}},
            {"actions": [{"type": "click", "selector": "button"}]},
            {"colorScheme": "automatic"},
        ]:
            candidate = copy.deepcopy(valid)
            candidate["captures"][0].update(changed)
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                validate_plan(candidate)
        duplicated = copy.deepcopy(valid)
        duplicated["captures"] *= 2
        with self.assertRaises(ValueError):
            validate_plan(duplicated)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "https://outside.example/")
            self.end_headers()
            return
        body = b'<!doctype html><html lang="en"><title>Fixture</title><main><h1>Fixture</h1><p>A short article.</p></main></html>'
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


class ScreenshotCaptureTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_capture_provenance_failure_and_no_overwrite(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        origin = f"http://127.0.0.1:{server.server_port}"
        candidate = plan(origin)
        failed = copy.deepcopy(candidate["captures"][0])
        failed.update({"id": "missing-target", "selector": "#missing"})
        redirect = copy.deepcopy(candidate["captures"][0])
        redirect.update({"id": "outside-origin", "url": origin + "/redirect"})
        candidate["captures"].extend([failed, redirect])
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "images"
            result = await collect(candidate, output)
            self.assertEqual(result["status"], "partial")
            successful, missing, outside = result["captures"]
            self.assertEqual(successful["status"], "completed")
            image = (output / successful["file"]).read_bytes()
            self.assertTrue(image.startswith(b"\x89PNG\r\n\x1a\n"))
            self.assertEqual(
                hashlib.sha256(image).hexdigest(), successful["fileSHA256"]
            )
            self.assertEqual(successful["finalUrl"], origin + "/")
            self.assertTrue(successful["capturedAt"])
            for record in [missing, outside]:
                self.assertEqual(record["status"], "failed")
                self.assertNotIn("file", record)
                self.assertFalse((output / f"{record['id']}.png").exists())
            self.assertEqual(result, json.loads((output / "manifest.json").read_text()))
            with self.assertRaisesRegex(ValueError, "new output"):
                await collect(candidate, output)
