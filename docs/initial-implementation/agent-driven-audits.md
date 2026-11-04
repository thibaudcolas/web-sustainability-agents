# Repeatable audits driven by agents

The coordinator skill now owns scope clarification, plan creation, collector execution and evidence review. `audit/workflow.py` implements the file-based handoffs. It accepts an arbitrary origin and selected public pages; the new path does not depend on the two Wagtail site constants in the earlier sampling experiment.

An agent can run it from Codex, Claude Code, OpenCode or pi using ordinary shell tools. Only Codex execution has been exercised here. Installing skills alone does not install Python, browsers or the collector checkout.

## Scope is an agent decision

Start with the owner's purpose and existing context. Ask concise questions when the answer changes the sample or interpretation: important visitor tasks, audience/support requirements, restricted processes and available source or internal documents. Record answers and assumptions in the plan. Optional questions need not stop independent public exploration; required unanswered questions prevent dependent collection. Do not ask the owner to repeat information already supplied.

The plan contains one exact origin, meaningful page tasks, explicit journeys, consent branches, selected checks, source locations and unresolved questions. The public baseline requires no internal access. Supplied source is useful for corroborating fixes, dependencies and document intent, but a checkout is not proof of deployment. This new public session path records source locations without automatically collecting their contents; the earlier source-assisted experiments remain available as examples.

The sample should represent content and functional diversity, with stated omissions. A two-page trial is an execution test, not representative whole-site coverage. The [STAR coverage discussion](skill-audit-workflow.md#current-star-coverage) still applies.

## Agent commands and handoffs

```sh
uv run --locked --script audit/workflow.py init \
  --origin https://example.org --page https://example.org/ \
  --plan .audit-work/example-plan.json
# The agent refines tasks, branches, journeys and assumptions in the plan.
uv run --locked --script audit/workflow.py collect \
  --plan .audit-work/example-plan.json --session .audit-work/example-run-1
# The agent applies the frozen review skills and writes review.json.
uv run --locked --script audit/workflow.py score \
  --session .audit-work/example-run-1 --review .audit-work/example-run-1/review.json
```

Collection runs the staged measurement, [interaction probes](interaction-checks.md) and [carbon declaration interpreter](../knowledge-base/carbon-disclosures.md). Wappalyzer remains a separate scan. First-load, consent and scroll measurements retain their established boundaries; the supplementary browser states do not become additional headline bytes.

A new session contains the plan, exact command receipts, script/lock hashes, skill snapshots, raw evidence, selected checks, a scoped rubric, an evidence index and a review template. Collectors are checkpointed; a command can finish with page-level errors, so the agent inspects both. The scorer requires one judgment per selected check, verifies referenced evidence and frozen methodology, and groups checks once per WSG guideline. Unknowns remain visible and cannot silently disappear from the denominator.

This is agent orchestration through explicit tools and artifacts, not a hidden model call in a Python wrapper. The agent decides what to investigate, runs the tools, interprets the evidence and asks follow-up questions. A deterministic calculator handles arithmetic. Bounded review roles can run as subagents or sequentially using the same contracts.

## Broader checks and interpretation

The new catalog has **12 browser review checks** plus **three disclosure/hosting checks**, covering 15 guideline groups. Eleven of those groups add scoped expectations beyond the historical 21-group method, giving **32 distinct groups with some defined review method across the two catalogs**. This union is not one scored audit and does not imply complete criterion coverage. The historical reports and scores retain their original rubric.

The guideline skill now includes a pinned extract of all **71 guidelines and 197 success criteria**. It preserves source version, digest, direct links and the W3C license. Agents load the relevant entries to understand the intended outcome and tradeoffs. The [101-row assessment crosswalk](wsg-check-expansion.md) covers all requested automated, manual quantitative and manual qualitative rows in the older assessment, mapping them to 83 current criteria across 40 guideline groups.

Those 101 routes are a coverage development plan. They are not 101 implemented tools or completed judgments. A manual quantitative task can become a browser scenario; a qualitative task can become evidence-backed agent review. Both still need a repeatable task definition and sufficient evidence. Internal operational claims need records or owner evidence when public observations cannot establish them.

The interpretation rules deliberately avoid shortcuts: initial unused-code coverage is not removable bytes; quiet snapshots do not prove that motion never occurs; print emulation does not establish PDF pagination; a visible heading is not task success; carbon.txt is an evidence index rather than proof of renewable hosting. Qualitative review evaluates user benefit, accessibility, privacy and organizational scope alongside environmental impact.

## Optional client energy

The [GreenFrame adapter](../knowledge-base/greenframe.md) prepares explicit initial, post-consent and post-scroll scenarios without server containers. Its prerequisites and generated files were tested, but the CLI is absent in this environment and no GreenFrame measurement is reported. Before comparative use, validate the runner, browser/image identity and repeated idle-host measurements. Keep GreenFrame modeled energy, co2-runner package energy and SWDM estimates separate.

## Next validation

The next useful benchmark should test the workflow itself: selecting scope, asking a necessary question, running the right scripts, handling a failed action and preserving unknowns. Use controlled sites and owner-reviewed judgments before adding further live sites. Then run a paired Harbor campaign with Sol/low and Neuralwatt DeepSeek/high; the existing campaigns evaluate frozen evidence and do not establish the accuracy of this new orchestration.

Historical methodology tasks now load frozen skill copies from `benchmarks/frozen-methodology-skills/`. Changing current skill instructions or references therefore does not silently change the inputs of an old benchmark. Cross-harness behavior, source evidence integration and skill/no-skill comparisons remain explicit [backlog items](backlog.md#repeatable-collection-and-broader-interpretation).

## Pilot reproduction

The coordinator executed the full collection workflow once for each known content site, using two pages and one explicit journey per site. Separate GPT-6.1 Sol/low reviewers applied the frozen skills without reading earlier human report conclusions. See the separate [guide findings](guide-audit.md#expanded-agent-review) and [Wagtail.org findings](wagtail-audit.md#expanded-agent-review). Both preserve uncertain journey results instead of treating collector failures as site defects. These are live development reviews, not a controlled model-comparison campaign or owner-validated ground truth.

The published [guide manifest](assets/agent-sessions/guide/manifest.json) and [Wagtail manifest](assets/agent-sessions/wagtail/manifest.json) hash exact JSON artifacts. Formatting is intentionally excluded for these frozen files. Raw command logs and skill copies remain private; receipts retain their hashes. The scope and evidence were inspected before publication. Collection ran with uncommitted implementation changes, so the script hashes supplement the recorded base Git revision. Before review, packet construction was strengthened to pin scope, weights, receipt and skill files; this changed packet provenance, not site observations or review expectations.

Recalculate either published score without network or model calls (use a new output path):

```sh
uv run --locked --script audit/assess.py   --reviews docs/initial-implementation/assets/agent-sessions/guide/reviews.json   --rubric docs/initial-implementation/assets/agent-sessions/guide/rubric.json   --weights docs/initial-implementation/assets/agent-sessions/guide/impact-weights.json   --assets docs/initial-implementation/assets/agent-sessions/guide   --output .audit-work/guide-agent-recalculated.json
```

Replace `guide` with `wagtail` for the second site. Recollecting the live site or rerunning a reviewer can produce different evidence or judgments and requires a new session. The existing annual scenarios and headline scores retain their original input captures; no mixed-campaign total is calculated.
