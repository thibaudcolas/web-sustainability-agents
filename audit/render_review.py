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
import html
import json
import os
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from audit.report_details import (  # noqa: E402 # ty: ignore[unresolved-import]
    AREAS,
    area_results,
    energy_rows,
    first_visits,
    source_excerpt,
    validate_presentation,
)

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
    """Display decimal kB or MB without changing artifact base units."""
    return (
        f"{value / 1_000_000:.3f} MB"
        if value >= 1_000_000
        else f"{value / 1000:.1f} kB"
    )


def footprint(value: float) -> str:
    """Round display only, keeping positive estimates visible below 0.01 gCO₂e."""
    displayed = max(0.01, value) if value > 0 else value
    return f"{displayed:.2f} gCO₂e"


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


LABELS = {
    "pass": "Passed this check",
    "fail": "Problem found",
    "cantTell": "Needs investigation",
    "inapplicable": "Not relevant here",
    "untested": "Not reviewed",
}


STATUS_SYMBOLS = {
    "pass": "✅",
    "fail": "❌",
    "cantTell": "❓",
    "inapplicable": "➖",
    "untested": "⚪",
}


def prose(value: Any) -> str:
    """Escape HTML in editorial text while retaining ordinary Markdown formatting."""
    return html.escape(str(value), quote=False).strip()


def validate_editorial(editorial: JSON, review: JSON, review_sha: str) -> None:
    """Bind a presentation revision to its exact judgments and complete check set."""
    if (
        editorial.get("schemaVersion") != "1.0"
        or editorial.get("site") != review["site"]
        or editorial.get("reviewSHA256") != review_sha
    ):
        raise ValueError("Editorial draft must match the original site and review hash")
    expected = [row["checkId"] for row in review["rows"]]
    actual = [row["checkId"] for row in editorial["checks"]]
    if len(actual) != len(set(actual)) or set(actual) != set(expected):
        raise ValueError("Editorial draft needs every check exactly once")
    if [row["checkId"] for row in editorial["findings"]] != [
        row["checkId"] for row in review.get("topFindings", [])[:5]
    ]:
        raise ValueError(
            "Editorial draft must preserve the priority finding IDs and order"
        )
    for field in ["model", "reasoning", "harness"]:
        if not editorial.get("writer", {}).get(field):
            raise ValueError("Record actual editorial model, reasoning and harness")
    for row in editorial["checks"]:
        if any(
            not isinstance(row.get(key), str) or not row[key].strip()
            for key in ["title", "summary", "nextStep"]
        ):
            raise ValueError("Every check needs readable title, summary and next step")
    for row in editorial["findings"]:
        if any(
            not isinstance(row.get(key), str) or not row[key].strip()
            for key in ["title", "summary", "whyItMatters", "action"]
        ):
            raise ValueError(
                "Every finding needs readable observations, consequence and action"
            )
    if not editorial.get("overview") or not editorial.get("nextSteps"):
        raise ValueError("Supply an overview and next auditing steps")


def illustrations(path: Path | None, site: str, check_ids: set[str]) -> JSON:
    """Validate optional, separately captured images before adding them to a report."""
    if path is None:
        return {"captures": []}
    manifest = read(path)
    if manifest.get("origin") != site:
        raise ValueError("Screenshot origin does not match the audited site")
    for capture in manifest["captures"]:
        if capture["status"] != "completed":
            continue
        name = capture["file"]
        file = (path.parent / name).resolve()
        if (
            Path(name).name != name
            or file.parent != path.parent.resolve()
            or file.suffix not in {".png", ".webp"}
            or hashlib.sha256(file.read_bytes()).hexdigest() != capture["fileSHA256"]
        ):
            raise ValueError("Screenshot file path or digest is invalid")
        if (
            not capture.get("alt")
            or not capture.get("caption")
            or not capture.get("capturedAt")
        ):
            raise ValueError("Screenshot needs alt text, caption and capture time")
        if not set(capture["checkIds"]) <= check_ids:
            raise ValueError("Screenshot refers to an unknown check")
        final = urlsplit(capture["finalUrl"])
        if f"{final.scheme}://{final.netloc}" != site:
            raise ValueError("Screenshot redirected outside the audited origin")
    return manifest


