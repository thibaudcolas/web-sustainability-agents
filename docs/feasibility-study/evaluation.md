# Evaluation and methodology improvement

**The evaluation target is a correct, useful, evidence-supported audit.** A schema-valid response, a plausible explanation, or a passing tool execution is insufficient. This plan is proposed; no results below are claimed as measured.

The selected implementation direction is [Harbor for the overall benchmark](../evaluation/design.md), with Inspect AI or Promptfoo only where they improve narrower diagnostics. Every model-bearing release campaign includes Neuralwatt DeepSeek V4.1 Flash and Codex; compare Jev and Neuralwatt Clef Flash on suitable typed decisions. The [provider plan](../evaluation/models.md) separates model effects from harness effects and specifies resource accounting.

## Questions the evaluation must answer

1. Does the system find real issues and avoid unsupported ones?
2. Does it distinguish inapplicability, missing evidence, and actual failure?
3. Do its conclusions follow from the captured evidence and the pinned requirements?
4. Are recommendations useful without harming task completion, accessibility, privacy, or security?
5. Does additional agent or model complexity improve quality or reduce total effort?
6. Can repeated runs distinguish website changes from methodology and model changes?

Anthropic's [agent evaluation guidance](https://www.anthropic.com/research/demystifying-evals-for-ai-agents) distinguishes tasks, trials, graders, and transcripts, and discusses code, model, and human grading. Use those distinctions, while keeping the audit's final artifacts and observed actions as the main evidence of success.

## Evaluation layers

| Layer                       | Test material                                                    | Grade                                                         |
| --------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------- |
| Source ingestion            | Pinned WSG/STAR data, changed IDs, missing fixtures              | Exact counts, integrity, explicit migration failures          |
| Deterministic checks        | Controlled responses, traces, source files, and known budgets    | Exact expected outcomes and units                             |
| Retrieval and applicability | Relevant and irrelevant documents; applicable and exempt targets | Retrieval recall and applicability confusion matrix           |
| Semantic decisions          | Human-labeled evidence/claim pairs                               | Accuracy, per-class precision/recall, calibration, abstention |
| Specialist reviews          | Hidden defects, clean cases, and ambiguous cases                 | Finding quality, evidence support, recommendation safety      |
| Orchestration               | Missing tools, rate limits, partial workers, conflicting outputs | Budget compliance, recovery, correct incomplete status        |
| End-to-end audits           | Frozen sites and bounded live journeys                           | Adjudicated precision/recall, coverage, usability, cost       |
| Interventions               | Before/after changes under matched conditions                    | Resource change, successful task completion, regressions      |

Run deterministic contract checks on every relevant change. Run small model regressions on prompt or adapter changes. Use a larger frozen evaluation for releases and periodic live-site evaluations for drift. Keep network-free replay separate from live collection so failures can be localized.

## Collection and instrumentation experiments

The [tool review](../knowledge-base/deterministic-tools.md) and [local decision-model examples](decision-model-examples.md) identify a separate question: does the collector obtain valid, sufficient evidence? Compare scripted Playwright with an established measurement harness or an adaptive driver before attributing differences to the reviewer.

Use controlled fixtures with known request/state behavior. Include cold/warm cache, revalidation, compression, deferred media, consent differences, service workers, persistent polling, and inaccessible or unsupported controls. Assert observed requests and task outcomes, with tolerances for noisy measurements. Test adapter failures and missing fields explicitly.

Add negative controls for instrumentation: request routing that disables caching, injected diagnostic traffic, animation-suppression styles, focus emulation, and state changes from accessibility probes. A collector should record or reject an incompatible profile rather than silently interpret the altered behavior as the site's baseline. Preserve separate diagnostic and measurement runs where necessary.

For adaptive drivers, keep the task, starting state, allowed actions, budgets, and independent success assertion fixed. Record completion rate, evidence recall, incorrect actions, retries, unsupported states, latency, requests, and artifact size. Verify completion from application state rather than the driver's `DONE` answer. Compare fixed observation windows for application measurements; report time spent waiting for model decisions separately because it changes exposure to polling and other background work.

