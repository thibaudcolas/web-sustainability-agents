import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from audit.render_review import JSON, source_descriptions, validate_inputs


class RenderProvenanceTests(unittest.TestCase):
    def test_context_links_to_public_source_without_inventing_origin_homepage(self):
        packet = {
            "site": "https://example.com",
            "evidenceIndex": {
                "context": {"artifact": "context.json", "jsonPointer": "/records/0"},
                "disclosure": {
                    "artifact": "disclosures.json",
                    "jsonPointer": "/sites/0",
                },
                "discovery": {"artifact": "staged.json", "jsonPointer": "/discovery/0"},
            },
        }
        documents = {
            "context.json": {
                "records": [
                    {
                        "source": "https://example.com/project/policy/",
                        "kind": "public-document",
                    }
                ]
            },
            "disclosures.json": {"sites": [{"origin": "https://example.com"}]},
            "staged.json": {"discovery": [{"origin": "https://example.com"}]},
        }
        descriptions = source_descriptions(
            Path("."), packet, ["context", "disclosure", "discovery"], documents
        )
        self.assertIn("[Policy](https://example.com/project/policy/)", descriptions[0])
        self.assertEqual(
            descriptions[1], "Disclosure discovery for the origin `https://example.com`"
        )
        self.assertEqual(len(descriptions), 2)

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

    def test_nested_source_manifest_is_accepted_but_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            session, score, review = self.make_session(directory)
            (session / "energy").mkdir()
            nested = session / "energy/manifest.json"
            nested.write_text('{"pages": []}')
            wrapper_path = session / "reviews.json"
            wrapper = json.loads(wrapper_path.read_text())

            def select_source(name: str) -> None:
                wrapper["sourceSHA256"] = {
                    name: hashlib.sha256(nested.read_bytes()).hexdigest()
                }
                wrapper_path.write_text(json.dumps(wrapper))
                score["sourceSHA256"]["reviews"] = hashlib.sha256(
                    wrapper_path.read_bytes()
                ).hexdigest()

            select_source("energy/manifest.json")
            validate_inputs(session, score, review)
            for name in (str(nested), "energy/../energy/manifest.json"):
                select_source(name)
                with self.assertRaisesRegex(ValueError, "artifact name"):
                    validate_inputs(session, score, review)


class EditorialContractTests(unittest.TestCase):
    def setUp(self):
        self.session = Path("docs/reports/assets/fresh-guide")
        self.review = json.loads((self.session / "review.json").read_text())
        self.editorial = json.loads((self.session / "editorial.json").read_text())
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

        from audit.render_review import footprint, render, traffic

        output = render(self.session, "evidence", self.editorial)
        body, appendix = output.split(
            '??? note "Technical files for reproducing this report"'
        )
        self.assertFalse(re.search(r"\]\([^)]*\.json\)", body))
        self.assertIn("evidence/review.json", appendix)
        targets = re.findall(r"\]\(#(evidence-[^)]+)\)", body)
        for target in targets:
            self.assertIn('id="' + target + '"', body)
        self.assertEqual(self.review["reviewer"]["reasoning"], "high")
        self.assertEqual(self.editorial["writer"]["reasoning"], "high")
        self.assertNotIn("**low reasoning**", body)
        self.assertIn("**high reasoning**", body)
        probes = json.loads((self.session / "probes.json").read_text())
        self.assertGreaterEqual(len(probes["pages"]), 5)
        self.assertIn(f"**{len(probes['pages'])} pages** reviewed", body)
        self.assertNotIn("smaller sample than the default", body)
        self.assertIn("## Page measurements", body)
        self.assertNotIn("## After waiting and scrolling", body)
        self.assertIn("No cookie banner was observed in this sample", body)
        self.assertNotIn("Each cookie choice starts a separate fresh visit", body)
        self.assertIn("New in Wagtail 8.1", body)
        self.assertIn("**cumulative totals**", body)
        self.assertEqual(footprint(0.00876), "0.01 gCO₂e")
        self.assertEqual(footprint(0.00001), "0.01 gCO₂e")
        self.assertEqual(footprint(0.0345), "0.03 gCO₂e")
        self.assertEqual(footprint(1.2345), "1.23 gCO₂e")
        self.assertEqual(traffic(1000), "1.0 kB")
        self.assertEqual(traffic(1000000), "1.000 MB")

    def test_failed_navigation_is_unavailable_even_when_byte_accounting_is_complete(
        self,
    ):
        from unittest.mock import patch

        from audit.render_review import read, render

        staged = read(self.session / "staged.json")
        for run in staged["runs"]:
            run["navigationError"] = "net::ERR_FAILED"
            run["documentStatus"] = None
            for phase in run["phases"]:
                phase["receivedBytes"] = 0
                phase["accountingStatus"] = "complete_within_protocol"
            run["rating"] = {
                "status": "calculated",
                "trace": {"co2": {"total": 0, "rating": "A+"}},
            }

        def failed_read(path):
            return staged if path == self.session / "staged.json" else read(path)

        with patch("audit.render_review.read", side_effect=failed_read):
            output = render(self.session, "evidence", self.editorial)
        measurements = output.split("## Page measurements")[1].split(
            "## Estimated annual footprint"
        )[0]
        self.assertIn("Unavailable (navigation failed)", measurements)
        self.assertNotIn("0.0 kB", measurements)
        self.assertNotIn("0.00 gCO₂e", measurements)
        self.assertNotIn("A+", measurements)

    def test_screenshot_tampering_and_wrong_origin_are_rejected(self):
        import copy

        from audit.render_review import illustrations

        source = self.session / "screenshots/manifest.json"
        manifest = json.loads(source.read_text())
        completed = [
            index
            for index, capture in enumerate(manifest["captures"])
            if capture["status"] == "completed"
        ]
        self.assertTrue(completed, "The fresh report needs a usable illustration")
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
                        changed["captures"][completed[0]]["fileSHA256"] = "changed"
                    else:
                        changed["captures"][completed[0]]["file"] = "../outside.png"
                    target.write_text(json.dumps(changed))
                    with self.assertRaises(ValueError):
                        illustrations(target, self.review["site"], ids)
