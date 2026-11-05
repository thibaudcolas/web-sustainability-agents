import copy
import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

from audit.wsg_reference import (
    CLASSES,
    REFERENCES,
    Document,
    extract_wsg,
    main,
    validate_classifications,
)


class WSGReferenceTests(unittest.TestCase):
    def setUp(self):
        self.reference = json.loads((REFERENCES / "wsg.json").read_text())
        self.classifications = json.loads(
            (REFERENCES / "assessment-crosswalk.json").read_text()
        )

    def test_current_inventory_is_complete_and_aggregates_all_criteria(self):
        validate_classifications(self.classifications, self.reference)
        criteria = [c for g in self.reference["guidelines"] for c in g["criteria"]]
        self.assertEqual(len(criteria), 197)
        self.assertEqual(len(self.classifications["guidelines"]), 71)
        counts = Counter(
            row["classification"] for row in self.classifications["criteria"]
        )
        self.assertEqual(
            self.classifications["categoryCounts"],
            {name: counts[name] for name in CLASSES},
        )
        self.assertEqual(
            sum(g["criterionCount"] for g in self.classifications["guidelines"]), 197
        )
        self.assertTrue((REFERENCES / self.reference["licenseNotice"]).is_file())

    def test_missing_duplicate_and_misidentified_criteria_are_rejected(self):
        for mutation in (
            "missing",
            "duplicate",
            "identity",
            "class",
            "rationale",
            "access",
            "support",
        ):
            data = copy.deepcopy(self.classifications)
            row = data["criteria"][0]
            if mutation == "missing":
                data["criteria"].pop()
            elif mutation == "duplicate":
                data["criteria"][1] = row
            elif mutation == "identity":
                row["guideline"] = "99.1"
            elif mutation == "class":
                row["classification"] = "unknown"
            elif mutation == "rationale":
                row["rationale"] = ""
            elif mutation == "access":
                row["evidenceAccess"] = ["unknown"]
            else:
                row["supportingClasses"] = [row["classification"]]
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_classifications(data, self.reference)

    def test_source_drift_and_invented_execution_outcomes_are_rejected(self):
        changed = copy.deepcopy(self.classifications)
        changed["wsgSourceSha256"] = "different-source"
        with self.assertRaisesRegex(ValueError, "same WSG source"):
            validate_classifications(changed, self.reference)
        changed = copy.deepcopy(self.classifications)
        changed["criteria"][0]["outcome"] = "pass"
        with self.assertRaisesRegex(ValueError, "not execution outcomes"):
            validate_classifications(changed, self.reference)

    def test_guideline_aggregates_and_top_level_counts_cannot_drift(self):
        for level in ("top", "guideline", "class-list", "membership"):
            changed = copy.deepcopy(self.classifications)
            group = changed["guidelines"][0]
            if level == "top":
                changed["categoryCounts"]["automated"] += 1
            elif level == "guideline":
                group["categoryCounts"]["automated"] += 1
            elif level == "class-list":
                group["classifications"] = []
            else:
                group["criterionCount"] += 1
            with self.subTest(level=level), self.assertRaises(ValueError):
                validate_classifications(changed, self.reference)

    def test_validation_needs_no_historical_source_and_does_not_rewrite_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            reference = Path(directory) / "wsg.json"
            original = (REFERENCES / "wsg.json").read_bytes()
            reference.write_bytes(original)
            with patch("sys.argv", ["wsg_reference.py", "--output", str(reference)]):
                main()
            self.assertEqual(reference.read_bytes(), original)

    def test_inline_markup_and_void_elements_preserve_text_and_boundaries(self):
        doc = Document(
            '<main><p>Use <abbr>CSS</abbr> safely.<br> Keep text.</p><img src="x"><p>Next &amp; last.</p></main>'
        )
        self.assertEqual(
            [p.text() for p in doc.root.descendants("p")],
            ["Use CSS safely. Keep text.", "Next & last."],
        )

    def test_incomplete_source_extraction_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "71-guideline"):
            extract_wsg(
                b'<html><section id="changed"><h3>2.1 Changed draft</h3></section></html>'
            )
