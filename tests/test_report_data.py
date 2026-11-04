import json
import unittest
from pathlib import Path

from audit.report import display_bytes, enrich_reports, export_reports, report_stem


class ReportDataTests(unittest.TestCase):
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
        self.assertEqual(display_bytes(58992), "59.0 KB")
        self.assertEqual(display_bytes(1107665), "1.11 MB")
        self.assertEqual(display_bytes(0), "0.0 KB")

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
