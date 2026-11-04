# Sources and implementation evidence

This ledger records executed work. The [feasibility source ledger](../feasibility-study/sources.md) documents the earlier research and methodology inspection.

## Initial executable-slice evidence

The subsequent implementation uses Playwright 1.64.1, CO2.js 0.19.0, Harbor 0.23.0, Codex CLI 0.166.0, and the npm-distributed OpenCode 1.19.5. The local `opencode --version` reported 2.2.5, but `opencode-ai@2.2.5` was unavailable in the registry used by Harbor. Record those as distinct installations rather than assuming interchangeable version numbers. Package versions were checked against the npm registry; runtime dependencies are recorded in `package-lock.json` and the benchmark configurations.

| Evidence                       | Source and interpretation                                                                                                                                                                                                                                                                            |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Controlled observations        | `benchmarks/corpus.json`; actual cold/warm captures of original project-owned fixtures, with browser/protocol metadata and hashes                                                                                                                                                                    |
| Live targets                   | [Guide homepage](https://guide.wagtail.org/en/), [image-management instructions](https://guide.wagtail.org/en/how-to-guides/manage-images/), [Wagtail homepage](https://wagtail.org/), [sustainability page](https://wagtail.org/sustainability/); [sanitized observations](assets/live-sample.json) |
| Provider preflight             | [Sanitized DeepSeek tool-call response](assets/provider-preflight.json); one authenticated request, including provider-attributed energy and cost                                                                                                                                                    |
| Harbor integration             | [Separate verifier documentation](https://docs.harborframework.com/tasks/separate-verifier), [environment-variable boundaries](https://docs.harborframework.com/jobs/environment-variables), and inspection of the installed 0.23.0 implementation                                                   |
| Neuralwatt routing             | [OpenCode integration](https://docs.neuralwatt.com/integrations/opencode); actual model requests through its OpenAI-compatible adapter                                                                                                                                                               |
| OpenCode failure investigation | [Harbor issue 4019](https://github.com/harbor-framework/harbor/issues/4019) describes a matching completed-output/nonzero-exit symptom. This similarity does not establish the underlying cause in our environment.                                                                                  |

The source-assisted fixture uses a runner-supplied excerpt and deployment identity. It is a controlled context test, not independent verification of a production deployment. The incomplete case removes observations deliberately; it is distinct from the collector's actual HTTP-error test. The [checkpoint](first-slice.md) distinguishes these development cases from broader methodology and accuracy claims.

The executable slice passed `just lint`, `just build-docs`, `just test` (11 Python tests and 7 JavaScript tests), `just check-links`, and `just check-external-links`. The skill metadata validator also passed. Six oracle controls passed, six no-operation controls failed their grader as intended, and both required model arms produced reports for all six revised cases. OpenCode's six execution errors and Harbor's historical Codex redaction corruption are recorded separately from grader acceptance. Published restored artifacts were regraded against their original references, with matching rewards; identical-input hashes were checked across model arms.

## Model switch and real-site review

The [current checkpoint](review-checkpoint.md) records Codex CLI routing to Neuralwatt's Responses endpoint with DeepSeek/high, and the Sol/low baseline. The [WIP audit](wagtail-audit.md) links its runtime observations, source revisions, arithmetic checks, and guideline coverage register. Source copies remain read-only.

The source inspection covers tracked public files in `local/guide` and `local/wagtail.org`; production revision identity remains unknown. Additional browser probes distinguish initial load from scrolling, JavaScript-disabled behavior, successful journeys, and opt-out state. A separate font browser probe failed with `ERR_NETWORK_CHANGED`; an HTTP retrieval of the exact stylesheet observed in the successful browser capture corroborated the font rules. The font artifact records this fallback.

The [documentation style guide](../contributing/style-guide.md) now explicitly relies on git history for editorial dates. Removed datelines were authoring choices, not a requirement of the workspace skill. Source publication dates and recorded measurement timestamps remain evidence.

The revised campaigns completed six fixture trials per model and two real-site review trials per model, without harness errors. The real-site grader corrections and original scores are documented in the [checkpoint results](review-checkpoint.md#results-and-interpretation); corrected oracle/no-operation controls and new grader regression tests validate the revised contract. They do not independently validate recommendation quality.

Checkpoint verification passed `just lint`, `just test` (11 Python and 9 JavaScript tests), `just build-docs`, `just check-links`, and `just check-external-links` (zero errors). Paired model inputs and instruction hashes match within each task. These checks validate the implementation and report provenance, not whole-site sustainability conformance.
