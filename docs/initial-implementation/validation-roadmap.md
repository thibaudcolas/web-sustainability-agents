# What to validate next

The next milestone is **one reproducible install-to-report audit**, with useful recommendations, bounded recovery and a report that opens outside this repository. The [project assessment](project-assessment.md) explains why this takes priority over another large crawl or more check IDs. The [backlog](backlog.md) owns individual changes; this page owns the acceptance gates.

## Validation sequence

| Gate | Work                                  | Evidence needed to proceed                                                                                                                                                              |
| ---- | ------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | Stabilize collection and completion   | Controlled challenge/readiness/worker fixtures; bounded recovery; whole-audit status; final review linked to reconciliation; original failures preserved                                |
| 2    | Validate installation and delivery    | Fresh installation in an unrelated working directory; browser launch; durable outputs; portable report bundle; interruption, update and removal checks                                  |
| 3    | Evaluate a complete agent-driven task | Independently reviewed labels, reference/no-op controls, one consequential scope question, real collection and a recoverable failure; paired Sol/high and Neuralwatt DeepSeek/high runs |
| 4    | Verify another harness                | Same controlled task under Codex and Claude Code, with sequential fallback; OpenCode/pi remain experimental until tested                                                                |
| 5    | Improve qualitative depth             | Criterion-clause mappings; experience/content and governance/lifecycle comparisons; matched skill/no-skill and public/source-assisted tasks                                             |
| 6    | Establish broader reliability         | Held-out sites beyond the Wagtail ecosystem, independent recommendation review, score comprehension and matched measurement protocols                                                   |

Gates 1 and 2 can be developed together. Fix ambiguous question/action labels and prepare a clean pinned benchmark image before the paired campaign. Expand from one complete task to the three in the [qualitative validation plan](../evaluation/design.md#next-qualitative-validation). Keep hardware-energy experiments separate from browser tests and model campaigns.

Run a small **Jev/Clef claim-support experiment** alongside these gates, using reviewed labels and the same generative baselines. Initially it only flags disagreements for review. Adoption requires measured gains in unsupported-claim detection or review effort, including service failures, abstention and total cost. It is not a prerequisite for the usable preview.

## Immediate review material

- [Current site reports](../reports/README.md): usefulness, priorities, coverage communication and plausible fixes.
- [Current case-by-case comparison](../evaluation/scope-review-cases.md): strict labels and recommendation contracts needing independent review.
- [Installation and your first audit](../using/README.md): implemented plugin/project-skill routes and their validation limits.

Preserve published grades and evidence. Corrections create new cases, rubrics or captures rather than rewriting the baseline. The [evaluation project](../evaluation/README.md) records campaign scope and limits; the [backlog](backlog.md) owns detailed work items, including measurement validity, energy comparability and traffic calibration.

## Acceptance for the next usable preview

A new user can install the required components, ask an agent to audit one site or scoped service, clarify relevant scope, and receive a report whose claims resolve to preserved evidence. They do not supply collector commands or repair internal JSON. Failed or incomplete collection remains visible. The same saved judgments reproduce the same score, and an explicit new calculation can retain old evidence after a tool upgrade. The report distinguishes initial load from interactions, measured from modeled quantities, public from supplied context, and attempted checks from full WSG/STAR coverage.

A successful preview does not require every WSG criterion, every harness, or decision-model routing. It does require useful recommendations and enough provenance for another person or agent to inspect them.
