import json
import os
import tempfile
import unittest
from pathlib import Path

from audit.source import MAX_FILE_BYTES, snapshot, validate_selection
from audit.workflow import prepare_packet, read, write


class SourceTests(unittest.TestCase):
    def test_explicit_files_have_hash_and_no_deployment_claim(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            root = workspace / "repo"
            root.mkdir()
            (root / "package.json").write_text('{"dependencies":{"example":"1.2.3"}}\n')
            plan = {
                "origin": "https://example.com",
                "sourceRoots": ["repo"],
                "sourceFiles": [{"root": "repo", "path": "package.json"}],
            }
            result = snapshot(plan, workspace)
            row = result["files"][0]
            self.assertEqual(row["status"], "captured")
            self.assertFalse(row["deploymentVerified"])
            self.assertEqual(len(row["sha256"]), 64)
            self.assertIsNone(result["repositories"][0]["revision"])

    def test_missing_and_oversized_are_not_empty_success(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "large.md").write_text("x" * (MAX_FILE_BYTES + 1))
            result = snapshot(
                {
                    "origin": "https://example.com",
                    "sourceRoots": ["."],
                    "sourceFiles": [
                        {"root": ".", "path": name}
                        for name in ["missing.md", "large.md"]
                    ],
                },
                root,
            )
            self.assertEqual(
                [row["status"] for row in result["files"]], ["unavailable", "too_large"]
            )
            self.assertTrue(
                all(
                    row["text"] is None and row["sha256"] is None
                    for row in result["files"]
                )
            )

    def test_large_file_identity_is_not_exposed_as_reviewed_contents(self):
        import hashlib

        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            raw = b"x" * 65_000
            (workspace / "lock.json").write_bytes(raw)
            result = snapshot(
                {
                    "origin": "https://example.com",
                    "sourceRoots": ["."],
                    "sourceFiles": [{"root": ".", "path": "lock.json"}],
                },
                workspace,
            )
            row = result["files"][0]
            self.assertEqual(row["status"], "metadata_only")
            self.assertIsNone(row["text"])
            self.assertEqual(row["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertFalse(row["deploymentVerified"])

    def test_root_traversal_secrets_and_symlink_escapes_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / "repo").mkdir()
            (workspace / "outside.md").write_text("outside")
            (workspace / "repo/link.md").symlink_to(workspace / "outside.md")
            (workspace / "repo/.env").write_text("not source")
            (workspace / "repo/alias.md").symlink_to(workspace / "repo/.env")
            os.mkfifo(workspace / "repo/pipe.txt")
            for name in [
                "alias.md",
                "pipe.txt",
                "../outside.md",
                "link.md",
                ".env",
                ".git/config",
                "node_modules/example/index.js",
            ]:
                with self.subTest(name=name), self.assertRaises(ValueError):
                    validate_selection(
                        {
                            "sourceRoots": ["repo"],
                            "sourceFiles": [{"root": "repo", "path": name}],
                        },
                        workspace,
                    )
            with self.assertRaises(ValueError):
                validate_selection(
                    {
                        "sourceRoots": [],
                        "sourceFiles": [{"root": "repo", "path": "README.md"}],
                    },
                    workspace,
                )

    def test_source_only_rules_are_opt_in_by_selected_files(self):
        with tempfile.TemporaryDirectory() as directory:
            session = Path(directory)
            write(
                session / "checks.json",
                {
                    "checks": [
                        {
                            "id": "public",
                            "guideline": "2.1",
                            "expectation": "Public disclosure",
                        },
                        {
                            "id": "source",
                            "guideline": "3.12",
                            "expectation": "Dependency declarations",
                            "requiresSource": True,
                        },
                    ]
                },
            )
            write(
                session / "base-rubric.json",
                {"guidelines": [{"number": "2.1"}, {"number": "3.12"}]},
            )
            for name in ["plan.json", "receipt.json", "impact-weights.json"]:
                write(session / name, {})
            (session / "skills").mkdir()
            prepare_packet(session, {"origin": "https://example.com"})
            self.assertEqual(
                [r["id"] for r in read(session / "packet.json")["checks"]], ["public"]
            )
            prepare_packet(
                session,
                {
                    "origin": "https://example.com",
                    "sourceFiles": [{"root": "repo", "path": "package.json"}],
                },
            )
            self.assertEqual(len(read(session / "packet.json")["checks"]), 2)
            self.assertEqual(
                json.loads((session / "rubric.json").read_text())["rubricVersion"],
                "agent-breadth-v2",
            )
