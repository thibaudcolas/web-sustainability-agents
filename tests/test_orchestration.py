import json
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

from typer.testing import CliRunner

from audit.cli import app
from audit.orchestrate import accept, digest, read, reconcile, status, tasks
from scripts.install_audit import install

ROOT = Path(__file__).resolve().parent.parent


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.session = self.root / "session"
        self.session.mkdir()
        required = [
            "plan.json",
            "checks.json",
            "base-rubric.json",
            "rubric.json",
            "impact-weights.json",
        ]
        for role in ["evidence-review", "guideline-review", "claims-review"]:
            required.append(f"skills/sustainability-{role}/SKILL.md")
        for name in required:
            path = self.session / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{}")
        (self.session / "receipt.json").write_text(
            json.dumps(
                {
                    "sourceSHA256": {
                        name: digest(ROOT / name)
                        for name in ["audit/assess.py", "audit/assess.py.lock"]
                    }
                }
            )
        )
        required.append("receipt.json")
        (self.session / "raw.json").write_text("{}")
        self.packet = {
            "frozenFiles": {name: digest(self.session / name) for name in required},
            "sourceSHA256": {"raw.json": digest(self.session / "raw.json")},
            "site": "https://example.com",
            "checks": [{"id": "one", "guideline": "2.1"}],
            "evidenceIndex": {"page:0": {}},
        }
        (self.session / "packet.json").write_text(json.dumps(self.packet))
        self.output = self.root / "tasks"
        tasks(self.session, self.output, "native-subagents")

    def result(self, role: str) -> dict[str, Any]:
        result: dict[str, Any] = {
            "site": self.packet["site"],
            "packetSHA256": digest(self.session / "packet.json"),
            "reviewer": {
                "model": "gpt-6.1-sol",
                "reasoning": "high",
                "harness": "test",
            },
        }
        if role == "guidelines":
            result["rows"] = [
                {
                    "checkId": "one",
                    "guideline": "2.1",
                    "outcome": "cantTell",
                    "evidenceIds": ["page:0"],
                }
            ]
        else:
            result["role"] = role
            result["issues"] = [
                {
                    "id": "issue",
                    "checkIds": ["one"],
                    "evidenceIds": ["page:0"],
                    "summary": "Insufficient evidence",
                    "requestedChange": "Keep unknown",
                }
            ]
        return result

    def save(self, role: str, result: dict[str, Any]) -> None:
        (self.output / f"{role}.result.json").write_text(json.dumps(result))

    def test_presence_is_not_acceptance_and_changed_worker_result_invalidates_receipt(
        self,
    ):
        self.save("evidence", self.result("evidence"))
        self.assertEqual(status(self.output)["roles"][1]["state"], "needs-validation")
        accept(self.output / "evidence.task.json")
        edited = self.result("evidence")
        edited["issues"] = []
        self.save("evidence", edited)
        states = {r["role"]: r["state"] for r in status(self.output)["roles"]}
        self.assertEqual(states["evidence"], "changed-after-validation")
        self.assertFalse(status(self.output)["readyForReconciliation"])

    def test_wrong_site_invented_evidence_and_low_reasoning_are_rejected(self):
        for change in ["site", "evidence", "reasoning"]:
            result = self.result("claims")
            if change == "site":
                result["site"] = "https://elsewhere.example"
            if change == "evidence":
                result["issues"][0]["evidenceIds"] = ["invented"]
            if change == "reasoning":
                result["reviewer"]["reasoning"] = "low"
            self.save("claims", result)
            with self.assertRaises(ValueError):
                accept(self.output / "claims.task.json")

    def test_changed_raw_evidence_blocks_acceptance_and_status(self):
        self.save("evidence", self.result("evidence"))
        accept(self.output / "evidence.task.json")
        (self.session / "raw.json").write_text("changed")
        with self.assertRaisesRegex(ValueError, "Frozen session file changed"):
            status(self.output)
        self.save("claims", self.result("claims"))
        with self.assertRaisesRegex(ValueError, "Frozen session file changed"):
            accept(self.output / "claims.task.json")
        with self.assertRaisesRegex(ValueError, "Frozen session file changed"):
            tasks(self.session, self.root / "new-tasks", "sequential")

    def test_pass_and_fail_require_evidence(self):
        for outcome in ["pass", "fail"]:
            result = self.result("guidelines")
            result["rows"][0].update(outcome=outcome, evidenceIds=[])
            self.save("guidelines", result)
            with self.assertRaisesRegex(ValueError, "need evidence"):
                accept(self.output / "guidelines.task.json")

    def test_reconciliation_requires_response_to_every_issue(self):
        for role in ["evidence", "guidelines", "claims"]:
            self.save(role, self.result(role))
            accept(self.output / f"{role}.task.json")
        resolutions = self.output / "resolutions.json"
        resolutions.write_text(json.dumps({"resolutions": []}))
        with self.assertRaisesRegex(ValueError, "every advisor"):
            reconcile(self.output, resolutions)
        resolutions.write_text(
            json.dumps(
                {
                    "resolutions": [
                        {
                            "issue": f"{role}:issue",
                            "decision": "applied",
                            "reason": "Preserved missing-evidence outcome",
                        }
                        for role in ["evidence", "claims"]
                    ]
                }
            )
        )
        reconcile(self.output, resolutions)
        self.assertTrue((self.output / "reconciliation.accepted.json").exists())
        self.assertEqual(
            read(self.output / "reconciliation.accepted.json")["resolutionsSHA256"],
            digest(resolutions),
        )


class InstallationTests(unittest.TestCase):
    def test_installs_only_entrypoint_and_records_runtime_without_overwriting(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            outputs = install(ROOT, project, "codex", True)
            self.assertEqual(len(outputs), 1)
            self.assertFalse((project / ".agents").exists())
            install(ROOT, project, "codex")
            skill = project / ".agents/skills/sustainability-audit"
            self.assertTrue((skill / "scripts/runtime.py").is_file())
            self.assertEqual(
                json.loads((skill / "runtime-location.json").read_text())["root"],
                str(ROOT),
            )
            (skill / "SKILL.md").write_text("local customization")
            with self.assertRaisesRegex(ValueError, "Existing skills"):
                install(ROOT, project, "codex")
            self.assertEqual((skill / "SKILL.md").read_text(), "local customization")

    def test_plugin_entrypoint_matches_canonical_source(self):
        for name in ["SKILL.md", "scripts/runtime.py", "scripts/runtime.py.lock"]:
            self.assertEqual(
                (ROOT / "skills/sustainability-audit" / name).read_bytes(),
                (ROOT / ".agents/skills/sustainability-audit" / name).read_bytes(),
            )


class CLITests(unittest.TestCase):
    def test_tool_forwards_collector_flags_and_help_verbatim(self):
        for arguments in [
            ["workflow", "init", "--help"],
            [
                "screenshots",
                "--plan",
                "/project/plan with spaces.json",
                "--output",
                "/project/capture",
            ],
        ]:
            with (
                self.subTest(arguments=arguments),
                patch("audit.cli.runtime") as runtime,
            ):
                result = CliRunner().invoke(app, ["tool", *arguments])
                self.assertEqual(result.exit_code, 0, result.output)
                runtime.assert_called_once_with(["tool", *arguments])
