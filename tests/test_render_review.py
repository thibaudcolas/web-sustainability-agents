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
