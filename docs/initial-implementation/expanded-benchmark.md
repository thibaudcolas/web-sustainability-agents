# Expanded evidence benchmark

This campaign expands the original development tasks around owner feedback: phases, consent, as-is failures, disclosures, technology, energy, traffic, source identity, and recommendation restraint. It uses Harbor 0.23.0 with Codex CLI 0.166.0 for both Sol/low and Neuralwatt DeepSeek V4.1 Flash/high. The [historical checkpoint](review-checkpoint.md) remains unchanged.

## Cases and contract

Twelve frozen cases live in `benchmarks/expanded-cases.json`. Some project compact fields from actual site observations; others are explicitly controlled synthetic counterexamples. They test interpretation, not whether a browser collector can reproduce synthetic scenarios. The [manifest](assets/expanded-benchmark-manifest.json) hashes each input, instruction, skill, grader, and separate reference.

| Case                | Distinction                                                                         |
| ------------------- | ----------------------------------------------------------------------------------- |
| Phases              | Initial headline versus cumulative post-scroll traffic and causal savings           |
| Consent absent      | Optional missing selector versus completed choice or enforcement                    |
| Resource errors     | Measured 404 versus unknown aborted-transfer bytes                                  |
| Disclosure scope    | Arithmetic under stated assumptions versus incompatible profiles and hosting claims |
| Fingerprints        | Detection versus execution, absence, and useful architecture advice                 |
| Energy boundary     | Non-overlapping CPU package, unit conversion, missing baseline, SWDM boundaries     |
| Energy missing      | Empty counter versus valid zero or unavailable energy                               |
| Traffic scenario    | Bucket median versus actual site analytics and exact ordinal rank                   |
| Traffic missing     | Limited lookup versus global absence or substituted parent origin                   |
| Media source        | MIME type, screenshot legibility, source deployment uncertainty                     |
| Preserve and attest | Useful cache reuse and controlled deployment attestation                            |
| Policy and coverage | Untrusted instructions, policy versus execution, incomplete STAR sampling           |

The Python verifier adds numeric value/unit/basis checks, per-site scope, explicit null overall score, and structured recommendation decisions to the original outcome/evidence checks. It rejects missing or fabricated IDs, duplicate answers, unknown-as-zero, Boolean numeric values, nonfinite values, and unsupported recommendation actions. Free-text explanations are required but are not automatically validated for semantic quality. This still needs independent owner review.

References and the verifier run in a separate Python container. The agent receives only input, instructions, and skill version 0.3.0. Oracle controls must pass; no-operation controls must fail. Neither validates that coordinator-authored labels are independently correct. The corpus is public development material, not a held-out benchmark.

## Validated controls

All 12 revised oracle tasks passed and all 12 revised no-operation tasks failed as intended, with zero harness exceptions. The [published controls](assets/expanded-benchmark-controls.json) retain reports, diagnostic regrades, and task hashes. The initial control run also passed before review clarified epistemic question wording and aligned numeric precision; only the revised tasks are used for the model comparison.

## Model comparison results

The [published results](assets/expanded-benchmark-results.json) contain both controls, both model campaigns, the unchanged-input setup retry, reports, diagnostic regrades, and matching task hashes. The original grader and reference labels remain unchanged.

| Configured system                               | Accepted reports      | Answer labels | Numeric fields, units, and bases | Recommendation actions |
| ----------------------------------------------- | --------------------- | ------------- | -------------------------------- | ---------------------- |
| GPT-6.1 Sol, low, Codex CLI                     | 10/12                 | 33/35         | 14/14                            | 12/12                  |
| Neuralwatt DeepSeek V4.1 Flash, high, Codex CLI | 10/12 completed cases | 33/35         | 13/14                            | 12/12                  |

DeepSeek's initial campaign accepted 10 reports, rejected one, and had one setup exception before inference: npm omitted Codex's platform binary. A single retry of that case with identical inputs completed and was rejected. The published artifact retains the original exception and retry separately; the table uses the completed response for case comparison. Sol had no harness exceptions. These are contract-check counts, not independently validated accuracy estimates.

The coordinator reviewed the rejected reports and recommendation explanations:

- Sol's `resource-errors/q2` and `energy-missing/q1` chose `inconclusive` where the reference expects `fail` for a claim that zero was established. Both retain null measurements and appropriate advice. These expose a judgment-label ambiguity rather than an observed numeric or recommendation failure.
- DeepSeek's `energy-boundary/q2` similarly chooses `inconclusive` for sole-site attribution, while explaining the whole-system boundary correctly and preserving the correct conversion and unknown savings.
- DeepSeek's `traffic-missing/q1` and `m1` assign 31,867 annual pageviews from an unranked extrapolation after a lookup limited to the top million. That lookup does not establish that the origin is unranked: the appropriate value is unknown. Calling the estimate a scenario does not establish its prerequisite. The recommendation to extend the lookup is useful, but does not repair the unsupported numeric assignment.

The two systems therefore have equal all-or-nothing report acceptance with different failure consequences. This does not support choosing a winner. Keep deterministic prerequisites around traffic estimation, and separate evidence sufficiency from direct site-state judgments in the next rubric version. Independently review those labels before changing accepted answers; do not retrospectively improve these scores. Recommendation action matches also do not establish the quality of full audit prose or implementation advice.

Usage fields preserve available harness accounting. Provider billing and inference energy were not reconciled for this campaign; missing values are unknown. The local browser-energy experiment does not measure remote model inference.

## Reproduce

```sh
uv run --locked --script benchmarks/build_expanded.py
harbor run -p .audit-work/expanded-tasks-v2 -a oracle -n 2 \
  --jobs-dir "$PWD/.audit-work/jobs"
harbor run -p .audit-work/expanded-tasks-v2 -a nop -n 2 \
  --jobs-dir "$PWD/.audit-work/jobs"
harbor run -c benchmarks/neuralwatt.json -p .audit-work/expanded-tasks-v2 \
  --jobs-dir "$PWD/.audit-work/jobs"
CODEX_AUTH_JSON_PATH="${CODEX_AUTH_JSON_PATH:-${CODEX_HOME:-$HOME/.codex}/auth.json}" \
  harbor run -c benchmarks/frozen-configs/codex-low.json -p .audit-work/expanded-tasks-v2 \
  --jobs-dir "$PWD/.audit-work/jobs"
```

Do not rebuild tasks during a campaign. Run hardware-energy measurements before or after Docker/model workloads. Model inference energy is a separate ledger; local co2-runner energy does not measure remote inference.

## Interpretation limits

Use paired inputs to compare the two configured systems on these cases. Reasoning settings differ by the owner's requested baseline, so this is not a controlled estimate of reasoning effort alone. A single attempt per case does not establish variance or general model superiority. The contract tests bounded decisions; it does not yet grade a complete top-five report, autonomous site exploration, or source-file discovery.

The [backlog](backlog.md) tracks independent label review, held-out cases, recommendation quality, and inference accounting before stronger claims.
