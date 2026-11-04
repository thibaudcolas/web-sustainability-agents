#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = []
# [tool.uv]
# required-version = ">=0.12.20,<0.13"
# ///
"""Install complete audit skills into a project without overwriting existing skills."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def install(
    root: Path, project: Path, harness: str, dry_run: bool = False
) -> list[str]:
    """Install the runtime-linked skill set atomically with respect to conflicts."""
    directory = ".claude/skills" if harness == "claude-code" else ".agents/skills"
    target = project.resolve() / directory
    skills = [root / ".agents/skills/sustainability-audit"]
    if not skills or any(not (skill / "SKILL.md").is_file() for skill in skills):
        raise ValueError("Complete audit skills are required")
    conflicts = [
        str(target / skill.name)
        for skill in skills
        if (target / skill.name).exists() or (target / skill.name).is_symlink()
    ]
    if conflicts:
        raise ValueError("Existing skills were not changed: " + ", ".join(conflicts))
    outputs = [str(target / skill.name) for skill in skills]
    if dry_run:
        return outputs
    target.mkdir(parents=True, exist_ok=True)
    for skill in skills:
        shutil.copytree(
            skill,
            target / skill.name,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
    (target / "sustainability-audit/runtime-location.json").write_text(
        json.dumps(
            {"root": str(root.resolve()), "installation": "project-skills"}, indent=2
        )
        + "\n"
    )
    return outputs


def main() -> None:
    """Install into the explicitly selected project, or preview every path."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument(
        "--harness", choices=["codex", "claude-code", "opencode", "pi"], required=True
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    print(  # noqa: T201 - command output
        json.dumps(
            {
                "skills": install(ROOT, args.project, args.harness, args.dry_run),
                "dryRun": args.dry_run,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
