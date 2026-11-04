# What to validate next

**Review and strengthen the first executable slice before expanding the agent architecture.** The [initial implementation](first-slice.md) now exercises collection, ratings, evidence review, and Harbor. The remaining uncertainties are mostly empirical: capture validity, grader correctness, provider integration, useful model judgments, and portability.

## Accepted direction

- Live-site audits work without source access; supplied code and internal documents can strengthen them.
- Deterministic collectors and rules produce evidence; models interpret bounded questions and investigate gaps.
- Digital Carbon Ratings is a separately labeled reporting layer with pinned calculation assumptions.
- Harbor is the primary benchmark runner. Inspect AI and Promptfoo are optional diagnostic tools.
- Model-bearing release campaigns include Neuralwatt DeepSeek V4.1 Flash and Codex. Jev and Neuralwatt Clef Flash are decision-model candidates.
- Shared Agent Skills, evidence contracts, and a sequential fallback form the portable core. Native delegation is an adapter capability to test.

## Validation sequence

| Milestone                           | Concrete work                                                                                   | Evidence needed to proceed                                                                        |
| ----------------------------------- | ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| 1. Provider and harness preflight   | Pin Harbor and agent versions; configure DeepSeek/Neuralwatt and Codex; verify Clef/Jev access  | Small successful tool/decision round trips, preserved usage, valid artifacts; failures classified |
| 2. Capture and rating fixtures      | Implement a small Playwright collector and CO2.js adapter                                       | Correct cold/warm, consent, media, incomplete-capture, byte-unit, and rating-boundary results     |
| 3. Grader validation                | Implement the twelve benchmark families with reviewed labels and a separate verifier            | Reference solution passes; no-operation and fabricated-evidence outputs fail appropriately        |
| 4. Paired baseline campaign         | Run rules, DeepSeek, and Codex; compare same evidence and end-to-end tasks separately           | Findings, unknowns, serious errors, completion, effort, cost, and uncertainty reported            |
| 5. Context and decision experiments | Add matching/stale/internal evidence, Jev/Clef, and calibrated escalation                       | Demonstrated benefit over the simpler baseline without unsupported passes                         |
| 6. Portability and delegation       | Run a shared subset in Codex, Claude Code, OpenCode, and pi; compare sequential/delegated modes | Skills load, evidence remains scoped, artifacts validate, and added complexity earns its cost     |
| 7. Independent validation           | Expand the corpus and evaluate held-out sites with expert review                                | Sufficient independent evidence for the specific automation claims proposed                       |

Milestones can overlap where independent, but a working provider connection does not establish audit accuracy, and passing a self-authored grader does not establish a trustworthy benchmark.

## Decisions the first implementation must settle

**Capture scope:** choose a small number of representative successful tasks, fixed observation windows, cache/consent profiles, and resource-size definitions. Validate that instrumentation does not invalidate those conditions. Compare an existing measurement harness before rebuilding extensive reporting.

**Rating contract:** agree on the initial page-view profile, hosting convention, SWDM/CO2.js revision, raw-value boundary handling, and incomplete-result behavior. Confirm that contextual estimates remain distinct from the standardized comparison profile.

**Reference judgments:** have a second reviewer assess the initial rule mappings, acceptable exceptions, and semantic labels. Cases with unresolved disagreement should remain research cases rather than secret “correct” answers.

**Provider behavior:** confirm Clef preview enrollment, TypeSafe version availability, tool-call compatibility, energy extensions, and unit consistency. The first slice now exercises DeepSeek and Codex; Clef/Jev access and complete campaign energy accounting still need validation. Record exact OpenAI model and reasoning settings for the Codex arm rather than using “Codex” as the model name.

**Evidence boundaries:** verify that public-only tasks cannot inspect fixture source, that local evidence is tied to the target/deployment, and that stale/internal claims cannot override contradictory observations without justification.

**Automation policy:** choose which low-consequence decisions may be automatically accepted and which need human review. Derive thresholds from held-out outcomes; do not set them from a model's confidence field alone.

## First useful deliverable

Use the [demo and test-site shortlist](test-sites.md) to choose the fixture seeds and controlled application. It recommends adapting STAR examples and running a pinned bakerydemo, with a small real-site validation set afterward.

Aim for one reproducible audit report from a controlled site, with a public-only and a source-assisted variant. It should include measured resource facts, a transparently calculated Digital Carbon Rating where applicable, supported findings, unknowns, and recommendations grounded in evidence. Harbor should evaluate both variants with DeepSeek and Codex against the same reviewed expectations.

That delivers a complete path from collection to judgment to evaluation without requiring every WSG criterion or every harness at once. It also gives us real failure cases for deciding whether a Clef/Jev layer and sub-agent delegation improve results.

The [first executable slice](first-slice.md) now supplies controlled captures, six frozen-evidence Harbor tasks, a shared skill, and initial measurements of guide.wagtail.org and wagtail.org. It is narrower than the full deliverable: repository investigation, complete browser journeys, semantic grading, and an independent judgment set remain to be validated. Its checkpoint identifies the next empirical work.
