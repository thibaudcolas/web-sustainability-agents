# Implementation backlog and sequencing

Keep accepted feedback attached to the evidence, collector, review rule, or evaluator that must change. This backlog separates the current experiments from later validation. A finding's usefulness and its measurement correctness can fail independently.

## Sequence

1. Establish per-site report and data contracts, so judgments have stable scope and units.
2. Add bounded energy and traffic enrichment with explicit provenance and uncertainty.
3. Freeze expanded development cases; validate oracle and negative controls; compare Sol/high and Neuralwatt DeepSeek/high on identical inputs.
4. Broaden WSG/STAR investigation using the tested distinctions, retaining unknowns and sample limits.
5. Independently review labels, scoped-score expectations and recommendations before claiming quality improvements or calibrated site rankings.

The current task follows this sequence. It is not necessary to finish every future research question before gathering useful evidence.

## Follow-up experiments

| ID  | Idea and component                                                                | Validation needed before adoption                                                                                   | Priority                                    |
| --- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- | ------------------------------------------- |
| B01 | Independent byte accounting, including frames, 204 aborts, workers, and streaming | Compare matching Chromium states against another collector; preserve resource failures                              | Next measurement gate                       |
| B02 | Match co2-runner and sitespeed.io energy protocols                                | Same browser, hardware, journey, duration, counter domains, and first-sample treatment; sequential repeated runs    | Next energy gate                            |
| B03 | Baseline-adjusted and phase-specific hardware energy                              | Validate idle baseline and phase boundaries; retain startup/shutdown separately; do not add overlapping counters    | After B02                                   |
| B04 | CrUX-to-pageviews calibration beyond US government sites                          | Owner analytics with matched origin and period, held-out sites, dispersion and calibration error                    | Before traffic estimates drive priorities   |
| B05 | Annual impact scenarios                                                           | Representative page mix, visits versus views, repeat visits, grid assumptions, and explicit scenario ranges         | After B04                                   |
| B06 | Autonomous repository discovery                                                   | Known deployment provenance; held-out expected locations; compare public-only, supplied excerpts, and full checkout | After bounded evidence comparison           |
| B07 | Recommendation quality evaluator                                                  | Independent owner labels for usefulness, correctness, accessibility, prerequisites, and avoidable regressions       | Before claiming model superiority           |
| B08 | Knowledge benchmark beyond observed examples                                      | WSG/STAR interpretation and legitimate exceptions, protected labels, held-out versions, contamination checks        | Next benchmark expansion                    |
| B09 | Broader STAR sampling                                                             | Site inventory, template and complete-process coverage, mobile/assistive contexts, random sample and rationale      | Before whole-site conclusions               |
| B10 | Clef/Jev routing and model selection                                              | Calibrated typed decisions, abstention, cost/quality comparison against the same unrouted baseline                  | After review baseline stabilizes            |
| B11 | Inference energy and cost accounting                                              | Reconcile full Harbor campaign requests against Neuralwatt usage; distinguish missing values from zero              | Before efficiency claims                    |
| B12 | Charts and report presentation                                                    | Stable long-form data, accessible alternatives, honest partial/unknown states, no cumulative double counting        | Data contract first                         |
| B13 | Validate the implemented scoped audit score                                       | Independent rubric/applicability review, sensitivity to sampling and weighting, no conformance claim                | Provisional implementation; validation next |
| B14 | Portable orchestration across agent harnesses                                     | Same skills/contracts and controlled evidence under Codex, Claude Code, OpenCode/pi                                 | After task contract stabilizes              |
| B15 | First load versus successful task cost                                            | Consent enforcement, search fallback, screenshot readability at high DPR, usable video activation                   | Expand interaction fixtures                 |

## Benchmark execution efficiency

**B16:** Preinstall the pinned Codex adapter dependencies in a reusable environment image. The expanded campaign repeatedly installs OS packages in each trial; setup currently dominates model review time. Validate that the rebuilt environment preserves task inputs, reference isolation, and model settings before comparing its runtime or energy. Do not change task images during an active campaign. One trial also failed before inference because npm omitted Codex’s platform binary; record setup failures separately and allow a bounded unchanged-input retry.

The broader campaign adds two Sol setup failures: another missing platform binary and a temporary Debian package-resolution failure. Both passed unchanged-input retries. Prioritize the reusable image before another full campaign; preserve these exceptions separately from model errors.

