import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from audit.render_review import JSON, validate_inputs


class RenderProvenanceTests(unittest.TestCase):
    def make_session(self, directory: str) -> tuple[Path, JSON, JSON]:
        session = Path(directory)

        def write(name: str, value: JSON) -> None:
            (session / name).write_text(json.dumps(value))

        def digest(name: str) -> str:
            return hashlib.sha256((session / name).read_bytes()).hexdigest()

        write("packet.json", {"site": "https://example.com"})
        review = {"packetSHA256": digest("packet.json")}
        write("review.json", review)
        write("evidence.json", {"status": "observed"})
        write("rubric.json", {"version": "test"})
        write("impact-weights.json", {"weights": {}})
        write(
            "reviews.json",
            {
                "reviewFileSHA256": digest("review.json"),
                "sourceSHA256": {"evidence.json": digest("evidence.json")},
            },
        )
        score = {
            "sourceSHA256": {
                "reviews": digest("reviews.json"),
                "rubric": digest("rubric.json"),
                "impactWeights": digest("impact-weights.json"),
            }
        }
        return session, score, review

    def test_changed_review_cannot_be_presented_with_old_score(self):
        with tempfile.TemporaryDirectory() as directory:
            session, score, review = self.make_session(directory)
            validate_inputs(session, score, review)
            (session / "review.json").write_text('{"altered": true}')
            with self.assertRaisesRegex(ValueError, "Reviewer output changed"):
                validate_inputs(session, score, review)

    def test_changed_evidence_cannot_be_presented_as_scored(self):
        with tempfile.TemporaryDirectory() as directory:
            session, score, review = self.make_session(directory)
            validate_inputs(session, score, review)
            (session / "evidence.json").write_text('{"status": "invented"}')
            with self.assertRaisesRegex(ValueError, "source evidence changed"):
                validate_inputs(session, score, review)


class EditorialContractTests(unittest.TestCase):
    def setUp(self):
        self.session = Path("docs/initial-implementation/assets/breadth-sessions/guide")
        self.review = json.loads((self.session / "review.json").read_text())
        self.editorial = json.loads(
            Path(
                "docs/initial-implementation/assets/report-editions/guide/editorial.json"
            ).read_text()
        )
        self.digest = hashlib.sha256(
            (self.session / "review.json").read_bytes()
        ).hexdigest()

    def test_editing_cannot_change_site_judgments_or_priority_order(self):
        import copy

        from audit.render_review import validate_editorial

        validate_editorial(self.editorial, self.review, self.digest)
        for mutation in ["site", "hash", "missing", "duplicate", "reorder"]:
            with self.subTest(mutation=mutation):
                data = copy.deepcopy(self.editorial)
                if mutation == "site":
                    data["site"] = "https://another.example"
                elif mutation == "hash":
                    data["reviewSHA256"] = "changed"
                elif mutation == "missing":
                    data["checks"].pop()
                elif mutation == "duplicate":
                    data["checks"].append(data["checks"][0])
                else:
                    data["findings"].reverse()
                with self.assertRaises(ValueError):
                    validate_editorial(data, self.review, self.digest)

    def test_readable_report_keeps_raw_downloads_in_technical_appendix(self):
        import re

        from audit.render_review import render, traffic

        output = render(self.session, "evidence", self.editorial)
        body, appendix = output.split(
            '??? note "Technical files for reproducing this report"'
        )
        self.assertFalse(re.search(r"\]\([^)]*\.json\)", body))
        self.assertIn("evidence/review.json", appendix)
        targets = re.findall(r"\]\(#(evidence-[^)]+)\)", body)
        for target in targets:
            self.assertIn('id="' + target + '"', body)
        self.assertIn("**low reasoning**", body)
        self.assertIn("**high reasoning**", body)
        self.assertIn("Complete within the test conditions", body)
        self.assertNotIn("a Digital Carbon Rating is withheld", body)
        self.assertIn("**Digital Carbon Ratings:** A+", body)
        self.assertEqual(traffic(1000), "1.0 kB")
        self.assertEqual(traffic(1000000), "1.000 MB")

    def test_screenshot_tampering_and_wrong_origin_are_rejected(self):
        import copy

        from audit.render_review import illustrations

        source = Path(
            "docs/initial-implementation/assets/report-editions/guide/screenshots/manifest.json"
        )
        manifest = json.loads(source.read_text())
        ids = {row["checkId"] for row in self.review["rows"]}
        illustrations(source, self.review["site"], ids)
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "manifest.json"
            for record in manifest["captures"]:
                if record["status"] == "completed":
                    (target.parent / record["file"]).write_bytes(
                        (source.parent / record["file"]).read_bytes()
                    )
            for mutation in ["origin", "hash", "path"]:
                with self.subTest(mutation=mutation):
                    changed = copy.deepcopy(manifest)
                    if mutation == "origin":
                        changed["origin"] = "https://another.example"
                    elif mutation == "hash":
                        changed["captures"][0]["fileSHA256"] = "changed"
                    else:
                        changed["captures"][0]["file"] = "../outside.png"
                    target.write_text(json.dumps(changed))
                    with self.assertRaises(ValueError):
                        illustrations(target, self.review["site"], ids)
