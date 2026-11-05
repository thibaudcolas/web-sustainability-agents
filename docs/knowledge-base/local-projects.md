# Lessons from existing audit projects

The review inspected public source snapshots with clean working trees. It did not run either project's audits or test suite.

| Project                                                                          | Inspected source snapshot                                                                                         |
| -------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| [claude-seo](https://github.com/AgriciDaniel/claude-seo)                         | [6be93f4](https://github.com/AgriciDaniel/claude-seo/tree/6be93f45064ffbadced572b5d5c95f55fd263af0)               |
| [accessibility-agents](https://github.com/Community-Access/accessibility-agents) | [decf6ba](https://github.com/Community-Access/accessibility-agents/tree/decf6bac7f086c19afb242797b4974671ceff597) |

Citations use commit permalinks so readers can inspect the same material. Findings concern these snapshots, not every release or capability of either project.

The tooling follow-up reviews [executable tools and measurement caveats](deterministic-tools.md), including a newer accessibility-agents checkout. It also examines [jevotron and jev-ultrafast](../feasibility-study/decision-model-examples.md). This page preserves the original snapshot and its orchestration/evaluation findings.

## Claude-seo

The [full-audit skill](https://github.com/AgriciDaniel/claude-seo/blob/6be93f45064ffbadced572b5d5c95f55fd263af0/skills/seo-audit/SKILL.md) renders the homepage, explores the site, delegates to specialists, and persists an audit directory containing structured data, specialist findings, screenshots, and an action plan. Some specialists depend on site type, credentials, or prior history. It describes a sequential fallback when delegation is unavailable.

The useful transferable pattern is **one orchestrator with explicit specialist outputs and capability-aware routing**. A sustainability version could dispatch media review when media is present, infrastructure review when evidence is available, and governance review when documents are supplied.

Two inspected tests reveal practical reliability concerns:

- [Audit instruction guards](https://github.com/AgriciDaniel/claude-seo/blob/6be93f45064ffbadced572b5d5c95f55fd263af0/tests/test_audit_instructions.py) check that rendering and artifact persistence remain in the instructions.
- [Turn-budget regressions](https://github.com/AgriciDaniel/claude-seo/blob/6be93f45064ffbadced572b5d5c95f55fd263af0/tests/test_audit_agent_turn_budget.py) require sufficient budgets and early partial writes, following reports of agents stopping before saving findings.

For sustainability audits, adopt partial-result persistence and explicit worker completion states. A timed-out reviewer must produce “incomplete,” not an empty collection interpreted as a pass.

Adapt the scoring and crawling choices carefully. The audit skill's weighted SEO health score and 500-page crawl cap are project policies. Neither is a sustainability methodology. A shared evidence capture and sampling plan should determine what each reviewer sees; specialist agents should not independently repeat a large crawl.

The inspected static instruction tests establish that required text remains present. They do not demonstrate that an executing agent follows it, discovers the right defects, or writes an accurate report. Include both contract tests and behavioral evaluations in the new project.

## Accessibility-agents

The [web audit skill](https://github.com/Community-Access/accessibility-agents/blob/decf6bac7f086c19afb242797b4974671ceff597/skills/web-accessibility-wizard/SKILL.md) defines discovery, specialist reviews, testing, reporting, and CI. Its dispatch contract asks specialists to return JSON; a renderer combines results and computes report content. The [shared schema](https://github.com/Community-Access/accessibility-agents/blob/decf6bac7f086c19afb242797b4974671ceff597/skills/a11y-core/schemas/findings.schema.json) includes rule references, locations, severity, recommendations, optional evidence, and qualitative confidence.

This is a stronger starting point for reproducible sustainability reporting than free-form specialist essays. Extend the contract to make evidence references, methodology versions, applicability, unknowns, and collection errors explicit. The schema's qualitative confidence is an author's assessment; it should not be treated as a calibrated probability.

The project also includes a particularly relevant evaluation pattern:

1. [Fixture preparation](https://github.com/Community-Access/accessibility-agents/blob/decf6bac7f086c19afb242797b4974671ceff597/scripts/audit-fixture.mjs) removes answer-bearing comments from an intentionally defective page and writes a line map.
2. [Recall grading](https://github.com/Community-Access/accessibility-agents/blob/decf6bac7f086c19afb242797b4974671ceff597/scripts/audit-recall.mjs) compares findings with planted defects using location proximity and identifying terms.
3. The grader reports findings beyond its answer key without automatically treating them as false positives, because the key is not exhaustive.

Adopt the separation of hidden labels from audit inputs. Improve the evaluation with stable fixture IDs, explicit clean examples, independent adjudication of extra findings, and checks that the matching algorithm itself is correct. The line-map handling is an instructive reminder that a grader can produce false failures even when the auditor found the defect.

The wizard also includes human interaction gates. These are interaction-design choices in that project, not evidence that every sustainability workflow needs the same interruptions. For a pre-agreed recurring audit, batch unresolved evidence requests into a review queue and keep routine collection automatic.

## What to reuse and what to establish independently

| Pattern                   | Proposed use                                                               | Additional validation needed                                         |
| ------------------------- | -------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| Progressive skill loading | Load only the specialist's rubric and references                           | Check routing recall; missed routing can hide all downstream defects |
| Domain specialists        | Separate technical, user-experience, infrastructure, and governance review | Compare with one reviewer at equal evidence and comparable budgets   |
| Structured findings       | Validate and merge outputs in code                                         | Reject unsupported claims and broken evidence references             |
| Partial artifacts         | Preserve completed work on timeouts                                        | Ensure report distinguishes completed, skipped, and failed checks    |
| Deterministic rendering   | Produce stable tables and deltas                                           | Verify aggregation and unknown denominators                          |
| Hidden planted defects    | Measure detection on controlled cases                                      | Add precision, applicability, calibration, and real-site validation  |

The source review supports reusing architecture patterns. It provides no measured evidence that either project's accuracy transfers to WSG. Before copying implementation files, check the license and attribution of the exact files and dependencies involved.
