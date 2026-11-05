import copy
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

from audit.annual import annual_document, client_energy_scenario, model_pages
from audit.render_review import read, render


class AnnualProjectionTests(unittest.TestCase):
    def setUp(self):
        self.site = "https://example.org"
        self.url = self.site + "/"
        self.traffic: dict[str, Any] = {
            "origin": self.site,
            "rankBucket": 5000000,
            "traffic": {"status": "scenario", "annualPageviews": 1000000},
        }
        self.energy: dict[str, Any] = {
            "schemaVersion": "greenframe-energy-v2",
            "origin": self.site,
            "pages": [
                {
                    "url": self.url,
                    "phase": "initial",
                    "status": "completed",
                    "samples": 3,
                    "clientDeviceSummaryWh": {"median": 0.002},
                    "networkSummaryWh": {"median": 0.001},
                    "sampleMetrics": [
                        {
                            "clientDeviceEnergy": {
                                "value": value,
                                "unit": "Wh/scenario",
                            },
                            "networkEnergy": {"value": 0.001, "unit": "Wh/scenario"},
                        }
                        for value in (0.001, 0.002, 0.003)
                    ],
                }
            ],
        }

    def project(
        self,
        energy: dict[str, Any] | None = None,
        traffic: dict[str, Any] | None = None,
        grid: float = 494,
    ) -> dict[str, Any]:
        return client_energy_scenario(
            self.site, energy or self.energy, traffic or self.traffic, {self.url}, grid
        )

    def test_client_projection_converts_units_and_excludes_network(self):
        result = self.project()
        self.assertEqual(result["value"], 2)  # 0.002 Wh × one million / 1000.
        self.assertEqual(result["kgCO2ePerYear"], 0.988)
        self.assertEqual(result["sampledPageCount"], 1)
        self.assertEqual(self.project(grid=100)["kgCO2ePerYear"], 0.2)
        twice = copy.deepcopy(self.traffic)
        twice["traffic"]["annualPageviews"] *= 2
        self.assertEqual(self.project(traffic=twice)["value"], 4)
        self.assertNotIn("rating", result)

    def test_missing_inputs_stay_unavailable(self):
        result = client_energy_scenario(self.site, None, self.traffic, {self.url}, 494)
        self.assertIsNone(result["value"])
        updates: list[dict[str, Any]] = [
            {"origin": "https://other.org"},
            {"rankBucket": None},
        ]
        for update in updates:
            self.assertIsNone(self.project(traffic={**self.traffic, **update})["value"])
        failed = copy.deepcopy(self.energy)
        failed["pages"][0]["status"] = "failed"
        self.assertIsNone(self.project(energy=failed)["value"])

    def test_rejects_scope_sample_and_numeric_errors(self):
        for mutation in ("origin", "duplicate", "outside", "median", "boolean"):
            energy = copy.deepcopy(self.energy)
            if mutation == "origin":
                energy["origin"] = "https://other.org"
            elif mutation == "duplicate":
                energy["pages"] *= 2
            elif mutation == "outside":
                energy["pages"][0]["url"] += "unsampled/"
            elif mutation == "median":
                energy["pages"][0]["clientDeviceSummaryWh"]["median"] = 0.5
            else:
                energy["pages"][0]["clientDeviceSummaryWh"]["median"] = True
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.project(energy=energy)
        for grid in (float("nan"), -1, True, float("inf")):
            with self.assertRaises(ValueError):
                self.project(grid=grid)

    def test_first_visit_matches_report_and_keeps_partial_inputs(self):
        staged = read(Path("docs/reports/assets/fresh-wagtail/staged.json"))
        first = model_pages(staged, "first")["https://wagtail.org"]
        self.assertEqual(first[0]["branches"][0]["bytes"], 944428)
        self.assertEqual(first[0]["accountingStatus"], "partial")
        self.assertTrue(all(len(p["branches"]) == 1 for p in first))
        averaged = model_pages(staged)["https://wagtail.org"]
        self.assertTrue(all(len(p["branches"]) == 2 for p in averaged))
        self.assertNotEqual(first[0]["gramsPerView"], averaged[0]["gramsPerView"])

    def test_published_report_validates_annual_inputs_and_rejects_changed_results(self):
        session = Path("docs/reports/assets/fresh-guide")
        supplement = Path("docs/reports/assets/report-refinement/guide")
        traffic = supplement.parent / "traffic.json"
        energy = supplement / "energy.json"
        document = annual_document(
            (session / "staged.json").read_bytes(),
            traffic.read_bytes(),
            energy.read_bytes(),
        )
        with tempfile.TemporaryDirectory() as directory:
            annual = Path(directory) / "annual.json"
            annual.write_text(json.dumps(document))
            output = render(
                session,
                "artifacts",
                read(session / "editorial.json"),
                energy=energy,
                annual_path=annual,
                traffic_path=traffic,
            )
            self.assertIn("4.93 kgCO₂e/year", output)
            self.assertIn("0.49 kgCO₂e/year less", output)
            self.assertIn("2.76 kWh/year", output)
            self.assertIn("3 energy-sampled URLs out of 6", output)
            self.assertIn("not a predicted saving", output)
            document["clientEnergyScenarios"][0]["value"] *= 2
            annual.write_text(json.dumps(document))
            with self.assertRaisesRegex(ValueError, "do not match"):
                render(
                    session,
                    "artifacts",
                    read(session / "editorial.json"),
                    energy=energy,
                    annual_path=annual,
                    traffic_path=traffic,
                )
