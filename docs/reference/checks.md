# Browser, source and contextual checks

The `agent-breadth-v3` catalog contains **43 checks across 40 WSG guideline groups**: 22 browser reviews, three disclosure/hosting reviews, eight optional source reviews and ten contextual reviews. All 40 groups have **partial** methods; none has full-guideline coverage. The contextual extension adds eight groups through explicit qualitative expectations rather than automatic policy-presence checks.

New audits select relevant contextual checks during setup using visitor tasks, public evidence and owner priorities. The owner does not need to choose IDs or provide internal code. Each selected subset has its own denominator. The low-level workflow preserves the context-free `agent-breadth-v2` default: 25 public checks in 24 groups, with eight source checks joining only when files are explicitly selected. Existing v2 sessions and historical scores remain unchanged.

The current catalog therefore offers partial methods for **40/71 guideline groups (56.3%)**, or **32/71 (45.1%)** without source checks when all ten contextual checks are selected. The historical/current union of 46 groups includes older methods and is not the current workflow's coverage. None of these counts is the score coverage of one report or complete success-criterion coverage. The [current WSG auditability classifications](../knowledge-base/assessment-crosswalk.md) cover all 197 criteria as a planning inventory, independently of implemented checks.

## Contextual evidence and decisions

The `sustainability-context-review` role helps setup select and collect useful evidence, then supports the existing guideline and claims reviewers. It can run as a bounded native agent task or sequentially. These expectations use the pinned 16 October 2026 WSG draft and its criterion identifiers; a manual qualitative classification does not prevent an agent from collecting and interpreting evidence.

