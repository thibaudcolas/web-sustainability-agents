# Portable agent orchestration

**Use a shared audit CLI to manage tools and artifacts, with a coordinator skill that delegates to the host's agents.** The user installs the integration and asks for an audit of a URL. The agent chooses a representative sample, runs the workflow, asks relevant questions, and delivers the report. The user should not need to assemble commands or transport prompts between workers.

The [Wagtail CLI](https://github.com/wagtail/wagtail-cli) is the primary design precedent: one discoverable entry skill, an installable Python CLI, and detailed workflow skills loaded from that CLI. Adopt that structure before adding an external orchestration framework. This page explains the architecture and remaining validation work; the [user guide](../using/README.md) identifies implemented entry points and compatibility limits.

## What to reuse from the reference projects

### Wagtail CLI: package and progressive instruction loading

The inspected Wagtail CLI revision, `fd8c3e6682cadabb1dff9c2a6d3f58af9d809d07`, packages a Python CLI using Typer, httpx, Pydantic and uv's build backend. Its published command is `wt`; installation uses `uv tool install`, with `uvx` available for one-off execution. Its design principles prioritize familiar Click/Typer behavior, predictable defaults, automation and clear messages. These are concrete technical precedents supplied for this project, not a request to choose a new framework. [Package configuration](https://github.com/wagtail/wagtail-cli/blob/fd8c3e6682cadabb1dff9c2a6d3f58af9d809d07/pyproject.toml), [design principles](https://github.com/wagtail/wagtail-cli/blob/fd8c3e6682cadabb1dff9c2a6d3f58af9d809d07/docs/contributing/design-principles.md).

The public `wagtail` skill is a small routing stub. Detailed skills live in the installed package's `skill-data` directory, outside automatic skill discovery. The CLI exposes `skills list`, `skills get NAME`, `skills get NAME --full`, and `skills path NAME`; agents load only relevant instructions and references. This makes workflow instructions follow the installed tool version and avoids advertising every internal specialist as a separate user entry point. [Agent skills guide](https://github.com/wagtail/wagtail-cli/blob/fd8c3e6682cadabb1dff9c2a6d3f58af9d809d07/docs/agent-skills.md), [skill loading implementation](https://github.com/wagtail/wagtail-cli/blob/fd8c3e6682cadabb1dff9c2a6d3f58af9d809d07/src/wagtail_cli/cli/skills.py).

For sustainability auditing, use one public audit skill that loads `core`, then setup, collection, review or reporting instructions as needed. Have the coordinator pass the relevant resolved instruction path to each worker. Snapshot the loaded instructions into the audit session: reading whatever version happens to be installed later would weaken reproducibility. Follow the same package structure and CLI conventions while retaining this repository's Python and uv version constraints.

Wagtail CLI also distributes its stub as an Agent Plugin. The portable plugin standard covers shared skills and MCP components; installation, permissions and client extensions remain client-specific. This supports a small common package, not a claim that every harness can load the same native agent descriptors. [Agent Plugins overview](https://agent-plugins.org/), [compatible clients](https://agent-plugins.org/compatible-clients).

### claude-seo and accessibility-agents: execution and delegation

The inspected claude-seo revision, `6be93f45064ffbadced572b5d5c95f55fd263af0`, gives skills a plugin-relative launcher rather than expecting the user to manage each Python tool. Its audit skill discovers site context, delegates specialist work when available, and falls back to sequential execution. It also asks specialists to leave partial findings so a turn limit does not discard all progress. These are useful patterns for our setup, collection and review roles. Its large crawl limit and SEO weights do not transfer to a sustainability audit. [Audit skill](https://github.com/AgriciDaniel/claude-seo/blob/6be93f45064ffbadced572b5d5c95f55fd263af0/skills/seo-audit/SKILL.md), [runtime](https://github.com/AgriciDaniel/claude-seo/blob/6be93f45064ffbadced572b5d5c95f55fd263af0/scripts/runtime.py).

The inspected accessibility-agents checkout, `7597f1a2cd315f144bc6a212ecceabf0268ea044`, separates domain specialists, requires structured findings, resolves the skill root before dispatch, and renders reports from saved results. An absolute package path matters when the user's current directory is an unrelated website repository. Adopt its explicit contracts and deterministic rendering; do not copy every specialist or its repeated approval checkpoints. Our coordinator should reuse supplied scope and ask only when an unanswered question changes the work. [Web audit coordinator](https://github.com/Community-Access/accessibility-agents/blob/7597f1a2cd315f144bc6a212ecceabf0268ea044/skills/web-accessibility-wizard/SKILL.md).

## Choose the orchestration boundary

| Approach                         | What it gives us                                                                                             | Main cost or gap                                                                      | Recommendation                                           |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| Shared CLI plus native subagents | Existing agent conversation, credentials and tools; portable artifact contracts; host-specific role adapters | Delegation, permissions and context inheritance vary by host                          | Primary interactive workflow                             |
| acpx sessions and flows          | Common headless ACP interface, machine output, inspectable multi-step execution                              | Evolving pre-1.0 interface, additional adapters, model/configuration parity to verify | First external-runner experiment                         |
| LangGraph application            | Explicit graph state, persistent checkpoints and interruption handling                                       | We would own a separate agent application and harness integrations                    | Reconsider if service-level durability becomes necessary |
| Harbor jobs                      | Controlled environments, agent adapters, trajectories and verifiers                                          | Benchmark execution is a different product experience from interactive auditing       | Keep as the evaluation runner                            |

Agent Skills standardizes the instruction/resource package, not subagent scheduling or result acceptance. Claude Code has custom subagent configuration and skill preloading; OpenCode has subagent modes and task permissions. Those are adapter features, not a universal runtime contract. A named role must still receive its actual instructions, scope and output destination. [Agent Skills specification](https://agentskills.io/specification), [Claude Code subagents](https://code.claude.com/docs/en/sub-agents), [OpenCode agents](https://opencode.ai/docs/agents/).

LangGraph's checkpointers persist thread state and support continuation, interruptions and fault tolerance. That is useful when the application needs to survive process or service restarts, but it does not by itself reproduce another coding agent's native skill loading or permissions. For the current local workflow, a small set of versioned files and validators is a more proportionate starting point. This is a project recommendation, not a claim that file persistence is equivalent to LangGraph's execution guarantees. [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence).

## The optional acpx experiment

An external runner is worth testing if we need unattended audits, scheduled execution or controlled switching between agent hosts. It is not a prerequisite for the one-URL interactive workflow. Keep the CLI and artifact contracts usable without it.

acpx provides one-shot and persistent agent sessions, structured output, timeouts, permission configuration and profiles for multiple coding agents. Its documented command shape can send a role task from a file. The project identifies itself as pre-1.0, so pin both acpx and the relevant agent adapter when testing it. A common command shape does not establish equivalent model access or tool behavior. [acpx overview](https://github.com/openclaw/acpx), [CLI reference](https://github.com/openclaw/acpx/blob/main/docs/CLI.md).

Its experimental flows distinguish agent turns, deterministic actions, pure computation, constrained decisions and checkpoints. They persist run state, transcripts, errors and artifacts. This resembles the audit's collection → review → calculation → report sequence. An audit flow could call our Python collectors in action steps and request structured specialist reviews in isolated agent steps. The documented flow runtime does not remove the need for our evidence hashes, semantic review, or explicit handling of unresolved questions. [acpx flows](https://github.com/openclaw/acpx/blob/main/docs/flows.md).

A bounded trial should run one read-only review task through acpx under two supported agents, validate the same output schema and evidence references, and interrupt one run deliberately. Check how the selected model and reasoning settings are applied, whether skill references resolve, and what is retained after cancellation. Do not treat a stream ending successfully as proof that the requested audit artifact is valid. No acpx run or compatibility result is claimed here.

## Protocols are useful at different layers

**ACP** standardizes client-to-coding-agent communication, originally centered on editors and IDEs, with sessions, tools and related interactions. It can support an external agent runner such as acpx. It does not specify this project's audit stages or make all hosts' native subagents interchangeable. [ACP introduction](https://agentclientprotocol.com/get-started/introduction).

**MCP** is an option for exposing our deterministic tools to agents that benefit from structured tool discovery. It focuses on exchanging context and capabilities; it does not dictate the host's model orchestration. Start with the CLI contract and add an MCP adapter only when it improves a supported host's experience. [MCP architecture](https://modelcontextprotocol.io/docs/learn/architecture).

**A2A** targets interoperable agent applications that discover one another, exchange tasks and return results. It could be useful if a future audit delegates to a separately hosted specialist service. Requiring agent servers and discovery for local review workers would add a boundary we do not currently need. The official A2A CLI is a client for A2A-compatible agents, not a drop-in controller for arbitrary native coding-agent subagents. [A2A overview](https://a2a-protocol.org/latest/), [A2A CLI](https://github.com/a2aproject/a2a-cli).

**Harbor** remains the benchmark boundary. It supports multiple installed-agent integrations and has a separate ACP registry integration. Its documentation distinguishes capabilities such as native-session resume and trajectory loading; adapter presence alone is not parity. Use it to test the same audit task under different execution modes, keeping setup errors separate from judgment errors. [Harbor agent integrations](https://docs.harborframework.com/agents/pre-integrated-agents), [Harbor ACP integration](https://docs.harborframework.com/agents/acp).

## A concrete audit sequence

Keep one coordinator and a small set of bounded specialists. Default to 5–10 representative public pages, including the homepage, unless the owner requests another scope or the site has fewer relevant pages. Page selection is agent judgment; a CLI should validate a plan, not invent arbitrary URLs to satisfy a count.

| Stage                    | Agent responsibility                                                                            | Deterministic responsibility                                            |
| ------------------------ | ----------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| Setup and scope          | Understand purpose, inspect site structure, select pages/tasks, resolve consequential questions | Locate installed package, check dependencies, validate the plan         |
| Collection               | Choose supported interactions, inspect failures, request targeted additional evidence           | Run one bounded capture campaign and preserve command/evidence receipts |
| Quantitative review      | Interpret measurement completeness, units and appropriate comparisons                           | Validate cited evidence and calculation inputs                          |
| Guideline review         | Apply scoped WSG expectations and preserve unknowns                                             | Enforce selected check IDs and outcome schema                           |
| Claims and source review | Assess disclosures, deployment relevance and feasible recommendations                           | Preserve source identity, scope and retrieval provenance                |
| Reconciliation           | Resolve conflicting interpretations or request discriminating evidence                          | Reject missing work and conflicting duplicate authoritative rows        |
| Report writing           | Explain findings clearly and choose useful illustrations                                        | Calculate scores, validate editorial links and render the report        |

Collection should normally have one owner. Three reviewers can inspect the same frozen packet independently without each recrawling the website. The report writer starts after reconciled judgments are accepted. Give it a writing skill and template; it may improve explanations but cannot silently change findings, evidence or scores.

The coordinator may use native subagents, a compatible external runner, or sequential roles. Preserve the same input and output requirements in all three modes. Record which mode actually ran: sequential application of three skills is not three independent agent reviews.

## CLI and artifact contract

The low-level workflow retains `audit/workflow.py init`, `collect`, and `score`. The agent-facing CLI and durable handoffs are described in the [workflow reference](../using/workflow.md). The table below is a target capability map, not a promise that every label exists as a command or that packaging and cross-host execution have been validated:

| Capability             | Input                                                        | Result or acceptance rule                                                          |
| ---------------------- | ------------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| `skills list/get/path` | Installed package and requested role                         | Version-matched instructions, references and absolute resource paths               |
| `doctor` / `prepare`   | Installed package and selected optional tools                | Machine-readable readiness and bounded setup diagnostics                           |
| `plan validate`        | Origin, selected pages, tasks, consent actions and questions | Reject inconsistent scope; preserve reason for a smaller sample                    |
| `collect`              | Validated plan and new session path                          | Frozen packet, receipts, explicit failed observations                              |
| `tasks prepare`        | Frozen packet and declared roles                             | Separate task files with skill path, owned checks, schema, limits and output paths |
| `results accept`       | Task identity and worker artifact                            | Validate origin, packet digest, owned checks, model settings and completion status |
| `reconcile`            | Accepted specialist outputs                                  | One authoritative review plus a record of resolved and unresolved disagreements    |
| `score` / `report`     | Reconciled review and editorial content                      | Validated scores and readable report, without fresh implicit observations          |
| `status`               | Session directory                                            | Validated completed stages, missing/failed work and next permitted actions         |

Each task needs a stable ID, role, package/skill version, exact evidence digest, authorized evidence roots, deadline, output schema and unique output path. Results need a terminal or partial status, actual execution mode/model/reasoning, cited evidence, and unresolved questions. A worker's “done” message is advisory; artifact validation is the completion gate.

Prefer disjoint ownership of authoritative guideline rows. Other specialists can propose corrections against those rows. Reconciliation should preserve the proposal and the coordinator's reason for accepting or rejecting it; do not vote by model count, silently pick the most favorable result, or let the final writer settle evidence disputes while polishing prose.

The CLI must resolve its own package root independently of the user's working directory. Keep session output outside an ephemeral plugin cache. A plugin update should not replace the skill snapshots or inputs of an existing session. Native adapter files can expose convenient commands and role defaults without duplicating the methodology.

## Recovery and checkpoints

Record stage receipts and attempt IDs. Distinguish a tool failure, an invalid worker artifact, an unresolved site observation and a human question. All can prevent a particular conclusion, but they need different next actions.

Resume from the last validated immutable artifact, not simply the last filename that exists. A failed review can retry against the same packet with a new attempt ID. A new collection should create a linked capture session, because live pages may have changed. Preserve the original attempt and never reinterpret a failed observation as a clean result.

A scope checkpoint is needed when a missing answer materially affects what may be audited. A reconciliation checkpoint is needed when evidence cannot resolve a consequential disagreement. These are useful boundaries for agent or owner decisions; they are not a requirement to ask permission before every reversible step. Deterministic validation gates can proceed automatically within the already authorized audit scope.

## Remaining decisions

The direction is established: a Python CLI following Wagtail CLI's conventions, one public discovery skill, progressively loaded role instructions, and host-native agents around explicit artifact contracts. We do not need another broad framework selection before testing this.

Three narrower choices remain:

- **First supported hosts:** validate Codex and Claude Code first, then OpenCode/pi. Keep other integrations labeled experimental until they complete the same clean-install and interruption scenarios.
- **Incomplete audit policy:** recommend allowing clearly labeled partial reports with unknowns and coverage gaps, while rejecting contradictory scores, invalid evidence references and silently missing roles. Define which failures prevent a report and which permit an explicitly limited one.
- **External runner timing:** defer acpx integration until a concrete unattended or scheduled use case requires it. A bounded adapter experiment can then test the same contracts without changing the audit methodology.

Package naming and the final command alias should be resolved when distributing the CLI. They do not block validating the workflow. None of these choices requires asking users to select an orchestration framework each time they request an audit.

## What to validate before calling this portable

1. Install into a clean environment and start from a directory with no audit source checkout. A URL request should lead to the same task contracts and report outputs without manually supplied collector commands.
2. Run the same controlled site with native delegation and the sequential fallback. Check sample selection, role completion, contradictions, unknowns and artifact provenance.
3. Interrupt collection and review separately. Verify that status is truthful, partial evidence remains inspectable and retries cannot overwrite an accepted result.
4. Repeat under a second harness with actual model/reasoning settings preserved. Include a required scope question and a failed selector, not just a successful frozen-evidence review.
5. Evaluate an acpx adapter only after the role contracts are stable. Compare the same task, including permissions, cancellation, reference loading and output validation.

Use the required Sol 6.1/high and Neuralwatt DeepSeek V4.1 Flash/high arms for new model comparisons; retain historical low-reasoning results with their original labels. Measure recommendation usefulness and unsupported conclusions, not just whether every stage produced a file. The [evaluation project](../evaluation/README.md) owns those comparisons; the [portable-audit design](../feasibility-study/portable-audits.md) covers optional project evidence and harness boundaries in more detail.
