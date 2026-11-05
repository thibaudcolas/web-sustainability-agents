#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = []
# [tool.uv]
# required-version = ">=0.12.20,<0.13"
# ///
"""Extract the pinned WSG draft and validate current criterion auditability classes."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
REFERENCES = ROOT / ".agents/skills/sustainability-guideline-review/references"
SOURCE = "https://www.w3.org/TR/2026/DNOTE-web-sustainability-guidelines-20261016/"
CANONICAL = "https://www.w3.org/TR/web-sustainability-guidelines/"
CLASSES = (
    "automated",
    "manual, quantitative",
    "manual, qualitative",
    "static analysis",
    "consulting",
)
EVIDENCE_ACCESS = {"public-site", "public-documents", "source", "owner-records"}
VOID = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}
JSON = dict[str, Any]


@dataclass
class Element:
    """Represent only the HTML structure needed by the frozen source extractor."""

    tag: str
    attrs: dict[str, str]
    children: list[Element | str] = field(default_factory=list)

    def text(self) -> str:
        """Return text with normalized whitespace, retaining inline boundaries."""
        return " ".join(
            "".join(
                c.text_raw() if isinstance(c, Element) else c for c in self.children
            ).split()
        )

    def text_raw(self) -> str:
        """Retain source whitespace until the complete containing text is joined."""
        return "".join(
            c.text_raw() if isinstance(c, Element) else c for c in self.children
        )

    def descendants(self, tag: str) -> list[Element]:
        """Find descendant elements in document order."""
        found = []
        for child in self.children:
            if isinstance(child, Element):
                if child.tag == tag:
                    found.append(child)
                found.extend(child.descendants(tag))
        return found

    def elements(self) -> list[Element]:
        """Return direct child elements only."""
        return [c for c in self.children if isinstance(c, Element)]


class Document(HTMLParser):
    """Parse the explicitly closed structures of the pinned WSG document."""

    def __init__(self, source: str) -> None:
        """Parse an HTML document into a small standard-library-only tree."""
        super().__init__(convert_charrefs=True)
        self.root = Element("document", {})
        self.stack = [self.root]
        self.feed(source)
        self.close()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Record an element and descend unless it is an HTML void element."""
        child = Element(tag, {k: v or "" for k, v in attrs})
        self.stack[-1].children.append(child)
        if tag not in VOID:
            self.stack.append(child)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Handle explicitly closed tags without changing the containing node."""
        self.stack[-1].children.append(Element(tag, {k: v or "" for k, v in attrs}))

    def handle_endtag(self, tag: str) -> None:
        """Close to the matching open element, tolerating HTML optional endings."""
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        """Retain text in its containing element."""
        self.stack[-1].children.append(data)


def heading(section: Element, tag: str) -> Element | None:
    """Find the section's own heading, not one from a nested section."""
    for child in section.elements():
        if child.tag == tag:
            return child
        if child.tag == "div" and child.attrs.get("class") == "header-wrapper":
            return next(iter(child.descendants(tag)), None)
    return None


def extract_wsg(raw: bytes) -> JSON:
    """Extract current guidelines and full criterion text, rejecting draft drift."""
    document = Document(raw.decode("utf-8")).root
    guidelines: list[JSON] = []
    for section in document.descendants("section"):
        title = heading(section, "h3")
        if title is None or not re.match(r"^[2-5]\.\d+ ", title.text()):
            continue
        number, name = title.text().split(" ", 1)
        criteria = []
        for child in section.elements():
            if child.tag != "section":
                continue
            criterion = heading(child, "h4")
            if criterion is None or not criterion.text().startswith(
                "Success Criterion:"
            ):
                continue
            identifier = criterion.attrs["id"]
            criteria.append(
                {
                    "id": identifier,
                    "title": criterion.text()
                    .removeprefix("Success Criterion:")
                    .strip(),
                    "url": CANONICAL + "#" + identifier,
                    "text": "\n".join(
                        c.text() for c in child.elements() if c.tag != "div"
                    ),
                    "considerations": [
                        v.strip()
                        for v in child.attrs.get("data-considerations", "").split(",")
                        if v.strip()
                    ],
                    "categories": [
                        v.strip()
                        for v in child.attrs.get("data-categories", "").split(",")
                        if v.strip()
                    ],
                }
            )
        guidelines.append(
            {
                "id": number,
                "title": name,
                "url": CANONICAL + "#" + section.attrs["id"],
                "summary": "\n".join(
                    c.text() for c in section.elements() if c.tag == "p"
                ),
                "criteria": criteria,
            }
        )
    if len(guidelines) != 71 or sum(len(g["criteria"]) for g in guidelines) != 197:
        raise ValueError("Expected the pinned 71-guideline, 197-criterion WSG draft")
    identifiers = [c["id"] for g in guidelines for c in g["criteria"]]
    if len(set(identifiers)) != 197 or any(
        not c["text"] for g in guidelines for c in g["criteria"]
    ):
        raise ValueError("Duplicate identifiers or missing criterion text")
    if SOURCE not in raw.decode("utf-8"):
        raise ValueError("Document does not identify the pinned publication")
    return {
        "schemaVersion": "1.0",
        "source": CANONICAL,
        "sourceVersion": SOURCE,
        "sourceSha256": hashlib.sha256(raw).hexdigest(),
        "status": "W3C Group Note Draft, 16 October 2026; work in progress, not W3C endorsement",
        "copyright": "Copyright © 2026 World Wide Web Consortium. W3C® liability, trademark and permissive document license rules apply.",
        "license": "https://www.w3.org/copyright/software-license-2023/",
        "licenseNotice": "WSG-LICENSE.txt",
        "modifications": "Structured extraction for software use: headings, summaries, criterion text and classification metadata. Whitespace normalized; examples, additional information and introductory/conformance material omitted. Consult the original for complete guidance. This is not a replacement specification.",
        "guidelineCount": 71,
        "criterionCount": 197,
        "guidelines": guidelines,
    }


