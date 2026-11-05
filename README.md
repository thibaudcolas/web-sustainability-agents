# Web sustainability agents

Give your agent a website URL. It prepares the audit tools, samples representative pages, measures browsing behavior, coordinates specialist reviews, and produces a sustainability report with clear priorities and evidence.

**Development preview:** the plugin and skill workflow are implemented; broader cross-harness and independent audit validation remain in progress.

## Install and ask

Install the repository as a plugin in a compatible client. For Claude Code:

```text
/plugin marketplace add thibaudcolas/web-sustainability-agents
/plugin install web-sustainability-agents@web-sustainability-agents
```

Then ask:

```text
Use sustainability-audit to audit https://example.org.
```

The agent owns setup and execution. It defaults to 5–10 representative pages, uses native specialist subagents where supported, and asks only questions that materially affect the work. Source code and internal documents can strengthen an audit when available.

See **[installation and your first audit](docs/using/README.md)** for Codex, project-skill installation, prerequisites, actual compatibility limits and expected outputs. The plugin registers one discovery skill; the version-matched CLI loads deeper instructions as needed. New Sol 6.1 and DeepSeek V4.1 Flash reviews use high reasoning.

## Explore

- [Example reports](docs/reports/README.md): four Wagtail ecosystem sites, including public-only and source-assisted audits.
- [Knowledge base](docs/knowledge-base/README.md): WSG/STAR, carbon, scoring, measurements and tools.
- [Project assessment](docs/initial-implementation/project-assessment.md): what works, what misses the goals and the next milestone.
- [Implementation project](docs/initial-implementation/README.md): roadmap and prioritized backlog.
- [Evaluation project](docs/evaluation/README.md): Harbor campaigns, comparisons and reviewable cases.
- [Feasibility study](docs/feasibility-study/README.md): research and design rationale.

Scoped scores and development benchmarks do not establish full WSG conformance or general audit accuracy.

## Contribute

See [Contributing](docs/contributing/README.md) for development commands and [skill maintenance](docs/contributing/skills.md) for publishing. The MkDocs workspace originated from [research-workspace-template](https://github.com/thibaudcolas/research-workspace-template).

## License

MIT — see [LICENSE](LICENSE). Bundled WSG references retain their W3C license.
