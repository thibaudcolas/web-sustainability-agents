---
search:
  boost: 3
---

# Run a sustainability audit with an agent

Use an agent to investigate a live website, collect repeatable measurements, and produce one evidence-linked sustainability report per site. Start with a public URL; add source code or internal documents when available. The agent applies the Web Sustainability Guidelines (WSG), explains uncertainty, and identifies the next useful improvements and investigations.

**Development preview:** the working installation is a repository checkout plus Agent Skills. There is no released Agent Plugin, standalone audit package, or one-command installer yet. Codex has been exercised; the other harnesses below have documented skill-loading mechanisms but still need an end-to-end compatibility test. See [example reports](../reports/README.md) before deciding whether this preview fits your needs.

## Install the working preview

You need Git, uv `>=0.12.20,<0.13`, Node.js 26 with npm, and an agent with terminal access and its own model authentication. uv manages Python 3.14 and the pinned script dependencies. Commands below run from the audit checkout, not from the website's source repository.

```sh
git clone https://github.com/thibaudcolas/web-sustainability-agents.git
cd web-sustainability-agents
uv sync --locked
npm ci
uv run python -m playwright install chromium
uv run --locked --script audit/workflow.py --help
```

This installs the repository development environment and browser; reducing that dependency footprint is part of the packaging work. On a Linux runner missing browser system libraries, use Playwright's `install --with-deps chromium` setup for that runner. The baseline does not need Harbor, Docker, GreenFrame or provider API keys beyond those used by your agent. Optional energy adapters have separate prerequisites.

Record `git rev-parse HEAD` when sharing a run. This preview follows repository revisions, rather than a published stable release. Python script lockfiles pin collector dependencies; the agent records its model and reasoning settings separately.

## Load the audit skills

The four audit skills live in `.agents/skills/sustainability-*`. Keep each complete folder, including references and licenses. The fifth skill, `research-workspace`, is only for maintaining this repository's documentation.

| Agent       | Local setup                                                                 | Start the audit                                           |
| ----------- | --------------------------------------------------------------------------- | --------------------------------------------------------- |
| Codex       | Start in this checkout; `.agents/skills/` is discovered directly            | Name `sustainability-audit` in your request               |
| Claude Code | Copy the four complete audit folders into this checkout's `.claude/skills/` | Invoke `/sustainability-audit` or name it in your request |
| OpenCode    | Start in this checkout; `.agents/skills/` is a supported location           | Ask it to load `sustainability-audit`                     |
| pi          | Start in this checkout; `.agents/skills/` is a supported location           | Invoke `/skill:sustainability-audit`                      |

