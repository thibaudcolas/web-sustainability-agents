# Scope and qualitative review benchmark

This new `scope-v1` family adds nineteen controlled development cases. It tests energy boundaries, repeated-visit selection, area scoring, evidence-based priorities, source provenance and qualitative organizational review. It also exercises the ten contextual expectations introduced with `contextual-review-v1`. Earlier case families, references and published results remain frozen.

The fixtures are synthetic evidence packets, not observations of real organizations. Their references are coordinator-authored and public for review. Passing the verifier shows agreement with this bounded contract; it does not establish independent audit accuracy, full WSG coverage or the benefit of skills over another workflow.

## Case scope

| Case                                          | Decision tested                                                                                                                                  |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `energy-measured-modeled-boundaries`          | Preserve local CPU observations, site-isolation unknowns and modeled scenario energy as separate quantities.                                     |
| `inference-energy-missing-not-zero`           | Missing remote inference energy stays unknown even when reported cost is zero.                                                                   |
| `initial-first-visit-and-median-three`        | Keep the first successful initial visit separate from the median of three matching visits.                                                       |
| `median-cannot-mix-consent-and-cache`         | Successful runs with different consent and cache states cannot supply the requested matching-state median.                                       |
| `area-score-known-only-and-coverage`          | Calculate per-area scores and applicable coverage with explicit unknown and not-applicable denominators.                                         |
| `ci-priority-requires-applicability-evidence` | A severity number cannot turn an unknown or not-applicable check into a demonstrated CI failure.                                                 |
| `branch-link-not-immutable-source-proof`      | A mutable branch excerpt supports a scoped declared requirement, not a pinned deployed version.                                                  |
| `commit-pin-does-not-repair-snippet-mismatch` | A commit identifier does not validate a snippet that differs from the verified source bytes.                                                     |
| `star-qualitative-scope-and-evidence`         | Produce a bounded qualitative STAR-style discussion without inventing a numeric scale.                                                           |
| `star-public-claim-missing-operations`        | Preserve observed public strengths and unknown organizational practices separately.                                                              |
| `audience-research-changes-low-data-journey`  | Connect audience research to a tested design change while retaining the participant and task scope.                                              |
| `inclusive-testing-attendance-not-coverage`   | A general testing claim does not establish participation from the constrained target groups.                                                     |
| `governance-practice-public-operation-record` | Public dated reviews can demonstrate bounded governance practice and comparable target progress.                                                 |
| `impact-business-model-outputs-not-outcomes`  | A theory of change and activity count do not establish avoided journeys or causal outcomes.                                                      |
| `service-necessity-and-access-tradeoff`       | Evaluate alternatives and audience constraints before replacing tested channels with a mandatory app.                                            |
| `data-minimization-purpose-and-retention`     | Judge required personal-data categories against purpose records and the tested task.                                                             |
| `content-lifecycle-policy-and-stale-path`     | A concrete sampled contradiction supports a scoped lifecycle finding, without a site-wide verdict.                                               |
| `end-of-life-plan-versus-tested-retirement`   | Distinguish retirement guidance, implemented measures and a future deletion obligation.                                                          |
| `ci-duplicate-trigger-unmeasured-priority`    | Investigate an overlapping CI trigger candidate at low provisional priority without inventing savings or displacing demonstrated visitor impact. |

