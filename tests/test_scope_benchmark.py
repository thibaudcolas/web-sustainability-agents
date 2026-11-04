import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

from benchmarks.grade_breadth import grade


class ScopeBenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.cases = json.loads(Path("benchmarks/scope-cases.json").read_text())[
            "cases"
        ]

    def oracle(self, reference: dict[str, Any]) -> dict[str, Any]:
        return {
            "schemaVersion": "0.2.0",
            "summary": {"site": reference["site"], "overallScore": None},
            **{
                section: [
                    {
                        **row,
                        "explanation": "Controlled reference contract, not independently validated audit accuracy.",
                    }
                    for row in reference[section]
                ]
                for section in ["answers", "metrics", "recommendations"]
            },
        }

    def test_all_new_references_and_empty_controls(self):
        self.assertEqual(len(self.cases), 19)
        self.assertEqual(sum(c["requiresCollector"] for c in self.cases), 4)
        for case in self.cases:
            with self.subTest(case=case["id"]):
                self.assertEqual(
                    grade(self.oracle(case["reference"]), case["reference"])["reward"],
                    1,
                )
                self.assertEqual(grade(None, case["reference"])["reward"], 0)

    def test_new_family_is_disjoint_and_context_dimensions_resolve(self):
        new_ids = {c["id"] for c in self.cases}
        for family in ["expanded", "methodology", "breadth"]:
            prior = json.loads(Path(f"benchmarks/{family}-cases.json").read_text())
            self.assertFalse(new_ids & {c["id"] for c in prior["cases"]})
        contextual = json.loads(Path("audit/context-checks.json").read_text())
        contextual_ids = {c["id"] for c in contextual["checks"]}
        dimensions = {d for c in self.cases for d in c["dimensions"]}
        self.assertTrue(contextual_ids <= dimensions)
        for case in self.cases:
            evidence = {f["id"] for f in case["input"]["facts"]}
            self.assertEqual(evidence, set(case["reference"]["allowedEvidenceIds"]))
            self.assertGreater(len(case["referenceRationale"]), 40)

    def test_pitfalls_cannot_be_replaced_with_convenient_numbers(self):
        mutations = {
            "inference-energy-missing-not-zero": (0, 0),
            "initial-first-visit-and-median-three": (0, 1000),
            "median-cannot-mix-consent-and-cache": (0, 100),
            "area-score-known-only-and-coverage": (4, 0),
            "star-qualitative-scope-and-evidence": (0, 4),
        }
        for name, (index, value) in mutations.items():
            reference = next(c["reference"] for c in self.cases if c["id"] == name)
            report = copy.deepcopy(self.oracle(reference))
            report["metrics"][index]["value"] = value
            self.assertEqual(grade(report, reference)["reward"], 0)

    def test_builder_isolates_references_and_freezes_current_skills(self):
        manifest = Path(
            "docs/initial-implementation/assets/scope-benchmark-manifest.json"
        )
        before = manifest.read_bytes() if manifest.exists() else None
        try:
            with tempfile.TemporaryDirectory() as directory:
                command = [
                    sys.executable,
                    "benchmarks/build_expanded.py",
                    "--scope",
                    "--output",
                    str(Path(directory) / "tasks"),
                ]
                subprocess.run(command, check=True, capture_output=True)  # noqa: S603 - repository builder and generated temporary directory
                frozen = json.loads(manifest.read_text())
                self.assertEqual(len(frozen["cases"]), 19)
                for case in self.cases:
                    task = Path(directory) / "tasks" / case["id"]
                    environment = task / "environment"
                    self.assertFalse((environment / "reference.json").exists())
                    self.assertFalse((environment / "solution").exists())
                    supplied = json.loads((environment / "input.json").read_text())
                    self.assertNotIn("referenceRationale", supplied)
                    self.assertEqual(
                        bool(supplied["facts"]), not case["requiresCollector"]
                    )
                    reference = json.loads((task / "tests/reference.json").read_text())
                    solution = json.loads((task / "solution/report.json").read_text())
                    collection = reference.get("requiredCollection")
                    self.assertEqual(
                        grade(solution, reference, collection)["reward"], 1
                    )
                    if collection:
                        self.assertEqual(
                            collection["sourceSHA256"],
                            hashlib.sha256(
                                (environment / "bundle.json").read_bytes()
                            ).hexdigest(),
                        )
                        self.assertEqual(grade(solution, reference)["reward"], 0)
                failed = subprocess.run(command, capture_output=True)  # noqa: S603 - same trusted builder command
                self.assertNotEqual(failed.returncode, 0)
                self.assertIn(b"must not be overwritten", failed.stderr)
        finally:
            if before is None:
                manifest.unlink(missing_ok=True)
            else:
                manifest.write_bytes(before)
