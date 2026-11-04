#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11,<3.15"
# dependencies = []
# [tool.uv]
# required-version = ">=0.12.20,<0.13"
# ///
"""Collect frozen controlled evidence into a verifiable audit handoff artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def collect(source: Path, output: Path) -> dict[str, Any]:
    """Preserve exact source identity and expose scoped facts for agent interpretation."""
    raw = source.read_bytes()
    bundle = json.loads(raw)
    result = {
        "collectionVersion": "breadth-collector-v1",
        "sourceSHA256": hashlib.sha256(raw).hexdigest(),
        "site": bundle["site"],
        "facts": bundle["facts"],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    return result


def main() -> None:
    """Run locally with uv or inside the pinned Harbor image's Python interpreter."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("/app/bundle.json"))
    parser.add_argument(
        "--output", type=Path, default=Path("/app/output/collection.json")
    )
    args = parser.parse_args()
    collect(args.source, args.output)


if __name__ == "__main__":
    main()
