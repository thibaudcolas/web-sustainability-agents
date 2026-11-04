import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from defusedxml.common import DefusedXmlException

from audit.scope import inspect_page, inventory, parse_sitemap, public_copy, sample_urls


class ScopeTests(unittest.TestCase):
    def test_namespaced_sitemap_and_index(self):
        kind, urls = parse_sitemap(
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://example.com/a/</loc></url></urlset>'
        )
        self.assertEqual((kind, urls), ("urlset", ["https://example.com/a/"]))
        self.assertEqual(
            parse_sitemap(
                "<sitemapindex><sitemap><loc>https://example.com/sitemap.xml</loc></sitemap></sitemapindex>"
            )[0],
            "sitemapindex",
        )

    def test_entities_and_html_fallback_are_rejected(self):
        with self.assertRaises(DefusedXmlException):
            parse_sitemap(
                '<!DOCTYPE urlset [<!ENTITY file SYSTEM "file:///etc/passwd">]><urlset><url><loc>&file;</loc></url></urlset>'
            )
        with self.assertRaises(ValueError):
            parse_sitemap("<html><body>Not a sitemap</body></html>")

    def test_nested_image_locations_are_not_page_urls(self):
        _, urls = parse_sitemap(
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">'
            "<url><loc>https://example.com/page/</loc><image:image>"
            "<image:loc>https://example.com/image.png</image:loc>"
            "</image:image></url></urlset>"
        )
        self.assertEqual(urls, ["https://example.com/page/"])

    def test_sampling_is_order_independent_unique_and_bounded(self):
        urls = [f"https://example.com/{i}/" for i in range(20)]
        picked = sample_urls(urls + urls, "seed", 2)
        self.assertEqual(picked, sample_urls(list(reversed(urls)), "seed", 2))
        self.assertEqual(len(set(picked)), 2)
        self.assertTrue(set(picked) <= set(urls))

    def test_publication_removes_url_identifiers_in_keys_and_text(self):
        value = {
            "https://name:pass@example.com/?token=secret": "See https://example.com/path?q=secret#part"
        }
        self.assertEqual(
            public_copy(value), {"https://example.com/": "See https://example.com/path"}
        )


class ScopeFailureTests(unittest.IsolatedAsyncioTestCase):
    async def test_malformed_sitemap_pointer_is_recorded_without_aborting(self):
        async def fetched(client, url):
            if url.endswith("/robots.txt"):
                return {
                    "status": 200,
                    "contentType": "text/plain",
                }, "Sitemap: https://[invalid"
            if url.endswith("/sitemap.xml"):
                return {"status": 200, "contentType": "application/xml"}, "<urlset/>"
            return {"status": 404}, ""

        with patch("audit.scope.fetch", side_effect=fetched):
            result = await inventory(MagicMock(), "https://guide.wagtail.org")
        self.assertFalse(result["inventoryComplete"])
        self.assertEqual(
            result["sitemaps"][-1]["status"], "skipped_invalid_or_external_origin"
        )

    async def test_browser_timeout_retains_response_and_closes_context(self):
        browser = MagicMock(version="test")
        context = AsyncMock()
        page = AsyncMock()
        page.url = "https://guide.wagtail.org/en/"
        page.goto.return_value = MagicMock(status=200)
        page.evaluate.side_effect = TimeoutError
        context.new_page.return_value = page
        browser.new_context = AsyncMock(return_value=context)
        result = await inspect_page(browser, page.url, "purposeful")
        self.assertEqual(result["status"], 200)
        self.assertEqual(result["error"], "TimeoutError")
        self.assertNotIn("initial", result)
        context.close.assert_awaited_once()
