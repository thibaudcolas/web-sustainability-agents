import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

from audit.annual import annual_scenario, model_pages
from audit.assess import assess, grouped_outcome, validate_provenance
from audit.reviews import resolve


class AssessmentTests(unittest.TestCase):
    def setUp(self):
        self.rubric = {
            "rubricVersion": "test",
            "guidelines": [
                {"number": str(i), "expectation": "A scoped test"} for i in range(6)
            ],
        }
        self.weights = {
            "weights": dict(zip(map(str, range(6)), [3, 2, 7, 4, 9, 8], strict=True))
        }
        self.review: dict[str, Any] = {
            "site": "https://example.com",
            "evidenceIndex": {
                "evidence": {
                    "artifact": "example.json",
                    "jsonPointer": "/e",
                    "sourceSHA256": "digest",
                },
                "e": {
                    "artifact": "example.json",
                    "jsonPointer": "/e",
                    "sourceSHA256": "digest",
                },
            },
            "rows": [
                {
                    "guideline": str(i),
                    "outcome": value,
                    "evidenceIds": ["evidence"],
                    "rationale": "A substantive explanation of the evidence.",
                }
                for i, value in enumerate(
                    ["pass", "pass", "fail", "cantTell", "inapplicable", "untested"]
                )
            ],
        }

    def test_unknowns_remain_in_denominator_and_weights_are_grouped_once(self):
        result = assess(self.review, self.rubric, self.weights)
        self.assertEqual(result["value"], 50)
        self.assertEqual(result["impactWeighted"]["value"], 31.25)
        self.assertEqual(result["checkedGuidelines"], 4)
        self.review["rows"].append(copy.deepcopy(self.review["rows"][0]))
        self.assertEqual(assess(self.review, self.rubric, self.weights)["value"], 50)
        self.assertEqual(
            assess(self.review, self.rubric, self.weights)["impactWeighted"]["value"],
            31.25,
        )

    def test_unresolved_and_failed_expectations_prevent_group_pass(self):
        self.assertEqual(grouped_outcome(["pass", "untested"]), "cantTell")
        self.assertEqual(grouped_outcome(["pass", "cantTell"]), "cantTell")
        self.assertEqual(grouped_outcome(["cantTell", "fail"]), "fail")
        self.assertEqual(grouped_outcome(["pass", "inapplicable"]), "pass")
        self.assertEqual(grouped_outcome([]), "untested")

    def test_empty_score_and_zero_weight_are_not_perfect_scores(self):
        self.review["rows"] = []
        result = assess(self.review, self.rubric, self.weights)
        self.assertIsNone(result["value"])
        self.assertIsNone(result["impactWeighted"]["value"])
        self.review["rows"] = [
            {
                "guideline": "0",
                "outcome": "pass",
                "evidenceIds": ["e"],
                "rationale": "An evidenced passing scoped expectation.",
            }
        ]
        self.weights["weights"]["0"] = 0
        result = assess(self.review, self.rubric, self.weights)
        self.assertEqual(result["value"], 100)
        self.assertEqual(result["checkedGuidelines"], 1)
        self.assertIsNone(result["impactWeighted"]["value"])

    def test_missing_evidence_and_unknown_guidelines_are_rejected(self):
        self.review["rows"][0]["evidenceIds"] = []
        with self.assertRaises(ValueError):
            assess(self.review, self.rubric, self.weights)

    def test_fabricated_identifier_cannot_be_scored(self):
        self.review["rows"][0]["evidenceIds"] = ["fabricated"]
        with self.assertRaises(ValueError):
            assess(self.review, self.rubric, self.weights)

    def test_changed_rubric_and_nonexistent_pointer_are_rejected(self):
        raw = b'{"observations": []}'
        digest = hashlib.sha256(raw).hexdigest()
        reviews = {
            "rubricSHA256": hashlib.sha256(b"original").hexdigest(),
            "sourceSHA256": {"e.json": digest},
            "reviews": [
                {
                    "evidenceIndex": {
                        "x": {
                            "artifact": "e.json",
                            "jsonPointer": "/observations/0",
                            "sourceSHA256": digest,
                        }
                    }
                }
            ],
        }
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            (path / "e.json").write_bytes(raw)
            with self.assertRaisesRegex(ValueError, "different rubric"):
                validate_provenance(reviews, b"changed", path)
            with self.assertRaisesRegex(ValueError, "does not exist"):
                validate_provenance(reviews, b"original", path)
        self.review["rows"][0]["guideline"] = "outside"
        with self.assertRaises(ValueError):
            assess(self.review, self.rubric, self.weights)


