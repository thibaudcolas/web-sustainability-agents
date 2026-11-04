#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = []
# [tool.uv]
# required-version = ">=0.12.20,<0.13"
# ///
"""Prepare bounded native-agent review tasks and validate their durable handoffs."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

# Direct uv script execution starts with audit/ on the import path.
if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from audit.workflow import (  # noqa: E402 # ty: ignore[unresolved-import]
    validate_frozen_files,
)

JSON = dict[str, Any]
ROLES = {
    "evidence": (
        "sustainability-evidence-review",
        "Identify measurement errors, unsupported numeric interpretations, phase confusion and incomplete evidence. Return issues; do not invent guideline outcomes or scores.",
    ),
    "guidelines": (
        "sustainability-guideline-review",
        "Review every selected check using review-template.json and the frozen rubric. Return a complete review object, including useful top findings; do not calculate a score.",
    ),
    "claims": (
        "sustainability-claims-review",
        "Check disclosures, footprint assumptions, source corroboration and recommendation prerequisites. Return issues; distinguish unknown practice from absent documentation.",
    ),
}


def read(path: Path) -> JSON:
    """Load an object from a durable artifact."""
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError("Expected an object")
    return value


def digest(path: Path) -> str:
    """Identify the exact bytes supplied to a worker."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: JSON) -> None:
    """Persist an artifact without overwriting a previous handoff."""
    if path.exists():
        raise ValueError(f"Refusing to replace {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def tasks(session: Path, output: Path, mode: str) -> None:
    """Generate three bounded review contracts on one immutable evidence packet."""
    if output.exists():
        raise ValueError("Choose a new task directory")
    packet = read(session / "packet.json")
    validate_frozen_files(session, packet)
    output.mkdir(parents=True, mode=0o700)
    for role, (skill, instruction) in ROLES.items():
        write(
            output / f"{role}.task.json",
            {
                "schemaVersion": "1.0",
                "role": role,
                "site": packet["site"],
                "session": str(session.resolve()),
                "packetSHA256": digest(session / "packet.json"),
                "executionMode": mode,
                "skill": str(session.resolve() / "skills" / skill / "SKILL.md"),
                "supportingSkills": [
                    str(
                        session.resolve()
                        / "skills/sustainability-context-review/SKILL.md"
                    )
                ]
                if role in {"guidelines", "claims"}
                and any(
                    row.get("method") == "qualitative-context-review"
                    for row in packet["checks"]
                )
                else [],
                "instruction": instruction
                + " Load any supportingSkills listed in this task before judging contextual records.",
                "output": str(output.resolve() / f"{role}.result.json"),
                "checkIds": [row["id"] for row in packet["checks"]],
                "modelPolicy": {"gpt-6.1-sol": "high", "deepseek-v4.1-flash": "high"},
                "contract": "guidelines: original review-template.json shape; evidence/claims: {role, site, packetSHA256, reviewer:{harness,model,reasoning}, issues:[{id,checkIds,evidenceIds,summary,requestedChange}]}. Every issue needs real check/evidence IDs. No additional browsing or mutable source access; request missing evidence through the coordinator.",
            },
        )


def validate(task: JSON, result: JSON) -> None:
    """Check identity, recorded settings, check ownership and evidence references."""
    session = Path(task["session"])
    packet = read(session / "packet.json")
    validate_frozen_files(session, packet)
    if task["packetSHA256"] != digest(session / "packet.json"):
        raise ValueError("Task packet changed")
    if (
        result.get("site") != task["site"]
        or result.get("packetSHA256") != task["packetSHA256"]
    ):
        raise ValueError("Worker returned a different site or packet")
    settings = result.get("reviewer", {})
    if not all(
        isinstance(settings.get(k), str) and settings[k].strip()
        for k in ("harness", "model", "reasoning")
    ):
        raise ValueError("Record actual reviewer settings")
    if (
        any(model in settings["model"].lower() for model in task["modelPolicy"])
        and settings["reasoning"] != "high"
    ):
        raise ValueError("This task requires high reasoning")
    check_ids = set(task["checkIds"])
    evidence_ids = set(packet["evidenceIndex"])
    if task["role"] == "guidelines":
        rows = result.get("rows", [])
        if (
            len(rows) != len(check_ids)
            or {row.get("checkId") for row in rows} != check_ids
        ):
            raise ValueError(
                "Guideline reviewer must cover every selected check exactly once"
            )
        mapping = {row["id"]: row["guideline"] for row in packet["checks"]}
        for row in rows:
            if row.get("guideline") != mapping[row["checkId"]] or row.get(
                "outcome"
            ) not in {"pass", "fail", "cantTell", "inapplicable", "untested"}:
                raise ValueError("Invalid check mapping or outcome")
            if row["outcome"] in {"pass", "fail"} and not row.get("evidenceIds"):
                raise ValueError("Passing or failing judgments need evidence")
            if not set(row.get("evidenceIds", [])).issubset(evidence_ids):
                raise ValueError("Invented evidence reference")
    else:
        if result.get("role") != task["role"] or not isinstance(
            result.get("issues"), list
        ):
            raise ValueError("Return the assigned role and an issues list")
        seen = set()
        for issue in result["issues"]:
            if (
                not isinstance(issue.get("id"), str)
                or not issue["id"]
                or issue["id"] in seen
            ):
                raise ValueError("Use unique issue IDs")
            seen.add(issue["id"])
            if not issue.get("checkIds") or not set(issue["checkIds"]).issubset(
                check_ids
            ):
                raise ValueError("Issue must identify assigned checks")
            if not issue.get("evidenceIds") or not set(issue["evidenceIds"]).issubset(
                evidence_ids
            ):
                raise ValueError("Issue must cite actual evidence")
            if not issue.get("summary") or not issue.get("requestedChange"):
                raise ValueError(
                    "Issue must explain the concern and requested resolution"
                )


def accept(task_path: Path) -> None:
    """Validate a result and freeze its acceptance receipt."""
    task = read(task_path)
    result_path = Path(task["output"])
    result = read(result_path)
    validate(task, result)
    write(
        task_path.with_name(f"{task['role']}.accepted.json"),
        {
            "role": task["role"],
            "taskSHA256": digest(task_path),
            "resultSHA256": digest(result_path),
            "packetSHA256": task["packetSHA256"],
            "executionMode": task["executionMode"],
        },
    )


def status(directory: Path) -> JSON:
    """Report validated handoffs rather than mistaking a file's presence for success."""
    records = []
    for task_path in sorted(directory.glob("*.task.json")):
        task = read(task_path)
        session = Path(task["session"])
        if task["packetSHA256"] != digest(session / "packet.json"):
            raise ValueError("Task packet changed")
        validate_frozen_files(session, read(session / "packet.json"))
        receipt_path = directory / f"{task['role']}.accepted.json"
        state = "pending"
        if Path(task["output"]).exists():
            state = "needs-validation"
        if receipt_path.exists() and not Path(task["output"]).exists():
            state = "missing-after-validation"
        elif receipt_path.exists():
            receipt = read(receipt_path)
            if receipt["taskSHA256"] != digest(task_path) or receipt[
                "resultSHA256"
            ] != digest(Path(task["output"])):
                state = "changed-after-validation"
            else:
                validate(task, read(Path(task["output"])))
                state = "accepted"
        records.append({"role": task["role"], "state": state, "task": str(task_path)})
    return {
        "roles": records,
        "readyForReconciliation": len(records) == len(ROLES)
        and all(row["state"] == "accepted" for row in records),
    }


def reconcile(directory: Path, resolutions_path: Path) -> None:
    """Require an explicit coordinator response to every advisor issue."""
    if not status(directory)["readyForReconciliation"]:
        raise ValueError("Accept all worker handoffs first")
    required: set[str] = set()
    for role in ("evidence", "claims"):
        result = read(directory / f"{role}.result.json")
        required.update(f"{role}:{issue['id']}" for issue in result["issues"])
    resolutions = read(resolutions_path)
    rows = resolutions.get("resolutions", [])
    if len(rows) != len(required) or {row.get("issue") for row in rows} != required:
        raise ValueError("Resolve every advisor issue exactly once")
    if any(
        row.get("decision")
        not in {"applied", "retained-with-reason", "needs-new-evidence"}
        or not row.get("reason")
        for row in rows
    ):
        raise ValueError("Explain each resolution and remaining evidence gap")
    write(
        directory / "reconciliation.accepted.json",
        {
            "resolutionsSHA256": digest(resolutions_path),
            "acceptedSHA256": {
                role: digest(directory / f"{role}.accepted.json") for role in ROLES
            },
            "next": "Coordinator writes review.json, preserving unresolved evidence; workflow score validates the final review. This receipt validates coverage of responses, not their semantic correctness.",
        },
    )


def main() -> None:
    """Expose portable review contracts to the host agent without another model runtime."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    dispatch = commands.add_parser("tasks")
    dispatch.add_argument("--session", type=Path, required=True)
    dispatch.add_argument("--output", type=Path, required=True)
    dispatch.add_argument(
        "--mode", choices=["native-subagents", "sequential"], required=True
    )
    accepted = commands.add_parser("accept")
    accepted.add_argument("--task", type=Path, required=True)
    progress = commands.add_parser("status")
    progress.add_argument("--tasks", type=Path, required=True)
    merge = commands.add_parser("reconcile")
    merge.add_argument("--tasks", type=Path, required=True)
    merge.add_argument("--resolutions", type=Path, required=True)
    args = parser.parse_args()
    if args.action == "tasks":
        tasks(args.session.resolve(), args.output.resolve(), args.mode)
    elif args.action == "accept":
        accept(args.task.resolve())
    elif args.action == "status":
        print(json.dumps(status(args.tasks.resolve()), indent=2))  # noqa: T201
    else:
        reconcile(args.tasks.resolve(), args.resolutions.resolve())


if __name__ == "__main__":
    main()
