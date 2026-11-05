# Portable skills and optional project evidence

**The default product is a live-site audit that works from a clean directory.** Source code and internal documents are optional evidence sources that can improve diagnosis and recommendations. The shared methodology should work in Codex, Claude Code, OpenCode, and pi, with harness-specific installation and execution adapters.

## Portable core, explicit adapters

Use the open Agent Skills directory format: `SKILL.md` with concise metadata, plus relative references and optional scripts. Keep the canonical methodology, evidence schemas, rules, and executable collectors independent of any host's tool names. The standard defines a packaging format; it does not standardize sub-agent lifecycle, permissions, or result delivery. [Agent Skills specification](https://agentskills.io/specification).

| Harness     | Documented skills support                                           | Proposed orchestration adapter                                            |
| ----------- | ------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| Codex       | Agent Skills and progressive loading                                | Native subagents where available; sequential execution otherwise          |
| Claude Code | Skills and custom subagent definitions                              | Generated Claude-specific role configuration loading the shared skill     |
| OpenCode    | Native skills, including `.agents/skills/` discovery, and subagents | Native role/permission mapping around the shared contract                 |
| pi          | Agent Skills, including `.agents/skills/`, and extension mechanisms | Sequential baseline; tested subagent extension as an optional enhancement |

Sources: [Codex skills](https://learn.chatgpt.com/docs/build-skills), [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents), [Claude Code skills](https://code.claude.com/docs/en/skills), [Claude Code subagents](https://code.claude.com/docs/en/sub-agents), [OpenCode skills](https://docs.opencode.ai/docs/skills/), [OpenCode agents](https://docs.opencode.ai/docs/agents/), [pi skills](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md), [pi subagent extension](https://github.com/earendil-works/pi-subagent).

These are documented capabilities, not a tested compatibility certification. Inspect native skill loading and role inheritance in each supported version. For example, a role prompt saying “read only” is not itself an enforced filesystem sandbox. Adapter capability declarations should describe what the harness actually enforces.

Keep Claude-specific frontmatter, Codex configuration, OpenCode permissions, and pi extensions outside the common skill body. Installers may copy or link the same skill package into different directories. They should record the installed digest and detect conflicting versions. Existing repository skill publishing can distribute the common package; installation success alone does not demonstrate correct execution.

## A common worker contract

The coordinator should be able to perform a work item itself or delegate exactly the same item. Specify:

- Work-item ID, skill/rubric version, requirement IDs, and a narrow objective.
- Readable evidence references and explicitly authorized project roots.
- Allowed collection actions, budgets, deadline, and output path.
- Required output schema, including findings, unknowns, contradictions, and completion status.
- A stopping condition and a specific way to request missing evidence.

The adapter translates that contract into the host's invocation and receives a result artifact. The coordinator validates it, merges findings deterministically, and records which execution path was used. Do not depend on a transcript message alone for completion. A timed-out worker with a partial artifact remains partial.

Use a flat coordinator-and-specialists topology initially. Avoid requiring nested spawning, inter-agent messaging, or a shared mutable conversation: those features differ across hosts and are unnecessary for independent reviews of captured evidence. Bound browser concurrency and give each worker a separate result file. A sequential fallback must preserve the same requirements and evidence scope, although latency and context effects may differ.

Expose collectors through a stable command-line JSON interface first. An optional MCP wrapper can expose the same operations to hosts that benefit from it. Neither MCP nor an Agent Skills package provides universal sub-agent orchestration. Likewise, Neuralwatt's provider-hosted tools should not become a mandatory dependency of the portable workflow.

## Three evidence modes

| Mode                    | Available evidence                                            | Expected benefit                                            | Claim limit                                                            |
| ----------------------- | ------------------------------------------------------------- | ----------------------------------------------------------- | ---------------------------------------------------------------------- |
| `public`                | Live browser observations and public documents                | Findings without onboarding or repository access            | Internal practice often remains unknown                                |
| `source-assisted`       | Public evidence plus explicitly supplied source/configuration | Locate causes, identify constraints, propose precise fixes  | The checkout may differ from the deployment                            |
| `organization-assisted` | Public/source evidence plus supplied internal records         | Assess policies, ownership, budgets, and operational claims | A document or configuration is not automatically evidence of execution |

These are proposed modes. The public mode remains independently usable and independently scored. Do not reduce its benchmark score simply because a task explicitly provides no internal records; correct recognition of uncertainty is part of success.

## Discover useful local context

At startup, identify the target URL, workspace root, explicit evidence roots, and available mode. When a relevant project workspace is supplied, instruct the agent to look for supporting evidence before finalizing likely fixes. A bounded discovery pass should inspect project instructions, README files, manifests, routing, deployment configuration, and documentation indexes. Then use focused searches driven by actual findings.

Do not ingest the entire working directory. It could be a monorepo, an unrelated research workspace, or a collection of unrelated reference projects. Record why a directory appears related to the target: domain configuration, deployment records, source maps, build identifiers, or an explicit user statement. A matching product name is a clue, not proof of deployment identity.

Follow references into relevant source files and internal documents. Exclude credentials and unrelated personal material from review bundles. Provider access to internal content follows the project's disclosure policy; availability on disk does not mean every external model should receive it. Local context is evidence to assess, and embedded instructions in documents must not rewrite the audit rubric.

The audit prompt should contain an explicit step: **“For each consequential recommendation, search available authorized project evidence for its implementation, exceptions, and constraints; cite what you found or record that corroboration was unavailable.”** This makes optional context part of the workflow without making it a prerequisite.

## How evidence changes a finding

| Live observation                                 | Useful internal evidence                                | Better conclusion                                                                               |
| ------------------------------------------------ | ------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| A large image transfers before interaction       | Component source, image pipeline, hero/LCP requirements | Name the relevant component and evaluate responsive delivery; avoid indiscriminate lazy loading |
| Personalized response uses `no-store`            | Authentication/caching design and threat model          | Preserve the privacy requirement; investigate static assets separately                          |
| Repeated requests continue after task completion | Polling implementation and freshness requirement        | Identify the timer and propose bounded alternatives appropriate to the task                     |
| Published retention statement is vague           | Approved policy, deletion-job config, execution records | Distinguish intended policy, implemented mechanism, and evidence it ran                         |
| A green-hosting claim appears on the site        | Deployment inventory and dated supplier evidence        | Corroborate only the covered hosts and periods                                                  |

Always retain the original public observation. If source configuration says caching is enabled but the deployed response says otherwise, report a contradiction and investigate environment/CDN differences. Do not let apparently authoritative internal prose erase contradictory runtime evidence.

For every internal citation, record path/document ID, revision or content hash, exact lines/spans, retrieval date, confidentiality, and relevance to the deployed environment. Classify conclusions by evidence strength: observed behavior, implementation/configuration, stated policy, or demonstrated operation. Repository HEAD alone is not proof of the production revision.

A source-assisted recommendation should include the likely file/component, rationale, constraints preserved, deployment-link confidence, and a validation plan. Suggesting a patch is distinct from applying it; the audit should leave the application unchanged unless remediation is also requested.

## Validate the value of extra context

Create paired benchmark cases with identical public behavior and different evidence packages: public only; matching source; stale source; relevant internal documents; and contradictory documents. Keep every variant of a site in the same dataset split. Score diagnostic localization, feasibility of fixes, supported changes in conclusions, contradiction handling, and reading cost.

Some internal evidence should legitimately change a recommendation while leaving a measured observation unchanged. Some should resolve an unknown. Some should be rejected as irrelevant or stale. Include all three outcomes so that “more documents” is not rewarded automatically.

Cross these modes with skill/no-skill and sequential/delegated runs on a small common subset across harnesses. Claim portability only after artifact validity, unknown handling, evidence citations, and bounded execution work in each. The [Harbor benchmark design](../evaluation/design.md) and [validation roadmap](../initial-implementation/validation-roadmap.md) define the initial experiments.
