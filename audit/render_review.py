#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = []
# [tool.uv]
# required-version = ">=0.12.20,<0.13"
# ///
"""Render a per-site Markdown review from a frozen scored session."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

JSON = dict[str, Any]


def read(path: Path) -> JSON:
    """Read session JSON."""
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object")
    return value


def cell(value: Any) -> str:
    """Keep generated table text within one Markdown cell."""
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def traffic(value: float) -> str:
    """Display decimal KB or MB without changing artifact base units."""
    return (
        f"{value / 1_000_000:.3f} MB"
        if value >= 1_000_000
        else f"{value / 1000:.1f} KB"
    )


def validate_inputs(session: Path, score_document: JSON, review: JSON) -> None:
    """Reject changed judgments, expectations or evidence after score calculation."""
    for key, name in {
        "reviews": "reviews.json",
        "rubric": "rubric.json",
        "impactWeights": "impact-weights.json",
    }.items():
        if (
            hashlib.sha256((session / name).read_bytes()).hexdigest()
            != score_document["sourceSHA256"][key]
        ):
            raise ValueError("Scored review inputs changed")
    wrapper = read(session / "reviews.json")
    if (
        wrapper["reviewFileSHA256"]
        != hashlib.sha256((session / "review.json").read_bytes()).hexdigest()
    ):
        raise ValueError("Reviewer output changed after scoring")
    if (
        review["packetSHA256"]
        != hashlib.sha256((session / "packet.json").read_bytes()).hexdigest()
    ):
        raise ValueError("Review packet changed")
    for name, expected in wrapper["sourceSHA256"].items():
        if (
            Path(name).name != name
            or hashlib.sha256((session / name).read_bytes()).hexdigest() != expected
        ):
            raise ValueError("Scored source evidence changed")


def render(session: Path, prefix: str) -> str:
    """Present scoped judgments and their evidence without recomputing model decisions."""
    packet = read(session / "packet.json")
    review = read(session / "review.json")
    assessment = read(session / "scores.json")
    validate_inputs(session, assessment, review)
    if len(assessment["scores"]) != 1:
        raise ValueError("Render exactly one site")
    score = assessment["scores"][0]
    if score["rubricVersion"] != "agent-breadth-v2":
        raise ValueError("This report template targets agent-breadth-v2")
    if {packet["site"], review["site"], score["site"]} != {packet["site"]}:
        raise ValueError("Review and score must match the packet origin")
    staged = read(session / "staged.json")
    probes = read(session / "probes.json")
    source = read(session / "source.json")
    counts = score["counts"]
    rules = {row["id"]: row for row in packet["checks"]}
    titles = {row["number"]: row for row in score["guidelines"]}

    def artifact(name: str, label: str) -> str:
        return f"[{label}]({prefix}/{name})"

    def citations(ids: list[str]) -> str:
        return ", ".join(
            artifact(packet["evidenceIndex"][identifier]["artifact"], identifier)
            for identifier in ids
        )

    number = (
        f"{score['value']:.1f}/100" if score["value"] is not None else "Unavailable"
    )
    lines = [
        f"# {urlsplit(packet['site']).netloc}: expanded WIP audit",
        "",
        '!!! note "Scoped development audit"',
        "",
        f"    This report applies `{score['rubricVersion']}` to {len(probes['pages'])} public pages, {len(probes['journeys'])} declared journey and {len(source['files'])} selected source files. The new rubric and sample differ from earlier audits; scores are not a time trend.",
        "",
        f"**Scoped score: {number} — {counts['pass']}/{score['checkedGuidelines']} passing guideline groups**, with {counts['fail']} failed and {counts['cantTell']} unresolved. {len(review['rows'])} check judgments aggregate into {score['checkedGuidelines']}/{score['totalGuidelines']} checked groups ({score['checkedCoveragePercent']:.1f}%).",
        "",
        f"Unknowns stay in the denominator but are not defects. {counts['inapplicable']} groups are inapplicable and {counts['untested']} untested. **No full WSG guideline is verified.** See {artifact('scores.json', 'the score calculation')} and the [scoring method](../knowledge-base/audit-scoring.md).",
        "",
        "## Key measures",
        "",
        "| Page / branch | Initial load | After consent | After scrolling | Accounting |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for run in staged["runs"]:
        phases = {row["phase"]: row for row in run["phases"]}
        values = [
            traffic(phases[name]["receivedBytes"]) if name in phases else "Unavailable"
            for name in ["initial", "after_consent", "after_scroll"]
        ]
        status = phases.get("initial", {}).get("accountingStatus", "unavailable")
        lines.append(
            f"| {cell(run['url'])} / {cell(run['branch'])} | {' | '.join(values)} | {status} |"
        )
    ratings = [run.get("rating", {}) for run in staged["runs"]]
    calculated = [
        rating["trace"]["co2"]["rating"]
        for rating in ratings
        if rating.get("status") == "calculated"
    ]
    lines += [
        "",
        f"Digital Carbon Ratings: {', '.join(calculated) if calculated else 'unavailable for these captures'}. Ratings use the fixed SWDM profile; incomplete capture prevents a badge. No new hardware-energy or annual-footprint result is included in this campaign.",
        "",
        "## Top findings",
        "",
    ]
    for index, finding in enumerate(review.get("topFindings", [])[:5], 1):
        rule = rules[finding["checkId"]]
        lines += [
            f"### {index}. {finding['title']}",
            "",
            f"**{finding['priority'].capitalize()} priority · `{finding['checkId']}` · [WSG {rule['guideline']}]({titles[rule['guideline']]['url']})**",
            "",
            finding["summary"],
            "",
            finding["recommendation"],
            "",
            f"Evidence: {citations(finding['evidenceIds'])}.",
            "",
        ]
    lines += [
        "## Quantitative evidence",
        "",
        f"The {artifact('staged.json', 'staged capture')} preserves fresh above-the-fold measurements before interaction, then actual cookie choice and scrolling in each context. Later totals are cumulative; differences include background activity and are not measured causal savings. Technology detection and the supplementary probes are separate from headline traffic.",
        "",
        f"The {artifact('probes.json', 'supplementary observations')} contain seven page states and bounded keyboard, request, response-header and code-coverage evidence. Code offsets are not removable transfer bytes; a dozen forward Tab observations do not establish complete keyboard accessibility. No energy test ran alongside the model campaigns.",
        "",
        "## Qualitative and source review",
        "",
        f"{artifact('disclosures.json', 'Carbon.txt interpretation')} separates discovery and declared relationships from verified claims. {artifact('source.json', 'Source evidence')} retains the selected files, hashes, revision and tracked working-tree state. Large files may have identity metadata only. The supplied source is a candidate implementation; **deployment remains unverified**.",
        "",
        "The table below preserves every reviewer judgment. Passing narrow checks does not establish the entire linked guideline. Read the next-evidence column when a conclusion depends on task context, untested controls, source identity or internal records.",
        "",
        "## Detailed check judgments",
        "",
        "| Check / WSG | Outcome | Rationale | Next evidence or validation |",
        "| --- | --- | --- | --- |",
    ]
    for row in review["rows"]:
        rule = rules[row["checkId"]]
        url = titles[rule["guideline"]]["url"]
        lines.append(
            f"| `{row['checkId']}` · [WSG {row['guideline']}]({url}) | {row['outcome']} | {cell(row['rationale'])} | {cell(row['nextEvidence'])} |"
        )
    lines += [
        "",
        f"Full confidence labels and exact citations: {artifact('review.json', 'original model review')}. Evidence locations and scoped expectations: {artifact('packet.json', 'review packet')}. The scorer groups repeated checks once per guideline; a demonstrated failure takes precedence over an unresolved check in the same group.",
        "",
        "## Next steps for auditing",
        "",
        "1. Review the proposed priorities and task assumptions with the site owner. Validate source-candidate fixes against the deployed revision before editing production.",
        "2. Complete keyboard, form, narrow-layout and triggered-media journeys. Test constrained font/media delivery and readability, including intended pixel densities and assistive use.",
        "3. Obtain scoped hosting, monitoring-budget, maintenance and operational records where public or selected source evidence remains insufficient. Do not infer organization-wide absence from this sample.",
        "4. Expand representative templates, languages and states, and use the [broader benchmark](breadth-benchmark.md) to test the interpretation changes before adopting them.",
        "",
        f"The [current catalog](../reference/checks.md) defines partial review methods in 39/71 groups across all catalogs; this individual campaign attempts {score['checkedGuidelines']}. STAR scope, inventory, sampling, page review and reporting are represented, but the sample and process coverage remain incomplete. No full-guideline conformance percentage is claimed.",
        "",
        "## Methodology and reproducibility",
        "",
        f"{artifact('plan.json', 'The plan')} fixes tasks, pages, consent branches, source selection and journey postconditions. {artifact('receipt.json', 'Command receipts')} record locked Python collectors, script hashes, collection timestamps and the base Git revision; uncommitted implementation changes are identified by their hashes. Frozen skill and input hashes remain in the packet.",
        "",
        f"Reviewer: {review['reviewer']['harness']}, `{review['reviewer']['model']}`, {review['reviewer']['reasoning']} reasoning. It used the session's frozen skills and indexed evidence without consulting prior reports. These are development judgments, not owner-validated reference labels or a calibrated sustainability ranking.",
        "",
        "Measurements use a 1280 × 800 fresh desktop context and three-second staged observation windows. Supplemental page states use the separate bounded probe protocol. The two live-site collection jobs and model campaigns can overlap; elapsed timings are not controlled performance or energy comparisons. KB/MB are decimal units. Failed resources stay in the as-is evidence, and unavailable measurements remain unknown.",
        "",
        f"{artifact('manifest.json', 'The publication manifest')} hashes exact artifacts. Logs and private skill copies are omitted. Recalculate with `audit/assess.py` using this bundle's `reviews.json`, `rubric.json`, `impact-weights.json` and evidence directory. Recollection and LLM judgments can vary; deterministic aggregation of the same evidence and judgments reproduces exactly.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    """Render an inspected session with caller-selected publication links."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", type=Path, required=True)
    parser.add_argument("--artifact-prefix", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(args.session, args.artifact_prefix))


if __name__ == "__main__":
    main()
