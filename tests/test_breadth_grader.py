import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

from benchmarks.collect_breadth import collect
from benchmarks.grade_breadth import grade

JSON = dict[str, Any]


class BreadthGraderTests(unittest.TestCase):
    def setUp(self):
        self.cases = json.loads(Path("benchmarks/breadth-cases.json").read_text())[
            "cases"
        ]

    def oracle(self, reference: JSON) -> JSON:
        return {
            "schemaVersion": "0.2.0",
            "summary": {"site": reference["site"], "overallScore": None},
            **{
                section: [
                    {
                        **row,
                        "explanation": "Controlled oracle explanation for the protected benchmark contract.",
                    }
                    for row in reference[section]
                ]
                for section in ["answers", "metrics", "recommendations"]
            },
        }

    def test_all_sixteen_references_pass_and_noops_fail(self):
        self.assertEqual(len(self.cases), 16)
        self.assertEqual(sum(case["requiresCollector"] for case in self.cases), 4)
        for case in self.cases:
            reference = copy.deepcopy(case["reference"])
            collection = None
            if case["requiresCollector"]:
                collection = {
                    "collectionVersion": "breadth-collector-v1",
                    "sourceSHA256": "pinned-source",
                    "site": reference["site"],
                    "facts": case["input"]["facts"],
                }
                reference["requiredCollection"] = collection
            with self.subTest(case=case["id"]):
                self.assertEqual(
                    grade(self.oracle(reference), reference, collection)["reward"], 1
                )
                self.assertEqual(grade(None, reference, collection)["reward"], 0)

    def test_required_collection_cannot_be_omitted_or_change_scope(self):
        reference = copy.deepcopy(self.cases[0]["reference"])
        good = {
            "collectionVersion": "breadth-collector-v1",
            "site": reference["site"],
            "facts": [{"id": "e1", "value": "captured"}],
            "sourceSHA256": "source",
        }
        reference["requiredCollection"] = good
        report = self.oracle(reference)
        bad_scope = {**good, "site": "https://other.example"}
        bad_source = {**good, "sourceSHA256": "different"}
        bad_facts = {**good, "facts": []}
        for collection in [None, {}, bad_scope, bad_source, bad_facts]:
            self.assertEqual(grade(report, reference, collection)["reward"], 0)

    def test_collector_preserves_source_bytes_and_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "bundle.json"
            output = Path(directory) / "output/collection.json"
            bundle = {
                "site": "https://audit.example",
                "facts": [{"id": "e1", "value": {"runtimeVersion": None}}],
            }
            source.write_text(json.dumps(bundle))
            result = collect(source, output)
            self.assertEqual(
                result["sourceSHA256"], hashlib.sha256(source.read_bytes()).hexdigest()
            )
            self.assertEqual(result["facts"], bundle["facts"])
            self.assertEqual(json.loads(output.read_text()), result)

    def test_false_task_success_and_model_boundary_are_rejected(self):
        for name in ["journey-false-success", "energy-boundary-greenframe"]:
            case = next(c for c in self.cases if c["id"] == name)
            report = self.oracle(case["reference"])
            report["answers"][0]["outcome"] = "pass"
            self.assertEqual(grade(report, case["reference"])["reward"], 0)

    def test_all_mappings_exist_and_evidence_ids_are_resolvable(self):
        wsg = json.loads(
            Path(
                ".agents/skills/sustainability-guideline-review/references/wsg.json"
            ).read_text()
        )
        groups = {g["id"] for g in wsg["guidelines"]}
        for case in self.cases:
            self.assertTrue(set(case["guidelines"]) <= groups)
            ids = {fact["id"] for fact in case["input"]["facts"]}
            self.assertEqual(ids, set(case["reference"]["allowedEvidenceIds"]))
            for row in (
                case["reference"]["answers"] + case["reference"]["recommendations"]
            ):
                self.assertTrue(set(row["evidenceIds"]) <= ids)
