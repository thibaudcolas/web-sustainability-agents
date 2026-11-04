# Methodology and skill benchmark

Ten new controlled cases extend the previous 12-case development corpus, bringing these two evidence-review families to **22 cases**. Historical reports, labels, instructions and scores remain unchanged. The older builder now uses a frozen copy of review skill 0.3.0; the new family uses evidence-review 0.4.0 plus guideline-review and claims-review 0.1.0.

| Case                      | Tested distinction                                                                |
| ------------------------- | --------------------------------------------------------------------------------- |
| Annual proxy              | Explicit page mix and kg/year conversion versus measured organizational footprint |
| Annual incomplete rank    | Limited lookup does not establish an unranked population                          |
| Partial footprint         | Labeled partial-input estimate is allowed; a DCR or statistical bound is not      |
| Scoring unknowns          | Unknowns in the denominator, applicability, and impact weights                    |
| Scoring grouping          | Duplicate rules count once per guideline; failure/unknown precedence              |
| Preference initialization | Initial dark support versus live change and measured energy savings               |
| Declared-file alternative | Root 404 versus working declared manifest; offline execution remains separate     |
| Policy and source         | Redirected policy route and candidate source versus verified production fix       |
| STAR coverage             | Small sample and missing internal records versus whole-site claims                |
| Recommendation restraint  | High-DPR legibility, code/content licensing, and untrusted instructions           |

The [manifest](assets/methodology-benchmark-manifest.json) hashes every input, instruction, reference, verifier and skill resource. Reference judgments remain coordinator-authored development labels. This is not a held-out knowledge benchmark or an independent accuracy estimate.

Questions now explicitly ask whether a claim is supported. `fail` means unsupported, whether contradicted or insufficiently evidenced; it does not automatically identify a site defect. This separates evidence sufficiency from direct-state uncertainty without retroactively changing the earlier campaign. Numeric score requests appear in the metric fields; the mini-task summary remains unscored because a synthetic question set is not a site audit.

All ten oracle controls passed and all ten no-operation controls failed, with no harness exceptions. The [control artifact](assets/methodology-benchmark-controls.json) preserves those runs. Both model arms use Harbor 0.23.0 and Codex CLI 0.166.0: GPT-6.1 Sol/low and Neuralwatt DeepSeek V4.1 Flash/high.

## Completed model comparison

The [published results](assets/methodology-benchmark-results.json) include both model arms, controls, full reports, diagnostic regrades, usage fields and matching hashes for every supplied skill resource. Neither model campaign had a harness exception or required a retry.

| Configured system                    | Accepted reports | Supported/unsupported claim labels | Numeric values, units and bases | Recommendation action labels |
| ------------------------------------ | ---------------: | ---------------------------------: | ------------------------------: | ---------------------------: |
| GPT-6.1 Sol, low                     |            10/10 |                              19/19 |                           12/12 |                        10/10 |
| Neuralwatt DeepSeek V4.1 Flash, high |             8/10 |                              19/19 |                           12/12 |                         8/10 |

Both systems reject the unsupported unranked traffic extrapolation, calculate the requested footprint and score values, distinguish partial estimates from DCR eligibility, and preserve coverage limits. This is performance against author-created references, not independently established audit accuracy.

DeepSeek's two rejected reports retain the intended advice in prose but use different action labels:

- `partial-footprint`: `preserve` instead of reference `fix`, while explicitly supporting publication of the labeled partial-input estimate.
- `preference-initialization`: `preserve` instead of reference `investigate`, while recommending the proposed investigation and retention of initial theme support.

These expose a weakness in the recommendation schema. “Publish” does not fit remediation verbs cleanly, and a proposal combining preservation and investigation invites more than one action. The coordinator's review identifies label disagreements, not observed numeric mistakes or harmful recommendations. Original scores remain unchanged; future automation must not route actions solely from such ambiguous verbs. Backlog B22 calls for single-action cases or an explicit action set and independent label review.

Do not infer model superiority or a causal skill improvement from these totals. This campaign changes cases, question semantics and supplied skills together, has one attempt per case, and lacks a no-skill ablation. It also does not validate an autonomous full audit. Billing and remote inference energy remain unreconciled; local hardware measurements do not cover model inference. Keep these results separate from the [earlier campaign](expanded-benchmark.md).

## Reproduce

```sh
uv run --locked --script benchmarks/build_expanded.py --methodology
harbor run -p .audit-work/methodology-tasks-v1 -a oracle -n 2 \
  --jobs-dir "$PWD/.audit-work/jobs"
harbor run -p .audit-work/methodology-tasks-v1 -a nop -n 2 \
  --jobs-dir "$PWD/.audit-work/jobs"
CODEX_AUTH_JSON_PATH="${CODEX_AUTH_JSON_PATH:-${CODEX_HOME:-$HOME/.codex}/auth.json}" \
  harbor run -c benchmarks/frozen-configs/codex-low.json -p .audit-work/methodology-tasks-v1 \
  --jobs-dir "$PWD/.audit-work/jobs"
harbor run -c benchmarks/neuralwatt.json -p .audit-work/methodology-tasks-v1 \
  --jobs-dir "$PWD/.audit-work/jobs"
```

The builder refuses to overwrite frozen tasks. Use a new `--output` directory for another build, and never change inputs during a campaign. Numeric/action checks do not validate the usefulness of prose. A paired no-skill ablation, independently reviewed references, held-out cases and repeated trials are still needed to establish a causal benefit from these skills.
