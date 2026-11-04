# Agent skills

This workspace publishes [Agent Skills](https://agentskills.io/) alongside its documentation. Audit skills contribute interpretation and investigation choices around deterministic measurements; they are not wrappers that turn every tool result into a pass.

## Available skills

| Skill                             | Version | Role                                                                                              |
| --------------------------------- | ------- | ------------------------------------------------------------------------------------------------- |
| `sustainability-audit`            | 0.3.0   | Coordinate a per-site audit, bounded review roles, calculation, reporting and next auditing steps |
| `sustainability-evidence-review`  | 0.5.0   | Interpret measurements, phases, partial accounting and model boundaries                           |
| `sustainability-guideline-review` | 0.2.0   | Apply scoped expectations, distinguish applicability and unknowns, and explain score coverage     |
| `sustainability-claims-review`    | 0.2.0   | Review footprint assumptions, disclosures, source corroboration and recommendation usefulness     |
| `research-workspace`              | 1.0.0   | Maintain documentation structure, navigation and source citations                                 |

The [agent-triggered workflow](initial-implementation/agent-driven-audits.md) adds scope clarification, editable plans, actual collector invocations, immutable evidence packets and scored reviews. The guideline skill packages a pinned WSG reference and an assessment crosswalk; read relevant entries progressively rather than putting the entire reference into every prompt.

The [implemented skill workflow](initial-implementation/skill-audit-workflow.md) includes portable JSON review packets, actual per-site reviewer output, reproducible scores, and the remaining validation limits. Delegation is optional: the same roles can run sequentially when a harness lacks subagents.

## Use a skill

Skills are maintained in the repository's `.agents/skills/` directory. Tools that support that directory can discover them locally. To use a skill in another repository, copy its complete folder into that repository's `.agents/skills/` directory.

For a harness that uses another installation location, install the same complete folders using its own mechanism or explicitly load the named `SKILL.md` files. The skills do not require a proprietary subagent API. We have exercised the Codex-based workflow; equivalent behavior in Claude Code, OpenCode and pi still needs validation. Copying skills alone does not install this repository's Python/Node collectors or evidence artifacts.

The documentation build also publishes these paths, relative to the site's base URL:

- `.well-known/agent-skills/<name>/SKILL.md`: each skill as raw Markdown.
- `.well-known/agent-skills/index.json`: skill descriptions, download URLs, and SHA-256 digests, following the [agent skills discovery proposal](https://github.com/cloudflare/agent-skills-discovery-rfc).
- `.well-known/ai-catalog.json`: publisher information, skill versions, and absolute download URLs, following [AI Catalog](https://ai-catalog.io/).

For a GitHub Pages project site, keep the repository path before `.well-known/`. Discovery requires a client that supports the relevant catalog format; publishing a catalog does not automatically install skills.

## Publish a skill

Create `.agents/skills/<name>/SKILL.md` with YAML front matter:

```yaml
---
name: my-skill
description: Describe the task this skill supports and when an agent should use it.
metadata:
  version: "1.0.0"
---
```

Use lowercase letters, digits, and single hyphens for the name, matching the directory name. Add the instructions below the front matter. Keep supporting references, scripts, and assets inside the skill folder: the build copies the whole folder. Symlinks are rejected. Every skill in this directory is published, so keep local-only material elsewhere.

Update `metadata.version` when releasing changes to the skill. Catalog versions come from skill metadata, independently of the workspace version. The catalog omits optional modification dates rather than reporting checkout time as a content update.

Run `just build-docs` and inspect `site/.well-known/`. Invalid metadata fails the build. The publishing hook in `scripts/publish_skills.py` generates catalogs from the skills and the `site_name` and `site_url` settings in `mkdocs.yml`. Update those settings when adopting this template. An empty skills directory produces empty catalogs.

GitHub Actions includes hidden files in its Pages artifact so `.well-known/` is deployed with the documentation. Publishing uses the existing deployment on pushes to `main`; no separate release or package upload is needed.
