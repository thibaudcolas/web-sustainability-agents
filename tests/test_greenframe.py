import json
import os
import tempfile
import unittest
from pathlib import Path
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
