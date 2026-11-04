#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = []
# [tool.uv]
# required-version = ">=0.12.20,<0.13"
# ///
"""Grade breadth judgments and required collection artifacts in an isolated verifier."""

from __future__ import annotations

import importlib
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

JSON = dict[str, Any]
grade_base = cast(
    Callable[[Any, JSON], JSON],
    importlib.import_module(
        f"{__package__}.grade_expanded" if __package__ else "grade_expanded"
    ).grade,
)


def grade(report: Any, reference: JSON, collection: Any = None) -> JSON:
    """Require the declared collection handoff in addition to structured judgments."""
    result = grade_base(report, reference)
    if (
        "requiredCollection" in reference
        and collection != reference["requiredCollection"]
    ):
        result["errors"].append("Missing, changed, or wrong-origin collection artifact")
        result["reward"] = 0
    return result


def load_json(path: Path) -> Any:
    """Treat missing and malformed agent artifacts as unsuccessful submissions."""
    try:
        raw = path.read_text()
        return json.loads(raw) if len(raw) <= 100_000 else None
    except FileNotFoundError, UnicodeError, json.JSONDecodeError:
        return None


def main() -> None:
    """Run with protected references outside the agent environment."""
    reference = json.loads(Path("/tests/reference.json").read_text())
    result = grade(
        load_json(Path("/app/output/report.json")),
        reference,
        load_json(Path("/app/output/collection.json")),
    )
    output = Path("/logs/verifier")
    output.mkdir(parents=True, exist_ok=True)
    (output / "reward.txt").write_text(str(result["reward"]))
    (output / "diagnostics.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