def page_name(url: str, title: str | None = None) -> str:
    """Give public URLs short readable labels without dropping their link targets."""
    path = urlsplit(url).path.strip("/")
    if not path or re.fullmatch(r"[a-z]{2}(?:-[A-Za-z]{2})?", path):
        return "Homepage"
    if path.split("/")[-1] == "search":
        return "Search results"
    if title:
        return re.split(r" \| | [-–—] ", title, maxsplit=1)[0].strip()
    return path.split("/")[-1].replace("-", " ").capitalize()


def pointer(document: Any, location: str) -> Any:
    """Resolve a packet's JSON pointer to describe evidence in human terms."""
    current = document
    for piece in location.lstrip("/").split("/") if location else []:
        key = piece.replace("~1", "/").replace("~0", "~")
        current = current[int(key)] if isinstance(current, list) else current[key]
    return current


def source_descriptions(
    session: Path,
    packet: JSON,
    ids: list[str],
    documents: dict[str, JSON] | None = None,
) -> list[str]:
    """Describe inspected pages/files without sending readers to raw JSON."""
    descriptions: list[str] = []
    documents = documents if documents is not None else {}
    for identifier in ids:
        reference = packet["evidenceIndex"][identifier]
        name = reference["artifact"]
        if name not in documents:
            documents[name] = read(session / name)
        item = pointer(documents[name], reference["jsonPointer"])
        if name == "source.json":
            description = (
                f"Selected local file `{prose(item.get('path', 'unavailable path'))}`"
            )
            repository = item.get("repository") or {}
            if repository.get("revision"):
                description += f" at revision `{repository['revision'][:12]}`"
            if item.get("status") not in {"captured", "completed"}:
                description += (
                    f" ({prose(item.get('status', 'unavailable')).replace('_', ' ')})"
                )
        else:
            url = item.get("url") or item.get("origin") or item.get("site")
            if isinstance(url, str) and url.startswith(("https://", "http://")):
                label = (
                    "Browser observations"
                    if name == "probes.json"
                    else "Captured public evidence"
                )
                description = f"{label} for [{page_name(url)}]({url})"
            else:
                description = (
                    "Retrieved sustainability and hosting disclosures for this site"
                )
        if description not in descriptions:
            descriptions.append(description)
    return descriptions


def anchor(label: str, target: str) -> str:
    """Render an escaped link inside a semantic HTML table."""
    return f'<a href="{html.escape(target, quote=True)}">{html.escape(label)}</a>'


def table_start(
    caption: str, headings: list[str], methods: dict[str, str] | None = None
) -> list[str]:
    """Name a simple data table and identify its column headers."""
    methods = methods or {}
    return [
        '<div class="audit-table-scroll" tabindex="0" role="region" aria-label="'
        + html.escape(caption, quote=True)
        + '">',
        "<table>",
        "<caption>" + html.escape(caption) + "</caption>",
        "<thead><tr>"
        + "".join(
            f'<th scope="col">{anchor(h, methods[h]) if h in methods else html.escape(h)}</th>'
            for h in headings
        )
        + "</tr></thead>",
        "<tbody>",
    ]


def table_row(cells: list[str]) -> str:
    """Associate measurements/statuses with their page or check row header."""
    return (
        '<tr><th scope="row">'
        + cells[0]
        + "</th>"
        + "".join(f"<td>{value}</td>" for value in cells[1:])
        + "</tr>"
    )


