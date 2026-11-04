import copy
import json
import unittest
from collections import Counter

from audit.wsg_reference import (
    CATEGORIES,
    REFERENCES,
    Document,
    extract_assessment,
    extract_wsg,
    validate_crosswalk,
)


class WSGReferenceTests(unittest.TestCase):
    def setUp(self):
        self.reference = json.loads((REFERENCES / "wsg.json").read_text())
        self.crosswalk = json.loads(
            (REFERENCES / "assessment-crosswalk.json").read_text()
        )
        self.rows = self.crosswalk["checks"]

    def test_published_reference_and_crosswalk_are_complete(self):
        self.assertEqual(len(self.reference["guidelines"]), 71)
        criteria = [c for g in self.reference["guidelines"] for c in g["criteria"]]
        self.assertEqual(len(criteria), 197)
        self.assertEqual(len({c["id"] for c in criteria}), 197)
        self.assertTrue(all(c["text"] for c in criteria))
        self.assertEqual(Counter(r["classification"] for r in self.rows), CATEGORIES)
        validate_crosswalk(self.crosswalk, self.reference, self.rows)
        self.assertTrue((REFERENCES / self.reference["licenseNotice"]).is_file())

    def test_mapping_rejects_dropped_rows_and_invalid_current_targets(self):
        missing = copy.deepcopy(self.crosswalk)
        missing["checks"].pop()
        with self.assertRaisesRegex(ValueError, "each selected"):
            validate_crosswalk(missing, self.reference, self.rows)
        wrong = copy.deepcopy(self.crosswalk)
        wrong["checks"][0]["targets"][0]["guideline"] = "2.6"
        with self.assertRaisesRegex(ValueError, "Invalid criterion"):
            validate_crosswalk(wrong, self.reference, self.rows)
        wrong["checks"][0]["targets"][0]["criterion"] = "nonexistent"
        with self.assertRaisesRegex(ValueError, "Invalid criterion"):
            validate_crosswalk(wrong, self.reference, self.rows)

    def test_source_drift_and_invented_execution_status_are_rejected(self):
        changed = copy.deepcopy(self.crosswalk)
        changed["wsgSourceSha256"] = "different-source"
        with self.assertRaisesRegex(ValueError, "same WSG source"):
            validate_crosswalk(changed, self.reference, self.rows)
        changed = copy.deepcopy(self.crosswalk)
        changed["checks"][0]["status"] = "passed"
        with self.assertRaisesRegex(ValueError, "not an executed result"):
            validate_crosswalk(changed, self.reference, self.rows)

    def test_inline_markup_and_void_elements_preserve_text_and_boundaries(self):
        doc = Document(
            '<main><p>Use <abbr>CSS</abbr> safely.<br> Keep text.</p><img src="x"><p>Next &amp; last.</p></main>'
        )
        self.assertEqual(
            [p.text() for p in doc.root.descendants("p")],
            ["Use CSS safely. Keep text.", "Next & last."],
        )

    def test_incomplete_source_extractions_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "71-guideline"):
            extract_wsg(
                b'<html><section id="changed"><h3>2.1 Changed draft</h3></section></html>'
            )
        with self.assertRaisesRegex(ValueError, "35/16/50"):
            extract_assessment(b"<table></table>")
