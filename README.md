# Web sustainability agents

Audit a live website with an agent: collect repeatable measurements, review evidence against the Web Sustainability Guidelines (WSG), and produce a per-site report with key measures, a scoped score, prioritized findings and next auditing steps. Add source code or internal documentation when available.

**Development preview.** The working distribution is this checkout plus Agent Skills. There is no released Agent Plugin or one-command installer yet. Codex has been exercised; Claude Code, OpenCode and pi compatibility still needs end-to-end validation.

## Try an audit

Use Git, uv `>=0.12.20,<0.13`, Node.js 26 with npm, and an authenticated agent with terminal access. uv manages Python 3.14.

```sh
git clone https://github.com/thibaudcolas/web-sustainability-agents.git
cd web-sustainability-agents
uv sync --locked
npm ci
uv run python -m playwright install chromium
uv run --locked --script audit/workflow.py --help
```

Start your agent in the checkout and ask:

```text
Use sustainability-audit to audit https://example.org. Start with three
representative public pages and one visitor journey. Ask about missing scope
that would materially change the work, run the collectors, apply the review
skills, and produce one report with evidence, a scoped score and next steps.
Keep the session under .audit-work/.
```

Codex discovers the included `.agents/skills/` folders. For other harnesses, source-assisted audits, expected outputs and troubleshooting, follow **[installation and your first audit](docs/using/README.md)**. That guide also describes the proposed Agent Plugin experience and what remains to implement. Installing skills alone does not install collectors or browsers.

## Explore

- [Example reports](docs/reports/README.md): current guide.wagtail.org and wagtail.org audits, with linked evidence.
- [Knowledge base](docs/knowledge-base/README.md): WSG/STAR, carbon, scoring, measurements and tools.
- [Feasibility study](docs/feasibility-study/README.md): research and design rationale.
- [Implementation project](docs/initial-implementation/README.md): current capabilities, roadmap and backlog.
- [Evaluation project](docs/evaluation/README.md): Harbor campaigns, model comparisons and reviewable cases.

The preview's scoped scores and development benchmarks do not establish full WSG conformance or general audit accuracy.

## Contribute

See [Contributing](docs/contributing/README.md) for `just init`, tests, lint and documentation commands. [Skill maintenance](docs/contributing/skills.md) covers publishing. The MkDocs workspace originated from [research-workspace-template](https://github.com/thibaudcolas/research-workspace-template).

## License

MIT — see [LICENSE](LICENSE). Bundled WSG references retain their W3C license.
