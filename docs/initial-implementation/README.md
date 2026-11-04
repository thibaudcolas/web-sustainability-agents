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

The [staged Python workflow](staged-auditing.md) measures initial load, cookie-choice, and scrolling states; discovers carbon.txt and footprint statements; and adds Wappalyzer context. Initial-load numbers lead the updated WIP report.

The [WIP Wagtail audit](wagtail-audit.md) is ready for owner review: measured page states, two journeys, source corroboration, actionable findings, and explicit coverage gaps. Each finding maps feedback to the relevant pipeline component.

The [model and real-site checkpoint](review-checkpoint.md) switches the active baseline to Codex CLI for both GPT-6.1 Sol/low and Neuralwatt DeepSeek V4.1 Flash/high. It compares controlled fixtures and public/source-assisted Wagtail evidence. The [first executable slice](first-slice.md) preserves the original Astra/OpenCode experiment and its limitations.

## Implementation documents

| Document                                               | Purpose                                                                              |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------ |
| [WIP Wagtail audit](wagtail-audit.md)                  | Findings, evidence, source corroboration, coverage, and feedback mapping             |
| [Model and real-site checkpoint](review-checkpoint.md) | Current settings, paired review experiments, and validation limits                   |
| [First executable slice and results](first-slice.md)   | What runs, reproduction commands, measurements, model reports, and known limitations |
| [Harbor benchmark](benchmark.md)                       | Benchmark tracks, planned case families, protected grading, and comparisons          |
| [Demo sites and benchmark targets](test-sites.md)      | Controlled fixture ideas, Wagtail targets, and future application candidates         |
| [Model comparison plan](model-comparison.md)           | Required model arms, comparison controls, and provider preflight                     |
| [Validation roadmap](validation-roadmap.md)            | The next empirical checks and evidence needed before expanding                       |
| [Sources and implementation evidence](sources.md)      | Executed experiments, pinned versions, provenance, and verification                  |

## Boundaries and next work

The implemented cases exercise frozen evidence review. The new audit exercises two bounded browser journeys. It does not yet validate representative task success, autonomous investigation of a real project checkout, recommendation quality, or a benefit from decision-model routing and sub-agent orchestration. Prioritize independent review of the reference judgments, stronger evidence checks and useful recommendations before extending the system.

Reusable reference material lives in the [knowledge base](../knowledge-base/README.md), including [deterministic tools](../knowledge-base/deterministic-tools.md), [provider contracts and inference accounting](../knowledge-base/provider-capabilities.md), and [Digital Carbon Ratings](../knowledge-base/digital-carbon-ratings.md).