For semantic reviewers, freeze the evidence across methods. Evaluate batching layout, model version, prompt, and acceptance threshold as separate changes. Cache keys must include relevant evidence and rubric versions; preserve raw repeated-trial results outside a cache that overwrites entries. Report performance both conditional on successful collection and across all attempted tasks, so collection failures do not disappear from the denominator.

## Corpus and reference judgments

Start by implementing and validating the twelve case families in the [benchmark seed plan](../initial-implementation/assets/benchmark-plan.json), then expand to a development corpus of 60–100 cases spread across a few pilot rules. Include passing, failing, inapplicable, insufficient-evidence, and collection-error cases. A larger dataset is required before making strong accuracy claims.

Include at least these case families:

- Public-only audits paired with matching, stale, irrelevant, and contradictory source/internal evidence; keep related variants in one split.
- Digital Carbon Rating calculation boundaries and misleading attempts to turn a page rating into WSG or physical-emissions assurance.

- Static content, commerce, authenticated applications, multilingual sites, and media-heavy pages.
- Necessary versus decorative media; genuine lazy loading versus attributes with eager requests.
- Already compressed files; authorization-dependent caching; third parties required for a task.
- Policies with actual records, policies with aspirations, outdated disclosures, contradictory documents, and plausible but unsupported claims.
- Non-English evidence, long documents, altered option order, irrelevant text, and missing source spans.
- Prompt injection in HTML or policy text, malicious instructions in metadata, inaccessible states, and partial traces.
- Clean examples and beneficial exceptions, including accessibility or resilience features that consume resources.

