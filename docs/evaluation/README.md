---
search:
  boost: 2
---

# Audit evaluation project

This project tests whether the audit collects the right evidence, interprets it accurately, and produces useful recommendations. Harbor is the primary runner. Keep model comparisons separate from live-site findings and from claims about the benefit of skills or delegation.

## Review the current results

Start with the [nineteen-case comparison](scope-review-cases.md): it shows synthetic facts, reference answers and both models' explanations. The [campaign method and results](scope-benchmark.md#completed-model-comparison) preserve setup failures, retries, source revision and paired provenance.

GPT-6.1 Sol/high and Neuralwatt DeepSeek V4.1 Flash/high each satisfy the strict reference contract on 16/19 complete reports. Both disagree on the same three items, exposing an unresolved-state question ambiguity and two recommendation contract defects. Their original labels and scores remain unchanged. Initial separate-agent scrutiny missed those recommendation defects; this is development evidence, not independent accuracy.

Four cases per model also exercise frozen-bundle collection, corroborated by manually inspected commands, successful returned receipts and matching artifacts. Both arms retain one ungraded startup failure and its successful unchanged-input retry. Recorded native CLI settings match the requested model and high reasoning. These are bounded interpretation and handoff tests, not a complete live-site orchestration test or a skill-benefit experiment.

## Campaigns and what they establish

| Campaign                                                                     | Scope                                        | Read it for                                                 |
| ---------------------------------------------------------------------------- | -------------------------------------------- | ----------------------------------------------------------- |
| [Scope and qualitative review](scope-benchmark.md)                           | 19 cases, including four collection handoffs | Current high/high comparison and post-hoc contract findings |
| [Broader interpretation](../initial-implementation/breadth-benchmark.md)     | 16 cases, including four collection handoffs | Historical low/high comparison and reference questions      |
| [Methodology and skills](../initial-implementation/methodology-benchmark.md) | 10 cases                                     | Scoring, annual estimation and scoped interpretation        |
| [Evidence review](../initial-implementation/expanded-benchmark.md)           | 12 cases                                     | Numeric/evidence boundaries and unsupported advice          |
| [Initial browser fixtures](../initial-implementation/first-slice.md)         | Six development tasks                        | Original integration and harness experiments                |

These are separate frozen families, not a single leaderboard. The four later families contain 57 cases; the six original tasks remain separate. Do not combine their percentages as though they share a rubric, model setting or independence guarantee. The historical sixteen-case campaign used Sol/low; the new family uses Sol/high. Published case labels are development references, not held-out ground truth.

## Design and next experiment

The [benchmark design](design.md) defines knowledge, evidence-review, execution and context-assisted tracks. The [model comparison protocol](models.md) distinguishes model, harness and system effects. The [test-site inventory](test-sites.md) identifies controlled and live material.

The [next qualitative validation](design.md#next-qualitative-validation) proposes matched evidence conditions, three complete execution tasks and a controlled specialist-skill comparison. Before another comparison, make question modes and atomic recommendation operations explicit, separate proposal support from action labels, and review recommendation usefulness independently. Then build an end-to-end task: scope clarification, real collector invocation, a recoverable collection failure, evidence review and a final report. Run both required model arms on identical tasks. Add another harness only after that task contract is stable; a skill-loading mechanism alone does not establish parity.

The [shared backlog](../initial-implementation/backlog.md) owns individual follow-ups. The [implementation roadmap](../initial-implementation/validation-roadmap.md) owns their sequence. Campaign pages record executed methods and results; keep those frozen when newer methods change.
