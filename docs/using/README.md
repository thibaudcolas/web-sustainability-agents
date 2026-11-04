---
search:
  boost: 3
---

# Run a sustainability audit with an agent

Install the audit entry point, then give your agent a URL. It prepares the tools, chooses a representative sample, collects evidence, coordinates specialist reviews and writes a readable report. You answer questions about your website; the agent operates the audit scripts.

**Development preview:** plugin manifests, native specialist descriptors, a progressive skill CLI and validated review handoffs are implemented. Local manifest validation and fixture tests do not yet establish end-to-end parity across every harness. The [reports](../reports/README.md) show current output, and the [evaluation project](../evaluation/README.md) records validation limits.

## Install

The host needs Git, uv `>=0.12.20,<0.13`, Node.js 26 with npm, and an authenticated agent with terminal access. The agent's setup role installs the locked Python dependencies and Playwright Chromium when needed. Browser system libraries may require runner-specific setup. Harbor, Docker and energy tools are not required for the baseline.

### As a plugin

The repository supplies an Agent Plugins manifest and a Claude-compatible marketplace. Install from `thibaudcolas/web-sustainability-agents` using your client's plugin mechanism. For example:

```text
Claude Code
/plugin marketplace add thibaudcolas/web-sustainability-agents
/plugin install web-sustainability-agents@web-sustainability-agents

Codex CLI
codex plugin marketplace add thibaudcolas/web-sustainability-agents
codex plugin add web-sustainability-agents@web-sustainability-agents
```

The plugin registers **one entry skill**, `sustainability-audit`. Detailed roles are loaded only when needed. Native specialist definitions ship for Claude Code; other hosts can delegate the same task files through their native subagent tools. Do not assume that installing the plugin proves the whole workflow works in every client. The installed Codex CLI and the [Claude plugin reference](https://code.claude.com/docs/en/plugins-reference) establish the command/manifest mechanisms; this project still needs a clean end-to-end install-and-audit campaign.

For local development, clone the repository and load it with your harness's local-plugin mechanism, such as `claude --plugin-dir /absolute/path/to/web-sustainability-agents`. The agent resolves tools from the plugin's location, so you can remain in the website's working directory.

### As a project skill

For a harness that reads project skills, use the supplied installer once:

```sh
git clone https://github.com/thibaudcolas/web-sustainability-agents.git
uv run --locked --script web-sustainability-agents/scripts/install_audit.py \
  --harness codex --project /absolute/path/to/your-project
```

Choose `codex`, `claude-code`, `opencode` or `pi`. The installer copies only the entry point and records the collector checkout's location. It refuses to overwrite existing skills; `--dry-run` previews paths. Keep the checkout available. Claude Code uses `.claude/skills/`; the other routes use `.agents/skills/`. Restart the agent after installation.

This follows the progressive-disclosure approach in [Wagtail CLI](https://github.com/wagtail/wagtail-cli): a small discovery skill loads version-matched instructions from a CLI. This prototype's CLI is invoked from its checkout with uv; it is not yet a published standalone PyPI package. The provisional name `wsa` in CLI help is not a reserved or released command.

## Give it a URL

In your agent, ask:

```text
Use sustainability-audit to audit https://example.org.
```

Or add the context you already know:

```text
Audit https://example.org for sustainability. Our main tasks are reading
articles and finding contact information. The matching source is in this
working directory. Use it to corroborate fixes, and keep internal evidence private.
```

Claude Code's plugin skill is also available as `/web-sustainability-agents:sustainability-audit`. Naming the skill in an ordinary request works with hosts that support discovery. You do not need to copy a workflow prompt, select technical checks or run collector commands yourself.

The default is **5–10 representative public pages**, including the homepage, plus a meaningful visitor journey. The agent discovers the other pages from navigation, site information and your priorities. It records why they were selected and explains any smaller sample. Ask for a narrower audit when that is what you need.

Questions should be about decisions that change the audit: important tasks, audience requirements, source access or restricted flows. Already supplied answers should not be requested again. A public-only audit works without code or internal documents.

## What the agent does

| Role                  | Responsibility                                                                                    |
| --------------------- | ------------------------------------------------------------------------------------------------- |
| Coordinator           | Own the conversation, scope, handoffs, disagreements and final delivery                           |
| Setup and sampling    | Check prerequisites and choose useful pages and journeys                                          |
| Collection            | Run the agreed capture once and explain incomplete observations                                   |
| Quantitative reviewer | Check measurement interpretation, units, phases and numeric claims                                |
| Guideline reviewer    | Judge the scoped WSG checks against evidence and the versioned rubric                             |
| Claims reviewer       | Check disclosures, source relationships and recommendation prerequisites                          |
| Report writer         | Explain priorities in plain language, choose illustrations and build a readable evidence appendix |

After collection, the three reviewers can work as independent native subagents on the same frozen packet. The coordinator reconciles their findings before scoring. If delegation is unavailable, the same tasks run sequentially and that mode is recorded. The CLI validates artifacts; it does not call models, run a second agent platform or hide a proprietary router.

New GPT-6.1 Sol audit and report-writing runs use **high reasoning**; Neuralwatt DeepSeek V4.1 Flash remains high. Historical low-reasoning results keep their original labels and scores.

## What you receive

The agent delivers one report per origin, with first-load page sizes in kB or MB, a scoped score, priorities, readable evidence explanations and next auditing steps. Cookie choices and scrolling appear separately from the headline numbers. Useful screenshots have alternative text, captions and their own capture context.

A private session under your working project's `.audit-work/` retains the plan, source evidence, command receipts, worker outputs and exact scoring inputs. The report should be understandable without opening JSON. Technical reproduction files remain available in its appendix. Review any captured source, text and images before publishing them.

The score describes the checks attempted, not full WSG conformance or a universal sustainability grade. Partial measurements and unanswered questions remain visible. The [workflow reference](workflow.md) documents the underlying commands for contributors and agents, rather than making them prerequisites for the owner.

## Updates and troubleshooting

Update the plugin through your client's mechanism, or update the checkout and reinstall the project entry point after preserving any local customization. Keep audit outputs outside the plugin cache so an update or removal does not delete them. Existing sessions retain frozen inputs.

If a skill is not discovered, name its `SKILL.md` path explicitly. If the runtime location is missing, refresh the installation. If a prerequisite is unavailable, the agent should identify that exact blocker. Collector or worker failures remain recorded; the agent should not quietly turn them into passes or ask you to become its command runner.
