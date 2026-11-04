import copy
import tempfile
import unittest
from pathlib import Path

from audit.workflow import JSON, init_plan, read, validate_plan, validate_review


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.plan: JSON = {
            "origin": "https://example.com",
            "purpose": "Read guidance",
            "pages": [
                {"id": "home", "url": "https://example.com/", "task": "Find the guide"}
            ],
            "checks": [],
        }

    def test_scope_questions_are_not_silently_answered(self):
        self.plan["questions"] = [
            {"required": True, "question": "Which restricted flow?", "answer": None}
        ]
        with self.assertRaises(ValueError):
            validate_plan(self.plan)
        self.plan["questions"][0]["answer"] = "Public pages only"
        validate_plan(self.plan)

    def test_origin_scope_and_identifiers(self):
        for url in [
            "https://sub.example.com/",
            "https://user:secret@example.com/",
            "file:///etc/passwd",
        ]:
            self.plan["pages"][0]["url"] = url
            with self.assertRaises(ValueError):
                validate_plan(self.plan)
        self.plan["pages"][0]["url"] = "https://example.com/"
        self.plan["pages"].append(copy.deepcopy(self.plan["pages"][0]))
        with self.assertRaises(ValueError):
            validate_plan(self.plan)

    def test_new_plan_records_assumptions_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.json"
            init_plan("https://example.com/", [], path)
            plan = read(path)
            validate_plan(plan)
            self.assertTrue(plan["assumptions"])
            self.assertEqual(plan["questions"], [])
            self.assertEqual(plan["energy"]["mode"], "readiness")
            with self.assertRaises(ValueError):
                init_plan("https://example.com", [], path)

    def test_energy_sample_is_bounded_and_explicit(self):
        for settings in [
            {"mode": "silent"},
            {"samples": True},
            {"samples": 1},
            {"pageIds": ["missing"]},
            {"pageIds": ["home", "home"]},
            [],
        ]:
            self.plan["energy"] = settings
            with self.assertRaises(ValueError):
                validate_plan(self.plan)
        self.plan["energy"] = {"mode": "run", "samples": 3, "pageIds": ["home"]}
        validate_plan(self.plan)

    def test_collection_records_energy_readiness_and_freezes_artifact(self):
        from unittest.mock import patch

        from audit.workflow import collect, write

        def fake_command(argv, session, name):
            if name == "energy":
                write(
                    session / "energy/manifest.json",
                    {
                        "pages": [
                            {"status": "unavailable_prerequisites", "metrics": None}
                        ]
                    },
                )
            return {"argv": argv, "exitCode": 0}

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root / "plan.json", self.plan)
            with patch("audit.workflow.run_command", side_effect=fake_command):
                collect(root / "plan.json", root / "session")
            receipt = read(root / "session/receipt.json")
            energy = receipt["commands"][-1]["argv"]
            self.assertEqual(energy[energy.index("--mode") + 1], "readiness")
            packet = read(root / "session/packet.json")
            self.assertIn("energy/manifest.json:pages:0", packet["evidenceIndex"])
            self.assertIn("energy/manifest.json", packet["frozenFiles"])


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.packet: JSON = {
            "site": "https://example.com",
            "checks": [
                {"id": "motion", "guideline": "2.10"},
                {"id": "motion-control", "guideline": "2.10"},
            ],
            "evidenceIndex": {"page:0": {"jsonPointer": "/pages/0"}},
        }
        self.review: JSON = {
            "site": "https://example.com",
            "packetSHA256": "digest",
            "reviewer": {"harness": "Codex", "model": "Sol", "reasoning": "low"},
            "rows": [
                {
                    "checkId": item["id"],
                    "guideline": item["guideline"],
                    "outcome": "cantTell",
                    "evidenceIds": ["page:0"],
                    "nextEvidence": "Observe user-activated movement",
                }
                for item in self.packet["checks"]
            ],
        }

    def test_every_selected_check_must_have_a_judgment(self):
        validate_review(self.review, self.packet, "digest")
        self.review["rows"].pop()
        with self.assertRaises(ValueError):
            validate_review(self.review, self.packet, "digest")

    def test_no_duplicate_check_or_fabricated_reference(self):
        self.review["rows"][1]["checkId"] = "motion"
        with self.assertRaises(ValueError):
            validate_review(self.review, self.packet, "digest")
        self.review["rows"][1]["checkId"] = "motion-control"
        self.review["rows"][0]["evidenceIds"] = ["invented"]
        with self.assertRaises(ValueError):
            validate_review(self.review, self.packet, "digest")

    def test_exact_packet_and_mapping_required(self):
        with self.assertRaises(ValueError):
            validate_review(self.review, self.packet, "changed")
        self.review["rows"][0]["guideline"] = "3.13"
        with self.assertRaises(ValueError):
            validate_review(self.review, self.packet, "digest")


class FrozenSessionTests(unittest.TestCase):
    def test_frozen_scope_weights_skills_and_scorer_cannot_change(self):
        from audit.workflow import ROOT, digest, validate_frozen_files, write

        with tempfile.TemporaryDirectory() as directory:
            session = Path(directory)
            required = [
                "plan.json",
                "checks.json",
                "base-rubric.json",
                "rubric.json",
                "impact-weights.json",
                "skills/reviewer/SKILL.md",
            ]
            for name in required:
                write(session / name, {"original": True})
            write(
                session / "receipt.json",
                {
                    "sourceSHA256": {
                        name: digest(ROOT / name)
                        for name in ["audit/assess.py", "audit/assess.py.lock"]
                    }
                },
            )
            required.append("receipt.json")
            packet = {
                "frozenFiles": {name: digest(session / name) for name in required}
            }
            validate_frozen_files(session, packet)
            for name in [
                "plan.json",
                "impact-weights.json",
                "skills/reviewer/SKILL.md",
            ]:
                raw = (session / name).read_bytes()
                write(session / name, {"changed": True})
                with self.assertRaises(ValueError):
                    validate_frozen_files(session, packet)
                (session / name).write_bytes(raw)
            receipt = read(session / "receipt.json")
            receipt["sourceSHA256"]["audit/assess.py"] = "different scorer"
            write(session / "receipt.json", receipt)
            packet["frozenFiles"]["receipt.json"] = digest(session / "receipt.json")
            with self.assertRaises(ValueError):
                validate_frozen_files(session, packet)

    def test_page_actions_cannot_be_silently_ignored(self):
        plan: JSON = {
            "origin": "https://example.com",
            "purpose": "Read content",
            "pages": [
                {
                    "id": "home",
                    "url": "https://example.com/",
                    "task": "Read",
                    "actions": [{"type": "click", "selector": "#accept"}],
                }
            ],
        }
        with self.assertRaisesRegex(ValueError, "branches"):
            validate_plan(plan)
        page: JSON = plan["pages"][0]
        page["branches"] = [{"name": "accept", "actions": page.pop("actions")}]
        validate_plan(plan)
        page["branches"][0]["actions"][0]["type"] = "unknown"
        with self.assertRaises(ValueError):
            validate_plan(plan)