def render(
    session: Path,
    prefix: str,
    editorial: JSON,
    screenshot_path: Path | None = None,
    image_prefix: str = "",
    editorial_link: str | None = None,
    receipt_link: str | None = None,
    presentation: JSON | None = None,
    energy: JSON | None = None,
    supplement_prefix: str | None = None,
) -> str:
    """Render readable findings with calculations and provenance kept deterministic."""
    packet = read(session / "packet.json")
    review = read(session / "review.json")
    assessment = read(session / "scores.json")
    validate_inputs(session, assessment, review)
    if len(assessment["scores"]) != 1:
        raise ValueError("Render exactly one site")
    score = assessment["scores"][0]
    if score["rubricVersion"] not in {"agent-breadth-v2", "agent-breadth-v3"}:
        raise ValueError("This report template targets agent-breadth-v2 or v3")
    if {packet["site"], review["site"], score["site"]} != {packet["site"]}:
        raise ValueError("Review and score must match the packet origin")
    review_sha = hashlib.sha256((session / "review.json").read_bytes()).hexdigest()
    validate_editorial(editorial, review, review_sha)
    presentation = presentation or {}
    validate_presentation(presentation, review, review_sha)
    reference_path = (
        Path(__file__).resolve().parents[1]
        / ".agents/skills/sustainability-guideline-review/references/wsg.json"
    )
    references = {r["id"]: r for r in read(reference_path)["guidelines"]}

    def guideline_link(number: str) -> str:
        item = references[number]
        return (
            f'<a class="audit-guideline" href="{html.escape(item["url"], quote=True)}" '
            f'title="{html.escape(item["summary"], quote=True)}">'
            f"WSG {html.escape(number)}: {html.escape(item['title'])}</a>"
        )

    rules = {row["id"]: row for row in packet["checks"]}
    images = illustrations(screenshot_path, packet["site"], set(rules))
    if screenshot_path and not image_prefix:
        raise ValueError("Provide the screenshot link prefix for the report location")
    staged = read(session / "staged.json")
    probes = read(session / "probes.json")
    source = read(session / "source.json")
    documents = {"staged.json": staged, "probes.json": probes, "source.json": source}
    headline_runs = first_visits(staged["runs"])
    has_consent = any(run["branch"] != "no_banner" for run in staged["runs"])
    page_labels = {
        run["url"]: page_name(
            run["url"],
            next(
                (
                    phase.get("state", {}).get("title")
                    for phase in run["phases"]
                    if phase["phase"] == "initial"
                ),
                None,
            ),
        )
        for run in headline_runs
    }
    counts = score["counts"]
    edited = {row["checkId"]: row for row in editorial["checks"]}
    judgments = {row["checkId"]: row for row in review["rows"]}
    number = (
        f"{score['value']:.1f}/100" if score["value"] is not None else "Unavailable"
    )
    journey_label = (
        "visitor journey" if len(probes["journeys"]) == 1 else "visitor journeys"
    )
    lines = [
        f"# {urlsplit(packet['site']).netloc}: sustainability audit",
        "",
        "## At a glance",
        "",
        '<div class="grid cards" markdown="1">',
        "",
        f"- **{number}** — scoped audit score<br>{counts['pass']} passing, {counts['fail']} with problems, {counts['cantTell']} needing more evidence.",
        f"- **{len(probes['pages'])} pages** reviewed<br>{len(probes['journeys'])} {journey_label} and {len(source['files'])} selected source files.",
        f"- **{score['checkedGuidelines']} of {score['totalGuidelines']} guideline groups** scored<br>{counts['untested']} untested; {counts['inapplicable']} not applicable. Tests cover selected aspects of each guideline.",
        "",
        "</div>",
        "",
        "## Results by WSG area",
        "",
        *table_start(
            "Selected checks by WSG area",
            ["Area", "Passing", "Guideline groups checked", "Needs evidence"],
        ),
    ]
    for area in area_results(score["guidelines"]):
        percentage = (
            f"{area['percent']:.0f}% ({area['counts']['pass']}/{area['checked']})"
            if area["percent"] is not None
            else "Not assessed"
        )
        lines.append(
            table_row(
                [
                    anchor(area["title"], f"#findings-{area['section']}"),
                    percentage,
                    f"{area['checked']} of {area['total']}",
                    str(area["counts"]["cantTell"]),
                ]
            )
        )
    lines += [
        "</tbody></table></div>",
        "",
        "Passing percentages apply to the selected checks. Full-guideline conformance has not been established.",
        "",
        "## Page measurements",
        "",
        *table_start(
            "Page measurements",
            [
                "Page",
                "First load",
                "After cookies" if has_consent else "After waiting",
                "After scrolling",
                "Estimated footprint",
                "Carbon rating",
                "Browser energy",
                "Network energy",
            ],
            {
                "First load": "#measure-first-load",
                "After cookies": "#measure-after-choice",
                "After waiting": "#measure-after-choice",
                "After scrolling": "#measure-scroll",
                "Estimated footprint": "#measure-carbon",
                "Carbon rating": "#measure-carbon",
                "Browser energy": "#measure-energy",
                "Network energy": "#measure-energy",
            },
        ),
    ]
    energy_by_url = (
        {
            url: (device, network)
            for url, device, network in energy_rows(energy, packet["site"])
        }
        if energy
        else {}
    )

    def phase_size(run: JSON, name: str) -> str:
        phase: JSON = next((p for p in run["phases"] if p["phase"] == name), {})
        if phase.get("receivedBytes") is None:
            return "Not measured"
        value = traffic(phase["receivedBytes"])
        if phase.get("accountingStatus") != "complete_within_protocol":
            value += " · " + anchor("partial", "#measure-completeness")
        return value

    def later_sizes(url: str, phase: str) -> str:
        values = []
        for run in staged["runs"]:
            if run["url"] != url:
                continue
            label = {
                "accept": "Accept cookies",
                "reject": "Reject optional cookies",
            }.get(run["branch"], "" if run["branch"] == "no_banner" else run["branch"])
            value = phase_size(run, phase)
            values.append(f"{html.escape(label)}: {value}" if label else value)
        return "<br>".join(values) or "Not measured"

    for run in headline_runs:
        url = run["url"]
        rating = run.get("rating", {})
        initial_complete = any(
            p["phase"] == "initial"
            and p.get("accountingStatus") == "complete_within_protocol"
            for p in run["phases"]
        )
        carbon = (
            rating["trace"]["co2"]
            if initial_complete and rating.get("status") == "calculated"
            else None
        )
        device, network = energy_by_url.get(url, ("Not sampled", "Not sampled"))
        lines.append(
            table_row(
                [
                    anchor(page_labels[url], url),
                    phase_size(run, "initial"),
                    later_sizes(url, "after_consent"),
                    later_sizes(url, "after_scroll"),
                    footprint(carbon["total"]) if carbon else "Withheld",
                    html.escape(carbon["rating"]) if carbon else "Withheld",
                    device,
                    network,
                ]
            )
        )
    lines += ["</tbody></table></div>", ""]
    lines += ["## Priorities", "", prose(editorial["overview"]), ""]
    used_images: set[str] = set()
    finding_map = {f["checkId"]: f for f in editorial["findings"]}
    finding_order = presentation.get("findingOrder", list(finding_map))
    originals = {f["checkId"]: f for f in review["topFindings"]}
    for index, identifier in enumerate(finding_order, 1):
        override = presentation.get("findingOverrides", {}).get(identifier, {})
        finding = {**finding_map[identifier], **override}
        original = {**originals[identifier], **override}
        identifier = finding["checkId"]
        guideline = rules[identifier]["guideline"]
        lines += [
            f"### {index}. {prose(finding['title'])}",
            "",
            '<div class="audit-finding" markdown="1">',
            "",
            f"**{original['priority'].capitalize()} priority** · {LABELS[judgments[identifier]['outcome']]} · {guideline_link(guideline)}",
            "",
            f"**What we found.** {prose(finding['summary'])}",
            "",
            f"**Why it matters.** {prose(finding['whyItMatters'])}",
            "",
            f"**Next step.** {prose(finding['action'])}",
            "",
        ]
        if identifier in presentation.get("sourceExcerpts", {}):
            lines += source_excerpt(
                session, packet, presentation["sourceExcerpts"][identifier]
            )
        for capture in images["captures"]:
            if (
                capture["status"] != "completed"
                or identifier not in capture["checkIds"]
                or capture["id"] in used_images
            ):
                continue
            used_images.add(capture["id"])
            src = f"{image_prefix}/{capture['file']}"
            lines += [
                '<figure class="audit-illustration" markdown="1">',
                "",
                f"[![{prose(capture['alt']).replace(']', '&#93;')} ]({src})]({src})",
                "",
                f"<figcaption>{html.escape(presentation.get('captions', {}).get(capture['id'], capture['caption']))}</figcaption>",
                "</figure>",
                "",
            ]
        lines += [
            f"[How we checked this: {prose(finding['title'])}](#evidence-{identifier})",
            "",
            "</div>",
            "",
        ]
    lines += [
        "## Further checks",
        "",
        "These outcomes apply to the selected checks and sample. Open a check's explanation for the observation, limitations and useful follow-up.",
        "",
        '??? note "Browse all check outcomes"',
        "",
        *[
            "    " + line
            for line in table_start("All selected check outcomes", ["Check", "Outcome"])
        ],
    ]
    for row in review["rows"]:
        identifier = row["checkId"]
        lines.append(
            "    "
            + table_row(
                [
                    anchor(edited[identifier]["title"], f"#evidence-{identifier}"),
                    f'<span aria-hidden="true">{STATUS_SYMBOLS[row["outcome"]]}</span> '
                    + LABELS[row["outcome"]],
                ]
            )
        )
    lines += ["    </tbody></table></div>", "", "## Next steps for auditing", ""]
    lines += [f"{i}. {prose(step)}" for i, step in enumerate(editorial["nextSteps"], 1)]
    if presentation.get("nextAuditChecks"):
        lines += [
            "",
            "### Broader checks to add next",
            "",
            "These checks need additional evidence and are outside the current score. Missing records do not establish a site defect.",
            "",
            *table_start(
                "Next contextual audit scope", ["Check", "Evidence so far", "Next step"]
            ),
        ]
        for item in presentation["nextAuditChecks"]:
            lines.append(
                table_row(
                    [
                        anchor(item["title"], references[item["guideline"]]["url"]),
                        html.escape(item["observation"]),
                        html.escape(item["nextStep"]),
                    ]
                )
            )
        lines += ["</tbody></table></div>", ""]
    lines += [
        "",
        "The sample covers selected pages and visitor tasks, not every page on the site. Expand it where the checks above identify an untested template, interaction or audience need."
        if len(probes["pages"]) >= 5
        else "This audit has a smaller sample than the default 5–10 representative pages. Expand it using the site's navigation, sitemap and important visitor tasks; do not assume the findings cover untested pages.",
        "",
        "## Detailed findings",
        "",
        "This appendix explains the evidence in ordinary language. Local source files help identify possible fixes, but we have not confirmed that the live site uses the same code revision. A missing selected file or document does not mean the organization has none.",
        "",
    ]
    for section, title in AREAS.items():
        lines += [f"### {title} {{#findings-{section}}}", ""]
        area_rows = [
            row
            for row in review["rows"]
            if rules[row["checkId"]]["guideline"].split(".")[0] == section
        ]
        if not area_rows:
            lines += [
                "No checks selected in this area. Include it in the next audit scope.",
                "",
            ]
        for row in area_rows:
            identifier = row["checkId"]
            item = edited[identifier]
            guideline = rules[identifier]["guideline"]
            lines += [
                f'<h4 id="evidence-{identifier}">{html.escape(item["title"])}</h4>',
                "",
                f"**{LABELS[row['outcome']]}** · {guideline_link(guideline)}",
                "",
                f"_{prose(references[guideline]['summary'])}_",
                "",
                prose(item["summary"]),
                "",
                f"**Next step:** {prose(item['nextStep'])}",
                "",
            ]
            if rules[identifier].get("assessmentScope"):
                lines += [
                    f"**Assessed scope:** {prose(rules[identifier]['assessmentScope'])}",
                    "",
                ]
            descriptions = source_descriptions(
                session, packet, row.get("evidenceIds", []), documents
            )
            if descriptions:
                lines += (
                    ["**Where we looked:**", ""]
                    + [f"- {description}." for description in descriptions]
                    + [""]
                )
    protocol = staged.get("protocol", {})
    viewport = protocol.get("viewport", {})
    reviewer = review["reviewer"]
    writer = editorial["writer"]
    profiles = [
        run["rating"]["profile"]
        for run in headline_runs
        if run.get("rating", {}).get("profile")
    ]
    carbon_methods = list(
        dict.fromkeys(
            f"Sustainable Web Design Model version {profile['version']} through `{profile['library']}`, assuming {profile['firstVisitPercentage']:.0%} first visits"
            for profile in profiles
        )
    )
    lines += [
        "## Methodology and reproducibility",
        "",
        f"The browser measurements were captured from **{staged.get('startedAt', 'unrecorded')}** to **{staged.get('finishedAt', 'unrecorded')}**. Initial-load tests used a {viewport.get('width', 'recorded')} × {viewport.get('height', 'recorded')} desktop viewport and a {protocol.get('observationMs', 0) / 1000:g}-second observation window. Cookie choices and scrolling were recorded afterward. Supplementary tests covered narrow layouts, color and motion preferences, print, JavaScript availability and bounded keyboard navigation.",
        "",
        f"**Audit judgments:** {prose(reviewer['harness'])}, {prose(reviewer['model'])}, **{prose(reviewer['reasoning'])} reasoning**. **Report wording:** {prose(writer['harness'])}, {prose(writer['model'])}, **{prose(writer['reasoning'])} reasoning**.",
        "",
        f"The scoring method is `{score['rubricVersion']}`. A guideline group counts once even if it has several checks. Observed problems take precedence over unresolved checks in that group. {counts['inapplicable']} groups were excluded as not applicable; {counts['untested']} were untested. Unknowns remain in the passing-percentage denominator; untested and inapplicable groups do not. Area percentages use the same rule as the overall score. No annual footprint is inferred from these sampled visits.",
        "",
        "### First load {#measure-first-load}",
        "",
        "Data downloaded before clicking or scrolling, using the first recorded initial visit for each URL, including its completeness limit. Decimal kB = 1,000 bytes; MB = 1,000,000 bytes.",
        "",
        "### Cookie choices and waiting {#measure-after-choice}",
        "",
        (
            "Each cookie choice starts a separate fresh visit. Accept and reject results stay separate; they are not combined into a median. The first-load column uses the first of those visits."
            if has_consent
            else "No cookie banner was observed in this sample. The intermediate checkpoint waits without clicking."
        )
        + " Later columns show **cumulative totals**, including the initial load of that visit. They are not additional amounts to add together or guaranteed savings.",
        "",
        "### Scrolling {#measure-scroll}",
        "",
        "Cumulative downloads after scrolling to the bottom, following the cookie-choice or waiting checkpoint of the same visit. Compare accept and reject values within their own visit; do not subtract the first-load headline from a different visit.",
        "",
        "### Partial measurements {#measure-completeness}",
        "",
        "A partial result means some requests failed or did not finish in the observation window, so their transferred size is uncertain. The site is measured as it behaved; a failed analytics request is context, not automatically a priority fix. Carbon estimates and ratings are withheld for incomplete initial captures. Unmarked transfer figures are complete within the test conditions, not a measure of every possible download.",
        "",
        "### Estimated footprint and Digital Carbon Rating {#measure-carbon}",
        "",
        "Both use the same initial visit as the first-load column. Footprints are estimates in grams of carbon dioxide equivalent (gCO₂e) per first visit. They display two decimal places, with a minimum of 0.01 gCO₂e for positive estimates. Digital Carbon Ratings use unrounded estimates from the fixed comparison model. "
        + (
            "Recorded model: " + "; ".join(carbon_methods) + ". "
            if carbon_methods
            else "No carbon model profile was recorded. "
        )
        + "The comparison gives no green-hosting credit. These are model assumptions, not verified electricity-supply facts. Ratings remain provisional because the capture protocol has not been independently validated; they do not establish whole-site sustainability.",
        "",
        "### Browser and network energy {#measure-energy}",
        "",
        "Energy is shown in milliwatt-hours (mWh = 0.001 Wh). Browser energy includes modeled CPU, memory, disk and display use. Not sampled means no energy experiment was supplied for that page; unavailable means a supplied experiment did not yield a usable result. Neither means zero energy.",
        "",
        "Illustrations were captured separately from the transfer measurements. Their capture dates, viewports, URLs and file hashes are retained in the screenshot manifest. Source excerpts reproduce captured text; branch links target the checked-out branch. Captured-revision links remain stable if that branch moves.",
        "",
        '??? note "Technical files for reproducing this report"',
        "",
        "    The report above can be read without these files. They retain exact evidence, original judgments and calculation inputs for independent reproduction.",
        "",
    ]
    if energy:
        # Insert the readable model boundary before the collapsed technical appendix.
        position = next(
            i
            for i, line in enumerate(lines)
            if line.startswith("Illustrations were captured separately")
        )
        lines[position:position] = [
            "**Energy method:** GreenFrame 2.0.1 uses separately recorded browser scenarios, with three fresh-context visits per page, page load followed by a three-second wait, and no cookie interaction or scrolling. The median client-device estimate and median network estimate are reported separately; their medians must not be added to derive a total. This is a resource-use model, not metered whole-device electricity. Browser startup and the collector warm-up are excluded; browser close is included.",
            "",
            "The pinned container uses Chromium 110 and a fixed Chrome 89 user-agent, independently of the transfer collector. The model assumes a 14 W display; that assumption contributes substantially to these short visits. CPU, memory and disk estimates use the collection host's properties. Background activity on this shared workstation was not independently isolated. These figures support repeat experiments under the same conditions, not device-independent rankings. GreenFrame network energy and SWDM carbon estimates overlap in scope and are not added together.",
            "",
        ]
    if supplement_prefix:
        lines += [
            f"    - [Report settings and source links]({supplement_prefix}/presentation.json)",
            f"    - [Report reproduction command and input hashes]({supplement_prefix}/report-receipt.json)",
        ]
        if energy:
            lines += [
                f"    - [Energy protocol, samples and provenance]({supplement_prefix}/energy.json)"
            ]
    for name, label in [
        ("plan.json", "Audit scope and tasks"),
        ("receipt.json", "Collector commands and versions"),
        ("review.json", "Original judgments"),
        ("scores.json", "Score calculation"),
        ("packet.json", "Evidence index"),
        ("staged.json", "Recorded transfers and disclosures"),
        ("probes.json", "Browser observations"),
        ("source.json", "Selected source evidence"),
        ("review-handoffs.json", "Specialist reviews and reconciliation"),
        ("chart-data.json", "Chart-ready measurements and scoring data"),
        ("chart-data.csv", "Measurement table for charts"),
        (
            "session.zip",
            "Frozen session, skill snapshots and reproduction instructions",
        ),
        ("manifest.json", "Publication hashes"),
    ]:
        if (session / name).exists():
            lines.append(f"    - [{label}]({prefix}/{name})")
    if editorial_link:
        lines.append(f"    - [Report wording and check explanations]({editorial_link})")
    if receipt_link:
        lines.append(f"    - [Editorial model and input provenance]({receipt_link})")
    lines += [
        "",
        f"    Original review SHA-256: `{review_sha}`. Recalculate with `audit/assess.py` using the preserved reviews, rubric, weights and evidence. New collection or model review requires a new session; it can produce different results.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    """Render a scored session with a separately validated editorial draft."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", type=Path, required=True)
    parser.add_argument("--artifact-prefix", required=True)
    parser.add_argument("--editorial", type=Path, required=True)
    parser.add_argument("--screenshots", type=Path)
    parser.add_argument("--image-prefix", default="")
    parser.add_argument("--presentation", type=Path)
    parser.add_argument("--energy", type=Path)
    parser.add_argument("--supplement-prefix")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        render(
            args.session,
            args.artifact_prefix,
            read(args.editorial),
            args.screenshots,
            args.image_prefix,
            os.path.relpath(args.editorial.resolve(), args.output.parent.resolve()),
            os.path.relpath(
                args.editorial.with_name("editorial-receipt.json").resolve(),
                args.output.parent.resolve(),
            )
            if args.editorial.with_name("editorial-receipt.json").exists()
            else None,
            read(args.presentation) if args.presentation else None,
            read(args.energy) if args.energy else None,
            args.supplement_prefix,
        )
    )


if __name__ == "__main__":
    main()
