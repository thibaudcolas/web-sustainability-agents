# Agent skills

Install one entry point, `sustainability-audit`, then ask your agent to audit a URL. It loads version-matched role instructions progressively through the audit CLI. See [installation and your first audit](using/README.md).

## Entry point and specialist roles

| Skill                             | Version | Role                                                                    |
| --------------------------------- | ------- | ----------------------------------------------------------------------- |
| `sustainability-audit`            | 0.4.0   | Discover the installed workflow and coordinate the audit                |
| `sustainability-setup`            | 0.1.0   | Prepare tools and select 5–10 representative pages and meaningful tasks |
| `sustainability-collection`       | 0.1.0   | Execute the accepted plan once and explain incomplete collection        |
| `sustainability-evidence-review`  | 0.5.0   | Check measurements, phases and numeric interpretation                   |
| `sustainability-guideline-review` | 0.2.0   | Judge selected WSG expectations and preserve unknowns                   |
| `sustainability-claims-review`    | 0.2.0   | Review disclosures, estimates and source-informed recommendations       |
| `sustainability-report`           | 0.1.0   | Write readable findings, evidence explanations and illustrated reports  |

The entry point loads the CLI-only `core` orchestration workflow, which assigns the roles. Evidence, guideline and claims reviews can run as native subagents against the same frozen packet, then the coordinator reconciles them before scoring and report writing. A sequential fallback uses identical task contracts and records that execution mode.

The plugin registers only the entry skill. Specialist sources remain in `.agents/skills/` for compatibility with existing collectors and frozen-task builders; development checkout discovery may therefore expose more roles. A future package can move those internal sources without changing the public entry point. The contributor-only `research-workspace` skill is not part of the audit plugin.

## Progressive discovery

The installed workflow exposes `skills list`, `skills get <role>`, `skills get <role> --full` and `skills path <role>` through the provisional Typer CLI. Full output includes references and templates; use it only when needed. The guideline role includes pinned WSG text and direct links, and the report role includes writing guidance and an editorial schema.

See [workflow and handoffs](using/workflow.md) for the actual interface. The [evaluation project](evaluation/README.md) distinguishes executing a skill from evidence that it improves accuracy. Historical cases preserve their own skill snapshots and model settings.

## Documentation catalogs and maintenance

The documentation build publishes the complete source skill catalog under `.well-known/agent-skills/` with discovery metadata. This documentation catalog is broader than the plugin's single registered entry point; it does not install the collector runtime.

[Skill maintenance](contributing/skills.md) covers metadata, versioning and publishing checks. Plugin entrypoint copies are checked against their canonical source so they cannot silently drift.
