# Audit workflow and artifacts

The agent owns the sequence below. The website owner only needs the [entry-point installation and a URL](README.md). These commands document the underlying interface for contributors, harness adapters and reproducibility.

The provisional Typer CLI runs as `uv run --locked --script audit/cli.py` from the checkout. An installed entry skill resolves its tool root through its bundled runtime helper. Other working directories should use that absolute CLI path and absolute output paths. This interface follows [Wagtail CLI's progressive skill loading](https://github.com/wagtail/wagtail-cli); it is not yet a published standalone package.

## Discover the next role

```sh
uv run --locked --script audit/cli.py skills list
uv run --locked --script audit/cli.py skills get core
uv run --locked --script audit/cli.py skills get report --full
uv run --locked --script audit/cli.py skills path setup
```

Only the small `sustainability-audit` entry point is registered by the plugin. The coordinator loads setup, context review, collection, evidence, guideline, claims and report workflows as needed. The development checkout retains specialist source folders under `.agents/skills/` for existing collectors and benchmark builders; this differs from installed plugin discovery.

## Setup, sample and collect

The setup role runs `doctor` and, when needed, `prepare` to install locked dependencies and Chromium. It discovers 5–10 representative pages including the homepage, records why they matter, and defines a complete visitor journey. Smaller samples need an explicit owner request or a reason such as a small or inaccessible site. The initial plan command supplies a skeleton; the agent completes the sample before collecting.

```sh
uv run --locked --script audit/cli.py tool workflow init \
  --origin https://example.org --plan /absolute/output/plan.json
uv run --locked --script audit/cli.py tool workflow collect \
  --plan /absolute/output/plan.json --session /absolute/output/session
```

The plan records purpose, selected pages and tasks, consent branches, explicit journey postconditions, source selections, questions and assumptions. Required unanswered scope questions block dependent collection. Source access is optional. See [checks and coverage](../reference/checks.md) and [browser probes](../reference/browser-probes.md) for actual collection capabilities.

The setup role also selects relevant `contextChecks`: access barriers for an important task, content and data lifecycle questions, or published goals and governance. Before collection, it records an explicit `contextScopes` entry for every selected contextual check: the task, audience, constraint and completion condition, or the service boundary and period relevant to an organizational check. Reviewers must keep that boundary. It freezes attributed public documents, owner records or task observations in `contextEvidence`, retaining explicit requests when evidence is unavailable. Source access is not required. These selected checks extend the session to `agent-breadth-v3`; intentionally context-free sessions retain v2.

Energy readiness is recorded by default. An accepted energy sample can use `plan.energy.mode: run`, up to three planned page IDs and three repetitions. Missing prerequisites produce a reason, not zero. Run the bounded GreenFrame experiment while other local workloads are paused and keep its model estimates separate from the transfer capture. See [the energy experiment and protocol](../initial-implementation/energy-traffic-experiment.md).

A single collection role owns the capture. Reviewers share its frozen packet instead of repeating the crawl. Inspect command failures and incomplete page observations; a successful process exit alone does not establish a complete measurement.

## Dispatch bounded native reviews

```sh
uv run --locked --script audit/cli.py tool orchestrate tasks \
  --session /absolute/output/session --output /absolute/output/review-tasks \
  --mode native-subagents
```

The CLI writes evidence, guideline and claims task JSON files with role instructions, actual skill paths, output paths, selected check IDs, site and packet digest. The host agent dispatches native subagents with those contracts. Use `--mode sequential` when delegation is unavailable; the tasks remain the same.

The guideline worker returns the complete row-level review. The evidence and claims workers return explicit issues with check IDs, evidence IDs and requested corrections. Workers record actual harness/model/reasoning settings. New Sol 6.1 and DeepSeek V4.1 Flash tasks require high reasoning.

```sh
uv run --locked --script audit/cli.py tool orchestrate accept \
  --task /absolute/output/review-tasks/evidence.task.json
uv run --locked --script audit/cli.py tool orchestrate status \
  --tasks /absolute/output/review-tasks
```

Accept each role separately. Validation checks packet identity, model settings, selected-check coverage and resolvable references. A file's presence is only “needs validation”; changing a validated result invalidates its acceptance. This detects contract violations, not semantic correctness or actual delegation. Retain host traces when available.

## Reconcile and score

The coordinator addresses every evidence/claims issue in a separate resolutions file. Each response names `role:issue-id`, a decision (`applied`, `retained-with-reason` or `needs-new-evidence`) and its reason. Missing evidence stays unresolved; agreement between workers is not new evidence.

```sh
uv run --locked --script audit/cli.py tool orchestrate reconcile \
  --tasks /absolute/output/review-tasks \
  --resolutions /absolute/output/resolutions.json
uv run --locked --script audit/cli.py tool workflow score \
  --session /absolute/output/session --review /absolute/output/session/review.json
```

The coordinator writes the final review from the guideline worker's output plus explicit resolutions. The existing scorer validates that final review and calculates once per guideline group. The reconciliation receipt proves that every advisor issue received a response; it does not prove the response was correct. Keep the role outputs and resolutions beside the session for review.

## Estimate annual impact

The agent retrieves an exact-origin CrUX rank and freezes the traffic proxy outside the scored session. It then calculates independent SWDM v4 and optional client-energy scenarios. Keep source month, mapping digest, page weights and electricity assumptions with the result; a missing rank is not zero traffic. These commands are agent-operated tools, not owner setup steps.

```sh
uv run --locked --script audit/cli.py tool traffic https://example.org \
  --output /absolute/output/traffic.json
uv run --locked --script audit/cli.py tool annual \
  --staged /absolute/output/session/staged.json \
  --traffic /absolute/output/traffic.json \
  --energy /absolute/output/energy/manifest.json \
  --visit-selection first --client-grid-intensity 494 \
  --output /absolute/output/annual.json
```

Use the GreenFrame manifest produced by collection. Omit `--energy` when no valid client-energy experiment is available. During report preparation, apply the claims-review skill to these additional inputs and keep the resource-model projection separate from SWDM and electricity-meter readings. A hypothetical improvement percentage illustrates scale without claiming a demonstrated saving.

If the plan declares `auditScope`, pass that exact URL as `--audit-scope` to the annual calculator. For a service under a shared host, such as `https://example.org/project/`, origin-wide CrUX traffic cannot establish project pageviews. Both annual projections remain unavailable; ask for traffic limited to the service. The renderer verifies the declared scope against the frozen plan and rejects an origin-only annual calculation for a path-scoped audit.

Failed document loads stop annual estimation by default. An explicitly chosen `--exclude-failed-pages` scenario can use the smaller successful-page sample. It retains the original evidence hash and lists excluded URLs, run IDs, HTTP outcomes and reasons. The report discloses the reduced sample; a failed first visit is never replaced silently by a later success. Inspect successful responses too: a security-check page is not representative documentation just because its HTTP status is successful.

## Write and illustrate the report

The report worker applies `sustainability-report` to the scored session and writes a separate editorial file. It keeps the score and check outcomes intact while producing plain-language explanations. Owner feedback may revise priorities through a separate review-bound presentation supplement with an explicit reason. Selected screenshots remain separate illustrations with their own capture time and state.

```sh
uv run --locked --script audit/cli.py tool render_review \
  --session /absolute/output/session \
  --editorial /absolute/output/editorial.json \
  --annual /absolute/output/annual.json --traffic /absolute/output/traffic.json \
  --energy /absolute/output/energy/manifest.json \
  --artifact-prefix session --output /absolute/output/report.md
```

Use the renderer's screenshot options when the writer has selected and inspected illustrations. The [reporting reference](../reference/reporting.md) explains the report layout, technical appendix and chart export. The coordinator checks the rendered report before delivery, including whether its narrative matches the evidence.

## Durable artifacts and recovery

| Artifact                                             | Purpose                                                              |
| ---------------------------------------------------- | -------------------------------------------------------------------- |
| Plan and collection receipt                          | Scope, assumptions, commands, failures and implementation provenance |
| Session packet, raw observations and skill snapshots | Frozen evidence and the exact review instructions                    |
| Role tasks, results and acceptance receipts          | Assigned work, actual settings and validated handoffs                |
| Resolutions and final review                         | Coordinator decisions and unresolved disagreements                   |
| Scores, editorial file, screenshots and report       | Reproducible calculation and readable delivery                       |

Use a new session for corrected collection or broader scope. Do not mutate observations behind a frozen packet. Preserve worker failures and allow a bounded retry rather than endless delegation. Store outputs in the user's working project, outside plugin caches. New plugin versions can change instructions while existing sessions keep their evidence and recorded settings.

The [orchestration research](../knowledge-base/agent-orchestration.md) explains the host-native design and alternatives. The next validation gate is a complete task across multiple harnesses; current contract tests and local manifest checks are narrower evidence.
