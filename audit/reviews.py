#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = []
# [tool.uv]
# required-version = ">=0.12.20,<0.13"
# ///
"""Prepare portable skill review packets and publish evidence-resolved judgments."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "docs/initial-implementation/assets"
EVIDENCE = ["staged-audit.json", "scope-extension.json", "wagtail-review-evidence.json"]
SKILLS = [
    "sustainability-evidence-review",
    "sustainability-guideline-review",
    "sustainability-claims-review",
]
JSON = dict[str, Any]
REPOSITORY_SCOPES = {
    "https://github.com/wagtail/guide": "https://guide.wagtail.org",
    "https://github.com/wagtail/wagtail.org": "https://wagtail.org",
}


def nodes(value: Any, pointer: str = "") -> list[tuple[str, JSON]]:
    """Index object nodes using JSON Pointer escaping."""
    result = []
    if isinstance(value, dict):
        result.append((pointer, value))
        for key, item in value.items():
            result.extend(
                nodes(
                    item, pointer + "/" + str(key).replace("~", "~0").replace("/", "~1")
                )
            )
    elif isinstance(value, list):
        for index, item in enumerate(value):
            result.extend(nodes(item, pointer + f"/{index}"))
    return result


def resolve(reference: str, site: str, sources: dict[str, JSON]) -> JSON:
    """Resolve reviewer locators to actual evidence; reject absent or ambiguous IDs."""
    filename, separator, identifier = reference.partition("#")
    filename = Path(filename).name
    if not separator or filename not in sources:
        raise ValueError(f"Unsupported evidence locator: {reference}")
    data = sources[filename]
    candidates = nodes(data)
    parts = re.split(r"/resources[/:]", identifier, maxsplit=1)
    if len(parts) == 2:
        parent = [(p, v) for p, v in candidates if v.get("id") == parts[0]]
        matches = [
            (p + f"/resources/{i}", r)
            for p, v in parent
            for i, r in enumerate(v.get("resources", []))
            if r.get("id") == parts[1]
        ]
    elif identifier.startswith("discovery"):
        marker = "/documents/" if "/documents/" in identifier else "/documents:"
        url = identifier.split(marker, 1)[-1]
        matches = [
            (f"/discovery/{i}/documents/{j}", doc)
            for i, item in enumerate(data.get("discovery", []))
            if item["site"] == site
            for j, doc in enumerate(item.get("documents", []))
            if doc["url"] == url
        ]
    elif identifier.startswith("declaredFileChecks:"):
        url = identifier.removeprefix("declaredFileChecks:")
        matches = [
            (f"/sites/{i}/declaredFileChecks/{j}", item)
            for i, entry in enumerate(data.get("sites", []))
            if entry["site"] == site
            for j, item in enumerate(entry.get("declaredFileChecks", []))
            if item["url"] == url
        ]
    else:
        matches = [(p, v) for p, v in candidates if v.get("id") == identifier]
    if len(matches) != 1:
        raise ValueError(
            f"Evidence locator resolved to {len(matches)} nodes: {reference}"
        )
    pointer, _ = matches[0]
    if owner(pointer, data) != site:
        raise ValueError(
            f"Evidence belongs to a different or unknown site: {reference}"
        )
    return {"artifact": filename, "jsonPointer": pointer}


def owner(pointer: str, data: JSON) -> str | None:
    """Identify the enclosing capture/site, allowing explicitly associated source."""
    candidates = nodes(data)
    parents = [
        (p, v) for p, v in candidates if p == pointer or pointer.startswith(p + "/")
    ]
    for _, value in parents:
        if value.get("site"):
            return str(value["site"])
        if value.get("repository") in REPOSITORY_SCOPES:
            return REPOSITORY_SCOPES[value["repository"]]
        url = value.get("url")
        if not url and value.get("requests"):
            url = next(
                (r["url"] for r in value["requests"] if r.get("type") == "document"),
                None,
            )
        if url:
            parsed = urlsplit(url)
            return f"{parsed.scheme}://{parsed.netloc}"
        if value.get("id") == "average-check":
            # Historical arithmetic explicitly concerns the two Wagtail disclosures.
            ids = value.get("evidenceIds", [])
            if set(ids) == {"sustainability-average", "footprint-total"}:
                return "https://wagtail.org"
    return None


def prepare(destination: Path) -> None:
    """Describe the same bounded reviews for any harness with file-reading tools."""
    destination.mkdir(parents=True, exist_ok=True)
    for path in sorted((ASSETS / "coverage").glob("*.json")):
        coverage = json.loads(path.read_text())
        packet = {
            "site": coverage["site"],
            "rubric": "audit/rubric.json",
            "rubricSHA256": hashlib.sha256(
                (ROOT / "audit/rubric.json").read_bytes()
            ).hexdigest(),
            "guidelines": [
                g["number"]
                for g in coverage["guidelines"]
                if g["status"] == "partial_evidence"
            ],
            "skills": [f".agents/skills/{name}/SKILL.md" for name in SKILLS],
            "evidence": [
                {
                    "path": f"docs/initial-implementation/assets/{name}",
                    "SHA256": hashlib.sha256((ASSETS / name).read_bytes()).hexdigest(),
                }
                for name in EVIDENCE
            ],
            "task": "Judge the supplied rubric expectations from raw evidence. Do not read prior human report conclusions. Inspect supplied local source read-only as needed, retaining deployment uncertainty. Return JSON with site, reviewer, rows and topRecommendations; do not calculate the aggregate score.",
            "rowFields": [
                "guideline",
                "outcome",
                "evidenceIds",
                "rationale",
                "confidence",
                "nextEvidence",
            ],
            "outcomes": ["pass", "fail", "cantTell", "inapplicable", "untested"],
            "evidenceLocator": "artifact.json#actual-id, or artifact.json#capture-id/resources/resource-id; source/file/page IDs must exist in the artifact",
        }
        (destination / path.name).write_text(json.dumps(packet, indent=2) + "\n")


def main() -> None:
    """Prepare packets or publish completed skill reviews without silent regrading."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", type=Path)
    parser.add_argument("--inputs", type=Path, nargs="+")
    parser.add_argument("--reviewer-model", default="unspecified")
    parser.add_argument("--output", type=Path, default=ASSETS / "skill-reviews.json")
    args = parser.parse_args()
    if args.prepare:
        prepare(args.prepare)
    if not args.inputs:
        if not args.prepare:
            parser.error("Specify --prepare or --inputs")
        return
    sources = {name: json.loads((ASSETS / name).read_text()) for name in EVIDENCE}
    digests = {
        name: hashlib.sha256((ASSETS / name).read_bytes()).hexdigest()
        for name in EVIDENCE
    }
    reviews = []
    for path in args.inputs:
        raw = path.read_bytes()
        review = json.loads(raw)
        evidence_index = {}
        for row in review["rows"] + review.get("topRecommendations", []):
            for identifier in row["evidenceIds"]:
                resolved = resolve(identifier, review["site"], sources)
                evidence_index[identifier] = {
                    **resolved,
                    "sourceSHA256": digests[resolved["artifact"]],
                }
        reviews.append(
            {
                **review,
                "rawReviewSHA256": hashlib.sha256(raw).hexdigest(),
                "evidenceIndex": evidence_index,
            }
        )
    result = {
        "schemaVersion": "0.1.0",
        "reviewerModel": args.reviewer_model,
        "status": "Independent bounded skill forward tests; coordinator reviewed evidence resolution; not owner-validated ground truth",
        "sourceSHA256": digests,
        "rubricSHA256": hashlib.sha256(
            (ROOT / "audit/rubric.json").read_bytes()
        ).hexdigest(),
        "skillSHA256": {
            name: hashlib.sha256(
                (ROOT / f".agents/skills/{name}/SKILL.md").read_bytes()
            ).hexdigest()
            for name in SKILLS
        },
        "reviews": reviews,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
