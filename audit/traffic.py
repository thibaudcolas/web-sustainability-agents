#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = ["httpx==0.28.1"]
# [tool.uv]
# required-version = ">=0.12.20,<0.13"
# ///
"""Look up exact origins in a pinned monthly CrUX mirror and derive traffic scenarios."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import lzma
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import httpx

JSON = dict[str, Any]
ROOT = Path(__file__).resolve().parent.parent
LOG = logging.getLogger(__name__)
REPOSITORY = "crissyfield/crux-dumps"


def origin(value: str) -> str:
    """Preserve protocol and full hostname rather than merging unrelated origins."""
    parsed = urlsplit(value)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username
        or parsed.password
    ):
        raise ValueError("Expected a public HTTP(S) origin")
    port = parsed.port
    suffix = (
        f":{port}"
        if port and (parsed.scheme, port) not in {("http", 80), ("https", 443)}
        else ""
    )
    host = parsed.hostname.lower()
    if ":" in host:
        host = f"[{host}]"
    return f"{parsed.scheme.lower()}://{host}{suffix}"


def traffic_scenario(rank: int | None, mapping: dict[int, int]) -> JSON:
    """Map an observed bucket to a cohort scenario, never an actual traffic count."""
    if rank is None or rank not in mapping:
        return {
            "status": "unavailable",
            "annualPageviews": None,
            "reason": "No observed matching rank bucket; absence is not the extrapolated unranked bucket",
        }
    return {
        "status": "scenario",
        "annualPageviews": mapping[rank],
        "unit": "pageviews/year",
        "rankBucket": rank,
        "method": "rank-to-pageviews bucket median",
        "calibrationPopulation": "US government websites, 2025 analytics and December 2025 CrUX ranks",
        "uncertainty": "No calibrated site-level interval; population and period differ. This is not measured site analytics or a forecast.",
        "annualEmissions": None,
        "annualEmissionsReason": "Requires representative page mix, revisit assumptions, and compatible emissions model",
    }


def download(
    client: httpx.Client, url: str, path: Path, limit: int = 60_000_000
) -> bytes:
    """Cache bounded immutable files; failed downloads never become complete cache entries."""
    if path.exists():
        return path.read_bytes()
    chunks = bytearray()
    with client.stream("GET", url) as response:
        response.raise_for_status()
        for chunk in response.iter_bytes():
            chunks.extend(chunk)
            if len(chunks) > limit:
                raise ValueError("CrUX file exceeded download limit")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(chunks)
    return bytes(chunks)


def main() -> None:
    """Fetch monthly rank buckets without Google credentials, retaining mirror provenance."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "urls", nargs="*", default=["https://guide.wagtail.org", "https://wagtail.org"]
    )
    parser.add_argument("--month", default="latest")
    parser.add_argument("--max-rank", type=int, default=50_000_000)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "docs/initial-implementation/assets/traffic-scenarios.json",
    )
    parser.add_argument(
        "--mapping", type=Path, default=ROOT / "audit/rank-pageviews.csv"
    )
    args = parser.parse_args()
    targets = {origin(value) for value in args.urls}
    mapping_raw = args.mapping.read_bytes()
    with args.mapping.open() as stream:
        mapping = {
            int(row["rank"]): int(row["pageviews"])
            for row in csv.DictReader(stream)
            if row["rank"].isdigit()
        }
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    result: JSON = {
        "schemaVersion": "0.1.0",
        "capturedAt": datetime.now(UTC).isoformat(),
        "rankSource": f"https://github.com/{REPOSITORY}",
        "rankSemantics": "coarse popularity bucket, not exact ordinal; exact protocol and full origin",
        "mappingSource": "https://github.com/thibaudcolas/ranking-to-pageviews",
        "mappingSHA256": hashlib.sha256(mapping_raw).hexdigest(),
        "files": [],
        "results": [],
        "lookupStatus": "running",
    }
    found: dict[str, int] = {}
    try:
        with httpx.Client(timeout=60, follow_redirects=True) as client:
            response = client.get(
                f"https://api.github.com/repos/{REPOSITORY}/commits/main"
            )
            response.raise_for_status()
            commit = response.json()["sha"]
            if not re.fullmatch(r"[0-9a-f]{40}", commit):
                raise ValueError("Invalid mirror commit")
            result["mirrorCommit"] = commit
            base = f"https://raw.githubusercontent.com/{REPOSITORY}/{commit}"
            cache = ROOT / ".audit-work/crux" / commit
            meta_raw = download(
                client, f"{base}/meta.json", cache / "meta.json", 1_000_000
            )
            months = [
                m for year in json.loads(meta_raw)["years"] for m in year["months"]
            ]
            selected = (
                max(months, key=lambda m: m["id"])
                if args.month == "latest"
                else next(m for m in months if m["id"] == args.month)
            )
            month = selected["id"]
            if not re.fullmatch(r"20\d{4}", month):
                raise ValueError("Invalid dataset month")
            result.update(
                datasetMonth=month, metadataSHA256=hashlib.sha256(meta_raw).hexdigest()
            )
            for file in sorted(selected["files"], key=lambda f: f["rank"]):
                rank = int(file["rank"])
                if rank > args.max_rank or targets <= found.keys():
                    break
                name = f"{rank}.txt.xz"
                path = cache / month / name
                url = f"{base}/{month[:4]}/{month[4:]}/{name}"
                raw = download(client, url, path)
                count = 0
                matches = []
                with lzma.open(path, "rt") as stream:
                    for line in stream:
                        count += 1
                        value = line.strip()
                        if value in targets:
                            matches.append(value)
                if count != file["count"]:
                    raise ValueError("Mirror row count differs from metadata")
                for value in matches:
                    if value in found:
                        raise ValueError("Origin found in multiple rank buckets")
                    found[value] = rank
                result["files"].append(
                    {
                        "url": url,
                        "rankBucket": rank,
                        "rows": count,
                        "compressedSHA256": hashlib.sha256(raw).hexdigest(),
                    }
                )
                LOG.info(
                    "Checked rank bucket %s; matched %s/%s origins",
                    rank,
                    len(found),
                    len(targets),
                )
            result["lookupStatus"] = "completed"
    except (
        httpx.HTTPError,
        OSError,
        ValueError,
        StopIteration,
        lzma.LZMAError,
    ) as error:
        result.update(lookupStatus="partial_or_failed", error=type(error).__name__)
    result["results"] = [
        {
            "origin": value,
            "rankBucket": found.get(value),
            "status": "found" if value in found else "not_found_within_lookup_scope",
            "traffic": traffic_scenario(found.get(value), mapping),
        }
        for value in sorted(targets)
    ]
    result["lookupMaxRank"] = max(
        (f["rankBucket"] for f in result["files"]), default=None
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