The contextual cases address bounded expectations under [audience evaluation](https://www.w3.org/TR/web-sustainability-guidelines/#audience-evaluation), [early user testing](https://www.w3.org/TR/web-sustainability-guidelines/#early-user-testing), [governance over time](https://www.w3.org/TR/web-sustainability-guidelines/#governance-over-time), [theory of change](https://www.w3.org/TR/web-sustainability-guidelines/#theory-of-change), [creation evaluation](https://www.w3.org/TR/web-sustainability-guidelines/#creation-evaluation), [obstacle consideration](https://www.w3.org/TR/web-sustainability-guidelines/#obstacle-consideration), [data ownership](https://www.w3.org/TR/web-sustainability-guidelines/#data-ownership), [outdated content](https://www.w3.org/TR/web-sustainability-guidelines/#outdated-content), [web sustainability goals](https://www.w3.org/TR/web-sustainability-guidelines/#web-sustainability-goals) and [end-of-life care](https://www.w3.org/TR/web-sustainability-guidelines/#end-of-life-care). These mappings do not claim complete guideline coverage.

## Contract and controls

The tasks supply the evidence, guideline, claims and contextual review skills, including their reference resources, and instruct the model to read them. Four cases require the model to invoke the frozen collector before judging. That collector reads a supplied bundle; it does not browse a live site. References and oracle solutions are outside the agent environment, and Harbor runs verification separately.

Questions validate claims: `pass` means supported and `fail` means unsupported, including insufficient evidence. A rejected claim is not automatically a failed website check. Metrics name their units and basis; unavailable quantities remain null. Recommendations name one action. Each case also has a public reference rationale for scrutiny, withheld from the agent input.

The verifier checks labels, values, units, evidence IDs, explanation presence and required collection artifacts. It does not judge explanation quality, recommendation usefulness or whether its own development references are correct. Oracle and no-operation controls validate the harness contract separately from model performance.

## Reproduction

The campaign froze commit `839c299e18c9fc7ca3f1c92c49b754d1710c1a9d`, including contextual skill version 0.1.0. Later workspace changes, including version 0.1.1, are outside this comparison. The [source verification](../initial-implementation/assets/scope-source-verification.json) rebuilds from that commit's Git blobs in an isolated temporary tree: every filename and byte in all nineteen generated tasks matches the actual campaign tasks, the manifest matches, and both model configurations match byte-for-byte.

Reproduce from that source revision in an isolated checkout. Building from the latest branch does not reproduce this snapshot. The builder refuses a nonempty output directory; do not rebuild during a campaign.

```sh
git worktree add --detach .audit-work/scope-reproduction \
  839c299e18c9fc7ca3f1c92c49b754d1710c1a9d
cd .audit-work/scope-reproduction
uv run --locked --script benchmarks/build_expanded.py --scope
harbor run -p .audit-work/scope-tasks-v1 -a oracle -n 2 \
  --jobs-dir "$PWD/.audit-work/scope-jobs" --job-name scope-oracle-v1
harbor run -p .audit-work/scope-tasks-v1 -a nop -n 2 \
  --jobs-dir "$PWD/.audit-work/scope-jobs" --job-name scope-nop-v1
CODEX_AUTH_JSON_PATH="${CODEX_AUTH_JSON_PATH:-${CODEX_HOME:-$HOME/.codex}/auth.json}" \
  harbor run -c benchmarks/codex.json -p .audit-work/scope-tasks-v1 \
  --jobs-dir "$PWD/.audit-work/scope-jobs" --job-name scope-sol-high-v1
harbor run -c benchmarks/neuralwatt.json -p .audit-work/scope-tasks-v1 \
  --jobs-dir "$PWD/.audit-work/scope-jobs" --job-name scope-deepseek-high-v1
```

Both model arms use Codex CLI, one attempt per case, high reasoning and identical frozen inputs. Record setup failures separately; retry infrastructure failures on unchanged inputs and retain every attempt. Do not retry graded predictions or choose the best answer. Run model campaigns outside hardware-energy measurement windows.

Use the current checkout's `benchmarks/publish_expanded.py --scope <completed job directories...>` to publish allowlisted projections of the completed jobs; projection changes do not alter the pinned tasks. The publisher regrades saved artifacts and compares input, reference, instruction, verifier, collector and complete skill-resource hashes across arms. Missing cost or energy is unknown. Token usage and harness cost estimates do not establish metered inference energy.

The task manifest covers those named resources; it does not bind Dockerfile or image identities, or every environmental dependency. Base-image pins and the requested CLI version remain inspectable in the builder and trial configuration. Runtime package installation adds mutable external dependencies. Scope result projections also retain native CLI model/effort records and collector-call/returned-observation hashes, with private transcripts excluded. Those records establish recorded CLI settings and frozen-bundle handoffs, not independent verification of provider computation or live browsing.

## Completed model comparison

Each required model arm produced **16/19 complete reports accepted by the original strict verifier**. Read the [full case review](scope-review-cases.md) for supplied facts, references and both models' explanations. The [published results](../initial-implementation/assets/scope-benchmark-results.json) retain all forty model attempts, including two startup failures and their unchanged-input retries. These counts measure agreement with a development contract; they are not independent accuracy estimates.

| Measure                                      | GPT-6.1 Sol (high) | DeepSeek V4.1 Flash (high) |
| -------------------------------------------- | ------------------ | -------------------------- |
| Completed graded cases                       | 19                 | 19                         |
| Strict complete-report accepts               | 16                 | 16                         |
| Strict complete-report rejections            | 3                  | 3                          |
| Ungraded startup failures retained           | 1                  | 1                          |
| Unchanged-input startup retries              | 1                  | 1                          |
| Required frozen-bundle handoffs corroborated | 4                  | 4                          |

Harbor 0.23.0 ran both arms through Codex CLI 0.166.0. Input, reference, instruction, grader, collector and skill-resource hashes match across arms. Recorded native CLI model/effort contexts match the requested model and high reasoning in all thirty-eight graded predictions. This verifies recorded client settings, not a provider's internal computation. Remote inference energy remains unknown.

The [case book](../initial-implementation/assets/scope-benchmark-cases.json) and [task manifest](../initial-implementation/assets/scope-benchmark-manifest.json) remain frozen. The [Harbor controls](../initial-implementation/assets/scope-benchmark-controls.json) accept 19/19 oracle reports and 0/19 no-operation reports, with no exceptions. These validate the execution and grading contract, not reference-label correctness.

The [startup-failure record](../initial-implementation/assets/scope-setup-failures.json) distinguishes DeepSeek's agent-setup timeout from Sol's missing optional Codex platform binary. Neither failed attempt produced a report or native session. Each exact case was retried once using its original configuration and frozen task: `-i inclusive-testing-attendance-not-coverage` for DeepSeek and `-i ci-duplicate-trigger-unmeasured-priority` for Sol. Both retries passed. No graded prediction was retried or selected by score.

The [collector review](../initial-implementation/assets/scope-collector-review.json) corroborates all eight required handoffs. Manual inspection matched actual direct or awaited collector commands to successful subprocess receipts and saved artifacts identical to the frozen collection references. This is trace, receipt and artifact evidence for frozen bundles, not formal execution attestation or live browser orchestration.

## Reference-contract findings

Both models disagree with the same three reference items. Their explanations expose ambiguities in the task contract; the original labels and rewards remain unchanged. The [post-hoc contract review](../initial-implementation/assets/scope-contract-review.json) records the diagnosis without a corrected score.

| Case/item                                | Original reference | Both model labels | Post-hoc diagnosis                                                                                                                                                                              |
| ---------------------------------------- | ------------------ | ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `inference-energy-missing-not-zero/q2`   | `pass`             | `inconclusive`    | The unresolved-energy statement can be read as a supported claim or a direct unknown-state question. Both models retain null energy and explain that missing is not zero.                       |
| `area-score-known-only-and-coverage/r1`  | `preserve`         | `fix`             | The proposal asks for reporting behavior that is not shown as already implemented. Both models calculate all seven area score and coverage quantities correctly.                                |
| `star-qualitative-scope-and-evidence/r1` | `investigate`      | `preserve`        | The proposal combines retaining a useful support route and requesting a missing baseline, with no defined primary operation. Both models explain both actions and retain the qualitative scope. |

A separate agent inspected the references before execution; the [initial review record](../initial-implementation/assets/scope-reference-review.json) states its limits. That scrutiny did not catch the two recommendation contract defects. The diagnosis above followed inspection of the predictions and is not independent labeling. Future cases need explicit question modes, one operation per recommendation, and separate judgments of proposal support and site-action type.

The remaining cases agree with the frozen references, including bounded public governance records, audience research, inclusive-testing coverage, service alternatives, data minimization, lifecycle decisions and unmeasured CI priority. This remains partial WSG interpretation evidence. The campaign has no skill ablation, independent usefulness scoring or complete live-audit task.
