# Model comparison protocol

Use Neuralwatt DeepSeek V4.1 Flash with high reasoning alongside GPT-6.1 Sol with high reasoning, both through Codex CLI. Historical campaigns retain their recorded low-reasoning Sol settings; the high setting applies to new runs. The [evaluation overview](README.md) links completed campaigns and current limits. Compare decision models on the same semantic tasks before adding them to an audit workflow; distinguish model, provider and harness effects.

The table below describes the planned comparison arms. Sol/DeepSeek evidence-review campaigns have run; Jev/Clef routing and cross-harness parity remain experiments to validate. Provider contracts and energy-accounting caveats live in the [knowledge base](../knowledge-base/provider-capabilities.md).

## Initial experimental arms

| Arm      | Configuration                                                    | Main question                                                      |
| -------- | ---------------------------------------------------------------- | ------------------------------------------------------------------ |
| Rules    | Frozen evidence and deterministic checks                         | What can software alone establish?                                 |
| DeepSeek | Rules plus one DeepSeek V4.1 Flash reviewer through Neuralwatt   | What does generative review add?                                   |
| Codex    | Same task package and shared skill in Codex, with recorded model | How well does the requested baseline perform end to end?           |
| Clef     | Same semantic cases through Neuralwatt Clef Flash                | Which narrow judgments work without generated explanations?        |
| Jev      | Same semantic cases through TypeSafe Jev                         | How does another decision model compare?                           |
| Cascade  | Best validated decision layer plus generative escalation         | Does total quality/cost improve at the chosen acceptance coverage? |

The rules arm has no inference. Decision-only arms cover questions within their interface; they are not standalone browser agents. The full release campaign includes DeepSeek and Codex even if a narrow Jev/Clef experiment uses only frozen inputs. Use the [benchmark](design.md) to distinguish model, harness, and complete-system comparisons.

Compare per-class precision/recall, unsupported passes, abstention, calibration, decision stability, finding quality, total latency, review effort, and cost. A generative model's written confidence is not directly comparable with a decision model's probability distribution. If probability calibration is compared, specify and validate how each system supplies probabilities.

Hold evidence, criterion wording, allowed tools, and practical budgets constant. Record reasoning effort, context/output limits, temperature where relevant, service tier, cache policy, retries, and escalation. Do not force unsupported settings into all adapters for the appearance of equality. Report settings and compare systems at useful quality/cost points.

## Provider preflight before the first campaign

Verify account-visible model discovery, a bounded generative/tool round trip, schema-valid output, one three-label decision request, truncation/error handling, usage retention, and successful artifact production in Harbor. Check that credentials reach only the intended agent or adapter process and are absent from logs. Use synthetic/public fixtures for initial tests.

The preflight must include DeepSeek V4.1 Flash and Codex. Add Clef and Jev once access and their contracts are verified. Keep a failed or inaccessible arm visible as incomplete; do not substitute a different model and reuse its label. Repeat this preflight when changing a provider or harness; the [validation roadmap](../initial-implementation/validation-roadmap.md) places the next work in sequence.

Historical campaign reproduction uses `benchmarks/frozen-configs/codex-low.json`. The default `benchmarks/codex.json` now requests high reasoning; using it creates a new run rather than reproducing the earlier configuration.
