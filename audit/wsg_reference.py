#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = []
# [tool.uv]
# required-version = ">=0.12.20,<0.13"
# ///
"""Extract the pinned WSG draft and validate the older assessment crosswalk."""

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
ARTICLE = "https://thib.me/assessing-web-sustainability-guidelines-on-automated-testing"
CATEGORIES = {"automated": 35, "manual, quantitative": 16, "manual, qualitative": 50}
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
    """Parse the explicitly closed section/table structures in the two sources."""

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


def extract_assessment(raw: bytes) -> list[JSON]:
    """Extract every selected assessment row while preserving its original group."""
    current = ""
    rows = []
    for row in Document(raw.decode("utf-8")).root.descendants("tr"):
        cells = row.descendants("td")
        if len(cells) != 2:
            continue
        category, name = (cell.text() for cell in cells)
        if not category:
            current = name
        elif category in CATEGORIES:
            number, old_title = current.split(" ", 1)
            rows.append(
                {
                    "oldGuideline": number,
                    "oldGuidelineTitle": old_title,
                    "oldCriterion": name,
                    "classification": category,
                }
            )
    if Counter(r["classification"] for r in rows) != Counter(CATEGORIES):
        raise ValueError(
            "Assessment rows differ from the source's 35/16/50 category counts"
        )
    return rows


def validate_crosswalk(crosswalk: JSON, reference: JSON, rows: list[JSON]) -> None:
    """Check exhaustive source correspondence and valid current criterion targets."""
    if (
        crosswalk["wsgSourceVersion"] != reference["sourceVersion"]
        or crosswalk["wsgSourceSha256"] != reference["sourceSha256"]
    ):
        raise ValueError("Crosswalk and reference must use the same WSG source bytes")
    expected = [
        (r["oldGuideline"], r["oldCriterion"], r["classification"]) for r in rows
    ]
    actual = [
        (r["oldGuideline"], r["oldCriterion"], r["classification"])
        for r in crosswalk["checks"]
    ]
    if expected != actual:
        raise ValueError(
            "Crosswalk must contain each selected original row exactly once in source order"
        )
    criteria = {
        c["id"]: (g["id"], c["url"])
        for g in reference["guidelines"]
        for c in g["criteria"]
    }
    for check in crosswalk["checks"]:
        if not check["targets"] or not check["probe"] or not check["interpretation"]:
            raise ValueError(
                "Every old row needs mapping, repeatable probe and interpretation"
            )
        for target in check["targets"]:
            if (
                target["criterion"] not in criteria
                or (target["guideline"], target["url"]) != criteria[target["criterion"]]
            ):
                raise ValueError("Invalid criterion target")
        if check["status"] not in {"candidate", "partial-existing-evidence"}:
            raise ValueError("Crosswalk is a capability plan, not an executed result")


def main() -> None:
    """Build offline from pinned source bytes and validate the semantic crosswalk."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--html", type=Path, required=True, help="Saved versioned WSG HTML"
    )
    parser.add_argument(
        "--assessment", type=Path, required=True, help="Saved 2023 assessment HTML"
    )
    parser.add_argument("--output", type=Path, default=REFERENCES / "wsg.json")
    parser.add_argument(
        "--crosswalk", type=Path, default=REFERENCES / "assessment-crosswalk.json"
    )
    args = parser.parse_args()
    reference = extract_wsg(args.html.read_bytes())
    assessment = args.assessment.read_bytes()
    rows = extract_assessment(assessment)
    crosswalk = json.loads(args.crosswalk.read_text())
    validate_crosswalk(crosswalk, reference, rows)
    if crosswalk["sourceSha256"] != hashlib.sha256(assessment).hexdigest():
        raise ValueError("Assessment source hash differs from the reviewed crosswalk")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(reference, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
