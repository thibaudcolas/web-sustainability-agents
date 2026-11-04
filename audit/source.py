#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = []
# [tool.uv]
# required-version = ">=0.12.20,<0.13"
# ///
"""Snapshot explicitly selected source evidence without treating it as deployed code."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

JSON = dict[str, Any]
ROOT = Path(__file__).resolve().parent.parent
MAX_BYTES = 64_000
MAX_FILE_BYTES = 2_000_000
ALLOWED_SUFFIXES = {
    ".py",
    ".toml",
    ".json",
    ".yaml",
    ".yml",
    ".md",
    ".txt",
    ".html",
    ".css",
    ".scss",
    ".js",
    ".ts",
}
ALLOWED_NAMES = {
    "LICENSE",
    "COPYING",
    "Dockerfile",
    "Makefile",
    "justfile",
    ".python-version",
    ".node-version",
    ".nvmrc",
    "uv.lock",
    "poetry.lock",
}


def validate_selection(
    plan: JSON, workspace: Path = ROOT
) -> list[tuple[str, Path, str]]:
    """Limit collection to explicit files inside named source roots."""
    roots = plan.get("sourceRoots", [])
    selections = plan.get("sourceFiles", [])
    if not isinstance(roots, list) or not all(isinstance(root, str) for root in roots):
        raise ValueError("sourceRoots must contain paths")
    if not isinstance(selections, list) or len(selections) > 30:
        raise ValueError("Select at most 30 source files")
    result = []
    seen: set[tuple[str, str]] = set()
    for item in selections:
        root_name, relative = item["root"], item["path"]
        if root_name not in roots or not isinstance(relative, str):
            raise ValueError("Each source file needs an explicitly declared root")
        root = (workspace / root_name).resolve()
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts or not path.parts:
            raise ValueError("Source paths must stay within their root")
        if path.name not in ALLOWED_NAMES and path.suffix not in ALLOWED_SUFFIXES:
            raise ValueError("Select text source, dependency or documentation files")
        if path.name.startswith(".env") or any(
            part in {".git", "node_modules", ".venv"} for part in path.parts
        ):
            raise ValueError(
                "Environment, Git internals and installed packages are outside source collection"
            )
        candidate = root / path
        if any(
            (root.joinpath(*path.parts[:index])).is_symlink()
            for index in range(1, len(path.parts) + 1)
        ):
            raise ValueError("Select regular source paths, not symlink aliases")
        if candidate.exists() and not candidate.is_file():
            raise ValueError("Selected source must be a regular file")
        if not candidate.resolve().is_relative_to(root):
            raise ValueError("Source symlink escapes declared root")
        if (root_name, relative) in seen:
            raise ValueError("Duplicate source selection")
        seen.add((root_name, relative))
        result.append((root_name, root, relative))
    return result


def git(root: Path, args: list[str]) -> str | None:
    """Read bounded repository metadata without executing project commands."""
    try:
        result = subprocess.run(  # noqa: S603
            ["git", "-C", str(root), *args],  # noqa: S607
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )  # noqa: S603, S607
    except OSError, subprocess.TimeoutExpired:
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def snapshot(plan: JSON, workspace: Path = ROOT) -> JSON:
    """Retain file text, exact digests and repository state with deployment unknown."""
    files = []
    repositories: dict[str, JSON] = {}
    for index, (label, root, relative) in enumerate(
        validate_selection(plan, workspace)
    ):
        if label not in repositories:
            status = git(root, ["status", "--porcelain", "--untracked-files=no"])
            repositories[label] = {
                "root": label,
                "revision": git(root, ["rev-parse", "HEAD"]),
                "trackedWorkingTreeDirty": bool(status) if status is not None else None,
                "deploymentVerified": False,
                "relationship": "Owner-supplied candidate source for this origin; deployment identity unknown",
            }
        path = root / relative
        record: JSON = {
            "id": f"source-{index + 1}",
            "root": label,
            "path": relative,
            "deploymentVerified": False,
        }
        try:
            with path.open("rb") as stream:
                raw = stream.read(MAX_FILE_BYTES + 1)
            record["observedBytes"] = len(raw)
            if len(raw) > MAX_FILE_BYTES:
                record.update(
                    status="too_large",
                    limitBytes=MAX_FILE_BYTES,
                    text=None,
                    sha256=None,
                )
            else:
                text = raw.decode("utf-8")
                record.update(
                    status="captured" if len(raw) <= MAX_BYTES else "metadata_only",
                    text=text if len(raw) <= MAX_BYTES else None,
                    sha256=hashlib.sha256(raw).hexdigest(),
                    lines=len(text.splitlines()),
                )
                if len(raw) > MAX_BYTES:
                    record["interpretationLimit"] = (
                        "Identity and size only; contents are not exposed to the reviewer and naming alone does not prove a valid dependency lock"
                    )
                tracked = git(root, ["ls-files", "--error-unmatch", "--", relative])
                record["trackedInRepository"] = tracked is not None
                record["repository"] = repositories[label]
        except (OSError, UnicodeError) as error:
            record.update(
                status="unavailable", error=type(error).__name__, text=None, sha256=None
            )
        files.append(record)
    return {
        "schemaVersion": "source-evidence-v1",
        "site": plan["origin"],
        "capturedAt": datetime.now(UTC).isoformat(),
        "repositories": list(repositories.values()),
        "files": files,
        "scope": "Only explicitly selected text files; no code execution, installed-package inventory, vulnerability scan, complete dependency audit or deployment attestation",
    }


def main() -> None:
    """Collect a source supplement from the same agent-authored audit plan."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text())
    result = snapshot(plan)
    result["planSHA256"] = hashlib.sha256(args.plan.read_bytes()).hexdigest()
    result["collectorSHA256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.touch(mode=0o600, exist_ok=True)
    args.output.chmod(0o600)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