These locations follow the official [Codex skill documentation](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills), [Claude Code skills](https://code.claude.com/docs/en/skills#choose-where-skills-load), [OpenCode skills](https://opencode.ai/docs/skills/#place-files), and [pi skills](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md). Loading a skill is distinct from validating the full audit on that harness.

For a fresh Claude Code setup, copy the folders from the checkout root:

```sh
mkdir -p .claude/skills
cp -R .agents/skills/sustainability-audit .claude/skills/
cp -R .agents/skills/sustainability-evidence-review .claude/skills/
cp -R .agents/skills/sustainability-guideline-review .claude/skills/
cp -R .agents/skills/sustainability-claims-review .claude/skills/
```

Check for existing customized copies before replacing them. Start a new agent session after setup. Keep these installation copies local unless your team intentionally shares them; the maintained originals remain under `.agents/skills/`.

If your agent does not discover skills, ask it to read `.agents/skills/sustainability-audit/SKILL.md` and follow the referenced workflow. It needs file access, terminal execution, and network/browser access for collection. Native subagents are optional: the coordinator can apply the specialist roles sequentially. Installing a skill never installs the collector runtime automatically.

## Ask for an audit

Start your agent from this checkout and use a request like:

```text
Use sustainability-audit to audit https://example.org.

Prioritize reading an article and finding contact information. Start with
three representative public pages and one complete visitor journey.
Use public evidence only; no account access or form submissions.

Measure first load without interaction, consent choices where available,
and scrolling. Lead the report with first-load figures. Look for carbon.txt
and public sustainability statements, and use technology detections as context.

Ask about missing scope decisions that would materially change the work.
Run the collectors, apply the review skills, and produce one Markdown report
with a scoped score, key measures, top findings, detailed evidence, next auditing
steps, and reproducibility information. Keep the session under .audit-work/.
```

Replace the example origin and tasks. The agent should refine the sample, discover actual consent controls, define journey completion, and record assumptions before collecting. It should inspect failures, preserve unknowns, and use the deterministic scorer after reviewing the evidence. This is an instruction to perform the work; the Python workflow itself does not call a model or make qualitative judgments.

Our comparison baseline uses GPT-6.1 Sol with low reasoning and Neuralwatt DeepSeek V4.1 Flash with high reasoning. Those are experiment settings, not mandatory requirements for using the skills. The [evaluation project](../evaluation/README.md) records what has been tested.

## Add source code or internal context

You can leave the agent in the audit checkout and point it at another accessible repository:

```text
Also inspect /absolute/path/to/site-source and its relevant documentation.
Use it to corroborate likely fixes. Record the revision and whether it matches
the live deployment. Select specific files for the audit packet; do not assume
that a local declaration proves deployed behavior. Keep internal evidence private.
```

The agent puts declared roots and explicit `{root, path}` selections in the plan. Source checks join the default scope only when files are selected. The collector reads up to thirty selected files without executing project code; larger files may contribute identity metadata only. See the [check and source reference](../reference/checks.md#source-evidence-in-the-same-packet).

If you start from the website's repository instead, provide the audit checkout's absolute path and ask the agent to run collector commands from there. Copying skill folders into the website repository is enough for discovery, but the collector checkout and its dependencies are still required. Internal evidence must be appropriate for the model/provider you choose.

## What you receive

A private session directory contains the frozen plan, evidence, skill snapshots, command receipts, review packet, model judgments and scoped scores. The agent prepares a Markdown report alongside them; a separate exporter produces chart-ready JSON/CSV. The [workflow reference](workflow.md) gives the exact commands and handoffs.

The report starts with key measures, scoped score and up to five priorities, then separates quantitative observations from qualitative findings. It ends with coverage gaps and reproducibility. The score is a proportion of attempted guideline groups with scoped passes; it is not full WSG conformance. Digital Carbon Ratings, annual scenarios and measured energy have separate meanings and availability. See [report contents and data](../reference/reporting.md).

Review the report and any evidence before publishing. A private session can contain copied source, page text and logs. Preserve the original session; publish a separate inspected copy when needed.

## Updates and troubleshooting

Use a clean checkout of the revision you want, rerun dependency setup, and refresh any copied skills together. Existing sessions retain their frozen inputs; use a new session directory for a new collection.

| Symptom                           | Next action                                                                                                          |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Skill not listed                  | Check the harness-specific location or explicitly load its `SKILL.md`                                                |
| Collector file not found          | Run from the audit checkout, even when the website source is elsewhere                                               |
| Browser cannot start              | Install the pinned browser and the host's required browser libraries                                                 |
| A consent action or journey fails | Inspect the actual page and selectors; preserve the failed attempt and collect a new session after correction        |
| Session directory already exists  | Choose a new directory; collection intentionally refuses to overwrite evidence                                       |
| Scorer rejects the review         | Check every selected check ID, packet hash, evidence ID and reviewer setting against the session template            |
| Many unknown findings             | Inspect whether the missing evidence needs another journey, selected source, or an owner answer; do not force passes |

## Proposed Agent Plugin experience

The intended experience is to install one audit package in a supported agent, name a URL and useful tasks, answer relevant scope questions, and receive a report plus reproducible evidence. Harness-specific installation should load the same skills and checks. A plugin should locate its own collectors so users do not need to switch working directories.

**This is a design target, not an installation command available today.** Before documenting a plugin install command, we need:

1. Versioned plugin manifests and distribution metadata, with the four audit skills and their references.
2. Reliable collector-path resolution and explicit dependency/browser setup, including useful missing-prerequisite diagnostics.
3. A stable output location independent of the plugin cache and a defined update/uninstall behavior that preserves audit sessions.
4. A clean-install test and the same complete audit task under Codex and at least one other harness, including sequential review when subagents are unavailable.

Claude Code's [plugin format](https://code.claude.com/docs/en/plugins) demonstrates packaging skills and optional agent integrations together. Codex CLI 0.166.0 also exposes plugin management, but this repository supplies no marketplace or plugin manifest. OpenCode/pi adapters can keep using skills without requiring identical packaging. No MCP server or automatic hooks are required by the current workflow.

The [implementation roadmap](../initial-implementation/validation-roadmap.md) tracks this packaging work alongside the next audit validation steps.
