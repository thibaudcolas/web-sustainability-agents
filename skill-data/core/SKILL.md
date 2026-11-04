---
name: sustainability-core
description: Coordinate the complete sustainability audit through explicit native-agent tasks and deterministic artifact handoffs.
license: MIT
metadata:
  version: "0.2.1"
---

# Coordinate the audit

The owner gives a URL and optional priorities. You own setup, scope, collection, review and report delivery. Keep the conversation about their website, not shell commands. Reuse their answers; ask only questions that materially change what is authorized or useful.

Use the CLI `tool <name> ...` to invoke existing deterministic tools. Pass absolute plan, session and output paths, because tools execute from their installed root. Keep outputs in a new `.audit-work/<site>/<run>/` directory under the user's working project, never in the plugin cache. Record actual model, reasoning and execution mode. New Sol 6.1 and DeepSeek V4.1 Flash reviews use high reasoning unless the user requests another setting.

## Native role sequence

1. **Setup and sampling** — load `setup`, dispatch `sustainability-setup` with URL, known priorities, working project and source roots. It resolves prerequisites, explores public navigation and returns a plan covering 5–10 representative pages by default, including the homepage and a complete visitor journey. The coordinator handles owner questions and approves the scope within existing authorization.
   Load `context-review` during setup and select relevant qualitative checks from the site's public tasks, content, data collection and stated commitments. Dispatch a bounded contextual evidence task or perform it sequentially: capture attributed documents/observations and explicit unresolved requests before freezing. The owner need not know check IDs or grant internal access. Include selected `contextChecks`, one concrete assessment boundary per check in `contextScopes`, and `contextEvidence` in the plan; new audits normally select useful public context and therefore use the v3 extension. Reviewers must retain each frozen `assessmentScope`; changing it requires a linked new session. Preserve v2 only for an explicitly context-free scope.
2. **Collection** — load `collection`, dispatch `sustainability-collection` with the accepted plan and a new session directory. One collector owns the browser run; workers do not independently recrawl the same pages. It returns the packet path, command receipt and a summary of failed or incomplete observations.
3. **Independent reviews** — run `tool orchestrate tasks --session <session> --output <review-tasks> --mode native-subagents`. Dispatch evidence, guideline and claims workers concurrently against the same frozen session. Each receives its task JSON, named skill and output path. If native subagents are unavailable, use `--mode sequential` and apply the same contracts one at a time. Do not fabricate parallel execution.
4. **Validate and reconcile** — run `tool orchestrate accept --task <role.task.json>` for each result, then `status --tasks <review-tasks>`. Respond to every evidence/claims issue in `resolutions.json` as `{resolutions:[{issue:"role:id",decision:"applied|retained-with-reason|needs-new-evidence",reason:"..."}]}` and validate with `reconcile`. Use the guideline result as the base of `session/review.json`, making explicit, evidence-supported corrections. Preserve unresolved disagreements and missing evidence; reviewer agreement alone adds no site evidence.
5. **Calculate** — run `tool workflow score --session <session> --review <session/review.json>`. The scorer verifies the final review and calculates outcomes; neither coordinator nor reviewer invents an intuitive score.
6. **Report** — load `report`, dispatch `sustainability-report` with the scored session, owner's audience and a separate editorial-output path. It writes plain-language findings without changing judgments and selects useful screenshots. The coordinator inspects the final report, resolves any writing/evidence mismatch, renders it, and gives the owner a link with the key priorities.

Native Claude agent descriptors ship in `agents/`. Other harnesses dispatch their native subagent primitive with the same skill and task file. Prefer specialist roles to one agent per WSG criterion. If worker capacity is limited, queue independent reviews; do not repeat collection. Workers write only their assigned outputs and never mutate the frozen session.

## Completion and recovery

Read returned artifacts and actual exit status; a worker saying “done” is not a completed audit. A missing or invalid result stays pending. Retry a recoverable worker failure once with the same scope, preserving the failed attempt. Escalate an unresolved error with its precise missing artifact rather than inventing findings. A changed collection requires a linked new session; never append observations behind a frozen packet hash.

The orchestration CLI validates identity, settings, references and acknowledgment of reviewer issues. It does not prove the semantic accuracy of prose or independently run subagents. Record the host's actual delegation trace when available. Finish with the report, remaining unknowns and concrete next auditing steps; keep implementation details in its reproduction appendix.
