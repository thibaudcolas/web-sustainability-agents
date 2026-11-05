# What to validate next

The public-site audit path, source-assisted reviews and paired frozen-evidence campaigns now run. The next gate is useful, well-supported end-to-end auditing, followed by a reliable installation experience. More check IDs alone will not establish either. The [qualitative validation plan](../evaluation/design.md#next-qualitative-validation) connects the current criterion classifications to evidence discovery, specialist review and recommendation-quality tests.

## Validation sequence

| Order | Work                                                        | Evidence needed to proceed                                                                                                                                            |
| ----- | ----------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1     | Review the current reports and disputed benchmark questions | Owner feedback tied to check/case IDs; independently reviewed reference semantics and recommendation usefulness                                                       |
| 2     | Evaluate a complete agent-driven audit                      | Controlled site task with scope clarification, actual collector calls, partial failure recovery, citations and a final report; paired Sol/high and DeepSeek/high runs |
| 3     | Package the working workflow                                | Clean-install test, resolved collector paths, explicit browser setup, persistent output location, and upgrade/uninstall behavior                                      |
| 4     | Verify another harness                                      | Same task and evidence contracts under Codex and another agent; sequential roles remain available                                                                     |
| 5     | Isolate the value of skills and source context              | Matched skill/no-skill and public/source-assisted cases with independently judged recommendations                                                                     |
| 6     | Experiment with Jev/Clef and delegation                     | Measured benefit over the simpler baseline, including abstention, cost, latency and unsupported advice                                                                |
| 7     | Establish broader reliability                               | Held-out sites and representative tasks, independent reviewers, calibrated scoring and repeated measurements                                                          |

Packaging design can proceed alongside the first two gates. Benchmark environment improvements should precede another large campaign: dependency installation caused avoidable setup failures. Keep hardware-energy experiments separate from browser tests and model campaigns.

## Immediate review material

- [Current site reports](../reports/README.md): usefulness, priorities, coverage communication and plausible fixes.
- [Case-by-case model comparison](breadth-review-cases.md): unknown deployed versions and untested successful-submission counts need clearer question contracts.
- [First draft of the user experience](../using/README.md): checkout/skills installation today and the proposed Agent Plugin experience.

Preserve published grades and evidence. Corrections create new cases, rubrics or captures rather than rewriting the baseline. The [evaluation project](../evaluation/README.md) records campaign scope and limits; the [backlog](backlog.md) owns detailed work items, including measurement validity, energy comparability and traffic calibration.

## Acceptance for the next usable preview

A new user can install the required components, ask an agent to audit one origin, clarify relevant scope, and receive a report whose claims resolve to preserved evidence. Failed or incomplete collection remains visible. The same saved judgments reproduce the same score. The report distinguishes initial load from interactions, measured from modeled quantities, public from supplied context, and attempted checks from full WSG/STAR coverage.

A successful preview does not require every WSG criterion, every harness, or decision-model routing. It does require useful recommendations and enough provenance for another person or agent to inspect them.
