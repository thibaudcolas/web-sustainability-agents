---
search:
  boost: 2
---

# Audit evaluation project

This project tests whether the audit collects the right evidence, interprets it accurately, and produces useful recommendations. Harbor is the primary runner. Keep model comparisons separate from live-site findings and from claims about the benefit of skills or delegation.

## Review the current results

Start with the [sixteen-case comparison](../initial-implementation/breadth-review-cases.md): it shows synthetic facts, reference answers and both models' explanations. The [campaign method and results](../initial-implementation/breadth-benchmark.md#completed-model-comparison) preserve setup failures, retries and exact provenance.

Both GPT-6.1 Sol/low and Neuralwatt DeepSeek V4.1 Flash/high pass 14/16 complete reports. They disagree with the references on the same two question contracts. Four cases per model also exercise agent-triggered collection from frozen bundles. This is useful development evidence, but not an independent accuracy estimate or a complete live-site orchestration test.

## Campaigns and what they establish

| Campaign                                                                     | Scope                                        | Read it for                                          |
| ---------------------------------------------------------------------------- | -------------------------------------------- | ---------------------------------------------------- |
| [Broader interpretation](../initial-implementation/breadth-benchmark.md)     | 16 cases, including four collection handoffs | Current comparison and ambiguous reference questions |
| [Methodology and skills](../initial-implementation/methodology-benchmark.md) | 10 cases                                     | Scoring, annual estimation and scoped interpretation |
| [Evidence review](../initial-implementation/expanded-benchmark.md)           | 12 cases                                     | Numeric/evidence boundaries and unsupported advice   |
| [Initial browser fixtures](../initial-implementation/first-slice.md)         | Six development tasks                        | Original integration and harness experiments         |

These are separate frozen families, not a single leaderboard. The three later families contain 38 cases; the six original tasks remain separate. Do not combine their percentages as though they share a rubric, model setting or independence guarantee. Published case labels are development references, not held-out ground truth.

## Design and next experiment

The [benchmark design](design.md) defines knowledge, evidence-review, execution and context-assisted tracks. The [model comparison protocol](models.md) distinguishes model, harness and system effects. The [test-site inventory](test-sites.md) identifies controlled and live material.

Next, independently review the disputed references and recommendation usefulness, then build an end-to-end task: scope clarification, real collector invocation, a recoverable collection failure, evidence review and a final report. Run both required model arms on identical tasks. Add another harness only after that task contract is stable; a skill-loading mechanism alone does not establish parity.

The [shared backlog](../initial-implementation/backlog.md) owns individual follow-ups. The [implementation roadmap](../initial-implementation/validation-roadmap.md) owns their sequence. Campaign pages record executed methods and results; keep those frozen when newer methods change.
