---
tags:
  - sustainability
  - implementation
  - evaluation
search:
  boost: 2
---

# Initial implementation work

This project turns the [feasibility study](../feasibility-study/README.md) into a small, executable audit workflow. It records implemented behavior and experimental results alongside the remaining development plan.

## Current checkpoint

The [first executable slice](first-slice.md) includes a Playwright collector, controlled browser fixtures, a CO2.js rating adapter, a portable evidence-review skill, and six Harbor development cases. Both Codex and Neuralwatt DeepSeek produced reports accepted by the narrow grader. OpenCode's execution errors remain unresolved, and the benchmark does not establish general audit accuracy.

The live sample covers guide.wagtail.org and wagtail.org, selected for the owner's familiarity with their purpose and past sustainability improvements. These observations help validate the method; they are not whole-site audit verdicts.

## Implementation documents

| Document                                             | Purpose                                                                              |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------ |
| [First executable slice and results](first-slice.md) | What runs, reproduction commands, measurements, model reports, and known limitations |
| [Harbor benchmark](benchmark.md)                     | Benchmark tracks, planned case families, protected grading, and comparisons          |
| [Demo sites and benchmark targets](test-sites.md)    | Controlled fixture ideas, Wagtail targets, and future application candidates         |
| [Model comparison plan](model-comparison.md)         | Required model arms, comparison controls, and provider preflight                     |
| [Validation roadmap](validation-roadmap.md)          | The next empirical checks and evidence needed before expanding                       |
| [Sources and implementation evidence](sources.md)    | Executed experiments, pinned versions, provenance, and verification                  |

## Boundaries and next work

The implemented cases exercise frozen evidence review. They do not yet validate complete browser journeys, autonomous investigation of a real project checkout, recommendation quality, or a benefit from decision-model routing and sub-agent orchestration. Prioritize independent review of the reference judgments, reliable harness completion, and stronger evidence checks before extending the system.

Reusable reference material lives in the [knowledge base](../knowledge-base/README.md), including [deterministic tools](../knowledge-base/deterministic-tools.md), [provider contracts and inference accounting](../knowledge-base/provider-capabilities.md), and [Digital Carbon Ratings](../knowledge-base/digital-carbon-ratings.md).
