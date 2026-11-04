import json
import unittest
from pathlib import Path
from typing import Any

from audit.coverage import register


class CoverageTests(unittest.TestCase):
    def site(self) -> dict[str, Any]:
        return {
            "site": "https://guide.wagtail.org",
            "pages": [],
            "files": [],
            "advertisedURLCount": 100,
            "selection": {"departure": "development sample"},
            "inventoryMeaning": "sitemap only",
        }

    def test_evidence_register_never_invents_passes_or_scores(self):
        guidelines = json.loads(
            Path(
                "docs/initial-implementation/assets/wsg-review-coverage.json"
            ).read_text()
        )["guidelines"]
        result = register(self.site(), guidelines, "digest")
        self.assertEqual(len(result["guidelines"]), 71)
        self.assertIsNone(result["counts"]["passed"])
        self.assertIsNone(result["counts"]["failed"])
        self.assertEqual(
            result["counts"]["partialEvidence"] + result["counts"]["notAssessed"], 71
        )
        self.assertEqual(
            {row["conformance"] for row in result["guidelines"]}, {"not_determined"}
        )

    def test_redirect_to_another_origin_does_not_establish_this_sites_policy(self):
        guidelines = json.loads(
            Path(
                "docs/initial-implementation/assets/wsg-review-coverage.json"
            ).read_text()
        )["guidelines"]
        site = self.site()
        site["pages"] = [
            {
                "id": "policy",
                "url": "https://guide.wagtail.org/privacy/",
                "finalUrl": "https://other.example/privacy/",
                "status": 200,
                "initial": {"title": "Privacy"},
                "selectionReason": "purposeful",
            }
        ]
        result = register(site, guidelines, "digest")
        policy = next(row for row in result["guidelines"] if row["number"] == "5.18")
        self.assertEqual(policy["status"], "not_assessed")

    def test_failed_recovery_and_home_redirect_do_not_establish_evidence(self):
        guidelines = json.loads(
            Path(
                "docs/initial-implementation/assets/wsg-review-coverage.json"
            ).read_text()
        )["guidelines"]
        site = self.site()
        site["pages"] = [
            {
                "id": "missing",
                "url": site["site"] + "/missing/",
                "selectionReason": "error_recovery",
                "error": "TimeoutError",
            },
            {
                "id": "policy",
                "url": site["site"] + "/privacy/",
                "finalUrl": site["site"] + "/",
                "status": 200,
                "initial": {"title": "Home"},
                "selectionReason": "purposeful",
            },
        ]
        result = register(site, guidelines, "digest")
        for row in result["guidelines"]:
            if row["number"] in {"4.4", "5.18"}:
                self.assertEqual(row["status"], "not_assessed")
