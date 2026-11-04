# Neuralwatt, Codex, Jev, and Clef comparisons

Reviewed November 4, 2026. **Use Neuralwatt's DeepSeek V4.1 Flash as the required non-OpenAI generative baseline, alongside Codex.** Compare typed decision models on the same semantic tasks before adding them to a full audit workflow. Codex is a harness, Neuralwatt is a provider, and DeepSeek/Jev/Clef are model families: record those dimensions separately.

No authenticated requests or model evaluations were run for this update. Public documentation and Neuralwatt's unauthenticated model catalog were inspected. Account access and end-to-end adapter behavior remain validation tasks.

## Verified provider surfaces

| Candidate                                      | Role                                 | Verified public interface                         | Remaining check                                                             |
| ---------------------------------------------- | ------------------------------------ | ------------------------------------------------- | --------------------------------------------------------------------------- |
| Neuralwatt `deepseek-v4.1-flash`               | Generative reviewer and agent model  | Chat Completions and documented Responses surface | Tool/structured-output behavior in the selected harness                     |
| Codex with an explicitly recorded OpenAI model | End-to-end audit baseline            | Noninteractive CLI and native skills/subagents    | Pinned benchmark runner, model, reasoning, and authentication configuration |
| Neuralwatt `clef-flash`                        | Typed evidence judgments and routing | `POST /v1/systemone`                              | Preview enrollment and account-visible model access                         |
| TypeSafe Jev                                   | Typed evidence judgments and routing | TypeSafe System One API                           | Choose and verify a versioned model available to the account                |