| Check                   | Bounded expectation                                                                                   | WSG criterion                                                                                                  |
| ----------------------- | ----------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `audience-needs`        | A selected decision responds to researched user and community needs                                   | [2.2: audience evaluation](https://www.w3.org/TR/web-sustainability-guidelines/#audience-evaluation)           |
| `inclusive-testing`     | A selected change has representative pre-release testing and reasoned responses to findings           | [2.14: early user testing](https://www.w3.org/TR/web-sustainability-guidelines/#early-user-testing)            |
| `governance-practice`   | A commitment has accountable review, results and a documented response over time                      | [5.1: governance over time](https://www.w3.org/TR/web-sustainability-guidelines/#governance-over-time)         |
| `impact-business-model` | Funding/revenue connects to impacts and a reviewed decision                                           | [5.9: theory of change](https://www.w3.org/TR/web-sustainability-guidelines/#theory-of-change)                 |
| `service-necessity`     | A selected decision evaluates desirability, feasibility and viability against alternatives            | [5.13: creation evaluation](https://www.w3.org/TR/web-sustainability-guidelines/#creation-evaluation)          |
| `access-barriers`       | A declared task works for represented constraints or has a usable justified alternative               | [5.13: obstacle consideration](https://www.w3.org/TR/web-sustainability-guidelines/#obstacle-consideration)    |
| `data-minimization`     | Requested personal data and meaningful choices have a task-related purpose                            | [5.18: data ownership](https://www.w3.org/TR/web-sustainability-guidelines/#data-ownership)                    |
| `content-lifecycle`     | A selected collection has a schedule and an applied review/archive decision preserving useful history | [5.18: outdated content](https://www.w3.org/TR/web-sustainability-guidelines/#outdated-content)                |
| `sustainability-goals`  | Service-specific measurable goals communicate dated, comparable progress                              | [5.6: web sustainability goals](https://www.w3.org/TR/web-sustainability-guidelines/#web-sustainability-goals) |
| `service-end-of-life`   | Scoped retirement guidance explains notice, migration/export and data handling responsibilities       | [5.22: end-of-life care](https://www.w3.org/TR/web-sustainability-guidelines/#end-of-life-care)                |

Select IDs in `plan.contextChecks`. Before collection, capture attributed UTF-8 text or Markdown as `plan.contextEvidence`: each record declares its absolute file path, source, kind (`public-document`, `owner-record` or `task-observation`), capture time with timezone, scope, check IDs and limitations. The contextual skill's reference supplies the complete record format. The workflow freezes up to thirty records of 64 KB each into `context.json`, indexes them with artifact hashes and JSON Pointers, and preserves per-check evidence requests. Failed or oversized records stay explicit. A captured record means review is possible, not that the check passes.

Before freezing, `plan.contextScopes` must map exactly the selected contextual check IDs to nonempty assessment scopes. Pin the task, audience, access constraints and completion condition for interactions, or the service/decision boundary and period for organizational checks. This differs from a source record's scope. The selected packet check, its evidence request and review-template row retain the declared `assessmentScope`; final review validation rejects a missing or changed scope. Reviewers cannot silently change it to fit the observations. The same successful desktop trace may support an anonymous desktop task while leaving a separately declared keyboard-only task unknown. A scope change requires a linked new session; existing context-free v2 plans need no contextual entries.

A [developer forward-test and separate native review](../reports/assets/report-refinement/context-forward-test.json) applied six contextual checks to existing frozen Guide and Wagtail.org evidence. Five outcomes agreed; the access-barrier reviews used different desktop and keyboard/device boundaries. Both observations could be valid for their stated scopes, but the disagreement exposed a missing plan contract. New sessions therefore pin per-check assessment scopes before collection. This small development exercise is not an accuracy estimate and does not change the original packets, reports or scores.

Public reports, research case studies, issue histories and actual task observations can support scoped judgments without internal access. A policy alone cannot establish performed testing, operational review or lifecycle execution. Missing public evidence remains `cantTell` after review; it is not proof that the practice is absent. The retirement check deliberately judges guidance rather than completed shutdown. Browser form evidence cannot verify retention enforcement or downstream deletion. Historical content and necessary authentication can remain valuable.

Packets include the exact selected expectations, scope and skill snapshots. Workers use the same frozen evidence, request missing facts through the coordinator and return ordinary evidence-linked outcomes. The scorer groups checks by guideline, so two contextual checks in one group do not earn extra weight. Collecting later records requires a linked new session; adding the new catalog does not rescore earlier reports or benchmarks.

## Qualitative coverage and gaps

Criterion-level coverage is not yet fully mapped: the ten contextual checks name current criterion IDs, while the other 33 checks map to guideline groups. The 197-criterion inventory makes that gap explicit, but does not fill it. Map each implemented expectation and benchmark case to the exact criterion clauses it tests before publishing a criterion coverage percentage.

The ten contextual checks are the clearest dedicated qualitative slice, but they are not the only judgment-based work. Browser and disclosure reviews also interpret whether media serves a task, controls respect preferences, an alternative remains usable, or a claim applies to this origin. Deterministic measurements supply evidence for these decisions; they do not settle them.

The Guide and Wagtail.org reports each assess 33 selected v2 checks, with scored denominators of 31 and 32 guideline groups. Their contextual previews remain outside those scores. The newer documentation and exporter reports use selected v3 contextual checks and public-only evidence, with denominators of 26 and 24 groups. Catalog availability does not mean every site received every check. The [assessment's coverage table](../initial-implementation/project-assessment.md#coverage-what-the-numbers-actually-mean) summarizes all four reports.

| Review area                         | Current support                                                                                | Main gap to validate                                                                                                    |
| ----------------------------------- | ---------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Journeys, content and media         | Browser observations plus evidence/guideline interpretation                                    | Complete constrained tasks, recovery paths, content usefulness and legibility tradeoffs across representative templates |
| User research and service decisions | Audience needs, inclusive testing, service necessity and access barriers                       | Finding and interpreting executed research/decision records; an agent walkthrough cannot substitute for affected users  |
| Governance and lifecycle            | Progress reviews, goals, funding impacts, data purpose, content review and retirement guidance | Comparable records over time, contradictory evidence, actual implementation and context-specific recommendations        |
| Hosting and footprint claims        | Claims-review skill, disclosures and explicit model assumptions                                | Independent scope/provider corroboration and operational evidence beyond published commitments                          |

[STAR's evaluation methodology](https://w3c.github.io/sustainableweb-ig/docs/star.html) addresses scope, exploration, sampling, evaluation and reporting. The workflow implements parts of each, but there is no validated percentage of STAR coverage. In particular, page-count defaults and one successful journey do not establish representative coverage of complete processes, states and audiences. Frozen-evidence benchmark success does not establish that an agent can discover the right evidence on a live site.

Two focused skill candidates are useful to evaluate: **experience and content review** for public task/necessity/tradeoff judgments, and **governance and lifecycle review** for scoped records, execution and progress. Keep context review as the evidence-selection coordinator and retain the existing claims specialist. Start with clearer task-specific references and evaluate the split before adding mandatory agents or one skill per guideline. The [next qualitative benchmark](../evaluation/design.md#next-qualitative-validation) defines the evidence needed to justify it.

## More browser evidence

The [interaction collector](browser-probes.md) now captures seven states per selected page: desktop, narrow, live reduced motion, live dark preference, print, fresh no-JavaScript, and fresh dark preference. Its new evidence includes metadata, image declarations, font details, selected response headers, bounded request records and twelve real Tab-key observations. The keyboard trace is not a complete accessibility assessment, and device emulation does not establish compatibility on actual hardware.

Ten new expectations cover media, fonts, semantics/forms, metadata, preferences, no-JavaScript content, API repetition, public caching, compression and keyboard reachability. Reviewers relate these observations to visitor tasks and the pinned WSG criteria. Headers can nominate a caching improvement but do not prove warm reuse; an unexecuted code range does not prove removable code; an image's natural size does not establish its smallest legible size.

Journeys can now specify a viewport and a `success` object containing a URL, selector and expected text. All supplied postconditions and required actions must succeed. The older `successSelector` flag remains an observation for historical compatibility. A generic heading can no longer establish declared completion while the browser remains on the starting page.

## Source evidence in the same packet

The agent selects individual files, rather than treating a whole repository as reviewed. Here, `site-source` is a placeholder for the supplied project checkout:

```json
{
  "sourceRoots": ["site-source"],
  "sourceFiles": [
    { "root": "site-source", "path": "package.json" },
    { "root": "site-source", "path": "README.md" },
    { "root": "site-source", "path": ".github/workflows/ci.yml" }
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

The [historical breadth campaign](../initial-implementation/breadth-benchmark.md) contains sixteen controlled cases, including four collection handoffs. It tests many of the distinctions that the broader live checks depend on. Review the synthetic cases separately from the live site judgments: the former have author-created reference labels, while the latter need owner feedback on usefulness, applicability and evidence interpretation.

When providing feedback, name a check ID or case ID and identify whether the problem is the expectation, missing evidence, interpretation, priority or proposed validation. This lets us improve the relevant collector, skill or benchmark without changing historical outcomes. The next validation priorities are complete keyboard/form journeys, constrained font/media experiments, owner-reviewed source recommendations and broader representative page sampling.

The reports are generated by `audit/render_review.py` from frozen scores and reviewer output. The renderer verifies score-input, raw-review, packet and evidence hashes before rendering; it does not produce new judgments. Each published bundle also includes chart-ready JSON/CSV for this campaign, the actual review prompt and output schema, and model/harness settings. Earlier annual and hardware-energy results are deliberately not attached to new capture totals.
