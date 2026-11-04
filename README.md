# Web sustainability agents

Research and implementation of agentic web sustainability audits, combining deterministic checks, bounded model reviews, portable skills, and evaluations based on the Web Sustainability Guidelines (WSG).

## Documentation

- [Feasibility study](docs/feasibility-study/README.md): research findings, proposed architecture, decision models, and evaluation approach.
- [Initial implementation work](docs/initial-implementation/README.md): the runnable audit slice, Harbor benchmark, observed results, and validation roadmap.
- [Knowledge base](docs/knowledge-base/README.md): reusable methodology, tooling, and provider references.

The initial implementation is a development experiment. Its small benchmark does not establish general audit accuracy or autonomous sustainability assurance.

## Getting started

Requirements: `uv`, `just`, `prek`, `lychee`, and Node.js (pinned in `.node-version`). Harbor and Docker are additional requirements for the model benchmarks.

```sh
just init         # Install dependencies, browser, and hooks
just docs         # Serve documentation on http://localhost:8001
just build-docs   # Build the documentation strictly
just lint         # Run lint, type, formatting, and prose checks
just test         # Run documentation, publishing, collector, and grader tests
just check-links  # Check local Markdown links
```

See [Contributing](docs/contributing/README.md) for the full workflow, [the executable slice](docs/initial-implementation/first-slice.md) for benchmark commands, and [Agent skills](docs/agent-skills.md) for skill installation and publishing.

The documentation uses MkDocs and Material, with search, tags, source links, and generated `llms.txt` / `llms-full.txt`. The workspace originated from [research-workspace-template](https://github.com/thibaudcolas/research-workspace-template).

## License

MIT — see [LICENSE](LICENSE).
