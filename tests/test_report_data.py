import copy
import json
import unittest
from pathlib import Path

from audit.report import (
    display_bytes,
    enrich_assessment,
    enrich_reports,
    export_reports,
    report_stem,
)


class ReportDataTests(unittest.TestCase):
    def test_failed_documents_cannot_be_charted_as_zero_or_normal_response_bytes(self):
        original = json.loads(
            Path("docs/initial-implementation/assets/staged-audit.json").read_text()
        )
        for state in ("navigation", "http"):
            evidence = copy.deepcopy(original)
            evidence["runs"] = evidence["runs"][:1]
            run = evidence["runs"][0]
            run["documentStatus"] = None if state == "navigation" else 429
            run["navigationError"] = (
                "net::ERR_FAILED" if state == "navigation" else None
            )
            run["rating"] = {
                "status": "calculated",
                "trace": {"co2": {"total": 0, "rating": "A+"}},
            }
            for phase in run["phases"]:
                phase["accountingStatus"] = "complete_within_protocol"
                if state == "navigation":
                    phase["receivedBytes"] = 0
                    phase["additionalBytes"] = 0
            report = next(iter(export_reports(evidence, "original-evidence").values()))
            self.assertTrue(all(row["value"] is None for row in report["observations"]))
            self.assertEqual(
                {row["status"] for row in report["observations"]}, {"unavailable"}
            )
            self.assertEqual(report["headline"][0]["display"], "Unavailable")
            self.assertIsNone(report["headline"][0]["receivedBytes"])
            self.assertEqual(report["ratings"][0]["rating"]["status"], "unavailable")
            self.assertNotIn("trace", report["ratings"][0]["rating"])
            self.assertEqual(report["sourceSHA256"], "original-evidence")

    def test_legacy_missing_navigation_status_is_explicit_without_changing_values(self):
        evidence = json.loads(
            Path("docs/initial-implementation/assets/staged-audit.json").read_text()
        )
        evidence["runs"] = evidence["runs"][:1]
        run = evidence["runs"][0]
        run.pop("documentStatus", None)
        run.pop("navigationError", None)
        report = next(iter(export_reports(evidence, "source").values()))
        self.assertEqual(report["headline"][0]["navigationStatus"], "unrecorded")
        self.assertEqual(
            report["headline"][0]["receivedBytes"], run["phases"][0]["receivedBytes"]
        )
        self.assertEqual(report["ratings"][0]["rating"], run["rating"])

    def test_scores_and_annual_scenarios_do_not_change_page_ratings(self):
        assets = Path("docs/initial-implementation/assets")
        reports = export_reports(
            json.loads((assets / "staged-audit.json").read_text()), "staged"
        )
        original = json.dumps(
            {site: report["ratings"] for site, report in reports.items()},
            sort_keys=True,
        )
        scores = json.loads((assets / "scored-audits.json").read_text())
        annual = json.loads((assets / "annual-footprints.json").read_text())
        enrich_assessment(reports, scores, annual, "scores", "annual")
        self.assertEqual(
            original,
            json.dumps(
                {site: report["ratings"] for site, report in reports.items()},
                sort_keys=True,
            ),
        )
        for site, report in reports.items():
            score = next(s for s in scores["scores"] if s["site"] == site)
            self.assertEqual(report["overallScore"]["value"], score["value"])
            rows = [
                r
                for r in report["observations"]
                if r["metric"] == "annual_browsing_footprint"
            ]
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["basis"], "scenario")
            self.assertEqual(rows[0]["unit"], "kgCO2e/year")
            self.assertEqual(rows[0]["sourceSHA256"], "annual")
            self.assertEqual(report["annualFootprint"]["site"], site)
        self.assertEqual(
            reports["https://wagtail.org"]["annualFootprint"]["transferInputs"],
            "partial",
        )

    def test_origins_and_phase_totals_remain_separate(self):
        evidence = json.loads(
            Path("docs/initial-implementation/assets/staged-audit.json").read_text()
        )
        reports = export_reports(evidence, "source-digest")
        self.assertEqual(
            set(reports), {"https://guide.wagtail.org", "https://wagtail.org"}
        )
        for origin, report in reports.items():
            self.assertIsNone(report["overallScore"]["value"])
            for row in report["observations"]:
                self.assertEqual(row["site"], origin)
                self.assertTrue(row["pageUrl"].startswith(origin + "/"))
            for headline in report["headline"]:
                self.assertEqual(headline["phase"], "initial")
            for run in evidence["runs"]:
                if not run["url"].startswith(origin + "/"):
                    continue
                for phase in run["phases"]:
                    rows = [
                        r
                        for r in report["observations"]
                        if r["runId"] == run["id"] and r["phase"] == phase["phase"]
                    ]
                    self.assertEqual(
                        sum(
                            r["value"] for r in rows if r["metric"] == "resource_bytes"
                        ),
                        phase["receivedBytes"],
                    )
                    self.assertEqual(
                        {r["status"] for r in rows}, {phase["accountingStatus"]}
                    )

    def test_decimal_display_does_not_change_base_units(self):
        self.assertEqual(display_bytes(58992), "59.0 kB")
        self.assertEqual(display_bytes(1107665), "1.11 MB")
        self.assertEqual(display_bytes(0), "0.0 kB")

    def test_export_names_do_not_merge_origins(self):
        origins = [
            "https://example.com",
            "http://example.com",
            "https://a.b.example",
            "https://a-b.example",
        ]
        self.assertEqual(len({report_stem(value) for value in origins}), len(origins))

    def test_energy_and_traffic_keep_distinct_units_and_boundaries(self):
        evidence = json.loads(
            Path("docs/initial-implementation/assets/staged-audit.json").read_text()
        )
        energy = json.loads(
            Path(
                "docs/initial-implementation/assets/energy-experiment.json"
            ).read_text()
        )
        traffic = json.loads(
            Path(
                "docs/initial-implementation/assets/traffic-scenarios.json"
            ).read_text()
        )
        reports = export_reports(evidence, "bytes-digest")
        ratings = json.dumps(
            {site: report["ratings"] for site, report in reports.items()},
            sort_keys=True,
        )
        enrich_reports(reports, energy, traffic, "energy-digest", "traffic-digest")
        self.assertEqual(
            ratings,
            json.dumps(
                {site: report["ratings"] for site, report in reports.items()},
                sort_keys=True,
            ),
        )
        for report in reports.values():
            energy_rows = [
                r for r in report["observations"] if r["metric"] == "cpu_package_energy"
            ]
            self.assertEqual(len(energy_rows), 3)
            self.assertEqual({r["unit"] for r in energy_rows}, {"J"})
            self.assertEqual(
                {r["phase"] for r in energy_rows}, {"whole_browser_session"}
            )
            scenarios = [
                r
                for r in report["observations"]
                if r["metric"] == "estimated_annual_pageviews"
            ]
            self.assertEqual(len(scenarios), 1)
            self.assertEqual(scenarios[0]["basis"], "scenario")
