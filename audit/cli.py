#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = ["typer==0.27.2"]
# [tool.uv]
# required-version = ">=0.12.20,<0.13"
# ///
"""Progressive skill discovery and deterministic tools for host-agent sustainability audits."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import typer

ROOT = Path(__file__).resolve().parent.parent
app = typer.Typer(name="wsa", help=__doc__, no_args_is_help=True)
skills = typer.Typer(
    help="Load only the workflow knowledge needed for this task.", no_args_is_help=True
)
app.add_typer(skills, name="skills")


def skill_paths() -> dict[str, Path]:
    """Keep the entrypoint separate from progressively loaded workflows."""
    paths = {
        p.parent.name.removeprefix("sustainability-"): p.parent
        for p in (ROOT / ".agents/skills").glob("sustainability-*/SKILL.md")
        if p.parent.name != "sustainability-audit"
    }
    paths["core"] = ROOT / "skill-data/core"
    return paths


@skills.command("list")
def list_skills() -> None:
    """List installed workflow names and exact local paths as JSON."""
    typer.echo(
        json.dumps({name: str(path) for name, path in skill_paths().items()}, indent=2)
    )


@skills.command("get")
def get_skill(name: str, full: bool = typer.Option(False, "--full")) -> None:
    """Print a workflow, optionally including its references and templates."""
    paths = skill_paths()
    if name not in paths:
        raise typer.BadParameter("Unknown workflow; use skills list")
    root = paths[name]
    typer.echo((root / "SKILL.md").read_text())
    if full:
        for directory in ("references", "assets"):
            for path in sorted((root / directory).rglob("*")):
                if path.is_file() and path.suffix in {".md", ".json", ".txt"}:
                    typer.echo(
                        f"\n## Resource: {path.relative_to(root)}\n\n{path.read_text()}"
                    )


@skills.command("path")
def skill_path(name: str) -> None:
    """Return a workflow's folder for native agent skill loading."""
    if name not in skill_paths():
        raise typer.BadParameter("Unknown workflow; use skills list")
    typer.echo(str(skill_paths()[name]))


def runtime(arguments: list[str]) -> None:
    """Delegate environment setup and collectors to the pinned runtime helper."""
    subprocess.run(  # noqa: S603 - fixed helper and argv forwarding
        [  # noqa: S607 - uv is an explicit prerequisite
            "uv",
            "run",
            "--locked",
            "--script",
            str(ROOT / ".agents/skills/sustainability-audit/scripts/runtime.py"),
            *arguments,
        ],
        check=True,
    )


@app.command()
def doctor() -> None:
    """Inspect prerequisites without changing the host."""
    runtime(["doctor"])


@app.command()
def prepare() -> None:
    """Install locked runtime dependencies and Chromium for the agent."""
    runtime(["prepare"])


@app.command(
    context_settings={
        "allow_extra_args": True,
        "ignore_unknown_options": True,
        "help_option_names": [],
    }
)
def tool(ctx: typer.Context, name: str) -> None:
    """Run a deterministic audit tool; remaining arguments are forwarded verbatim."""
    runtime(["tool", name, *ctx.args])


if __name__ == "__main__":
    app()