class AnnualTests(unittest.TestCase):
    def setUp(self):
        self.site = "https://example.com"
        self.pages = [
            {
                "url": self.site + "/",
                "gramsPerView": 0.04,
                "accountingStatus": "complete",
            },
            {
                "url": self.site + "/article/",
                "gramsPerView": 0.12,
                "accountingStatus": "complete",
            },
        ]
        self.traffic: dict[str, Any] = {
            "origin": self.site,
            "rankBucket": 5000000,
            "traffic": {"status": "scenario", "annualPageviews": 200000},
        }

    def test_mix_and_units_with_explicit_sensitivity(self):
        result = annual_scenario(self.site, self.pages, self.traffic)
        self.assertEqual(result["value"], 16)
        self.assertAlmostEqual(result["sensitivityKgPerYear"]["lowestSampledPage"], 8)
        self.assertAlmostEqual(result["sensitivityKgPerYear"]["highestSampledPage"], 24)
        self.assertEqual(result["basis"], "scenario")

    def test_partial_measurement_still_yields_labeled_estimate_not_rating(self):
        self.pages[0]["accountingStatus"] = "partial"
        result = annual_scenario(self.site, self.pages, self.traffic)
        self.assertEqual(result["value"], 16)
        self.assertEqual(result["transferInputs"], "partial")
        self.assertNotIn("rating", result)

    def test_wrong_origin_missing_rank_and_invalid_traffic_are_unavailable(self):
        for key, value in [("origin", "https://parent.example"), ("rankBucket", None)]:
            traffic = {**self.traffic, key: value}
            self.assertIsNone(annual_scenario(self.site, self.pages, traffic)["value"])
        for invalid_count in [None, True, float("nan"), -1, 10**1000]:
            traffic = {
                **self.traffic,
                "traffic": {"status": "scenario", "annualPageviews": invalid_count},
            }
            self.assertIsNone(annual_scenario(self.site, self.pages, traffic)["value"])

    def test_duplicate_pages_do_not_silently_change_mix(self):
        with self.assertRaises(ValueError):
            annual_scenario(self.site, self.pages + self.pages[:1], self.traffic)

    def test_large_finite_values_do_not_publish_infinity(self):
        self.traffic["traffic"]["annualPageviews"] = 1e308
        self.pages = [
            {"url": self.site, "gramsPerView": 1000, "accountingStatus": "complete"}
        ]
        self.assertEqual(
            annual_scenario(self.site, self.pages, self.traffic)["value"], 1e308
        )
        self.pages[0]["gramsPerView"] = 1e308
        with self.assertRaises(ValueError):
            annual_scenario(self.site, self.pages, self.traffic)

    def test_real_branch_averaging_and_model_match_frozen_guide(self):
        staged = json.loads(
            Path("docs/initial-implementation/assets/staged-audit.json").read_text()
        )
        pages = model_pages(staged)
        self.assertEqual(len(pages["https://wagtail.org"]), 2)
        self.assertTrue(
            all(
                p["accountingStatus"] == "complete"
                for p in pages["https://guide.wagtail.org"]
            )
        )
        expected = staged["runs"][0]["rating"]["trace"]["co2"]["total"]
        self.assertEqual(
            pages["https://guide.wagtail.org"][0]["gramsPerView"], expected
        )
        self.assertTrue(
            all(len(p["branches"]) == 2 for p in pages["https://wagtail.org"])
        )


class EvidenceResolverTests(unittest.TestCase):
    def test_resource_id_is_scoped_to_its_capture(self):
        data = {
            "e.json": {
                "captures": [
                    {
                        "id": "a",
                        "url": "https://example.com/",
                        "resources": [{"id": "r"}],
                    },
                    {
                        "id": "b",
                        "url": "https://example.com/",
                        "resources": [{"id": "r"}],
                    },
                ]
            }
        }
        self.assertEqual(
            resolve("e.json#a/resources/r", "https://example.com", data)["jsonPointer"],
            "/captures/0/resources/0",
        )
        with self.assertRaises(ValueError):
            resolve("e.json#r", "https://example.com", data)
        with self.assertRaises(ValueError):
            resolve("e.json#missing", "https://example.com", data)
        with self.assertRaises(ValueError):
            resolve("e.json#a", "https://other.example", data)

    def test_policy_discovery_respects_audited_origin(self):
        data = {
            "e.json": {
                "discovery": [
                    {
                        "site": "https://parent.example",
                        "documents": [{"url": "https://parent.example/policy/"}],
                    }
                ]
            }
        }
        with self.assertRaises(ValueError):
            resolve(
                "e.json#discovery:/documents/https://parent.example/policy/",
                "https://child.example",
                data,
            )
