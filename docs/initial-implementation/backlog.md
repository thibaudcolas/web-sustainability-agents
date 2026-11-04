# Implementation backlog and sequencing

Keep accepted feedback attached to the evidence, collector, review rule, or evaluator that must change. This backlog separates the current experiments from later validation. A finding's usefulness and its measurement correctness can fail independently.

## Sequence

1. Establish per-site report and data contracts, so judgments have stable scope and units.
2. Add bounded energy and traffic enrichment with explicit provenance and uncertainty.
3. Freeze expanded development cases; validate oracle and negative controls; compare Sol/low and Neuralwatt DeepSeek/high on identical inputs.
4. Broaden WSG/STAR investigation using the tested distinctions, retaining unknowns and sample limits.
5. Independently review labels and recommendations before claiming quality improvements or introducing an aggregate score.

The current task follows this sequence. It is not necessary to finish every future research question before gathering useful evidence.

## Follow-up experiments

| ID  | Idea and component                                                                | Validation needed before adoption                                                                                   | Priority                                  |
| --- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| B01 | Independent byte accounting, including frames, 204 aborts, workers, and streaming | Compare matching Chromium states against another collector; preserve resource failures                              | Next measurement gate                     |
| B02 | Match co2-runner and sitespeed.io energy protocols                                | Same browser, hardware, journey, duration, counter domains, and first-sample treatment; sequential repeated runs    | Next energy gate                          |
| B03 | Baseline-adjusted and phase-specific hardware energy                              | Validate idle baseline and phase boundaries; retain startup/shutdown separately; do not add overlapping counters    | After B02                                 |
| B04 | CrUX-to-pageviews calibration beyond US government sites                          | Owner analytics with matched origin and period, held-out sites, dispersion and calibration error                    | Before traffic estimates drive priorities |
| B05 | Annual impact scenarios                                                           | Representative page mix, visits versus views, repeat visits, grid assumptions, and explicit scenario ranges         | After B04                                 |
| B06 | Autonomous repository discovery                                                   | Known deployment provenance; held-out expected locations; compare public-only, supplied excerpts, and full checkout | After bounded evidence comparison         |
| B07 | Recommendation quality evaluator                                                  | Independent owner labels for usefulness, correctness, accessibility, prerequisites, and avoidable regressions       | Before claiming model superiority         |
| B08 | Knowledge benchmark beyond observed examples                                      | WSG/STAR interpretation and legitimate exceptions, protected labels, held-out versions, contamination checks        | Next benchmark expansion                  |
| B09 | Broader STAR sampling                                                             | Site inventory, template and complete-process coverage, mobile/assistive contexts, random sample and rationale      | Before whole-site conclusions             |
| B10 | Clef/Jev routing and model selection                                              | Calibrated typed decisions, abstention, cost/quality comparison against the same unrouted baseline                  | After review baseline stabilizes          |
| B11 | Inference energy and cost accounting                                              | Reconcile full Harbor campaign requests against Neuralwatt usage; distinguish missing values from zero              | Before efficiency claims                  |
| B12 | Charts and report presentation                                                    | Stable long-form data, accessible alternatives, honest partial/unknown states, no cumulative double counting        | Data contract first                       |
| B13 | Aggregate sustainability score                                                    | Defensible dimensions and weights, unknown/applicability handling, independent validation; avoid conformance claims | Deferred                                  |
| B14 | Portable orchestration across agent harnesses                                     | Same skills/contracts and controlled evidence under Codex, Claude Code, OpenCode/pi                                 | After task contract stabilizes            |
| B15 | First load versus successful task cost                                            | Consent enforcement, search fallback, screenshot readability at high DPR, usable video activation                   | Expand interaction fixtures               |

## Feedback routing

| Owner feedback                            | Pipeline location                        | Regression                                                                  |
| ----------------------------------------- | ---------------------------------------- | --------------------------------------------------------------------------- |
| First-load figures, KB/MB, separate sites | Collector phases and report export       | Origin isolation, units, immutable initial snapshot                         |
| Plausible is contextual                   | Resource accounting and prioritization   | Measured error response versus unknown failed-transfer bytes                |
| Discover published footprints             | Discovery and qualitative review         | Missing, malformed, stale, and differently scoped disclosures               |
| Adapt advice to technology                | Wappalyzer adapter and review rubric     | Fingerprint without execution; CMS source location without deployment proof |
| Source or fix is wrong                    | Provenance and recommendation review     | Matching, unknown, stale, and contradictory source                          |
| Energy number looks unexpectedly large    | Counter validation and experiment design | System-wide scope, overlapping domains, startup time, missing samples       |
| Rank-derived traffic looks implausible    | Traffic enrichment and calibration       | Origin mismatch, restricted lookup coverage, cross-population extrapolation |

Historical artifacts and model outcomes stay frozen. Corrections create a new rubric or case version; they do not rewrite old results. A benchmark success on author-created development cases is not an independent accuracy estimate.
