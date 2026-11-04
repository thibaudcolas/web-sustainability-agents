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
    area_results,
    energy_rows,
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


def size_range(values: list[float]) -> str:
    """Preserve independent observations as a range, not an invented average."""
    if not values:
        return "Not measured"
    low, high = traffic(min(values)), traffic(max(values))
    return low if low == high else f"{low}–{high}"


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


def table_start(caption: str, headings: list[str]) -> list[str]:
    """Name a simple data table and identify its column headers."""
    return [
        '<div class="audit-table-scroll" tabindex="0" role="region" aria-label="'
        + html.escape(caption, quote=True)
        + '">',
        "<table>",
        "<caption>" + html.escape(caption) + "</caption>",
        "<thead><tr>"
        + "".join(f'<th scope="col">{html.escape(h)}</th>' for h in headings)
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
        return f"[WSG {number}: {prose(item['title'])}]({item['url']})"

    rules = {row["id"]: row for row in packet["checks"]}
    images = illustrations(screenshot_path, packet["site"], set(rules))
    if screenshot_path and not image_prefix:
        raise ValueError("Provide the screenshot link prefix for the report location")
    staged = read(session / "staged.json")
    probes = read(session / "probes.json")
    source = read(session / "source.json")
    documents = {"staged.json": staged, "probes.json": probes, "source.json": source}
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
        for run in staged["runs"]
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
                    area["title"],
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
        "Data downloaded when a visitor first opens the page, before clicking or scrolling.",
        "",
        *table_start(
            "First-load transfers", ["Page", "First load", "Measurement completeness"]
        ),
    ]
    urls = list(dict.fromkeys(run["url"] for run in staged["runs"]))
    for url in urls:
        initial = [
            phase
            for run in staged["runs"]
            if run["url"] == url
            for phase in run["phases"]
            if phase["phase"] == "initial"
        ]
        initial = initial[:1]
        values = [
            phase["receivedBytes"]
            for phase in initial
            if phase.get("receivedBytes") is not None
        ]
        complete = bool(initial) and all(
            phase.get("accountingStatus") == "complete_within_protocol"
            for phase in initial
        )
        lines.append(
            table_row(
                [
                    anchor(page_labels[url], url),
                    traffic(values[0]) if values else "Not measured",
                    "Complete within the test conditions"
                    if complete
                    else "Some data could not be measured",
                ]
            )
        )
    lines += ["</tbody></table></div>"]
    incomplete = any(
        phase.get("accountingStatus") != "complete_within_protocol"
        for run in staged["runs"]
        for phase in run["phases"]
        if phase["phase"] == "initial"
    )
    lines += [
        "",
        "Some requests failed or did not finish in the observation window. Their transferred size is uncertain, so these figures are incomplete and a Digital Carbon Rating is withheld. The audit measures the site as it behaved; a failed analytics request is context, not automatically a priority fix."
        if incomplete
        else "The collector recorded the requests within its observation window. Later downloads and untested journeys are outside these first-load figures.",
        "",
    ]
    lines += ["### Browser energy", ""]
    if energy:
        lines += [
            "GreenFrame models energy from browser resource activity. These figures are the median of three visits to each page.",
            "",
            *table_start(
                "Modeled browser energy per visit",
                ["Page", "Client device model", "Network model"],
            ),
        ]
        for url, device, network in energy_rows(energy, packet["site"]):
            lines.append(
                table_row(
                    [anchor(page_labels.get(url, page_name(url)), url), device, network]
                )
            )
        lines += [
            "</tbody></table></div>",
            "",
            "The device estimate includes CPU, memory, disk and a modeled display. Other sampled pages have no energy result yet. See the methodology for the separate browser scenario and model assumptions.",
            "",
        ]
    else:
        lines += [
            "Energy was not collected for this session. Transfer sizes alone do not measure browser energy.",
            "",
        ]
    ratings = [
        run["rating"]["trace"]["co2"]["rating"]
        for run in staged["runs"]
        if run.get("rating", {}).get("status") == "calculated"
    ]
    if ratings:
        eligible = [
            run["rating"]
            for run in staged["runs"]
            if run.get("rating", {}).get("status") == "calculated"
        ]
        footprint = [item["trace"]["co2"]["total"] for item in eligible]
        profile = eligible[0]["profile"]
        lines += [
            f"**Digital Carbon Ratings:** {', '.join(dict.fromkeys(ratings))} for the eligible initial visits, using the fixed comparison model. This estimates a page-load footprint; it does not establish whole-site sustainability.",
            "",
            f"The eligible visits model **{min(footprint):.3g}–{max(footprint):.3g} gCO₂e per first visit**, using Sustainable Web Design Model version {profile['version']} through `{profile['library']}`. The comparison assumes {profile['firstVisitPercentage']:.0%} first visits and gives no green-hosting credit. These are fixed model assumptions, not verified electricity-supply facts. The rating remains provisional because the capture protocol has not been independently validated.",
            "",
        ]
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
        "## After cookie choices and scrolling"
        if has_consent
        else "## After waiting and scrolling",
        "",
        (
            "Each cookie choice starts a separate fresh visit. "
            if has_consent
            else "No cookie banner was observed in this sample. The intermediate checkpoint waits without clicking, then the page is scrolled to the bottom. "
        )
        + "The sizes below are **cumulative totals**, including the first load. They help locate later downloads; they are not additional amounts to add together or guaranteed savings.",
        "",
        '??? note "Compare the interaction measurements"',
        "",
        *[
            "    " + line
            for line in table_start(
                "Cumulative data after cookie choices and scrolling"
                if has_consent
                else "Cumulative data after waiting and scrolling",
                [
                    "Page",
                    "Cookie choice tested" if has_consent else "Intermediate action",
                    "After cookie choice" if has_consent else "After waiting",
                    "After scrolling to the bottom",
                ],
            )
        ],
    ]
    for run in staged["runs"]:
        phases = {phase["phase"]: phase for phase in run["phases"]}
        choice = {
            "accept": "Accept cookies",
            "reject": "Reject optional cookies",
            "no_banner": "No banner interaction",
        }.get(run["branch"], run["branch"].replace("_", " ").capitalize())
        values = [
            traffic(phases[name]["receivedBytes"]) if name in phases else "Not measured"
            for name in ["after_consent", "after_scroll"]
        ]
        lines.append(
            "    "
            + table_row(
                [
                    anchor(page_labels[run["url"]], run["url"]),
                    html.escape(choice),
                    *values,
                ]
            )
        )
    lines += [
        "    </tbody></table></div>",
        "",
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
                    LABELS[row["outcome"]],
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
            "The new contextual skill was tried against this audit’s existing evidence. The requests below are outside the current score; missing records are not site defects.",
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
        "## How we checked this",
        "",
        "This appendix explains the evidence in ordinary language. Local source files help identify possible fixes, but we have not confirmed that the live site uses the same code revision. A missing selected file or document does not mean the organization has none.",
        "",
    ]
    for row in review["rows"]:
        identifier = row["checkId"]
        item = edited[identifier]
        guideline = rules[identifier]["guideline"]
        lines += [
            f'<h3 id="evidence-{identifier}">{html.escape(item["title"])}</h3>',
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
    lines += [
        "## Methodology and reproducibility",
        "",
        f"The browser measurements were captured from **{staged.get('startedAt', 'unrecorded')}** to **{staged.get('finishedAt', 'unrecorded')}**. Initial-load tests used a {viewport.get('width', 'recorded')} × {viewport.get('height', 'recorded')} desktop viewport and a {protocol.get('observationMs', 0) / 1000:g}-second observation window. Cookie choices and scrolling were recorded afterward. Supplementary tests covered narrow layouts, color and motion preferences, print, JavaScript availability and bounded keyboard navigation.",
        "",
        f"**Audit judgments:** {prose(reviewer['harness'])}, {prose(reviewer['model'])}, **{prose(reviewer['reasoning'])} reasoning**. **Report wording:** {prose(writer['harness'])}, {prose(writer['model'])}, **{prose(writer['reasoning'])} reasoning**. The original judgments and calculated score are preserved. Any subsequent priority or wording changes are recorded in the presentation supplement.",
        "",
        f"The scoring method is `{score['rubricVersion']}`. A guideline group counts once even if it has several checks. Observed problems take precedence over unresolved checks in that group. {counts['inapplicable']} groups were excluded as not applicable; {counts['untested']} were untested. Unknowns remain in the passing-percentage denominator; untested and inapplicable groups do not. Area percentages use the same rule as the overall score. No annual footprint is inferred from these sampled visits.",
        "",
        "First-load transfer headlines use the first recorded initial visit for each URL, including its completeness limit. Later cookie-choice runs remain in the interaction table; they are not combined into a median. Decimal kB = 1,000 bytes; MB = 1,000,000 bytes. Energy is shown in milliwatt-hours (mWh = 0.001 Wh).",
        "",
        "Illustrations were captured separately from the transfer measurements. Their capture dates, viewports, URLs and file hashes are retained in the screenshot manifest. Source excerpts reproduce captured text; branch links target the branch checked out when the presentation supplement was prepared. Captured-revision links remain stable if that branch moves.",
        "",
        '??? note "Technical files for reproducing this report"',
        "",
        "    The report above can be read without these files. They retain exact evidence, original judgments and calculation inputs for independent reproduction.",
        "",
    ]
    if energy:
        # Insert the readable model boundary before the collapsed technical appendix.
        position = lines.index('??? note "Technical files for reproducing this report"')
        lines[position:position] = [
            "**Energy method:** GreenFrame 2.0.1 uses separately recorded browser scenarios, with three fresh-context visits per page, page load followed by a three-second wait, and no cookie interaction or scrolling. The median client-device estimate and median network estimate are reported separately; their medians must not be added to derive a total. This is a resource-use model, not metered whole-device electricity. Browser startup and the collector warm-up are excluded; browser close is included.",
            "",
            "The pinned container uses Chromium 110 and a fixed Chrome 89 user-agent, independently of the transfer collector. The model assumes a 14 W display; that assumption contributes substantially to these short visits. CPU, memory and disk estimates use the collection host's properties. Background activity on this shared workstation was not independently isolated. These figures support repeat experiments under the same conditions, not device-independent rankings. GreenFrame network energy and SWDM carbon estimates overlap in scope and are not added together.",
            "",
        ]
    if presentation:
        position = lines.index('??? note "Technical files for reproducing this report"')
        lines[position:position] = [prose(presentation["reason"]), ""]
    if supplement_prefix:
        lines += [
            f"    - [Presentation revision and source links]({supplement_prefix}/presentation.json)",
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
