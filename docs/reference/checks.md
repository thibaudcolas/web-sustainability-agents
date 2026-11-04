# Broader browser and source-assisted checks

The `agent-breadth-v2` session rubric contains **33 checks across 32 WSG guideline groups**: 22 browser reviews, three disclosure/hosting reviews, and eight optional source reviews. It adds 18 checks to the first agent-driven catalog. A public-only audit defaults to 25 checks in 24 groups; source checks join the default set only when files are explicitly selected.

Across the historical and current catalogs, **39/71 guideline groups (54.9%)** now have some defined scoped review method. That is methodology breadth, not the score coverage of one report or complete success-criterion coverage. Scope, page diversity, interaction depth and organizational evidence remain separate dimensions. The [101-row assessment crosswalk](../knowledge-base/assessment-crosswalk.md) remains the broader development map.

## More browser evidence

The [interaction collector](browser-probes.md) now captures seven states per selected page: desktop, narrow, live reduced motion, live dark preference, print, fresh no-JavaScript, and fresh dark preference. Its new evidence includes metadata, image declarations, font details, selected response headers, bounded request records and twelve real Tab-key observations. The keyboard trace is not a complete accessibility assessment, and device emulation does not establish compatibility on actual hardware.

Ten new expectations cover media, fonts, semantics/forms, metadata, preferences, no-JavaScript content, API repetition, public caching, compression and keyboard reachability. Reviewers relate these observations to visitor tasks and the pinned WSG criteria. Headers can nominate a caching improvement but do not prove warm reuse; an unexecuted code range does not prove removable code; an image's natural size does not establish its smallest legible size.

Journeys can now specify a viewport and a `success` object containing a URL, selector and expected text. All supplied postconditions and required actions must succeed. The older `successSelector` flag remains an observation for historical compatibility. A generic heading can no longer establish declared completion while the browser remains on the starting page.

## Source evidence in the same packet

The agent selects individual files, rather than treating a whole repository as reviewed:

```json
{
  "sourceRoots": ["local/project"],
  "sourceFiles": [
    { "root": "local/project", "path": "package.json" },
    { "root": "local/project", "path": "README.md" },
    { "root": "local/project", "path": ".github/workflows/ci.yml" }
  ]
}
```

`audit/source.py` reads up to thirty selected files without executing project code. It records revision, tracked working-tree state, file identity and SHA-256. Text is included up to 64 KB; larger files up to 2 MB retain identity metadata without exposing their contents to the reviewer. Missing, oversized or undecodable files remain explicit. Symlink aliases and non-regular files are rejected. The agent must inspect selected content before publishing it.

The workflow indexes these records in `packet.json`, so source citations receive the same artifact-hash and pointer validation as browser evidence. A supplied checkout remains candidate source: neither a matching name nor a source revision attests what is deployed. A metadata-only lockfile record proves file identity, not valid lock contents or installed versions.

| Check                 | Scoped expectation                                                                                        | WSG                                                                                                               |
| --------------------- | --------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `source-reuse`        | Concrete repeated interfaces use shared components where beneficial                                       | [3.4](https://www.w3.org/TR/web-sustainability-guidelines/#avoid-redundancy-and-duplication-in-code)              |
| `source-dependencies` | Selected manifests describe dependencies and a repeatable resolution mechanism                            | [3.12](https://www.w3.org/TR/web-sustainability-guidelines/#use-dependencies-sparingly-and-maintain-them)         |
| `source-runtime`      | Selected runtime declarations agree for the documented path; latest stable is a separate question         | [3.15](https://www.w3.org/TR/web-sustainability-guidelines/#use-the-latest-stable-language-version)               |
| `source-automation`   | Selected CI triggers and controls avoid demonstrably redundant work while preserving necessary validation | [4.6](https://www.w3.org/TR/web-sustainability-guidelines/#use-automation-wisely)                                 |
| `source-maintenance`  | Selected documentation explains development, testing or maintenance                                       | [5.10](https://www.w3.org/TR/web-sustainability-guidelines/#follow-a-product-management-and-maintenance-strategy) |
| `source-change-docs`  | Identifiable change documentation explains user-facing changes                                            | [5.12](https://www.w3.org/TR/web-sustainability-guidelines/#document-updates-and-evolutions)                      |
| `source-budgets`      | A selected document defines a concrete relevant budget and consequence                                    | [5.24](https://www.w3.org/TR/web-sustainability-guidelines/#define-performance-environmental-and-human-budgets)   |
| `source-open-source`  | Selected license/contribution documents explain reuse terms and participation                             | [5.25](https://www.w3.org/TR/web-sustainability-guidelines/#use-and-contribute-to-open-source)                    |

These expectations are deliberately narrower than their guidelines. Dependency declarations cannot establish necessity, security or installed versions; documents cannot establish staffing or repeated operational execution. An unsuccessful selected-file search does not prove an organization has no policy or budget. Unknowns should lead to specific further evidence requests.

## Historical development sample

The original breadth campaign included three pages per site: homepage, substantive task content, and search-results or emissions-disclosure content. It adds seventeen selected source files for the guide and thirteen for Wagtail.org. Two large lockfiles per repository provide identity metadata only; Wagtail's selected `CHANGELOG.md` path is unavailable. Those limitations remain in the packets.

Both revised journeys completed their declared postconditions: the guide uses Enter to submit search and then opens the image-management article; Wagtail uses the footer's sustainability link. This resolves the earlier collector-specific failures without rewriting that evidence or calling them site regressions. It does not establish optimal task efficiency or success for every user.

The [guide review](../initial-implementation/assets/breadth-sessions/guide/review.json) and [Wagtail review](../initial-implementation/assets/breadth-sessions/wagtail/review.json) retain the historical judgments; their report drafts have been removed. The [current reports](../reports/README.md) use fresh captures. Different samples and methods prevent interpreting their score differences as site improvement or deterioration.

## Review and eval breadth

The [new Harbor family](../initial-implementation/breadth-benchmark.md) adds sixteen controlled cases, including four collection handoffs. It tests many of the distinctions that the broader live checks depend on. Review the synthetic cases separately from the live site judgments: the former have author-created reference labels, while the latter need owner feedback on usefulness, applicability and evidence interpretation.

When providing feedback, name a check ID or case ID and identify whether the problem is the expectation, missing evidence, interpretation, priority or proposed validation. This lets us improve the relevant collector, skill or benchmark without changing historical outcomes. The next validation priorities are complete keyboard/form journeys, constrained font/media experiments, owner-reviewed source recommendations and broader representative page sampling.

The reports are generated by `audit/render_review.py` from frozen scores and reviewer output. The renderer verifies score-input, raw-review, packet and evidence hashes before rendering; it does not produce new judgments. Each published bundle also includes chart-ready JSON/CSV for this campaign, the actual review prompt and output schema, and model/harness settings. Earlier annual and hardware-energy results are deliberately not attached to new capture totals.
