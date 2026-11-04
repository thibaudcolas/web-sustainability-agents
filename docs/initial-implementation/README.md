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

The [broader check catalog](broader-checks.md) adds ten browser checks and eight source-assisted checks, with source citations now part of the scored packet. The [broader benchmark](breadth-benchmark.md) adds sixteen controlled cases, four collection handoffs and reviewable expected judgments.

The [repeatable agent workflow](agent-driven-audits.md) moves collection and scope decisions into the coordinator skill. It adds a portable per-origin plan, [interaction checks](interaction-checks.md), deeper [carbon.txt interpretation](../knowledge-base/carbon-disclosures.md), an optional [GreenFrame client adapter](../knowledge-base/greenframe.md), and a [crosswalk of all 101 relevant older assessment rows](wsg-check-expansion.md).

The [skill-guided workflow](skill-audit-workflow.md) adds scoped scores, annual browsing-footprint estimates, evidence-resolved reviewer judgments and an explicit WSG/STAR coverage roadmap. Both site reports end with next auditing steps and reproducibility details. The [methodology benchmark](methodology-benchmark.md) adds ten cases for the new skills, estimates and aggregation rules.

The [staged Python workflow](staged-auditing.md) measures initial load, cookie-choice, and scrolling states; discovers carbon.txt and footprint statements; and adds Wappalyzer context. Initial-load numbers lead the updated WIP report.

The separate [guide audit](guide-audit.md) and [Wagtail.org audit](wagtail-audit.md) lead with key measures and top findings, then separate quantitative evidence from qualitative review. The [reporting contract](reporting.md) defines chart-ready data; the [backlog](backlog.md) maps feedback to validation work.

The [energy and traffic experiment](energy-traffic-experiment.md) adds actual co2-runner CPU-package measurements and exact-origin CrUX scenarios. The [expanded benchmark](expanded-benchmark.md) compares 12 cases per model: both accept 10 complete reports, but label disagreements and an unsupported traffic estimate have different implications. The [broader WSG/STAR sample](scope-extension.md) adds inventory, metadata, preferences, recovery, and policy review, with separate evidence registers for each site.

The [model and real-site checkpoint](review-checkpoint.md) switches the active baseline to Codex CLI for both GPT-6.1 Sol/low and Neuralwatt DeepSeek V4.1 Flash/high. It compares controlled fixtures and public/source-assisted Wagtail evidence. The [first executable slice](first-slice.md) preserves the original Astra/OpenCode experiment and its limitations.

## Implementation documents

| Document                                                      | Purpose                                                                              |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| [WIP guide audit](guide-audit.md)                             | Guide findings, measurements, source corroboration, and coverage                     |
| [WIP Wagtail.org audit](wagtail-audit.md)                     | Wagtail.org findings, measurements, source corroboration, and coverage               |
| [Energy and traffic experiment](energy-traffic-experiment.md) | Executed energy measurements and CrUX-derived traffic scenarios                      |
| [Expanded benchmark](expanded-benchmark.md)                   | Paired model results, controls, substantive errors, and label disagreements          |
| [Broader WSG and STAR evidence](scope-extension.md)           | Inventory, sampled states, additional findings, and per-site registers               |
| [Skill-guided audit and coverage](skill-audit-workflow.md)    | Current scores, annual estimates, review roles and supported versus missing coverage |
| [Methodology and skill benchmark](methodology-benchmark.md)   | New controlled cases, model results and skill-validation limits                      |
| [Reporting contract](reporting.md)                            | Quantitative/qualitative structure and chart-ready data                              |
| [Ordered backlog](backlog.md)                                 | Validation gates and later experiments                                               |
| [Model and real-site checkpoint](review-checkpoint.md)        | Current settings, paired review experiments, and validation limits                   |
| [First executable slice and results](first-slice.md)          | What runs, reproduction commands, measurements, model reports, and known limitations |
| [Harbor benchmark](benchmark.md)                              | Benchmark tracks, planned case families, protected grading, and comparisons          |
| [Demo sites and benchmark targets](test-sites.md)             | Controlled fixture ideas, Wagtail targets, and future application candidates         |
| [Model comparison plan](model-comparison.md)                  | Required model arms, comparison controls, and provider preflight                     |
| [Validation roadmap](validation-roadmap.md)                   | The next empirical checks and evidence needed before expanding                       |
| [Sources and implementation evidence](sources.md)             | Executed experiments, pinned versions, provenance, and verification                  |

## Boundaries and next work

The implemented cases exercise frozen evidence review. The audits combine bounded browser journeys with a broader metadata and preference sample. They do not yet validate representative task success, autonomous investigation of a real project checkout, recommendation quality, or a benefit from decision-model routing and sub-agent orchestration. Prioritize independent review of reference judgments and recommendation usefulness, matched collector/energy comparisons, and complete user tasks before stronger quality claims or routing experiments.

Reusable reference material lives in the [knowledge base](../knowledge-base/README.md), including [deterministic tools](../knowledge-base/deterministic-tools.md), [provider contracts and inference accounting](../knowledge-base/provider-capabilities.md), and [Digital Carbon Ratings](../knowledge-base/digital-carbon-ratings.md).
