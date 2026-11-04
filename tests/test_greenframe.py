import json
import os
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

from audit.greenframe import clean_environment, parse_metrics, prepare, scenario


class GreenFrameTests(unittest.TestCase):
    def test_client_only_configuration_and_independent_phase(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            record = prepare("https://site.test/", work, "initial", None, 3)
            config = json.loads((work / ".greenframe.yml").read_text())
            self.assertEqual(config["containers"], [])
            self.assertEqual(config["databaseContainers"], [])
            self.assertFalse(config["distant"])
            self.assertFalse(config["useAdblock"])
            self.assertIsNone(record["metrics"])
            self.assertNotIn(".click", (work / "scenario.js").read_text())
            self.assertNotIn("scrollBy", (work / "scenario.js").read_text())
            with self.assertRaises(ValueError):
                prepare("https://site.test/", work, "initial", None, 3)

    def test_scroll_requires_explicit_consent_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                prepare("https://site.test", Path(directory), "after_scroll", None, 3)
            record = prepare(
                "https://site.test",
                Path(directory),
                "after_scroll",
                None,
                3,
                no_banner=True,
            )
            self.assertTrue(record["noBannerDeclared"])
        code = scenario("after_scroll", 'button[data-choice="accept"]')
        self.assertIn(".click", code)
        self.assertIn("step < 40", code)
        self.assertIn("Scroll bound reached", code)

    def test_metrics_retain_model_units_and_unknown_output(self):
        result = parse_metrics(
            "The estimated footprint is 0.038 g eq. co2 ± 10.3% (0.085 Wh)."
        )
        assert result is not None
        self.assertEqual(result["energy"]["unit"], "Wh/scenario")
        self.assertEqual(result["carbon"]["basis"], "GreenFrame model")
        self.assertEqual(result["reportedPrecisionPercent"], 10.3)
        self.assertIsNone(parse_metrics("scenario failed"))
        self.assertIsNone(parse_metrics("1..0 g eq. co2 ± 2% (1 Wh)"))

    def test_cloud_credentials_are_not_inherited(self):
        with patch.dict(
            os.environ,
            {
                "GREENFRAME_SECRET_TOKEN": "not-a-real-key",
                "GREENFRAME_PROJECT_NAME": "private",
                "PATH": "/bin",
            },
            clear=True,
        ):
            self.assertEqual(clean_environment(), {"PATH": "/bin"})


class GreenFrameEnergyTests(unittest.TestCase):
    def plan(self) -> dict[str, Any]:
        return {
            "origin": "https://site.test",
            "pages": [{"id": "home", "url": "https://site.test/"}],
            "energy": {"samples": 3, "pageIds": ["home"]},
        }

    def test_default_readiness_and_missing_tools_preserve_null_energy(self):
        from audit.greenframe import collect_energy

        with (
            tempfile.TemporaryDirectory() as directory,
            patch("audit.greenframe.preflight", return_value={"ready": False}) as check,
            patch("audit.greenframe.measure_page") as measure,
        ):
            result = collect_energy(self.plan(), Path(directory))
            check.assert_called_once()
            measure.assert_not_called()
            self.assertEqual(result["status"], "unavailable_prerequisites")
            self.assertIsNone(result["pages"][0]["metrics"])
            self.assertTrue((Path(directory) / "manifest.json").exists())

    def test_explicit_skip_does_not_probe_or_run(self):
        from audit.greenframe import collect_energy

        with (
            tempfile.TemporaryDirectory() as directory,
            patch("audit.greenframe.preflight") as check,
            patch("audit.greenframe.measure_page") as measure,
        ):
            result = collect_energy(self.plan(), Path(directory), "skip")
            check.assert_not_called()
            measure.assert_not_called()
            self.assertEqual(result["status"], "skipped_explicitly")
            self.assertIsNone(result["pages"][0]["metrics"])

    def test_run_failure_is_explicit_and_does_not_manufacture_zero(self):
        from audit.greenframe import collect_energy

        with (
            tempfile.TemporaryDirectory() as directory,
            patch("audit.greenframe.preflight", return_value={"ready": True}),
            patch(
                "audit.greenframe.measure_page", side_effect=ValueError("bad counters")
            ),
        ):
            result = collect_energy(self.plan(), Path(directory), "run")
            self.assertEqual(result["status"], "unavailable_measurement")
            self.assertIn("bad counters", result["pages"][0]["error"])
            self.assertIsNone(result["pages"][0]["metrics"])

    def test_component_scope_excludes_network_and_rejects_broken_counters(self):
        import copy

        from audit.greenframe import component_metrics

        result: dict[str, Any] = {
            "status": "finished",
            "score": {
                "wh": {
                    "cpu": 0.1,
                    "mem": 0.2,
                    "disk": 0,
                    "screen": 0.3,
                    "network": 1.0,
                    "total": 1.6,
                },
                "s": {"totalTime": 4.0},
            },
        }
        metrics = component_metrics(result)
        self.assertAlmostEqual(metrics["clientDeviceEnergy"]["value"], 0.6)
        self.assertEqual(metrics["networkEnergy"]["value"], 1.0)
        for value in [None, True, -1, float("nan"), 0]:
            invalid = copy.deepcopy(result)
            invalid["score"]["wh"]["cpu"] = value
            with self.assertRaises(ValueError):
                component_metrics(invalid)
        invalid = copy.deepcopy(result)
        invalid["score"]["wh"]["total"] = 2.0
        with self.assertRaises(ValueError):
            component_metrics(invalid)

    def test_scope_is_bounded_to_three_planned_pages_in_exact_origin(self):
        from audit.greenframe import collect_energy

        plan = self.plan()
        plan["pages"][0]["url"] = "https://other.site.test/"
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(ValueError):
            collect_energy(plan, Path(directory), "skip")
        plan = self.plan()
        plan["energy"]["pageIds"] = ["missing"]
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(ValueError):
            collect_energy(plan, Path(directory), "skip")
