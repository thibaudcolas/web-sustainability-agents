---
tags:
  - sustainability
  - implementation
search:
  boost: 2
---

# Initial implementation project

This project turns the [feasibility study](../feasibility-study/README.md) into a repeatable audit workflow. Its current deliverable is a development preview: portable skills, bounded browser/source collectors, evidence-linked judgments, deterministic scoring and per-site reports.

**To use the audit, start with [installation and your first audit](../using/README.md).** To review its outputs, use [example reports](../reports/README.md). Model campaigns now have their own [evaluation project](../evaluation/README.md).

## What works

The agent selects scope and triggers collection, then reviews a frozen packet using quantitative, guideline and claims roles. Current checks cover public browser behavior and disclosures, with optional selected source files. A deterministic scorer preserves pass, fail and unknown counts; the report includes coverage and next auditing steps.

The [check reference](../reference/checks.md) is the source of truth for implemented breadth and limits. [Workflow and artifacts](../using/workflow.md) describes the current handoffs. [Reporting](../reference/reporting.md) defines human and machine outputs. Reusable measurement and interpretation principles live in the [knowledge base](../knowledge-base/README.md).

## What we are validating next

Review the current site recommendations and benchmark reference questions, then test the complete agent workflow on controlled sites. In parallel, define reliable installation and plugin packaging. Cross-harness parity, independently judged recommendation quality, skill/no-skill comparisons, and decision-model routing remain unproven.

The [roadmap](validation-roadmap.md) states the next gates. The [backlog](backlog.md) keeps detailed ideas and feedback tied to pipeline components. The [evidence record](sources.md) preserves executed experiments and validation results.

## Historical implementation notes

These explain how the prototype developed; they are not current getting-started instructions.

- [First executable slice](first-slice.md): original fixtures, Astra/OpenCode experiments and integration results.
- [Model and real-site checkpoint](review-checkpoint.md): transition to Sol and DeepSeek under Codex.
- [Staged measurement experiment](staged-auditing.md): first-load, consent, scrolling and disclosure collection.
- [First skill-guided scoring campaign](skill-audit-workflow.md): the earlier 21-group rubric and annual scenarios.

Older reports and benchmark campaigns remain accessible through their own indexes. Historical source paths and immutable artifact bundles are retained for reproducibility.
