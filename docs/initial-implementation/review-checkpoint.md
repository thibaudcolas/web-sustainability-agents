---
search:
  boost: 0.5
---

# Model and real-site review checkpoint

!!! note "Historical experiment"

    This page preserves an earlier method and its results. Use the [current audit guide](../using/README.md) for instructions, [reports](../reports/README.md) for the latest site findings, and [evaluation](../evaluation/README.md) for model comparisons.

The active baseline uses **Codex CLI 0.166.0 for both model arms**: GPT-6.1 Sol with low reasoning, and Neuralwatt DeepSeek V4.1 Flash with high reasoning. OpenCode is no longer the default benchmark harness. The historical Astra/low and OpenCode/DeepSeek/low results remain unchanged in the [first experiment](first-slice.md#initial-benchmark-results).

This page records the model comparison behind an earlier Wagtail audit draft and what the experiment can establish. That draft has since been removed; the [current reports](../reports/README.md) use separate fresh captures.

## Configuration and compatibility

| Arm            | Requested model                  | Reasoning | Authentication and transport                                                      |
| -------------- | -------------------------------- | --------- | --------------------------------------------------------------------------------- |
| Codex baseline | `openai/gpt-6.1-sol`             | `low`     | Existing Codex login through `CODEX_AUTH_JSON_PATH`                               |
| Neuralwatt     | `neuralwatt/deepseek-v4.1-flash` | `high`    | Neuralwatt API key, explicit native Codex provider, Neuralwatt Responses endpoint |

The Neuralwatt recipe passes the key in the adapter's `OPENAI_API_KEY` variable because Harbor's Codex adapter resolves that variable. Its explicit provider points to `https://api.neuralwatt.com/v1`; the request is routed to Neuralwatt. No OpenAI key or Codex login is required for that arm. Credentials are never committed.

The local model catalog includes `gpt-6.1-sol`. Official [Sol documentation](https://developers.openai.com/api/docs/models/gpt-6.1-sol) and [Neuralwatt Responses documentation](https://docs.neuralwatt.com/api/responses) informed the compatibility check. DeepSeek's [model reference](https://portal.neuralwatt.com/models/deepseek-v4.1-flash) documents its reasoning controls. The benchmark explicitly requests high; a command-line setting and successful response do not independently measure the provider's internal reasoning budget or freeze served weights.

A standalone Chat Completions tool-call preflight succeeded with high reasoning; its [sanitized response](assets/provider-high-preflight.json) preserves requested effort, served model, token usage, and request-level energy attribution. A separate Harbor/Codex preflight successfully used the Responses transport, wrote its report, passed the frozen-evidence verifier, and completed with no trial error. This replaces the unsuccessful OpenCode integration for the active configuration; it does not explain or repair OpenCode's historical `EPIPE` failures.

Harbor's installed pi adapter was inspected as an alternative. In version 0.23.0 its generated custom-model entry contains an ID but no explicit reasoning capability metadata. That needs validation or a small adapter extension before claiming a custom DeepSeek model honors `--thinking high`. We did not run a pi campaign or establish that pi cannot support this model.

The shared evidence-review skill and task contract remain harness-independent. Using one harness here reduces one comparison variable; it does not establish portability to every harness, or make the two reasoning settings equivalent compute budgets. Astra/low remains a valid historical arm rather than being silently relabeled as Sol.

## Two levels of comparison

The six controlled development cases reuse the original frozen corpus and revised question wording. Their labels test narrow evidence distinctions. A second pair of tasks uses the actual Wagtail evidence: one public-only, one with selected source excerpts. Both ask nine bounded questions about analytics, media, caching, arithmetic, source identity, and organizational unknowns.

For each real-site mode, both models receive the same frozen input and instructions. The source-assisted task adds the supplied excerpts while preserving the public observations and questions. Neither model receives the coordinator's WIP report. These tasks test interpretation of curated evidence; they do not test autonomous browsing, discovering files in an entire checkout, or independently finding which questions to investigate.

The real-site expectations were authored from the observations by the same coordinator writing the report. They are provisional development labels awaiting owner review. The reference/no-operation controls validate execution of the scoring contract, not the truth of those labels. The grader checks outcomes, required evidence IDs, allowed citations, and unchanged rating objects; it does not establish that explanations or fixes are semantically sound.

The later opt-out, typography, and overflow follow-ups are included in the WIP report but were not questions in this frozen model-review task. Preserve that distinction when comparing model coverage with the coordinator's final report.

## Results and interpretation

All bounded model runs finished. The [model-switch results](assets/model-switch-results.json) retain the preflight and six-case campaigns, including requested reasoning, input hashes, actual reports, and trial status.

| Campaign                                             |               Accepted reports | Trial errors |
| ---------------------------------------------------- | -----------------------------: | -----------: |
| Codex / Sol, low: six fixtures                       |                         6 of 6 |            0 |
| Codex / Neuralwatt DeepSeek, high: six fixtures      |                         6 of 6 |            0 |
| Sol: public and source-assisted Wagtail reviews      | 2 of 2 after corrected regrade |            0 |
| DeepSeek: public and source-assisted Wagtail reviews | 2 of 2 after corrected regrade |            0 |

The [Wagtail model reports](assets/wagtail-model-reviews.json) preserve both the **original zero rewards** and the corrected artifact regrades. Two grader defects caused those original scores: a fixture-specific two-field rating check rejected the correctly preserved nested page calculations, and a required cold-capture citation rejected equivalent initial-phase observations in the scroll evidence. All four reports already had the expected nine outcomes and unchanged rating data. The correction uses deep structural equality for rating objects and explicit alternative evidence groups for each Wagtail page. It does not excuse fabricated IDs or missing evidence for a required page.

The [initial controls](assets/wagtail-initial-controls.json) preserve the failed original oracle scores and show regrades against their original references with the corrected rating check. Fresh [corrected controls](assets/wagtail-corrected-controls.json) pass both oracle tasks and reject both no-operation tasks through Harbor. Regression tests cover nested trace changes, missing fields, injected fields, equivalent citations, and missing evidence groups. Existing model reports were regraded without rerunning inference; their inputs and original references were not overwritten. Both original and revised references and the current grader digest are published.

For the six fixtures, model-arm input and instruction hashes match case by case. The real-site public inputs match across models, as do the source-assisted inputs. Public and source-assisted inputs intentionally differ. This remains a small, coordinator-authored development set with no held-out accuracy estimate.

### Explanation and recommendation review

The coordinator read all four real-site reports. This is qualitative review by the same agent coordinating the experiment, not an independent human assessment or a calibrated judge score.

| Aspect                            | Sol/low                                                                              | DeepSeek/high                                                                                                                        | Pipeline implication                                                                                                                                           |
| --------------------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Outcomes and carbon data          | Nine expected outcomes in each mode; calculations preserved                          | Same                                                                                                                                 | The narrow grader has reached a ceiling on these cases                                                                                                         |
| PNG filename versus WebP delivery | Explicitly avoids an unsupported conversion recommendation                           | Identifies WebP correctly, but adds filename changes and, in the source report, a conditional suggestion to preserve PNG if required | A false proposition is not necessarily a sustainability defect; do not manufacture a fix for an existing optimization                                          |
| Mobile viewport                   | Does not assert an unsupported viewport height                                       | Public report calls it an 800-pixel mobile viewport; the configured mobile height was 844                                            | Record profile dimensions with every observation and check numeric claims; the old input exposed the global desktop height but omitted the per-review viewport |
| Source identity                   | Keeps deployment unknown and identifies plausible GTM and image-format paths         | Also keeps deployment unknown and offers candidate paths                                                                             | Source excerpts can improve specificity without proving deployment identity                                                                                    |
| Screenshot recommendations        | Suggests lazy loading and responsive renditions, without fully addressing legibility | Suggests lazy loading or activation, without fully addressing legibility                                                             | Require screenshot readability, pixel density, zoom, and full-journey behavior as prerequisites                                                                |
| Analytics necessity               | Does not equate observed requests with unnecessary functionality                     | Same                                                                                                                                 | Preserve the owner-requirements question independently of observed loading                                                                                     |

The collector now includes viewport width, height, and device scale factor in newly recorded review snapshots. The original frozen inputs are retained, so that improvement is not retroactively credited to these runs. An automated claim checker and stronger recommendation rubric remain future work. The WIP audit's recommendations were revised during coordinator synthesis to include these prerequisites; they are not verbatim model output.

Sol produced more restrained image-format advice in this pair, supporting its use as the requested working baseline. That is not enough evidence to rank the models generally or claim that source access improves aggregate accuracy. Both source-assisted reports gained candidate file locations, while both public-only reports appropriately avoided inventing them. Full-checkout discovery was not tested.

### Accounting limits

Harbor reported about $0.2092 for the two Sol real-site reviews. The custom Neuralwatt/Codex arm did not report a reconciled campaign cost, and neither arm has a complete inference-energy ledger. Missing cost is not zero. The standalone Neuralwatt preflight reported 2.21 joules for its one small request; it cannot represent a multi-turn campaign. Published tokens are harness-reported totals, including repeated context across turns, not unique evidence size or a fair quality comparison by themselves.

The large repeated evidence objects also identify an efficiency opportunity: normalize and deduplicate observations before another large campaign, while preserving source IDs and traceability. Validate that a compact evidence view retains the same decisions and important uncertainties.

## Reproduce

Use Harbor 0.23.0, Docker, and the repository's locked Node dependencies. Build the six controlled tasks before the real-site tasks, because the latter reuse their environment and report contract.

```sh
just benchmark-build
node benchmarks/preflight.js
just benchmark-codex
just benchmark-neuralwatt
node benchmarks/build-site-review.js
harbor run -p .audit-work/site-tasks -a oracle -n 2 \
  --jobs-dir "$PWD/.audit-work/jobs"
harbor run -p .audit-work/site-tasks -a nop -n 2 \
  --jobs-dir "$PWD/.audit-work/jobs"
harbor run -c benchmarks/neuralwatt.json -p .audit-work/site-tasks \
  --jobs-dir "$PWD/.audit-work/jobs"
CODEX_AUTH_JSON_PATH="${CODEX_AUTH_JSON_PATH:-${CODEX_HOME:-$HOME/.codex}/auth.json}" \
  harbor run -c benchmarks/frozen-configs/codex-low.json -p .audit-work/site-tasks \
  --jobs-dir "$PWD/.audit-work/jobs"
```

Task builds use committed site evidence. Recollecting live pages is a deliberate separate step; do not change task files during a comparison. The summary publisher accepts `--output PATH` so new campaigns need not overwrite historical results. It records requested reasoning and provider settings, allowlists published fields, and independently regrades report artifacts.

## Next validation gate

Owner feedback on the WIP report should come before more architecture. Resolve whether each recommendation is correct, useful, and attached to the right implementation location. Turn accepted corrections into positive, negative, and legitimate-exception cases, including numeric units and recommendation prerequisites. Then evaluate autonomous source discovery with verified deployment context and a held-out set. Keep missing inference-energy coverage visible; changing harness does not by itself produce a complete provider energy ledger.
