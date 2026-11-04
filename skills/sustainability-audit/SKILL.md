---
name: sustainability-audit
description: Audit a live website for sustainability. Use when the user supplies a URL or asks for WSG findings, measurements, priorities or a sustainability report. Coordinate setup, sampling, collection and specialist review; the user does not need to operate the audit scripts.
license: MIT
metadata:
  version: "0.4.0"
---

# Sustainability audit

This is the entry point. A URL and the owner's priorities are enough to start. Load the workflow matching this installed version before doing the work.

Resolve the tool directory by running the `scripts/runtime.py doctor` helper beside this skill with `uv run --locked --script`. Its JSON identifies `root`. Then run:

```sh
uv run --locked --script <root>/audit/cli.py skills get core
```

The placeholder is the resolved tool directory, not the user's project directory. The helper finds a plugin checkout automatically or the explicit location recorded by the project installer. Do not ask the user to copy a prompt or run the collector commands. If a host prerequisite is missing, explain that concrete requirement; otherwise own setup through delivery.

The CLI serves version-matched role instructions with `skills list`, `skills get <role>` and `skills path <role>`. Load only the relevant role and reference files. Native subagents are preferred when available and authorized; sequential execution uses the same role contracts. Do not create a second model-routing runtime.
