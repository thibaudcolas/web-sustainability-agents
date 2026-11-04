---
name: sustainability-collection
description: Execute an agreed sustainability audit plan once, inspect collector failures and hand a frozen evidence packet to review agents. Use after scope and setup are ready.
license: MIT
metadata:
  version: "0.2.1"
---

# Collect the agreed evidence

Use the coordinator's accepted plan and new session path. Run `tool workflow collect --plan <absolute-plan> --session <absolute-session>` through the installed audit CLI. Do not expand the scope or change the plan silently, and do not ask the owner to run the command.

Inspect both command exit status and page-level results: redirects, failed selectors, unsupported states, partial traffic measurement, unresolved source files and missing disclosures. Lead later reporting with initial load before interaction; keep cookie choices and scrolling as separate cumulative observations. Wappalyzer and supplementary probes do not count toward ordinary page-load traffic.

For selected contextual checks, inspect `context.json`: records must retain source, observation time, scope, limitations and captured text or an explicit failure. Its evidence requests are unresolved until a reviewer evaluates the actual records and browser observations. Do not repair missing context behind a frozen packet; return the precise request to the coordinator for a linked new session when needed.

Return the absolute packet and receipt paths, sample actually collected, completed/failed journeys, partial measurements and smallest next investigation. Collection failures are not automatically site defects. Never turn unavailable bytes into zero or an eligible carbon rating.

A failed collection remains preserved. A corrected selector or wider sample belongs in a new linked session, not overwritten evidence. Energy readiness is part of collection by default. Inspect `energy/manifest.json` and report readiness or its precise missing prerequisite; unavailable energy is never zero. Use `--energy run --greenframe-binary <pinned-local-binary>` on `workflow collect` for the accepted energy sample, or `tool greenframe --plan <plan> --output-dir <new-energy-directory> --mode run --binary <pinned-local-binary>` as a later supplement with its own timestamp. Configure `plan.energy.pageIds` for 1–3 planned pages and `samples` (default 3); an empty list samples the first planned page. An explicit `--energy skip` records the opt-out. Install the pinned local tool and image within existing authorization when practical; never change host hardware permissions or global configuration to make a measurement pass.

Run energy sequentially in a quiet window, after other browser collection and while local tests and model campaigns are paused. GreenFrame separates modeled browser-device CPU, memory, disk and screen energy from its modeled network energy, and excludes remote servers. Show the median of three matching complete repetitions in the report, with actual browser/image versions and the smaller energy sample. Keep individual values and their range in the technical artifacts. Keep these resource-model estimates separate from SWDM; they are not electricity-meter readings or total-device measurements. co2-runner's Linux counter instead measures the whole CPU package during a Firefox session, including background activity; it is not page-only energy.

Keep hardware-energy runs separate from other browser/model work. Review workers share this captured evidence rather than each launching a duplicate crawl.

Screenshots are a later illustrative step chosen by the report role: `tool screenshots --plan <illustration-plan> --output <new-image-directory>`. They retain their own capture time and cannot retroactively establish a prior scored observation.
