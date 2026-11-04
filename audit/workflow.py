#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = []
# [tool.uv]
# required-version = ">=0.12.20,<0.13"
# ///
"""Create, collect, and score portable per-site audit sessions triggered by agents."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
JSON = dict[str, Any]
DISCLOSURE_CHECKS = [
    {
        "id": "disclosure-scope",
        "guideline": "2.1",
        "expectation": "A retrieved public sustainability statement identifies the audited service and describes its impacts and mitigation. Judge disclosure only, not execution; an unresolved relationship is cantTell.",
    },
    {
        "id": "carbon-discovery",
        "guideline": "3.13",
        "expectation": "The sampled service exposes a discoverable, parseable carbon.txt with usable declared relationships. Missing carbon.txt is a scoped absence, not proof of high emissions or failure of the entire guideline. Judge redirects, delegation, supported versions and schema findings explicitly.",
    },
    {
        "id": "hosting-evidence",
        "guideline": "4.1",
        "expectation": "Hosting claims identify provider, service and supporting evidence with a relationship to this origin. Self-declaration without independently corroborated operational scope remains cantTell for sustainable hosting; do not set SWDM green-hosting flags from this check.",
    },
]


def read(path: Path) -> JSON:
    """Read a JSON object."""
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object: {path}")
    return value


def digest(path: Path) -> str:
    """Hash exact artifact bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: JSON) -> None:
    """Write private session data with stable JSON formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(mode=0o600, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def origin_of(url: str) -> str:
    """Validate an HTTP URL without embedded credentials."""
    parsed = urlsplit(url)
    _ = parsed.port
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username
        or parsed.password
    ):
        raise ValueError("Use an HTTP(S) URL without credentials")
    return f"{parsed.scheme}://{parsed.netloc}"


def validate_plan(plan: JSON) -> None:
    """Reject ambiguous site scope and unsupported interaction contracts."""
    origin = plan["origin"]
    if origin_of(origin) != origin or not plan.get("purpose", "").strip():
        raise ValueError("Use one exact origin and a nonempty audit purpose")
    pages = plan["pages"]
    if not isinstance(pages, list) or not 1 <= len(pages) <= 20:
        raise ValueError("Select 1–20 pages per bounded campaign")
    identifiers: set[str] = set()
    journeys = plan.get("journeys", [])
    if not isinstance(journeys, list) or len(journeys) > 10:
        raise ValueError("Select at most 10 journeys")
    for target in pages + journeys:
        if (
            not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", target["id"])
            or target["id"] in identifiers
        ):
            raise ValueError("Use unique stable page/journey IDs")
        identifiers.add(target["id"])
        if origin_of(target["url"]) != origin:
            raise ValueError("Every starting URL must match the audit origin")
        if not target.get("task", "").strip():
            raise ValueError("Name the visitor task for each selected page/journey")
        validate_actions(target.get("actions", []), {"click", "fill", "press"})
    for page in pages:
        if "actions" in page:
            raise ValueError("Page interactions belong in branches[].actions")
        branches = page.get("branches", [{"name": "no_banner", "actions": []}])
        if not branches or len(branches) > 4:
            raise ValueError("Choose 1–4 explicit consent branches")
        names = [branch.get("name") for branch in branches]
        if any(not isinstance(name, str) or not name for name in names) or len(
            set(names)
        ) != len(names):
            raise ValueError("Consent branches require unique names")
        for branch in branches:
            validate_actions(
                branch.get("actions", []), {"click", "fill", "press", "check", "select"}
            )
    if any(
        question.get("required") and not question.get("answer")
        for question in plan.get("questions", [])
    ):
        raise ValueError("Resolve required scope questions before collecting")
    if not isinstance(plan.get("checks", []), list):
        raise ValueError(
            "checks must be a list of check IDs; empty selects the catalog"
        )
    validate_context(plan)
    validate_energy(plan)


def validate_energy(plan: JSON) -> None:
    """Require a bounded planned energy sample and explicit execution mode."""
    settings = plan.get("energy", {})
    if not isinstance(settings, dict):
        raise ValueError("energy must be an object")
    if settings.get("mode", "readiness") not in {"readiness", "run", "skip"}:
        raise ValueError("Use energy mode readiness, run or skip")
    samples = settings.get("samples", 3)
    if (
        isinstance(samples, bool)
        or not isinstance(samples, int)
        or not 2 <= samples <= 10
    ):
        raise ValueError("Use 2–10 complete energy repetitions")
    pages = settings.get("pageIds", [])
    if (
        not isinstance(pages, list)
        or len(pages) > 3
        or not all(isinstance(item, str) for item in pages)
        or len(set(pages)) != len(pages)
        or set(pages) - {page["id"] for page in plan["pages"]}
    ):
        raise ValueError("Select up to three unique planned energy page IDs")


def validate_context(plan: JSON) -> None:
    """Validate explicit qualitative scope and attributed, pre-collected records."""
    checks = plan.get("contextChecks", [])
    known = {item["id"] for item in read(ROOT / "audit/context-checks.json")["checks"]}
    if (
        not isinstance(checks, list)
        or not all(isinstance(item, str) for item in checks)
        or len(set(checks)) != len(checks)
        or set(checks) - known
    ):
        raise ValueError("contextChecks must select unique contextual check IDs")
    records = plan.get("contextEvidence", [])
    if not isinstance(records, list) or len(records) > 30:
        raise ValueError("Select at most 30 contextual evidence records")
    selected = set(checks) | (set(plan.get("checks", [])) & known)
    identifiers: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Context evidence must be an attributed record")
        identifier = record.get("id", "")
        if (
            not isinstance(identifier, str)
            or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", identifier)
            or identifier in identifiers
        ):
            raise ValueError("Use unique stable contextual evidence IDs")
        identifiers.add(identifier)
        if record.get("kind") not in {
            "public-document",
            "owner-record",
            "task-observation",
        }:
            raise ValueError("Declare the contextual evidence kind")
        for key in ("path", "source", "scope", "capturedAt", "limitations"):
            if not isinstance(record.get(key), str) or not record[key].strip():
                raise ValueError(f"Context evidence requires {key}")
        if not Path(record["path"]).is_absolute():
            raise ValueError("Context evidence paths must be absolute")
        try:
            timestamp = datetime.fromisoformat(record["capturedAt"])
        except ValueError as error:
            raise ValueError("Use an ISO contextual capture timestamp") from error
        if timestamp.tzinfo is None:
            raise ValueError("Context capture timestamps require a timezone")
        check_ids = record.get("checkIds", [])
        if (
            not isinstance(check_ids, list)
            or not check_ids
            or not all(isinstance(item, str) for item in check_ids)
            or len(set(check_ids)) != len(check_ids)
            or set(check_ids) - selected
        ):
            raise ValueError(
                "Context evidence must identify selected contextual checks"
            )


def selected_checks(definitions: list[JSON], plan: JSON) -> list[JSON]:
    """Preserve v2 defaults while allowing the setup skill to select context."""
    requested = plan.get("checks") or [
        item["id"]
        for item in definitions
        if not item.get("optional")
        and (not item.get("requiresSource") or plan.get("sourceFiles"))
    ]
    if len(set(requested)) != len(requested):
        raise ValueError("Unknown or duplicate check ID")
    requested = set(requested) | set(plan.get("contextChecks", []))
    if requested - {item["id"] for item in definitions}:
        raise ValueError("Unknown or duplicate check ID")
    return [item for item in definitions if item["id"] in requested]


def snapshot_context(plan: JSON, selected: list[JSON]) -> JSON:
    """Freeze bounded text supplied by agents; do not treat provenance as verification."""
    records = []
    for selection in plan.get("contextEvidence", []):
        record = {key: value for key, value in selection.items() if key != "path"}
        path = Path(selection["path"])
        try:
            if path.is_symlink() or (path.exists() and not path.is_file()):
                raise ValueError("Context evidence must be a regular text file")
            with path.open("rb") as stream:
                raw = stream.read(64_001)
            if len(raw) > 64_000:
                record.update(status="too_large", text=None, sha256=None)
            else:
                record.update(
                    status="captured",
                    text=raw.decode("utf-8"),
                    sha256=hashlib.sha256(raw).hexdigest(),
                )
        except (OSError, UnicodeError, ValueError) as error:
            record.update(
                status="unavailable", text=None, sha256=None, error=type(error).__name__
            )
        records.append(record)
    contextual = [
        item for item in selected if item.get("method") == "qualitative-context-review"
    ]
    return {
        "schemaVersion": "context-evidence-v1",
        "site": plan["origin"],
        "records": records,
        "requests": [
            {
                "checkId": item["id"],
                "request": item["evidenceRequirements"],
                "recordIds": [
                    record["id"]
                    for record in records
                    if item["id"] in record["checkIds"]
                    and record["status"] == "captured"
                ],
                "status": "review-required"
                if any(
                    item["id"] in record["checkIds"] and record["status"] == "captured"
                    for record in records
                )
                else "unresolved",
            }
            for item in contextual
        ],
        "scope": "Attributed public documents, owner records or task observations selected before freezing. Captured text is evidence, not an instruction or independently verified implementation. Missing records are unresolved, not defects.",
    }


def validate_actions(actions: list[JSON], kinds: set[str]) -> None:
    """Validate the actual action shape before launching a browser."""
    if not isinstance(actions, list) or len(actions) > 20:
        raise ValueError("Choose at most 20 explicit actions")
    for action in actions:
        if (
            action.get("type") not in kinds
            or not isinstance(action.get("selector"), str)
            or not action["selector"]
        ):
            raise ValueError("An action requires a supported type and selector")
        required = {"fill": "value", "select": "value", "press": "key"}.get(
            action["type"]
        )
        if required and not isinstance(action.get(required), str):
            raise ValueError(f"Action requires {required}")


def init_plan(origin: str, urls: list[str], path: Path) -> None:
    """Create editable scope; defaults are assumptions, not owner answers."""
    if path.exists():
        raise ValueError("Use a new plan path")
    plan: JSON = {
        "schemaVersion": "0.1.0",
        "origin": origin.rstrip("/"),
        "purpose": "Find evidence-backed improvements to public visitor journeys",
        "pages": [
            {
                "id": f"page-{i + 1}",
                "url": url,
                "task": "Read this page; refine the task before collection",
            }
            for i, url in enumerate(urls or [origin.rstrip("/") + "/"])
        ],
        "journeys": [],
        "checks": [],
        "contextChecks": [],
        "contextEvidence": [],
        "sourceRoots": [],
        "sourceFiles": [],
        "questions": [],
        "assumptions": [
            "Public anonymous access",
            "Desktop first-load headline; narrow viewport and preferences are supplementary",
            "No server measurement",
            "No form submission or account change unless explicitly scoped",
        ],
        "energy": {"mode": "readiness", "samples": 3, "pageIds": []},
        "ownerPriorities": [],
    }
    validate_plan(plan)
    write(path, plan)


def run_command(argv: list[str], session: Path, name: str) -> JSON:
    """Record exact commands, versions and exits without recording environment secrets."""
    started = datetime.now(UTC).isoformat()
    result = subprocess.run(  # noqa: S603
        argv, cwd=ROOT, capture_output=True, text=True, timeout=3600, check=False
    )  # noqa: S603
    (session / f"{name}.stdout.txt").write_text(result.stdout)
    (session / f"{name}.stderr.txt").write_text(result.stderr)
    return {
        "argv": argv,
        "cwd": str(ROOT),
        "startedAt": started,
        "finishedAt": datetime.now(UTC).isoformat(),
        "exitCode": result.returncode,
        "logs": [f"{name}.stdout.txt", f"{name}.stderr.txt"],
    }


def catalog() -> list[JSON]:
    """Load the versioned public-browser and disclosure expectations."""
    return [
        *read(ROOT / "audit/probe-checks.json")["checks"],
        *DISCLOSURE_CHECKS,
        *read(ROOT / "audit/source-checks.json")["checks"],
        *read(ROOT / "audit/context-checks.json")["checks"],
    ]


def prepare_packet(session: Path, plan: JSON) -> None:
    """Freeze selected expectations, source digests and resolvable evidence locations."""
    definitions = read(session / "checks.json")["checks"]
    selected = selected_checks(definitions, plan)
    rubric = read(session / "base-rubric.json")
    has_context = any(
        item.get("method") == "qualitative-context-review" for item in selected
    )
    rubric["rubricVersion"] = "agent-breadth-v3" if has_context else "agent-breadth-v2"
    for guideline in rubric["guidelines"]:
        checks = [item for item in selected if item["guideline"] == guideline["number"]]
        guideline["expectation"] = (
            " ".join(item["expectation"] for item in checks) or None
        )
        guideline["role"] = "agent-review" if checks else "unsupported"
    write(session / "rubric.json", rubric)
    sources: dict[str, str] = {}
    index: JSON = {}
    for name, arrays in [
        ("staged.json", ["runs", "discovery"]),
        ("probes.json", ["pages", "journeys"]),
        ("disclosures.json", ["sites"]),
        ("source.json", ["files"]),
        ("context.json", ["records"]),
        ("energy/manifest.json", ["pages"]),
    ]:
        path = session / name
        if not path.exists():
            continue
        sources[name] = digest(path)
        data = read(path)
        for key in arrays:
            for i, _ in enumerate(data.get(key, [])):
                index[f"{name}:{key}:{i}"] = {
                    "artifact": name,
                    "jsonPointer": f"/{key}/{i}",
                    "sourceSHA256": sources[name],
                }
    write(
        session / "packet.json",
        {
            "schemaVersion": "0.1.0",
            "site": plan["origin"],
            "planSHA256": digest(session / "plan.json"),
            "rubricSHA256": digest(session / "rubric.json"),
            "sourceSHA256": sources,
            "frozenFiles": {
                str(path.relative_to(session)): digest(path)
                for path in [
                    session / name
                    for name in [
                        "plan.json",
                        "receipt.json",
                        "checks.json",
                        "base-rubric.json",
                        "rubric.json",
                        "impact-weights.json",
                    ]
                ]
                + sorted((session / "skills").rglob("*"))
                + sorted((session / "energy").rglob("*"))
                if path.is_file()
            },
            "checks": selected,
            "methodologyCoverage": {
                "meaning": "Defined partial review methods, not executed checks or full-guideline conformance",
                "catalogChecks": len(definitions),
                "catalogGuidelineGroups": len(
                    {item["guideline"] for item in definitions}
                ),
                "catalogPartialGuidelineGroups": len(
                    {item["guideline"] for item in definitions}
                ),
                "catalogFullGuidelineGroups": 0,
                "selectedChecks": len(selected),
                "selectedGuidelineGroups": len(
                    {item["guideline"] for item in selected}
                ),
                "selectedPartialGuidelineGroups": len(
                    {item["guideline"] for item in selected}
                ),
                "selectedFullGuidelineGroups": 0,
                "totalWSGGuidelines": len(rubric["guidelines"]),
            },
            "evidenceIndex": index,
            "collectionReceipt": "receipt.json",
            "skillSnapshot": "skills",
            "reviewContract": "One row per check ID: checkId, guideline, outcome, evidenceIds, rationale, confidence, nextEvidence. Outcomes pass/fail/cantTell/inapplicable/untested. Cite actual packet evidence IDs and specific observations. Supply reviewer object with harness, model, reasoning. Explicitly explain applicability and unresolved evidence. Do not score yourself.",
        },
    )
    write(
        session / "review-template.json",
        {
            "site": plan["origin"],
            "packetSHA256": digest(session / "packet.json"),
            "reviewer": {"harness": "", "model": "", "reasoning": ""},
            "rows": [
                {
                    "checkId": item["id"],
                    "guideline": item["guideline"],
                    "outcome": "untested",
                    "evidenceIds": [],
                    "rationale": "This check has not been reviewed yet.",
                    "confidence": "unknown",
                    "nextEvidence": "Apply the scoped check to the cited evidence.",
                }
                for item in selected
            ],
        },
    )


def collect(
    plan_path: Path,
    session: Path,
    energy: str | None = None,
    greenframe_binary: str = "greenframe",
) -> None:
    """Run collectors sequentially and freeze a review bundle in a new directory."""
    plan = read(plan_path)
    validate_plan(plan)
    definitions = catalog()
    selected = selected_checks(definitions, plan)
    if session.exists():
        raise ValueError("Use a new session directory; evidence is immutable")
    session.mkdir(parents=True, mode=0o700)
    write(session / "plan.json", plan)
    write(session / "targets.json", {"targets": plan["pages"]})
    context_catalog = read(ROOT / "audit/context-checks.json")
    write(
        session / "checks.json",
        {
            "catalogVersion": "agent-breadth-v3",
            "componentVersions": {
                "browser": read(ROOT / "audit/probe-checks.json")["rubricVersion"],
                "source": read(ROOT / "audit/source-checks.json")["rubricVersion"],
                "context": context_catalog["rubricVersion"],
            },
            "wsgSourceVersion": context_catalog["wsgSourceVersion"],
            "wsgSourceSha256": context_catalog["wsgSourceSha256"],
            "checks": definitions,
        },
    )
    write(session / "context.json", snapshot_context(plan, selected))
    shutil.copyfile(ROOT / "audit/rubric.json", session / "base-rubric.json")
    shutil.copyfile(ROOT / "audit/impact-weights.json", session / "impact-weights.json")
    shutil.copytree(ROOT / ".agents/skills", session / "skills")
    shutil.copytree(ROOT / "skill-data/core", session / "skills/sustainability-core")
    scripts = [
        "cli.py",
        "orchestrate.py",
        "run.py",
        "probes.py",
        "workflow.py",
        "assess.py",
        "disclosures.py",
        "source.py",
        "greenframe.py",
    ]
    receipt: JSON = {
        "schemaVersion": "0.1.0",
        "executionStatus": "running",
        "commands": [],
        "sourceSHA256": {
            str(path.relative_to(ROOT)): digest(path)
            for name in scripts
            for path in [ROOT / "audit" / name, ROOT / "audit" / f"{name}.lock"]
            if path.exists()
        },
        "skillSHA256": {
            str(path.relative_to(session / "skills")): digest(path)
            for path in sorted((session / "skills").rglob("*"))
            if path.is_file()
        },
        "gitRevision": subprocess.run(
            ["git", "rev-parse", "HEAD"],  # noqa: S607
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip(),  # noqa: S603, S607
        "planSHA256": digest(session / "plan.json"),
        "limitations": [
            "Live responses and LLM judgments can vary",
            "Only selected sourceFiles are captured; source roots alone do not trigger a scan and deployment identity remains unknown",
            "Energy readiness is recorded by default; measurements require an explicit run mode and a quiet local workload window",
            "Inspect captured text and logs before publishing; the session is private",
        ],
    }
    for name, argv in [
        (
            "source",
            [
                "uv",
                "run",
                "--locked",
                "--script",
                "audit/source.py",
                "--plan",
                str(session / "plan.json"),
                "--output",
                str(session / "source.json"),
            ],
        ),
        (
            "staged",
            [
                "uv",
                "run",
                "--locked",
                "--script",
                "audit/run.py",
                "--targets",
                str(session / "targets.json"),
                "--output",
                str(session / "staged.json"),
            ],
        ),
        (
            "probes",
            [
                "uv",
                "run",
                "--locked",
                "--script",
                "audit/probes.py",
                "--plan",
                str(session / "plan.json"),
                "--output",
                str(session / "probes.json"),
            ],
        ),
        (
            "disclosures",
            [
                "uv",
                "run",
                "--locked",
                "--script",
                "audit/disclosures.py",
                "--input",
                str(session / "staged.json"),
                "--output",
                str(session / "disclosures.json"),
            ],
        ),
        (
            "energy",
            [
                "uv",
                "run",
                "--locked",
                "--script",
                "audit/greenframe.py",
                "--plan",
                str(session / "plan.json"),
                "--output-dir",
                str(session / "energy"),
                "--mode",
                energy or plan.get("energy", {}).get("mode", "readiness"),
                "--binary",
                greenframe_binary,
            ],
        ),
    ]:
        write(session / "receipt.json", receipt)
        try:
            receipt["commands"].append(run_command(argv, session, name))
        except subprocess.TimeoutExpired:
            receipt["commands"].append(
                {"argv": argv, "exitCode": None, "error": "Collector deadline exceeded"}
            )
    receipt["executionStatus"] = (
        "completed"
        if all(row["exitCode"] == 0 for row in receipt["commands"])
        else "completed_with_errors"
    )
    write(session / "receipt.json", receipt)
    prepare_packet(session, plan)


def validate_review(review: JSON, packet: JSON, packet_sha: str) -> None:
    """Reject missing checks, swapped sites, stale packets and unknown evidence."""
    if review.get("site") != packet["site"] or review.get("packetSHA256") != packet_sha:
        raise ValueError("Review must identify this exact site and packet")
    if not all(
        review.get("reviewer", {}).get(key) for key in ["harness", "model", "reasoning"]
    ):
        raise ValueError("Record harness, model and reasoning settings")
    expected = {item["id"]: item["guideline"] for item in packet["checks"]}
    rows = review["rows"]
    if len(rows) != len(expected) or {row["checkId"] for row in rows} != set(expected):
        raise ValueError("Return exactly one row for every selected check")
    for row in rows:
        if row["guideline"] != expected[row["checkId"]]:
            raise ValueError("Check mapped to the wrong guideline")
        if (
            not isinstance(row.get("nextEvidence"), str)
            or not row["nextEvidence"].strip()
        ):
            raise ValueError("Record next evidence or validation needed for each check")
        if any(
            identifier not in packet["evidenceIndex"]
            for identifier in row["evidenceIds"]
        ):
            raise ValueError("Unknown evidence identifier")


def score(session: Path, review_path: Path) -> None:
    """Validate agent output and use the existing deterministic aggregation contract."""
    packet = read(session / "packet.json")
    validate_frozen_files(session, packet)
    review = read(review_path)
    validate_review(review, packet, digest(session / "packet.json"))
    if (session / "scores.json").exists():
        raise ValueError("Session already scored; keep revisions in a new session")
    reviews = {
        "rubricSHA256": packet["rubricSHA256"],
        "sourceSHA256": packet["sourceSHA256"],
        "reviewFileSHA256": digest(review_path),
        "reviews": [{**review, "evidenceIndex": packet["evidenceIndex"]}],
    }
    write(session / "reviews.json", reviews)
    result = run_command(
        [
            "uv",
            "run",
            "--locked",
            "--script",
            "audit/assess.py",
            "--reviews",
            str(session / "reviews.json"),
            "--rubric",
            str(session / "rubric.json"),
            "--weights",
            str(session / "impact-weights.json"),
            "--assets",
            str(session),
            "--output",
            str(session / "scores.json"),
        ],
        session,
        "score",
    )
    result["scorerSHA256"] = digest(ROOT / "audit/assess.py")
    result["scorerLockSHA256"] = digest(ROOT / "audit/assess.py.lock")
    write(session / "score-receipt.json", result)
    if result["exitCode"]:
        raise ValueError("Score validation failed; inspect score.stderr.txt")


def validate_frozen_files(session: Path, packet: JSON) -> None:
    """Reject altered scope, weights, skill resources and scoring implementation."""
    required = {
        "plan.json",
        "receipt.json",
        "checks.json",
        "base-rubric.json",
        "rubric.json",
        "impact-weights.json",
    }
    frozen = packet.get("frozenFiles", {})
    if not required.issubset(frozen):
        raise ValueError("Packet does not pin required session provenance")
    for name, expected in [*frozen.items(), *packet.get("sourceSHA256", {}).items()]:
        path = (session / name).resolve()
        if (
            not path.is_relative_to(session.resolve())
            or not path.is_file()
            or digest(path) != expected
        ):
            raise ValueError(f"Frozen session file changed: {name}")
    receipt = read(session / "receipt.json")
    for name in ["audit/assess.py", "audit/assess.py.lock"]:
        if digest(ROOT / name) != receipt["sourceSHA256"].get(name):
            raise ValueError(
                "Scorer changed; create a new explicitly versioned review campaign"
            )


def main() -> None:
    """Dispatch explicit steps; agents own scope clarification and interpretation."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init")
    init.add_argument("--origin", required=True)
    init.add_argument("--page", action="append", default=[])
    init.add_argument("--plan", type=Path, required=True)
    gather = commands.add_parser("collect")
    gather.add_argument("--plan", type=Path, required=True)
    gather.add_argument("--session", type=Path, required=True)
    gather.add_argument("--energy", choices=["readiness", "run", "skip"])
    gather.add_argument("--greenframe-binary", default="greenframe")
    judge = commands.add_parser("score")
    judge.add_argument("--session", type=Path, required=True)
    judge.add_argument("--review", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "init":
        init_plan(args.origin, args.page, args.plan.resolve())
    elif args.command == "collect":
        collect(
            args.plan.resolve(),
            args.session.resolve(),
            args.energy,
            args.greenframe_binary,
        )
    else:
        score(args.session.resolve(), args.review.resolve())


if __name__ == "__main__":
    main()