Use STAR fixtures as inspiration and expand them with paired negative and exempt examples. The [ACT test-case guidance](https://act-rules.github.io/pages/design/test-cases/) supports testing each applicability and expectation condition. Keep answer keys, comments, filenames that reveal labels, and reviewer notes outside the agent's accessible evidence.

Split by site, template family, and organization where possible. Near-identical pages from one template must not appear in both development and held-out sets. Preserve a locked test set; use a separate validation set for threshold selection. Repeatedly tuning against the final test set invalidates its role.

Have two reviewers independently label semantic cases, then adjudicate disagreements. Include sustainability expertise and relevant UX, accessibility, or infrastructure knowledge. Retain initial labels, disagreement reasons, and unresolved cases. An unresolved normative dispute should not be converted into a fabricated ground truth.

Grade findings by rule, target, state, and evidence, with documented matching rules. Do not require exact wording. Independently inspect unmatched findings before calling them false positives. Test the grader with deliberately duplicated findings, wrong locations, and paraphrases. The [local accessibility evaluation](../knowledge-base/local-projects.md#accessibility-agents) provides a useful starting example and a warning about matching errors.

## Controlled comparisons

| Configuration                        | What it tests                                         |
| ------------------------------------ | ----------------------------------------------------- |
| Rules only                           | Value and limits of automated evidence checks         |
| Rules plus one LLM reviewer          | Baseline semantic assistance                          |
| Rules plus specialist LLM sub-agents | Value of specialization and orchestration             |
| Rules plus Jev                       | Quality of narrow typed judgments                     |
| Rules plus Clef                      | Provider/model comparison on the same questions       |
| Rules plus a decision-model cascade  | Quality and savings after escalation and review costs |
| Human reference review               | Independent quality reference and effort comparison   |

Freeze evidence, scope, rules, and label definitions for the comparison. Compare both total quality and the semantic subset; rules-only abstention is not a classification error, but it reduces automated coverage. Give generative configurations comparable budgets and report actual usage.

Repeat stochastic configurations on the same cases. Record the distribution of outcomes, not only the best run. Multi-agent agreement is not a vote that guarantees correctness: shared evidence, prompts, and model training can create correlated errors.

Use paired comparisons on identical cases. For confidence intervals, resample at the site or template level when examples are correlated. Report per-domain results and sample sizes so an overall improvement cannot hide a governance or accessibility regression.

## Metrics and denominators

| Metric                 | Definition or purpose                                                                   |
| ---------------------- | --------------------------------------------------------------------------------------- |
| Finding precision      | Adjudicated true findings divided by all adjudicated reported findings                  |
| Finding recall         | Detected reference findings divided by all known reference findings                     |
| Unsupported-pass rate  | False criterion passes divided by all criterion passes; report counts too               |
| Missed-failure rate    | Actual failing cases not identified as failures divided by all actual failing cases     |
| Evidence validity      | Findings with real, correctly located, supporting evidence divided by reviewed findings |
| Applicability accuracy | Correct applicable/inapplicable/undetermined decisions by class                         |
| Coverage               | Counts by requirement, state, applicability, and execution status                       |
| Selective risk         | Error rate among automatically accepted decisions as acceptance coverage changes        |
| Calibration            | Brier score, log loss, and reliability plots on held-out labeled cases                  |
| Stability              | Decision flips and finding-set differences across repeated identical runs               |
| Human effort           | Review and adjudication minutes per audit and accepted finding                          |
| Cost and latency       | Total cost and median/tail latency, including all retries and escalations               |
| Recommendation outcome | Accepted useful changes, measured task/resource effects, and regressions                |

Precision is not the same as accuracy; the rare failure class matters. Calibration should be evaluated on the actual downstream decision, not inferred from a vendor's confidence field. Reliability plots with very few cases per bin are weak evidence; include uncertainty and class prevalence.

A favorable average score must not compensate for a fabricated citation or a recommendation that exposes private cached content. Track serious errors separately.

## Proposed release gates

The following are initial engineering policies to negotiate and validate, not WSG requirements or demonstrated service levels:

- All deterministic fixtures, schema checks, evidence-resolution checks, and source-migration checks pass.
- No fabricated evidence references, silent unknown-to-pass conversions, answer-key leaks, or out-of-scope actions occur in the release suite.
- Every scoped check ends with an explicit applicability and execution status, including interrupted runs.
- The candidate shows no unresolved serious recommendation regression on the paired review set.
- Automatic semantic acceptance is enabled only for rule families with enough held-out evidence to support the agreed precision and selective-risk target.
- Added agents or model calls have a documented quality or effort benefit at the accepted operational budget.

For illustration, observing zero errors in 100 independent accepted decisions still gives an approximate 95% upper error bound of 3%, using the rule of three. Correlated cases weaken that reassurance further. A small pilot therefore cannot substantiate a 99% reliability promise simply because it observed no errors.

## Changing the methodology without hiding regressions

Version the source inventory, criterion aliases, rule mappings, sampling policy, capture tools, prompts, model deployment, thresholds, aggregation logic, labels, and grader. A release manifest should identify all of them.

For each proposed change:

1. State the intended improvement and the failure cases motivating it.
2. Classify the change as a source update, interpretation change, collector change, model change, or bug fix.
3. Run old and new methods on the same captured evidence where possible.
4. Review newly failing, newly passing, newly unknown, and newly excluded cases.
5. Change reference labels only through independent adjudication, with a reason and retained history.
6. Publish the paired evaluation, affected coverage, accepted tradeoffs, and rollback point.

If the definition of a requirement changes, report results against both the previous and revised labels when meaningful. Do not relabel the test set to make the new method appear better. If a collector update needs new evidence, separate the collection effect from the reviewer effect.

Prioritization-weight changes can often be evaluated by replaying saved judgments without fresh inference. Prompt or criterion-meaning changes usually require re-evaluating judgments. This separation makes methodology experimentation cheaper and easier to interpret.

## Evals are also fallible

Use code for exact facts, independently labeled cases for semantic truth, and model graders for bounded assistance where calibrated against people. Do not make the same model both auditor and sole judge of its output.

Log observable actions, tool results, intermediate artifacts, model responses, and final findings. Private internal reasoning is not required to reproduce an audit. Classify failures as collection, retrieval, applicability, interpretation, orchestration, reporting, or grading errors before changing the prompt.

Finally, distinguish **better auditing** from **better sustainability outcomes**. The former is demonstrated by accurate, useful findings. The latter needs implemented changes, comparable measurements, and evidence that the service still meets user needs.
