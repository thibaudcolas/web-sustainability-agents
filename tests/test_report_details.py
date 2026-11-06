import copy
import hashlib
import json
import unittest
from pathlib import Path
from typing import Any, cast

from audit.render_review import interaction_label, render
from audit.report_details import (
    area_results,
    energy_rows,
    first_visits,
    source_excerpt,
    validate_presentation,
)


class ReportDetailsTests(unittest.TestCase):
    def test_cookie_labels_preserve_failed_and_unverified_actions(self):
        failed: dict[str, Any] = {
            "branch": "reject_analytics",
            "actions": [{"status": "failed"}],
            "phases": [{"phase": "after_consent", "interactionStatus": "failed"}],
        }
        self.assertEqual(interaction_label(failed), "Reject analytics (action failed)")
        failed["actions"].insert(0, {"status": "completed"})
        self.assertIn("action failed", interaction_label(failed))
        self.assertEqual(
            interaction_label({"branch": "accept_analytics"}),
            "Accept analytics (action unverified)",
        )
        self.assertEqual(
            interaction_label({"branch": "initial_no_banner_observed", "actions": []}),
            "",
        )
        self.assertEqual(
            interaction_label(
                {"branch": "acknowledge_notice", "actions": [{"status": "completed"}]}
            ),
            "Acknowledge cookie notice",
        )

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
        self.assertNotIn(self.supplement["reason"], output)
        self.assertNotIn("new contextual skill", output)
        self.assertNotIn("subsequent priority or wording changes", output)
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
        headline = output.split("## Page measurements")[1].split("## Priorities")[0]
        self.assertNotIn("Ranges show", headline)
        self.assertNotIn("–", headline)
        self.assertNotIn("1,000 bytes", headline)
        self.assertIn(">partial</a>", headline)

    def test_combined_table_keeps_cookie_visits_carbon_and_energy_distinct(self):
        import re

        for name in ("guide", "wagtail"):
            session = Path(f"docs/reports/assets/fresh-{name}")
            energy = json.loads(
                Path(
                    f"docs/reports/assets/report-refinement/{name}/energy.json"
                ).read_text()
            )
            editorial = json.loads((session / "editorial.json").read_text())
            output = render(session, "artifacts", editorial, energy=energy)
            measurements = output.split("## Page measurements")[1].split(
                "## Priorities"
            )[0]
            rows = re.findall(r'<tr><th scope="row">(.*?)</tr>', measurements)
            self.assertEqual(len(rows), 6 if name == "guide" else 7)
            self.assertEqual(measurements.count("<table>"), 1)
            self.assertNotIn("GreenFrame", measurements)
            self.assertNotIn("### Browser energy", output)
            self.assertNotIn("## After", output)
            # The homepage and the following page have different sampling coverage.
            self.assertIn("12.00 mWh" if name == "guide" else "12.08 mWh", rows[0])
            self.assertIn("Not sampled", rows[1])
            if name == "guide":
                self.assertIn("59.1 kB", rows[0])
                self.assertIn("0.01 gCO₂e", rows[0])
                self.assertIn("<td>A+</td>", rows[0])
            else:
                self.assertIn("<td>944.4 kB", rows[0])
                self.assertIn("Reject optional cookies: 944.4 kB", rows[0])
                self.assertIn("Accept cookies: 945.6 kB", rows[0])
                self.assertIn("Reject optional cookies: 1.108 MB", rows[0])
                self.assertIn("Accept cookies: 1.109 MB", rows[0])
                self.assertEqual(rows[0].count(">Withheld</td>"), 2)
                self.assertEqual(rows[0].count(">partial</a>"), 5)

    def test_area_links_group_each_check_and_tooltips_use_pinned_descriptions(self):
        import html

        reference = json.loads(
            Path(
                ".agents/skills/sustainability-guideline-review/references/wsg.json"
            ).read_text()
        )
        references = {r["id"]: r for r in reference["guidelines"]}
        output = render(self.session, "artifacts", self.editorial)
        details = output.split("## Detailed findings")[1].split("## Methodology")[0]
        for section in ("2", "3", "4", "5"):
            self.assertIn(f'href="#findings-{section}"', output)
            area = details.split(f"{{#findings-{section}}}")[1].split("### ")[0]
            expected = [
                r
                for r in self.packet["checks"]
                if r["guideline"].startswith(section + ".")
            ]
            self.assertEqual(area.count('<h4 id="evidence-'), len(expected))
            for row in expected:
                self.assertIn(f'id="evidence-{row["id"]}"', area)
                summary = references[row["guideline"]]["summary"]
                self.assertIn(f'title="{html.escape(summary, quote=True)}"', area)
                self.assertIn(f"_{summary}_", area)
