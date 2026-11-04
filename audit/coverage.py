#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = []
# [tool.uv]
# required-version = ">=0.12.20,<0.13"
# ///
"""Publish separate guideline evidence registers without inferring conformance."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

JSON = dict[str, Any]
ROOT = Path(__file__).resolve().parent.parent
HISTORICAL = {
    "https://guide.wagtail.org": {
        "2.4": ["F07"],
        "2.9": ["F04"],
        "2.17": ["F08"],
        "3.7": ["F04"],
        "3.11": ["F07"],
        "4.2": ["F05"],
        "4.3": ["F05"],
        "5.5": ["G01"],
    },
    "https://wagtail.org": {
        "2.9": ["F06"],
        "2.11": ["F09"],
        "2.15": ["F02"],
        "3.5": ["F01"],
        "3.7": ["F06"],
        "3.10": ["F10"],
        "4.2": ["F05"],
        "4.3": ["F05"],
        "5.5": ["F03", "F12"],
    },
}


def register(site: JSON, guidelines: list[JSON], digest: str) -> JSON:
    """Attach bounded evidence and explicit missing work to each of the 71 guidelines."""
    origin = site["site"]
    pages = [
        p
        for p in site["pages"]
        if p.get("status") == 200
        and p.get("initial")
        and f"{urlsplit(p.get('finalUrl', p['url'])).scheme}://{urlsplit(p.get('finalUrl', p['url'])).netloc}"
        == origin
    ]
    evidence: dict[str, JSON] = {}
    for number, findings in HISTORICAL[origin].items():
        evidence[number] = {
            "kind": "historical_observation_or_scoped_claim",
            "ids": [f"{origin}/{finding}" for finding in findings],
            "boundary": "See this site's report and original evidence; narrow observations or attributed claims, not whole-guideline conformance.",
        }
    if pages:
        for number, boundary in {
            "3.6": "Language and landmark/H1 observations only; semantic appropriateness and accessible task success require review.",
            "3.8": "Titles, canonical/description fields, and JSON-LD syntax only; relevance, correctness, and reuse are not established.",
            "3.9": "CSS query inventory and dark/reduced-motion snapshots; no energy saving or comprehensive preference support established.",
        }.items():
            evidence[number] = {
                "kind": "browser_observation",
                "ids": [p["id"] for p in pages],
                "boundary": boundary,
            }
    if site.get("files"):
        evidence["3.13"] = {
            "kind": "HTTP_observation",
            "ids": [f["id"] for f in site["files"]],
            "boundary": "Known paths plus declared manifest/icon alternatives. Retrieval and syntax do not establish all expected/beneficial-file criteria or applicability.",
        }
    missing = [
        p
        for p in site["pages"]
        if p["selectionReason"] == "error_recovery"
        and p.get("status") is not None
        and p.get("initial")
        and f"{urlsplit(p.get('finalUrl', p['url'])).scheme}://{urlsplit(p.get('finalUrl', p['url'])).netloc}"
        == origin
    ]
    if missing:
        evidence["4.4"] = {
            "kind": "browser_observation",
            "ids": [p["id"] for p in missing],
            "boundary": "Missing-path response and DOM snapshot; recovery affordances require review, with no completed search recovery or redirect inventory.",
        }
    for suffix, number, boundary in [
        (
            "/privacy/",
            "5.18",
            "Public privacy statement, not verified retention, deletion, or processing behavior.",
        ),
        (
            "/sustainability/",
            "2.1",
            "Public impact discussion, not evidence of all impact-management practices.",
        ),
        (
            "/digital-emissions/",
            "3.1",
            "Published measurement/monitoring approach, not verified performance budgets or continuous execution.",
        ),
    ]:
        matches = [
            p for p in pages if urlsplit(p.get("finalUrl", p["url"])).path == suffix
        ]
        if matches:
            evidence[number] = {
                "kind": "candidate_public_statement",
                "ids": [p["id"] for p in matches],
                "boundary": "Requires semantic review of the document. " + boundary,
            }
    licenses = [
        f
        for f in site.get("sourceCorroboration", {}).get("files", [])
        if f["path"] == "LICENSE"
    ]
    if licenses:
        evidence["5.25"] = {
            "kind": "supplied_source",
            "ids": [f["id"] for f in licenses],
            "boundary": "Repository license and contribution context; not a full assessment of organizational open-source practice.",
        }
    rows = [
        {
            "number": g["number"],
            "title": g["title"],
            "url": g["url"],
            "status": "partial_evidence" if g["number"] in evidence else "not_assessed",
            "evidence": evidence.get(g["number"]),
            "conformance": "not_determined",
        }
        for g in guidelines
    ]
    return {
        "schemaVersion": "0.1.0",
        "site": origin,
        "sourceSHA256": digest,
        "scope": "Per-site evidence register, not a criterion-level assessment or conformance score",
        "counts": {
            "guidelines": len(rows),
            "partialEvidence": len(evidence),
            "notAssessed": len(rows) - len(evidence),
            "passed": None,
            "failed": None,
        },
        "sampling": {
            "advertisedURLCount": site["advertisedURLCount"],
            "attemptedPageURLs": len(site["pages"]),
            "successfulPageURLs": len(pages),
            "stateSnapshots": sum(
                key in page
                for page in site["pages"]
                for key in ["initial", "preferences", "preferencesAfterReload"]
            ),
            "selection": site["selection"],
            "inventoryMeaning": site["inventoryMeaning"],
        },
        "guidelines": rows,
    }


def main() -> None:
    """Write one register per origin from the completed scope extension."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "docs/initial-implementation/assets/scope-extension.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "docs/initial-implementation/assets/coverage",
    )
    args = parser.parse_args()
    raw = args.input.read_bytes()
    source = json.loads(raw)
    registry_path = ROOT / "docs/initial-implementation/assets/wsg-review-coverage.json"
    registry_raw = registry_path.read_bytes()
    registry = json.loads(registry_raw)
    guidelines = registry["guidelines"]
    args.output.mkdir(parents=True, exist_ok=True)
    for site in source["sites"]:
        result = register(site, guidelines, hashlib.sha256(raw).hexdigest())
        result["guidelineSource"] = {
            "url": registry["source"],
            "version": registry["sourceVersion"],
            "sourceSHA256": registry["sourceSHA256"],
            "registrySHA256": hashlib.sha256(registry_raw).hexdigest(),
        }
        name = f"{urlsplit(site['site']).hostname}-{hashlib.sha256(site['site'].encode()).hexdigest()[:12]}"
        (args.output / f"{name}.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