def validate_classifications(data: JSON, reference: JSON) -> None:
    """Require one justified classification for every current WSG criterion."""
    if data.get("schemaVersion") != "2.0":
        raise ValueError("Expected current criterion classification schema 2.0")
    if (
        data.get("wsgSourceVersion") != reference["sourceVersion"]
        or data.get("wsgSourceSha256") != reference["sourceSha256"]
    ):
        raise ValueError(
            "Classifications and reference must use the same WSG source bytes"
        )
    if "checks" in data:
        raise ValueError(
            "Classifications must be keyed to current criteria, not legacy rows"
        )
    definitions = data.get("classDefinitions", {})
    if set(definitions) != set(CLASSES) or not all(definitions.values()):
        raise ValueError("Define all five auditability classes")
    expected = {
        criterion["id"]: (guideline, criterion)
        for guideline in reference["guidelines"]
        for criterion in guideline["criteria"]
    }
    rows = data.get("criteria", [])
    if [row["id"] for row in rows] != list(expected):
        raise ValueError("Include each current criterion exactly once in WSG order")
    if data.get("criterionCount") != len(expected) or data.get("guidelineCount") != len(
        reference["guidelines"]
    ):
        raise ValueError("Classification coverage counts differ from the WSG reference")
    for row in rows:
        guideline, criterion = expected[row["id"]]
        if (row.get("guideline"), row.get("title"), row.get("url")) != (
            guideline["id"],
            criterion["title"],
            criterion["url"],
        ):
            raise ValueError("Criterion identity must match the current WSG reference")
        if row.get("classification") not in CLASSES:
            raise ValueError("Unknown primary classification")
        supporting = row.get("supportingClasses", [])
        if len(supporting) != len(set(supporting)) or not set(supporting) <= set(
            CLASSES
        ) - {row["classification"]}:
            raise ValueError(
                "Supporting classes must be unique and distinct from the primary class"
            )
        access = row.get("evidenceAccess", [])
        if (
            not access
            or len(access) != len(set(access))
            or not set(access) <= EVIDENCE_ACCESS
        ):
            raise ValueError(
                "Each criterion needs explicit valid evidence access routes"
            )
        if any(
            not isinstance(row.get(key), str) or not row[key].strip()
            for key in ("rationale", "reviewRoute")
        ):
            raise ValueError(
                "Each criterion needs a rationale and repeatable review route"
            )
        if set(row) & {"status", "outcome", "oldGuideline", "oldCriterion", "targets"}:
            raise ValueError(
                "Classifications describe current auditability, not execution outcomes or legacy mappings"
            )
    counts = Counter(row["classification"] for row in rows)
    if data.get("categoryCounts") != {name: counts[name] for name in CLASSES}:
        raise ValueError("Primary class counts must reconcile with criterion rows")
    groups = data.get("guidelines", [])
    if [group["id"] for group in groups] != [
        group["id"] for group in reference["guidelines"]
    ]:
        raise ValueError("Include each current guideline exactly once in WSG order")
    for group, guideline in zip(groups, reference["guidelines"], strict=True):
        members = [row for row in rows if row["guideline"] == guideline["id"]]
        member_counts = Counter(row["classification"] for row in members)
        if (group.get("title"), group.get("url"), group.get("criterionCount")) != (
            guideline["title"],
            guideline["url"],
            len(members),
        ):
            raise ValueError("Guideline summary must match current WSG membership")
        classes = group.get("classifications", [])
        if len(classes) != len(set(classes)) or set(classes) != set(member_counts):
            raise ValueError(
                "Guideline classes must summarize their constituent criteria"
            )
        if group.get("categoryCounts") != {
            name: member_counts[name] for name in CLASSES
        }:
            raise ValueError(
                "Guideline class counts must reconcile with criterion rows"
            )


def main() -> None:
    """Validate maintained classifications; optionally refresh WSG from saved HTML."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--html",
        type=Path,
        help="Saved versioned WSG HTML; omit to validate the existing reference",
    )
    parser.add_argument("--output", type=Path, default=REFERENCES / "wsg.json")
    parser.add_argument(
        "--classifications", type=Path, default=REFERENCES / "assessment-crosswalk.json"
    )
    args = parser.parse_args()
    reference = (
        extract_wsg(args.html.read_bytes())
        if args.html
        else json.loads(args.output.read_text())
    )
    data = json.loads(args.classifications.read_text())
    validate_classifications(data, reference)
    if args.html:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(reference, indent=2, ensure_ascii=False) + "\n"
        )


if __name__ == "__main__":
    main()