The new [setup investigation](assets/benchmark-setup-review.json) verifies that Harbor 0.23.0 already skips all dependency installation when `codex --version` matches the requested version. A clean image containing Codex 0.166.0 can therefore avoid repeated apt/NVM/npm setup without an adapter patch. Pin the effective Node 22 runtime deliberately: the current task image starts on Node 24, but Harbor installs Node 22 during setup. Add Dockerfile and resolved image identity to future paired-provenance checks, keep authentication outside images, and never reuse a completed trial container as the clean base. The skip path was checked against the installed adapter with a fake environment; no end-to-end speedup is claimed yet. Source: [Harbor 0.23.0 Codex installer](https://github.com/harbor-framework/harbor/blob/v0.23.0/src/harbor/agents/installed/codex.py#L328-L381).

## Judgment labels

**B17:** Separate direct site-state propositions from evidence-sufficiency questions in the benchmark schema. Both model arms can preserve the correct unknown value and sensible advice while choosing different `fail`/`inconclusive` labels for phrases such as “known to be zero” or “attributable solely.” Preserve original scores and explanations; independently review the question contract before accepting alternative labels or rerunning models. A label mismatch is not automatically a harmful recommendation.

The [broader case review](breadth-review-cases.md) reproduces this problem for the claim that a deployed dependency version is unresolved. Add an explicit question mode in a new version. Separately distinguish an observed-event counter from an unmeasured outcome: both models returned null for successful submissions when the reference expected zero recorded successes, without an explicit counter in the facts.

The new scope cases expose two more recommendation-label ambiguities: reporting area scores does not establish an existing practice to “preserve,” and keeping a working route while requesting a baseline combines two actions. Future cases should separate proposal support from the site-action category and use atomic recommendations. Keep the current strict grades and model explanations; post-hoc interpretation is not a corrected accuracy estimate.

## Feedback routing

**B18:** Keep traffic-scenario prerequisites deterministic. The expanded DeepSeek run assigned an unranked extrapolation after a top-million-only lookup. Require an explicit matched rank bucket or a separately justified unranked population before selecting a mapping row; test incomplete, stale, and cross-origin lookup results. A model calling a number a scenario is insufficient validation.

**B19:** Turn the broader live sample into controlled interpretation cases before the next model campaign: initial versus live preference changes, root-path 404 versus a working declared manifest, policy-route redirects, localized error-page language, and licensing of code versus content. Add completed recovery tasks and owner-reviewed recommendations; keep development examples separate from held-out cases.

The [methodology benchmark](methodology-benchmark.md) implements ten new development cases covering those distinctions, annual estimates, and scoring. The [skill-guided workflow](skill-audit-workflow.md) now produces scoped judgments and scores; this is an implemented baseline, not independent proof of improvement.

**B20:** Compare the same evidence with and without specialist skills, holding model, reasoning, tool access and output contract fixed. Use blinded owner-reviewed recommendations and held-out cases; measure whether skills reduce unsupported advice and improve useful next investigations. The current skill forward tests demonstrate execution, not a causal advantage over a no-skill baseline.

**B21:** Review the distinction between eager instructional screenshots and below-fold customer logos. Create matched counterexamples with task context, request timing, native lazy-loading thresholds, legibility and intended rendering. Preserve medium-confidence reviewer judgments and disagreements rather than turning every offscreen request into a universal failure.

**B22:** Separate recommendation operations from their justification in the evaluation schema. A proposal that both preserves working behavior and investigates an unknown can legitimately invite multiple actions; publishing an estimate also does not fit a site-remediation verb cleanly. Use single-action proposals or an explicitly defined action set in a new case version. Preserve the current frozen labels/results and have an independent reviewer judge whether disagreements affect actual advice.

| Owner feedback                            | Pipeline location                        | Regression                                                                  |
| ----------------------------------------- | ---------------------------------------- | --------------------------------------------------------------------------- |
| First-load figures, kB/MB, separate sites | Collector phases and report export       | Origin isolation, units, immutable initial snapshot                         |
| Plausible is contextual                   | Resource accounting and prioritization   | Measured error response versus unknown failed-transfer bytes                |
| Discover published footprints             | Discovery and qualitative review         | Missing, malformed, stale, and differently scoped disclosures               |
| Adapt advice to technology                | Wappalyzer adapter and review rubric     | Fingerprint without execution; CMS source location without deployment proof |
| Source or fix is wrong                    | Provenance and recommendation review     | Matching, unknown, stale, and contradictory source                          |
| Energy number looks unexpectedly large    | Counter validation and experiment design | System-wide scope, overlapping domains, startup time, missing samples       |
| Rank-derived traffic looks implausible    | Traffic enrichment and calibration       | Origin mismatch, restricted lookup coverage, cross-population extrapolation |

Historical artifacts and model outcomes stay frozen. Corrections create a new rubric or case version; they do not rewrite old results. A benchmark success on author-created development cases is not an independent accuracy estimate.

## Repeatable collection and broader interpretation

**B23:** The pinned GreenFrame run now has three complete repetitions for three pages on each site, with image/browser provenance and separate client-device and network estimates. Next validate matched interaction scenarios, a current browser and sensitivity to the synthetic screen/CPU coefficients under controlled idle conditions. The shared-workstation sample and its older browser support reproducible model experiments, not device-independent rankings. See the [energy experiment](energy-traffic-experiment.md).

**B24:** Add carbon.txt schema validation and scoped provider corroboration after the current declaration interpreter. Test DNS/header delegation, conflicting documents, expired reporting periods, unknown versions and parent/subdomain relationships. A schema-valid declaration still cannot establish green hosting by itself.

**B25:** Work through the [current WSG auditability classifications](../knowledge-base/assessment-crosswalk.md) by criterion class, evidence access and check family. Prioritize completed public tasks, keyboard/forms, constrained media/font tests and document alternatives. Then add source/build/dependency evidence and owner records for organizational execution. Manual quantitative and qualitative checks belong in the agent workflow; they are not automatically excluded from automation.

**B26:** Extend the new session packet's provenance resolver to source excerpts, screenshots and independently retrieved proof documents before including them in its score. Retain source revision, dirty status and deployment relationship. Public observations and supplemental source recommendations already remain distinguishable.

The expanded catalog now includes ten contextual skill checks alongside browser and source checks. These cover eight more guideline groups, with bounded public or owner-record evidence and unresolved requests. Both live reports include a completed public journey and selected source evidence with revision, dirty status, content hashes and unknown deployment identity. This advances B25/B26; full task recovery, screenshot provenance, independently retrieved proof documents and organizational execution records remain open.

**B27:** Run the same frozen agent-triggered task through Codex and another harness, then evaluate with Harbor using Sol/high and Neuralwatt DeepSeek/high. Include scope clarification, actual tool invocation, partial failures and evidence citation in the verifier; the prior frozen-evidence campaigns do not test these behaviors. Preserve the existing benchmark skills in `benchmarks/frozen-methodology-skills/` when current skills evolve.

The broader Harbor campaign validates four collection handoffs per model under Codex, with actual collector calls corroborated in all eight trajectories. Another harness, live scope clarification and complete browser orchestration are still untested. Keep those requirements separate from artifact validation.

## Installation and report delivery

**B28:** Validate the [plugin and CLI experience](../using/README.md): versioned manifests, collector-path resolution, prerequisite checks, persistent session outputs, clean installation and update/uninstall tests. Follow the supplied Wagtail CLI design with one discoverable skill and progressively loaded role instructions. Keep the checkout/skills route available and validate another harness before claiming equivalent support.

**B29:** Make the report renderer independent of the example campaign: derive methodology statements from receipts, handle missing publication manifests, resolve documentation links outside the repo, and export only explicitly matched chart enrichments. Verify a newly collected arbitrary-origin session can become a self-contained review bundle without copying provenance wording from a Wagtail run. Move inspected archive publication into the CLI and enforce one editorial-receipt schema; the fresh audits still needed coordinator-owned packaging.

The new report skill and renderer separate editorial wording from scored judgments, explain evidence in an appendix, use kB and named cookie choices, and validate optional screenshot provenance. The current reports use fresh six-page and seven-page collections, independent Sol/high quantitative, guideline and claims reviewers, explicit reconciliation, and separate Sol/high report writing. Earlier drafts have been removed. Clean installation under another harness and independent recommendation evaluation remain necessary before claiming portability or better audit accuracy.

**B30:** Carry newly discovered, relevant cross-origin disclosures into a linked review supplement without rewriting frozen captures. The fresh main-site sustainability statement names the guide, while the guide’s own bounded discovery did not find that statement. Preserve retrieval provenance and explicit service scope, then re-review affected checks; do not silently transfer a parent policy or score between sites.

## Report feedback validation

**B31:** Evaluate proportionate priority, concise explanations and source excerpts with owner judgments. The current reports use visible WSG descriptions, per-area results, first-visit transfer headlines, median-of-three energy, short captions and a low-priority CI investigation. The new benchmark tests the underlying distinctions, but synthetic answer agreement does not measure how useful the finished report is to an owner.

**B32:** Validate the [proposed qualitative batch](../evaluation/design.md#next-qualitative-validation): explicit question modes and independently reviewed references first; then matched positive, problem, missing, conflicting, wrong-scope and applicability cases. Exercise actual discovery, clarifying questions, representative tasks and recovery in three controlled execution tasks. Use Harbor, Sol/high and Neuralwatt DeepSeek/high; measure supported recommendations and useful evidence requests as well as structured-answer agreement.

**B33:** Compare focused experience/content and governance/lifecycle review instructions with the current general roles and a no-skill baseline. Keep model, evidence, tools and budgets fixed. Promote them to separate audit skills only when they improve independently judged evidence support or recommendation usefulness enough to justify orchestration cost. Context selection and claims review remain shared responsibilities; do not create one agent per WSG criterion.

**B34:** Map the 33 browser/disclosure/source expectations to current criterion IDs and the specific clauses they assess; the ten contextual checks already name criteria. Link each method to execution evidence and benchmark cases, keeping full and partial coverage separate. Use the new 197-criterion inventory to prioritize gaps, not to claim implementation or validation coverage. This mapping precedes a reliable criterion-level coverage percentage.
