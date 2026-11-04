# Skill-guided audit, scores, and coverage

The audit now combines measured evidence with explicit qualitative review roles. Separate GPT-6.1 Sol/low reviewers applied three skills to raw evidence for each site, without reading the previous human report conclusions. A deterministic publisher resolves their evidence references to actual JSON locations, and a calculator aggregates their scoped judgments. The coordinator inspected the findings; they are not independent owner ground truth.

## Current score and expected WSG coverage

| Measure                            |        Guide |  Wagtail.org |
| ---------------------------------- | -----------: | -----------: |
| Scoped audit score                 | **71.4/100** | **58.8/100** |
| Passing scoped guideline checks    |    **10/14** |    **10/17** |
| Failed checks                      |            2 |            4 |
| Unresolved checks                  |            2 |            3 |
| Checked guideline coverage         | 14/71, 19.7% | 17/71, 23.9% |
| Not assessed                       |           57 |           54 |
| Inapplicable                       |            0 |            0 |
| Experimental impact-weighted score |     70.1/100 |     61.8/100 |
| Full guidelines verified           |            0 |            0 |

The denominator includes unresolved attempted checks. These are **scoped evidence scores**, not whole-site conformance or calibrated rankings of sustainability. In particular, the sites have different checked sets, so the scores are not a controlled head-to-head comparison. See the [scoring method and ACT/STAR research](../knowledge-base/audit-scoring.md).

The method currently defines bounded expectations for **21 of 71 guideline groups (29.6%)**. That is its expected supported scope, not 21 fully testable guidelines. The available evidence supports attempting 14 groups for the guide and 17 for Wagtail.org; unsupported groups remain in the full register. No current group has complete success-criterion coverage.

| WSG section          | Supported scoped groups / all groups | What current checks can establish                                                                                             | How to increase coverage                                                                                                       |
| -------------------- | -----------------------------------: | ----------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| User experience      |                                 6/17 | Bounded journeys, delivered media, no-JavaScript behavior, observed resource failures; font readability can remain unresolved | Complete search, playback and recovery tasks; constrained loading, high-DPR legibility, assistive use and owner/user judgments |
| Web development      |                                 9/16 | Sampled semantics/metadata, initialization preferences, search requests, media loading and expected files                     | Active motion/live preferences, useful metadata, dependency/build analysis, verified source deployment and backend profiling   |
| Hosting and systems  |                                 3/12 | Sampled public-asset cache reuse, text compression and 404 recovery affordances                                               | Matched hosting evidence, utilization, backups/restore, data processing and infrastructure records                             |
| Business and product |                                 3/26 | Scoped footprint/privacy disclosures and supplied source licensing                                                            | Retention/deletion execution, procurement, supplier evidence, governance, targets and maintenance records                      |

The exact supported IDs, expectation text, review role and WSG links live in `audit/rubric.json`. The [scored register](assets/scored-audits.json) lists all 71 guidelines per site, judgments, unknowns, and remaining tests. The earlier [scope register](scope-extension.md) remains evidence-inventory history; it is not silently rewritten as a conformance assessment.

## Current STAR coverage

| STAR stage           | Implemented now                                                                                            | Remaining work                                                                                                                                      |
| -------------------- | ---------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Define scope         | Exact origins, page/state profiles, public-first evidence, optional supplied source                        | Agree service boundaries and a support baseline with the owner; identify important restricted processes                                             |
| Explore              | Sitemap/robots inventory, technology detection, footprint/policy discovery, source candidates              | Verify template and functional inventories, third-party purposes and organizational applicability                                                   |
| Test or sample       | Purposeful pages, two reproducible additional URLs per site, selected state probes                         | Broaden template/state selection and complete interactions on selected pages; current 6/156 and 7/525 content-page samples are deliberately limited |
| Audit selected pages | Deterministic observations plus evidence-linked skill judgments                                            | Criterion-level evaluation, non-interference checks, user validation and operational evidence                                                       |
| Report               | Separate reports, methodology, source digests, scores with unknowns, annual scenarios and next audit steps | Owner verification and repeat campaigns under the same protocol                                                                                     |

These are stage-level implementation descriptions, not “five stages passed” or a STAR conformance percentage. The [sampling note](scope-extension.md) explains the departure from comprehensive evaluation. Website boundary, selected-page states, evidence depth, and guideline breadth are independent coverage dimensions.

## Skills and orchestration

