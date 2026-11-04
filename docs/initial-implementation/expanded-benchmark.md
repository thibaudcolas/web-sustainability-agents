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

## Reproduce

```sh
uv run --locked --script benchmarks/build_expanded.py
harbor run -p .audit-work/expanded-tasks -a oracle -n 2 \
  --jobs-dir "$PWD/.audit-work/jobs"
harbor run -p .audit-work/expanded-tasks -a nop -n 2 \
  --jobs-dir "$PWD/.audit-work/jobs"
harbor run -c benchmarks/neuralwatt.json -p .audit-work/expanded-tasks \
  --jobs-dir "$PWD/.audit-work/jobs"
CODEX_AUTH_JSON_PATH="${CODEX_AUTH_JSON_PATH:-${CODEX_HOME:-$HOME/.codex}/auth.json}" \
  harbor run -c benchmarks/codex.json -p .audit-work/expanded-tasks \
  --jobs-dir "$PWD/.audit-work/jobs"
```

Do not rebuild tasks during a campaign. Run hardware-energy measurements before or after Docker/model workloads. Model inference energy is a separate ledger; local co2-runner energy does not measure remote inference.

## Interpretation limits

Use paired inputs to compare the two configured systems on these cases. Reasoning settings differ by the owner's requested baseline, so this is not a controlled estimate of reasoning effort alone. A single attempt per case does not establish variance or general model superiority. The contract tests bounded decisions; it does not yet grade a complete top-five report, autonomous site exploration, or source-file discovery.

The [backlog](backlog.md) tracks independent label review, held-out cases, recommendation quality, and inference accounting before stronger claims.
