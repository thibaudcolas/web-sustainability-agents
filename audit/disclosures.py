#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = []
# [tool.uv]
# required-version = ">=0.12.20,<0.13"
# ///
"""Turn collected carbon.txt declarations into scoped, evidence-linked review inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

JSON = dict[str, Any]
ROOT = Path(__file__).resolve().parent.parent


def http_url(value: Any) -> bool:
    """Recognize usable HTTP URLs without treating them as trusted evidence."""
    if not isinstance(value, str):
        return False
    try:
        parts = urlsplit(value)
        _ = parts.port
        return parts.scheme in {"https", "http"} and bool(parts.hostname)
    except ValueError:
        return False


def validity(value: Any, captured_at: str) -> str:
    """Compare a declared validity date to capture time, preserving unknown values."""
    if value is None:
        return "not_declared"
    try:
        valid = date.fromisoformat(str(value))
        captured = datetime.fromisoformat(captured_at.replace("Z", "+00:00")).date()
    except ValueError:
        return "unrecognized_date"
    return "past_declared_validity" if valid < captured else "within_declared_validity"


def interpret(parsed: JSON, site: str, captured_at: str) -> JSON:
    """Normalize declarations without certifying schema, hosting, or implementation."""
    issues: list[str] = []
    org = parsed.get("org")
    if not isinstance(org, dict):
        issues.append("org must be a table")
        org = {}
    disclosures = org.get("disclosures")
    if not isinstance(disclosures, list) or not disclosures:
        issues.append("No nonempty org.disclosures array")
        disclosures = []
    version = parsed.get("version")
    if not isinstance(version, str):
        issues.append("Missing string version declaration")
    schemes = org.get("certification_schemes", [])
    if not isinstance(schemes, list):
        issues.append("org.certification_schemes is not an array")
        schemes = []
    scheme_ids = {
        entry.get("id")
        for entry in schemes
        if isinstance(entry, dict) and isinstance(entry.get("id"), str)
    }
    normalized = []
    for index, entry in enumerate(disclosures):
        if not isinstance(entry, dict):
            issues.append(f"org.disclosures[{index}] is not a table")
            continue
        url = entry.get("url")
        if not http_url(url):
            issues.append(f"org.disclosures[{index}].url is not an HTTP(S) URL")
        if not isinstance(entry.get("doc_type"), str):
            issues.append(f"org.disclosures[{index}] lacks string doc_type")
        domain = entry.get("domain")
        scope = (
            "not_declared"
            if domain is None
            else "exact_host_match"
            if isinstance(domain, str)
            and domain.lower().rstrip(".") == urlsplit(site).hostname
            else "different_or_invalid_declared_host"
        )
        references = entry.get("certification_schemes", [])
        if not isinstance(references, list):
            references = []
            issues.append(
                f"org.disclosures[{index}].certification_schemes is not an array"
            )
        unresolved = [
            item
            for item in references
            if not isinstance(item, str) or item not in scheme_ids
        ]
        normalized.append(
            {
                "pointer": f"/org/disclosures/{index}",
                "declaration": entry,
                "usableUrl": http_url(url),
                "domainScope": scope,
                "validityAtCapture": validity(entry.get("valid_until"), captured_at),
                "unresolvedCertificationReferences": unresolved,
                "claimsVerified": False,
                "interpretation": "Review document organization, audited service, method, period, and supporting evidence. A historical report remains historical evidence after its declared validity ends.",
            }
        )
    upstream = parsed.get("upstream", {})
    services = upstream.get("services", []) if isinstance(upstream, dict) else []
    if not isinstance(services, list):
        issues.append("upstream.services is not an array")
        services = []
    providers = [
        {
            "pointer": f"/upstream/services/{index}",
            "declaration": entry,
            "relationshipStatus": "self_declared",
            "greenHostingVerified": False,
        }
        for index, entry in enumerate(services)
        if isinstance(entry, dict)
    ]
    return {
        "schemaVersion": "carbon-review-v1",
        "declaredVersion": version,
        "interpretationProfile": "v0.x common fields; unknown versions retained without schema conformance claims",
        "syntaxReference": "https://carbontxt.org/syntax",
        "schemaValidated": False,
        "structuralIssues": issues,
        "disclosures": normalized,
        "providers": providers,
        "certificationSchemes": schemes,
        "hostingModelInput": "unchanged; self-declaration alone does not select renewable electricity in SWDM",
        "reviewQuestions": [
            "Which declarations cover this exact origin and service rather than its parent organization?",
            "Do document methods, periods, boundaries, and arithmetic support the reported footprint?",
            "Which declared provider serves the origin, CDN, storage, or build system, and what independent evidence supports its energy claim?",
            "Are certification references and historical reports applicable to the current claim?",
        ],
    }


def summarize(discovery: JSON) -> JSON:
    """Connect declarations to discovery attempts and retrieved documents."""
    attempts = discovery.get("carbonAttempts", [])
    documents = discovery.get("documents", [])
    records = []
    for index, attempt in enumerate(attempts):
        parsed = attempt.get("declarations")
        if not isinstance(parsed, dict):
            continue
        review = interpret(parsed, discovery["site"], attempt.get("capturedAt", ""))
        for disclosure in review["disclosures"]:
            url = disclosure["declaration"].get("url")
            matches = [
                {
                    "pointer": f"/documents/{j}",
                    "status": doc.get("status"),
                    "sha256": doc.get("sha256"),
                    "finalUrl": doc.get("finalUrl"),
                    "truncated": bool(doc.get("truncated")),
                    "textAvailable": bool(doc.get("textExcerpt")),
                }
                for j, doc in enumerate(documents)
                if url and url in {doc.get("url"), doc.get("finalUrl")}
            ]
            disclosure["retrievalEvidence"] = matches
            disclosure["retrievalStatus"] = (
                "retrieved_within_discovery_scope" if matches else "not_retrieved"
            )
        records.append(
            {
                "pointer": f"/carbonAttempts/{index}",
                "url": attempt.get("url"),
                "finalUrl": attempt.get("finalUrl"),
                "discoveredVia": attempt.get(
                    "discoveredVia",
                    "location retained; route not recorded in legacy capture",
                ),
                "sha256": attempt.get("sha256"),
                "capturedAt": attempt.get("capturedAt"),
                "review": review,
            }
        )
    present = any(
        any(
            key in attempt.get("declarations", {})
            for key in ("version", "org", "upstream")
        )
        for attempt in attempts
    )
    return {
        "site": discovery["site"],
        "presence": "present" if present else "not_established_within_discovery_scope",
        "records": records,
        "documentCount": len(documents),
        "claimsVerified": False,
        "scopeNote": "Presence, parseability, declared relationships, retrieval, and substantiation are separate results. Missing carbon.txt does not establish absence of a sustainability policy.",
    }


def main() -> None:
    """Export a derived review artifact without modifying source observations."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Staged collector JSON containing discovery",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.input.read_text())
    result = {
        "schemaVersion": "carbon-review-v1",
        "sourceSHA256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
        "scriptSHA256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "sites": [summarize(entry) for entry in data["discovery"]],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, default=str) + "\n")


if __name__ == "__main__":
    main()
