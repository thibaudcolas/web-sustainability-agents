import copy
import json
import unittest
from pathlib import Path
from typing import Any

from benchmarks.grade_expanded import grade


class ExpandedGraderTests(unittest.TestCase):
    def setUp(self):
        self.cases = json.loads(Path("benchmarks/expanded-cases.json").read_text())[
            "cases"
        ]

    def solution(self, reference: dict[str, Any]) -> dict[str, Any]:
        return {
            "schemaVersion": "0.2.0",
            "summary": {"site": reference["site"], "overallScore": None},
            **{
                section: [
                    {
                        **row,
                        "explanation": "This is a controlled reference explanation for contract validation.",
                    }
                    for row in reference[section]
                ]
                for section in ["answers", "metrics", "recommendations"]
            },
        }

    def test_all_oracles_pass_and_empty_reports_fail(self):
        for case in self.cases:
            with self.subTest(case=case["id"]):
                self.assertEqual(
                    grade(self.solution(case["reference"]), case["reference"])[
                        "reward"
                    ],
                    1,
                )
                self.assertEqual(grade(None, case["reference"])["reward"], 0)

    def test_units_basis_numeric_values_and_boolean_values(self):
        reference = self.cases[0]["reference"]
        for field, value in [
            ("unit", "B"),
            ("basis", "scenario"),
            ("value", 944379),
            ("value", True),
            ("value", float("nan")),
            ("value", 10**400),
        ]:
            report = self.solution(reference)
            report["metrics"][0][field] = value
            self.assertEqual(grade(report, reference)["reward"], 0)

    def test_missing_energy_cannot_be_zero(self):
        reference = next(
            c["reference"] for c in self.cases if c["id"] == "energy-missing"
        )
        report = self.solution(reference)
        report["metrics"][0]["value"] = 0
        self.assertEqual(grade(report, reference)["reward"], 0)

    def test_scope_score_fabricated_evidence_and_bad_recommendations(self):
        reference = self.cases[0]["reference"]
        good = self.solution(reference)
        mutations = []
        for key, value in [("site", "https://other.example"), ("overallScore", 100)]:
            changed = copy.deepcopy(good)
            changed["summary"][key] = value
            mutations.append(changed)
        changed = copy.deepcopy(good)
        changed["answers"][0]["evidenceIds"] = ["invented"]
        mutations.append(changed)
        changed = copy.deepcopy(good)
        changed["recommendations"][0]["action"] = "fix"
        mutations.append(changed)
        changed = copy.deepcopy(good)
        changed["answers"][0]["id"] = changed["answers"][1]["id"]
        mutations.append(changed)
        for report in mutations:
            self.assertEqual(grade(report, reference)["reward"], 0)

    def test_malformed_sections_do_not_crash_verifier(self):
        reference = self.cases[0]["reference"]
        invalids: list[Any] = [None, {}, [None], [{"id": []}]]
        for value in invalids:
            report = self.solution(reference)
            report["answers"] = value
            self.assertEqual(grade(report, reference)["reward"], 0)