| Skill                                   | Decisions it contributes                                                                                               |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `sustainability-audit`                  | Coordinator: scope, evidence collection, review roles, reconciliation, calculation, reporting, and next auditing steps |
| `sustainability-evidence-review` 0.4.0  | Quantitative interpretation: phases, completeness, units, model boundaries and annual-scenario labeling                |
| `sustainability-guideline-review` 0.1.0 | Applicability, scoped pass/fail/unknown judgments, aggregation rules and evidence required to resolve them             |
| `sustainability-claims-review` 0.1.0    | Disclosure scope, annual-estimate assumptions, source corroboration and recommendation usefulness                      |

The current forward test delegated one site per reviewer, each applying the three review roles. It did not use separate workers for every role or test a benefit from delegation itself. The coordinator skill also supports sequential execution when the harness lacks subagents. Instructions and file-based packets are portable; installations can differ between Codex, Claude Code, OpenCode/pi. Only the Codex-based workflow and these Sol reviews were executed here; cross-harness equivalence remains unvalidated.

The reviews uncovered an additional Wagtail.org finding: customer logos at about 3,198 CSS pixels were requested before scrolling. The reviewer classified the scoped deferral check as failed with medium confidence, while preserving the existing video deferral and recommending validation before changing image behavior. This is a qualitative interpretation of measured evidence, not a new byte capture. The guide's eager instructional screenshots remained unresolved because their instructional/legibility prerequisites differ.

The [published skill reviews](assets/skill-reviews.json) preserve original row judgments, recommendations, skill/rubric hashes and an evidence index. Each citation resolves to an existing artifact node and its digest. Source relationships remain candidates unless deployment identity is attested. The score calculator rejects unresolved evidence references and stale rubric/source provenance.

## Annual footprint scenarios

| Scenario                                    |                                Guide |          Wagtail.org |
| ------------------------------------------- | -----------------------------------: | -------------------: |
| CrUX-derived annual pageviews               |                              244,734 |              572,851 |
| Equal sampled-page mix estimate             |                  **5.3 kgCO2e/year** | **65.1 kgCO2e/year** |
| All views at lowest sampled page intensity  |                      2.1 kgCO2e/year |     50.1 kgCO2e/year |
| All views at highest sampled page intensity |                      8.4 kgCO2e/year |     80.2 kgCO2e/year |
| Transfer inputs                             | Complete within the bounded protocol |              Partial |

The [annual artifact](assets/annual-footprints.json) combines September 2026 CrUX rank buckets, the supplied cohort mapping, and CO2.js 0.19.0/SWDM v4. It averages initial-load branches within each page, then gives the two page URLs equal weight. This is a declared proxy for an unknown real page mix, with 100% first visits and unverified hosting modeled as non-green. It estimates browsing-related operational and embodied emissions for one hypothetical year, not a calendar-year measurement or a complete organizational footprint.

The low/high values vary only which sampled page represents every view. They are not statistical confidence intervals or bounds on the site's true footprint. The traffic estimate, unmeasured pages, revisits, scrolling/playback and partial accounting can all materially change results. Wagtail.org's estimate does not enable a DCR badge; measured CPU-package energy is kept separate. Owner analytics and a traffic-weighted page/state mix are the next useful refinements.

## Methodology and reproducibility

```sh
# Prepare portable packets; an agent applies the named skills to each packet.
uv run --locked --script audit/reviews.py --prepare .audit-work/review-packets
# Publish completed JSON reviews after coordinator inspection.
uv run --locked --script audit/reviews.py \
  --inputs .audit-work/scored-reviews/guide.json .audit-work/scored-reviews/wagtail.json \
  --reviewer-model 'GPT-6.1 Sol / low; separate subagent per site'
npx prettier --write docs/initial-implementation/assets/skill-reviews.json
uv run --locked --script audit/assess.py
uv run --locked --script audit/annual.py
npx prettier --write docs/initial-implementation/assets/scored-audits.json \
  docs/initial-implementation/assets/annual-footprints.json
uv run --locked --script audit/report.py
```

The first two commands require new reviewer output to reproduce an LLM judgment; the remaining commands recalculate from published artifacts without model calls or site traffic. Frozen calculations are repeatable; live collection and model reviews can vary. Do not edit a review's expectations and reuse its old rubric digest: create a new review campaign.

The [new methodology benchmark](methodology-benchmark.md) tests these distinctions with both configured model arms. The [backlog](backlog.md) tracks independent owner review, broader task coverage, and held-out evaluation before claiming the new skills improve accuracy.
