import copy
import tempfile
import unittest
from pathlib import Path
from typing import Any

from audit.orchestrate import tasks
from audit.workflow import (
    ROOT,
    catalog,
    digest,
    prepare_packet,
    read,
    selected_checks,
    snapshot_context,
    validate_frozen_files,
    validate_plan,
    write,
)


class ContextReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.plan: dict[str, Any] = {
            "origin": "https://example.com",
            "purpose": "Review the public service",
            "pages": [
                {"id": "home", "url": "https://example.com/", "task": "Find guidance"}
            ],
            "checks": [],
            "contextChecks": ["content-lifecycle"],
            "contextEvidence": [],
        }
        self.path = self.directory / "review.md"
        self.path.write_text(
            "The review owner retired guide v1 on 2026-10-01; its searchable archive remains linked."
        )
        self.record: dict[str, Any] = {
            "id": "review-example",
            "path": str(self.path),
            "kind": "public-document",
            "source": "https://example.com/reviews/2026-10/",
            "scope": "One collection and retirement decision",
            "capturedAt": "2026-11-04T10:00:00+00:00",
            "limitations": "Publisher self-report; CMS execution not independently verified",
            "checkIds": ["content-lifecycle"],
        }

    def test_contextual_catalog_maps_exact_pinned_criteria_and_partial_scopes(self):
        current = read(ROOT / "audit/context-checks.json")
        reference = read(
            ROOT / ".agents/skills/sustainability-guideline-review/references/wsg.json"
        )
        self.assertEqual(current["wsgSourceSha256"], reference["sourceSha256"])
        guidelines = {g["id"]: g for g in reference["guidelines"]}
        self.assertEqual(len(current["checks"]), 10)
        self.assertEqual(len({c["guideline"] for c in current["checks"]}), 8)
        for check in current["checks"]:
            criterion = next(
                c
                for c in guidelines[check["guideline"]]["criteria"]
                if c["id"] == check["criterion"]
            )
            self.assertEqual(check["url"], criterion["url"])
            self.assertFalse(check["requiresSource"])
            self.assertFalse(check["fullGuidelineCoverage"])
            self.assertTrue(check["evidenceRequirements"])

    def test_context_free_defaults_remain_v2_and_context_needs_no_source(self):
        definitions = catalog()
        public_plan = {**self.plan, "contextChecks": []}
        self.assertEqual(len(selected_checks(definitions, public_plan)), 25)
        source_plan = {**public_plan, "sourceFiles": [{"path": "README.md"}]}
        self.assertEqual(len(selected_checks(definitions, source_plan)), 33)
        chosen = selected_checks(definitions, self.plan)
        self.assertEqual(len(chosen), 26)
        self.assertIn("content-lifecycle", {c["id"] for c in chosen})
        self.assertFalse(any(c.get("requiresSource") for c in chosen))
        direct = {**public_plan, "checks": ["content-lifecycle"]}
        self.assertEqual(
            [c["id"] for c in selected_checks(definitions, direct)],
            ["content-lifecycle"],
        )

    def test_records_require_attribution_time_scope_and_selected_check(self):
        self.plan["contextEvidence"] = [self.record]
        validate_plan(self.plan)
        for key, invalid in [
            ("scope", ""),
            ("source", ""),
            ("limitations", ""),
            ("capturedAt", "2026-11-04"),
            ("path", "relative.md"),
            ("checkIds", ["governance-practice"]),
            ("kind", "verified-implementation"),
        ]:
            broken = copy.deepcopy(self.plan)
            broken["contextEvidence"][0][key] = invalid
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_plan(broken)
        self.plan["contextChecks"] = ["not-a-check"]
        with self.assertRaises(ValueError):
            validate_plan(self.plan)

    def test_missing_or_oversized_text_is_unresolved_not_a_silent_capture(self):
        self.plan["contextEvidence"] = [self.record]
        selected = selected_checks(catalog(), self.plan)
        captured = snapshot_context(self.plan, selected)
        self.assertEqual(captured["records"][0]["text"], self.path.read_text())
        self.assertEqual(captured["records"][0]["sha256"], digest(self.path))
        self.assertEqual(captured["requests"][0]["status"], "review-required")
        self.path.write_bytes(b"x" * 64_001)
        oversized = snapshot_context(self.plan, selected)
        self.assertEqual(oversized["records"][0]["status"], "too_large")
        self.assertIsNone(oversized["records"][0]["text"])
        self.assertEqual(oversized["requests"][0]["status"], "unresolved")
        self.path.unlink()
        missing = snapshot_context(self.plan, selected)
        self.assertEqual(missing["records"][0]["status"], "unavailable")
        self.assertEqual(missing["requests"][0]["recordIds"], [])

    def packet(self) -> Path:
        session = self.directory / "session"
        session.mkdir()
        self.plan["contextEvidence"] = [self.record]
        write(session / "plan.json", self.plan)
        write(session / "checks.json", {"checks": catalog()})
        for name in ["base-rubric.json", "impact-weights.json"]:
            original = "rubric.json" if name == "base-rubric.json" else name
            (session / name).write_bytes((ROOT / "audit" / original).read_bytes())
        write(
            session / "receipt.json",
            {
                "sourceSHA256": {
                    name: digest(ROOT / name)
                    for name in ["audit/assess.py", "audit/assess.py.lock"]
                }
            },
        )
        write(
            session / "context.json",
            snapshot_context(self.plan, selected_checks(catalog(), self.plan)),
        )
        for role in [
            "guideline-review",
            "claims-review",
            "evidence-review",
            "context-review",
        ]:
            (session / "skills" / f"sustainability-{role}").mkdir(parents=True)
            (session / "skills" / f"sustainability-{role}" / "SKILL.md").write_text(
                "Frozen role"
            )
        reference = (
            session / "skills/sustainability-context-review/references/review.md"
        )
        reference.parent.mkdir()
        reference.write_text("Frozen evidence interpretation")
        prepare_packet(session, self.plan)
        return session

    def test_frozen_context_is_indexed_versioned_and_routed_to_existing_reviewers(self):
        session = self.packet()
        packet = read(session / "packet.json")
        self.assertEqual(
            read(session / "rubric.json")["rubricVersion"], "agent-breadth-v3"
        )
        self.assertEqual(
            packet["evidenceIndex"]["context.json:records:0"]["jsonPointer"],
            "/records/0",
        )
        self.assertEqual(packet["methodologyCoverage"]["catalogGuidelineGroups"], 40)
        self.assertEqual(packet["methodologyCoverage"]["catalogFullGuidelineGroups"], 0)
        self.assertEqual(packet["methodologyCoverage"]["selectedGuidelineGroups"], 25)
        tasks(session, self.directory / "tasks", "sequential")
        for role in ["claims", "guidelines"]:
            task = read(self.directory / "tasks" / f"{role}.task.json")
            self.assertEqual(len(task["supportingSkills"]), 1)
            self.assertTrue(Path(task["supportingSkills"][0]).is_file())
        self.assertEqual(
            read(self.directory / "tasks/evidence.task.json")["supportingSkills"], []
        )
        write(session / "context.json", {"records": []})
        with self.assertRaisesRegex(ValueError, "Frozen session file changed"):
            validate_frozen_files(session, packet)

    def test_context_free_packet_retains_v2_rubric(self):
        self.plan["contextChecks"] = []
        self.record["checkIds"] = []
        # A context-free packet has no contextual record selection.
        session = self.directory / "plain"
        session.mkdir()
        fixtures: list[tuple[str, dict[str, Any]]] = [
            ("plan.json", self.plan),
            ("checks.json", {"checks": catalog()}),
            ("receipt.json", {}),
            ("base-rubric.json", read(ROOT / "audit/rubric.json")),
            ("impact-weights.json", {}),
        ]
        for name, value in fixtures:
            write(session / name, value)
        prepare_packet(session, self.plan)
        self.assertEqual(
            read(session / "rubric.json")["rubricVersion"], "agent-breadth-v2"
        )
        self.assertEqual(len(read(session / "packet.json")["checks"]), 25)
