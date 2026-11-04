"""Validated presentation supplements for frozen sustainability audit reports."""

from __future__ import annotations

import hashlib
import html
import json
import math
import re
from pathlib import Path
from statistics import median
from typing import Any
from urllib.parse import quote, urlsplit

JSON = dict[str, Any]
AREAS = {
    "2": "User experience design",
    "3": "Web development",
    "4": "Hosting, infrastructure and systems",
    "5": "Business strategy and product management",
}


def area_results(guidelines: list[JSON]) -> list[JSON]:
    """Use the same conservative denominator as the overall scoped score."""
    results = []
    for section, title in AREAS.items():
        rows = [r for r in guidelines if r["number"].split(".")[0] == section]
        counts = {
            status: sum(r["outcome"] == status for r in rows)
            for status in ("pass", "fail", "cantTell", "untested", "inapplicable")
        }
        checked = counts["pass"] + counts["fail"] + counts["cantTell"]
        results.append(
            {
                "title": title,
                "total": len(rows),
                "checked": checked,
                "counts": counts,
                "percent": 100 * counts["pass"] / checked if checked else None,
            }
        )
    return results


def validate_presentation(data: JSON, review: JSON, review_sha: str) -> None:
    """Allow explicit editorial/priority revisions without changing scored outcomes."""
    if not data:
        return
    if (
        data.get("schemaVersion") != "report-presentation-v1"
        or data.get("site") != review["site"]
        or data.get("reviewSHA256") != review_sha
        or not data.get("reason")
    ):
        raise ValueError("Presentation supplement must identify its review and reason")
    ids = {r["checkId"] for r in review.get("topFindings", [])[:5]}
    order = data.get("findingOrder", list(ids))
    if len(order) != len(ids) or set(order) != ids:
        raise ValueError("Presentation order must retain all priority findings")
    for identifier, override in data.get("findingOverrides", {}).items():
        allowed = {"priority", "title", "summary", "whyItMatters", "action", "reason"}
        if set(override) - allowed or any(
            not isinstance(v, str) or not v.strip() for v in override.values()
        ):
            raise ValueError("Finding override contains unsupported or empty fields")
        if identifier not in ids or not override.get("reason"):
            raise ValueError("Finding override needs a known finding and rationale")
        if override.get("priority") not in {None, "low", "medium", "high"}:
            raise ValueError("Unsupported priority override")


def source_excerpt(session: Path, packet: JSON, spec: JSON) -> list[str]:
    """Show captured source text, linking current branch and immutable revision."""
    reference = packet["evidenceIndex"][spec["evidenceId"]]
    if reference["artifact"] != "source.json":
        raise ValueError("Source excerpt requires captured source evidence")
    parts = reference["jsonPointer"].strip("/").split("/")
    if len(parts) != 2 or parts[0] != "files":
        raise ValueError("Source excerpt must identify one captured file")
    item = json.loads((session / "source.json").read_text())["files"][int(parts[1])]
    text = item.get("text", "")
    if not text or hashlib.sha256(text.encode()).hexdigest() != item["sha256"]:
        raise ValueError("Source excerpt text does not match its recorded digest")
    start, end = spec["startLine"], spec["endLine"]
    lines = text.splitlines()
    if not (
        isinstance(start, int)
        and isinstance(end, int)
        and 1 <= start <= end <= len(lines)
    ):
        raise ValueError("Source excerpt line range is invalid")
    repository = spec["repositoryUrl"].rstrip("/")
    parsed = urlsplit(repository)
    if (
        parsed.scheme != "https"
        or parsed.hostname != "github.com"
        or parsed.username
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("Source links require a public GitHub HTTPS repository URL")
    revision = item["repository"]["revision"]
    if spec["checkedOutRevision"] != revision:
        raise ValueError(
            "Branch supplement does not match the captured source revision"
        )
    path = quote(item["path"], safe="/")
    branch = quote(spec["branch"], safe="")
    suffix = f"/{path}#L{start}-L{end}"
    content = "\n".join(lines[start - 1 : end])
    fence = "`" * max(
        3,
        max((len(x) for x in re.findall(r"`+", content)), default=0) + 1,
    )
    language = {
        ".yml": "yaml",
        ".yaml": "yaml",
        ".py": "python",
        ".html": "html",
        ".js": "javascript",
    }.get(Path(path).suffix, "text")
    return [
        f"**Source:** [{html.escape(Path(item['path']).name)} on {html.escape(spec['branch'])}]({repository}/blob/{branch}{suffix}) · [Captured revision]({repository}/blob/{revision}{suffix})",
        "",
        f"{fence}{language}",
        content,
        fence,
        "",
    ]


def energy_rows(data: JSON, site: str) -> list[list[str]]:
    """Validate separately collected modeled energy; never substitute missing for zero."""
    if (
        data.get("schemaVersion") != "greenframe-energy-v2"
        or data.get("origin") != site
    ):
        raise ValueError("Energy supplement must match the audited origin and schema")
    rows = []
    for page in data["pages"]:
        url = page["url"]
        parsed = urlsplit(url)
        if f"{parsed.scheme}://{parsed.netloc}" != site or page["phase"] != "initial":
            raise ValueError(
                "Energy page must use the audited origin and initial phase"
            )
        if page["status"] != "completed":
            rows.append([url, "Unavailable", "Unavailable"])
            continue
        if page["samples"] != 3 or len(page["sampleMetrics"]) != 3:
            raise ValueError("Energy headline requires three complete matching samples")
        values = []
        for key in ("clientDeviceSummaryWh", "networkSummaryWh"):
            value = page[key]["median"]
            if (
                not isinstance(value, (int, float))
                or not math.isfinite(value)
                or value < 0
            ):
                raise ValueError("Energy median must be a finite nonnegative value")
            metric = (
                "clientDeviceEnergy"
                if key == "clientDeviceSummaryWh"
                else "networkEnergy"
            )
            samples = [sample[metric]["value"] for sample in page["sampleMetrics"]]
            if any(
                not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0
                for v in samples
            ):
                raise ValueError("Energy samples must be finite nonnegative values")
            if any(
                sample[metric]["unit"] != "Wh/scenario"
                for sample in page["sampleMetrics"]
            ):
                raise ValueError("Energy samples must use Wh/scenario")
            if not math.isclose(median(samples), value, rel_tol=1e-12, abs_tol=1e-15):
                raise ValueError("Energy median does not match the recorded samples")
            values.append(f"{value * 1000:.2f} mWh")
        rows.append([url, *values])
    return rows
