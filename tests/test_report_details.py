import copy
import hashlib
import json
import unittest
from pathlib import Path
from typing import Any, cast

from audit.render_review import render
from audit.report_details import (
    area_results,
    energy_rows,
    first_visits,
    source_excerpt,
    validate_presentation,
)


class ReportDetailsTests(unittest.TestCase):
    def setUp(self):
        self.session = Path("docs/reports/assets/fresh-guide")
        self.review = json.loads((self.session / "review.json").read_text())
        self.editorial = json.loads((self.session / "editorial.json").read_text())
        self.packet = json.loads((self.session / "packet.json").read_text())
        self.supplement = json.loads(
            Path(
                "docs/reports/assets/report-refinement/guide/presentation.json"
            ).read_text()
        )
        self.sha = hashlib.sha256(
            (self.session / "review.json").read_bytes()
        ).hexdigest()

    def test_area_denominators_reconcile_with_score(self):
        score = json.loads((self.session / "scores.json").read_text())["scores"][0]
        areas = area_results(score["guidelines"])
        self.assertEqual(sum(a["checked"] for a in areas), score["checkedGuidelines"])
        self.assertEqual(
            sum(a["counts"]["pass"] for a in areas), score["counts"]["pass"]
        )
        self.assertEqual(sum(a["total"] for a in areas), 71)
        self.assertIsNone(
            area_results([{"number": "2.1", "outcome": "untested"}])[0]["percent"]
        )
        self.assertEqual(
            area_results([{"number": "2.1", "outcome": "cantTell"}])[0]["percent"], 0
        )

    def test_priority_revision_is_explicit_and_bound(self):
        validate_presentation(self.supplement, self.review, self.sha)
        changed = copy.deepcopy(self.supplement)
        changed["reviewSHA256"] = "wrong"
        with self.assertRaises(ValueError):
            validate_presentation(changed, self.review, self.sha)
        output = render(
            self.session, "artifacts", self.editorial, presentation=self.supplement
        )
        self.assertIn("### 4. Check whether Renovate updates run CI twice", output)
        section = output.split("### 4.")[1].split("## After")[0]
        self.assertIn("**Low priority**", section)
        self.assertIn("```yaml\nname: CI", section)
        self.assertIn("/blob/main/.github/workflows/ci.yml#L1-L8", section)
        self.assertIn("/blob/31a4547eb1f6de55baea84269723313784f6b544/", section)

    def test_source_excerpt_rejects_mismatched_revision_or_range(self):
        spec = self.supplement["sourceExcerpts"]["source-automation"]
        source_excerpt(self.session, self.packet, spec)
        updates: list[dict[str, Any]] = [
            {"checkedOutRevision": "bad"},
            {"endLine": 9999},
            {"repositoryUrl": "https://evil.example/repo"},
        ]
        for update in updates:
            with self.assertRaises(ValueError):
                source_excerpt(self.session, self.packet, {**spec, **update})

    def test_missing_energy_is_not_zero_and_wrong_origin_is_rejected(self):
        data: dict[str, Any] = {
            "schemaVersion": "greenframe-energy-v2",
            "origin": "https://example.com",
            "pages": [
                {"url": "https://example.com/", "phase": "initial", "status": "failed"}
            ],
        }
        self.assertEqual(energy_rows(data, "https://example.com")[0][1], "Unavailable")
        with self.assertRaises(ValueError):
            energy_rows(data, "https://other.example")
        page = cast(dict[str, Any], data["pages"][0])
        page.update(status="completed", samples=2, sampleMetrics=[{}, {}])
        with self.assertRaises(ValueError):
            energy_rows(data, "https://example.com")

    def test_published_energy_medians_match_samples_and_reject_tampering(self):
        data = json.loads(
            Path("docs/reports/assets/report-refinement/guide/energy.json").read_text()
        )
        rows = energy_rows(data, "https://guide.wagtail.org")
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0][1], "12.00 mWh")
        data["pages"][0]["clientDeviceSummaryWh"]["median"] *= 2
        with self.assertRaisesRegex(ValueError, "median does not match"):
            energy_rows(data, "https://guide.wagtail.org")

    def test_first_visit_keeps_incomplete_status_and_withheld_rating(self):
        runs = [
            {
                "url": "https://example.com/",
                "size": 100,
                "complete": False,
                "rating": None,
            },
            {
                "url": "https://example.com/other",
                "size": 80,
                "complete": True,
                "rating": "A",
            },
            {
                "url": "https://example.com/",
                "size": 50,
                "complete": True,
                "rating": "A+",
            },
        ]
        selected = first_visits(runs)
        self.assertEqual(len(selected), 2)
        self.assertEqual(selected[0]["size"], 100)
        self.assertFalse(selected[0]["complete"])
        self.assertIsNone(selected[0]["rating"])
        self.assertEqual(selected[1], runs[1])

    def test_headline_uses_first_recorded_initial_visit(self):
        session = Path("docs/reports/assets/fresh-wagtail")
        editorial = json.loads((session / "editorial.json").read_text())
        output = render(session, "artifacts", editorial)
        headline = output.split("## Page measurements")[1].split("### Browser energy")[
            0
        ]
        self.assertNotIn("Ranges show", headline)
        self.assertNotIn("–", headline)
        self.assertNotIn("1,000 bytes", headline)
        self.assertIn("Some data could not be measured", headline)
