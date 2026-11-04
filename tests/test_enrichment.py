import copy
import gzip
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

from audit.energy import read_profile, summarize, validate_profile
from audit.traffic import origin, traffic_scenario


def profile() -> dict[str, Any]:
    return {
        "meta": {"oscpu": "Linux x86_64"},
        "counters": [
            {
                "name": "Power: CPU package",
                "category": "power",
                "samples": {
                    "schema": {"time": 0, "count": 1},
                    "data": [[10, 1_000_000_000], [20, 1_000_000_000]],
                },
            }
        ],
    }


class EnrichmentTests(unittest.TestCase):
    def test_energy_units_and_overlapping_domains(self):
        value = profile()
        overlapping = copy.deepcopy(value["counters"][0])
        overlapping["name"] = "Power: CPU cores"
        value["counters"].append(overlapping)
        result = validate_profile(value)
        self.assertAlmostEqual(result["joules"], 7.2)
        self.assertAlmostEqual(result["mWh"], 2)
        self.assertAlmostEqual(result["excludingFirstSampleJoules"], 3.6)

    def test_missing_empty_and_duplicate_counter_are_not_zero(self):
        invalids: list[dict[str, Any]] = [
            {},
            {"counters": []},
            {"counters": profile()["counters"] * 2},
        ]
        for value in invalids:
            self.assertIsNone(validate_profile(value)["joules"])
        value = profile()
        value["counters"][0]["samples"]["data"] = []
        self.assertIsNone(validate_profile(value)["joules"])

    def test_invalid_samples_are_rejected(self):
        for rows in [
            [[1, -1], [2, 1]],
            [[1, float("nan")], [2, 1]],
            [[2, 1], [1, 1]],
            [[1, True], [2, 1]],
        ]:
            value = profile()
            value["counters"][0]["samples"]["data"] = rows
            self.assertEqual(validate_profile(value)["status"], "invalid")

    def test_zero_counter_is_explicit_and_excluded_from_summary(self):
        value = profile()
        value["counters"][0]["samples"]["data"] = [[1, 0], [2, 0]]
        energy = validate_profile(value)
        self.assertEqual(energy["joules"], 0)
        self.assertTrue(energy["allZero"])
        rows = summarize(
            [
                {
                    "url": "https://example.com",
                    "energy": energy,
                    "journeyStatus": "completed",
                }
            ]
        )
        self.assertIsNone(rows[0]["medianJoules"])

    def test_gzip_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profile.json.gz"
            path.write_bytes(gzip.compress(json.dumps(profile()).encode()))
            self.assertEqual(read_profile(path), profile())

    def test_failed_journey_is_not_in_valid_energy_summary(self):
        energy = validate_profile(profile())
        rows = summarize(
            [
                {
                    "url": "https://example.com",
                    "energy": energy,
                    "journeyStatus": "failed",
                }
            ]
        )
        self.assertEqual(rows[0]["attempts"], 1)
        self.assertEqual(rows[0]["validRuns"], 0)

    def test_origin_matching_preserves_subdomain_scheme_and_nondefault_port(self):
        self.assertEqual(
            origin("https://Guide.Wagtail.org:443/en/?q=1"), "https://guide.wagtail.org"
        )
        self.assertNotEqual(
            origin("https://guide.wagtail.org"), origin("https://wagtail.org")
        )
        self.assertNotEqual(origin("http://wagtail.org"), origin("https://wagtail.org"))
        self.assertEqual(
            origin("https://wagtail.org:8443/path"), "https://wagtail.org:8443"
        )

    def test_absent_rank_does_not_use_unranked_prediction(self):
        self.assertIsNone(
            traffic_scenario(None, {100_000_000: 31867})["annualPageviews"]
        )
        result = traffic_scenario(5_000_000, {5_000_000: 572851})
        self.assertEqual(result["status"], "scenario")
        self.assertEqual(result["annualPageviews"], 572851)
        self.assertIsNone(result["annualEmissions"])

    def test_wrong_platform_category_and_malformed_containers_are_unavailable(self):
        values = []
        value = profile()
        value["meta"]["oscpu"] = "Windows"
        values.append(value)
        value = profile()
        value["counters"][0]["category"] = "not-power"
        values.append(value)
        value = profile()
        value["counters"] = [None]
        values.append(value)
        value = profile()
        value["counters"][0]["samples"] = None
        values.append(value)
        for value in values:
            self.assertIsNone(validate_profile(value)["joules"])