Neuralwatt's catalog returned `deepseek-v4.1-flash` with source identifier `deepseek-ai/DeepSeek-V4.1-Flash-1017` and tool/JSON/vision capabilities. The inspected public response did not include `clef-flash`, although its model page advertises the preview. That is not evidence that the user's account lacks access. The [saved catalog excerpt](assets/neuralwatt-model-snapshot.json) records the observation. [Public model catalog](https://api.neuralwatt.com/v1/models), [DeepSeek model page](https://portal.neuralwatt.com/models/deepseek-v4.1-flash), [Clef Flash page](https://neuralwatt.com/models/clef-flash).

Use the requested `deepseek-v4.1-flash` identifier rather than a moving alias such as `nw-flash`. Still record the served revision and date: Neuralwatt's changelog describes weight refreshes under the same model name. A fixed request string alone is insufficient provenance. [Model changelog](https://portal.neuralwatt.com/changelog?area=models).

The local CLI reported `codex-cli 0.166.0`; only version/help commands were inspected. Do not describe this research conversation as a controlled Codex benchmark trial. The eventual baseline must explicitly record its model and reasoning configuration.

## Keep generative and decision adapters distinct

Neuralwatt documents Responses support, including structured outputs, but also differences such as no response-retrieval endpoint or background execution. Therefore “OpenAI-compatible” is a starting point for integration tests, not proof that every Codex feature works unchanged. [Neuralwatt Responses API](https://docs.neuralwatt.com/api/responses).

OpenCode has a documented Neuralwatt provider route. Use it as the initial DeepSeek harness candidate; verify the current model ID and settings instead of copying older model examples from the integration page. Then test Codex against Neuralwatt's Responses endpoint if a same-harness model comparison is useful. Keep the ordinary Codex/OpenAI arm independently available. [Neuralwatt OpenCode integration](https://docs.neuralwatt.com/integrations/opencode), [Harbor routing](https://docs.harborframework.com/agents/base-url-management).

Neuralwatt Clef Flash uses `/v1/systemone`, not Chat Completions. Its documented contract accepts `state` and typed `questions`, returns distributions, and flags truncation. It documents up to 64 questions, no streaming, and preview-related 404s. Use a dedicated adapter that preserves probabilities, usage, energy, and truncation status. Reject truncated cases from automatic acceptance and record them as incomplete inputs. [Neuralwatt System One API](https://neuralwatt.com/docs/api/systemone).

Do not assume identical confidence semantics across providers merely because the wire format looks similar. Neuralwatt documents its Choice confidence as the winning probability; the reviewed TypeSafe documentation describes distribution concentration. Normalize from retained raw distributions for comparisons, while retaining provider-specific fields untouched. Always supply explicit instructions and criteria rather than depending on provider-specific fallbacks from question IDs. [TypeSafe confidence](https://docs.typesafe.ai/confidence.md), [TypeSafe API](https://docs.typesafe.ai/api.md).

The [earlier Jev review](decision-models.md) lists versioned candidates. Confirm available versions during authenticated preflight and record one; do not silently switch versions after a failed request. Comparing Jev and Clef should use the same text evidence and label meanings first. Evaluate image-assisted tasks separately where provider capabilities differ.

## Initial experimental arms

| Arm      | Configuration                                                    | Main question                                                      |
| -------- | ---------------------------------------------------------------- | ------------------------------------------------------------------ |
| Rules    | Frozen evidence and deterministic checks                         | What can software alone establish?                                 |
| DeepSeek | Rules plus one DeepSeek V4.1 Flash reviewer through Neuralwatt   | What does generative review add?                                   |
| Codex    | Same task package and shared skill in Codex, with recorded model | How well does the requested baseline perform end to end?           |
| Clef     | Same semantic cases through Neuralwatt Clef Flash                | Which narrow judgments work without generated explanations?        |
| Jev      | Same semantic cases through TypeSafe Jev                         | How does another decision model compare?                           |
| Cascade  | Best validated decision layer plus generative escalation         | Does total quality/cost improve at the chosen acceptance coverage? |

The rules arm has no inference. Decision-only arms cover questions within their interface; they are not standalone browser agents. The full release campaign includes DeepSeek and Codex even if a narrow Jev/Clef experiment uses only frozen inputs. Use the [benchmark](benchmark.md) to distinguish model, harness, and complete-system comparisons.

Compare per-class precision/recall, unsupported passes, abstention, calibration, decision stability, finding quality, total latency, review effort, and cost. A generative model's written confidence is not directly comparable with a decision model's probability distribution. If probability calibration is compared, specify and validate how each system supplies probabilities.

Hold evidence, criterion wording, allowed tools, and practical budgets constant. Record reasoning effort, context/output limits, temperature where relevant, service tier, cache policy, retries, and escalation. Do not force unsupported settings into all adapters for the appearance of equality. Report settings and compare systems at useful quality/cost points.

## Measure the auditor without mixing boundaries

Neuralwatt documents GPU-counter-based measurement followed by request attribution, with estimated/unavailable alternatives. Its catalog figures are averages of billed energy and may reflect billing caps. Use per-request consumed-energy records and preserve attribution method, rather than treating catalog averages or discounted charges as physical measurements. This is provider-reported attribution, not an independent whole-system energy audit. [Energy methodology](https://docs.neuralwatt.com/energy-methodology).

Collect request IDs, requested/served model and tier, token/cache counts, duration, cost, energy units, attribution method, and available carbon metadata. The per-request usage API can support reconciliation, but is account-gated; preserve inline response extensions first. Missing energy or carbon fields remain unavailable, never zero. [Per-request usage API](https://docs.neuralwatt.com/api/usage-requests).

A documentation inconsistency needs a unit fixture: the energy-methodology page describes a division by 3,600,000 while calling the inputs millijoules. That divisor converts **joules** to kWh; millijoules require 3,600,000,000. Preserve the API's declared units, check `energy_joules / 3_600_000` against `energy_kwh`, and resolve discrepancies before interpreting results. Do not infer that this documentation error proves the service's measurements are wrong.

Keep three ledgers: provider-reported inference energy, locally measured collector/runtime resources, and unmeasured components. Record training/embodied/facility/network boundaries as covered, estimated, or excluded. Do not add overlapping provider totals or fill missing Codex/TypeSafe energy with zero. Energy comparisons across providers require compatible boundaries; cost and latency remain comparable operational measures when energy is unavailable.

Use total resources per completed, adjudicated task or accepted finding, including retries and escalations. Also report failed attempts, so a cheap system that frequently fails does not look efficient by dropping failures. Repeated trials should record cache warmth and alternate execution order to reduce confounding from changing load.

Keep the website's SWDM/DCR estimate separate from the auditor's inference accounting. They use different units of service and boundaries; a page-view estimate is not a measured offset for model usage.

## Provider preflight before the first campaign

Verify account-visible model discovery, a bounded generative/tool round trip, schema-valid output, one three-label decision request, truncation/error handling, usage retention, and successful artifact production in Harbor. Check that credentials reach only the intended agent or adapter process and are absent from logs. Use synthetic/public fixtures for initial tests.

The preflight must include DeepSeek V4.1 Flash and Codex. Add Clef and Jev once access and their contracts are verified. Keep a failed or inaccessible arm visible as incomplete; do not substitute a different model and reuse its label. The [validation roadmap](validation-roadmap.md) makes these checks the first implementation milestone.
