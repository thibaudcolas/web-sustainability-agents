#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = []
# [tool.uv]
# required-version = ">=0.12.20,<0.13"
# ///
"""Resolve the installed audit runtime and run pinned setup or collector commands."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

TOOLS = {
    "workflow",
    "run",
    "probes",
    "disclosures",
    "source",
    "screenshots",
    "render_review",
    "report",
    "assess",
    "greenframe",
    "orchestrate",
}


def runtime_root(start: Path) -> Path:
    """Find a complete plugin checkout or the installer's explicit runtime locator."""
    locator = start.parent.parent / "runtime-location.json"
    if locator.exists():
        value = json.loads(locator.read_text())
        candidates = [Path(value["root"])]
    else:
        candidates = list(start.resolve().parents)
    for root in candidates:
        if (root / "audit/workflow.py").is_file() and (
            root / "package-lock.json"
        ).is_file():
            return root.resolve()
    raise ValueError(
        "Audit runtime is missing; reinstall the plugin or refresh the skill installation"
    )


def command(root: Path, tool: str, arguments: list[str]) -> list[str]:
    """Resolve an allowlisted script without interpreting shell text."""
    if tool not in TOOLS or not (root / "audit" / f"{tool}.py").is_file():
        raise ValueError("Unknown or unavailable audit tool")
    return [
        "uv",
        "run",
        "--locked",
        "--script",
        str(root / "audit" / f"{tool}.py"),
        *arguments,
    ]


def doctor(root: Path) -> dict[str, Any]:
    """Report runtime identity and prerequisites without installing anything."""
    return {
        "root": str(root),
        "executables": {name: shutil.which(name) for name in ("uv", "node", "npm")},
        "pythonEnvironmentPresent": (root / ".venv").is_dir(),
        "nodeDependenciesPresent": (root / "node_modules").is_dir(),
        "setupCommand": "prepare",
        "browserCheck": "Run the collector after prepare; directory presence alone does not prove browser readiness",
    }


def run(argv: list[str], root: Path) -> None:
    """Execute a fixed argv in the resolved tool root, retaining native output."""
    subprocess.run(argv, cwd=root, check=True)  # noqa: S603


def main() -> None:
    """Serve the agent's setup and execution entry point from any working directory."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    commands.add_parser("doctor")
    commands.add_parser("prepare")
    tool = commands.add_parser("tool")
    tool.add_argument("name", choices=sorted(TOOLS))
    tool.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    root = runtime_root(Path(__file__))
    if args.action == "doctor":
        print(json.dumps(doctor(root), indent=2))  # noqa: T201
    elif args.action == "prepare":
        missing = [name for name in ("uv", "node", "npm") if not shutil.which(name)]
        if missing:
            parser.error(
                "Install these host prerequisites first: " + ", ".join(missing)
            )
        run(["uv", "sync", "--locked"], root)
        run(["npm", "ci"], root)
        run(["uv", "run", "python", "-m", "playwright", "install", "chromium"], root)
    else:
        run(command(root, args.name, args.arguments), root)


if __name__ == "__main__":
    main()
