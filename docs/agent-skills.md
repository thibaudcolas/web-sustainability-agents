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

The [agent-triggered workflow](using/workflow.md) adds scope clarification, editable plans, actual collector invocations, immutable evidence packets and scored reviews. The guideline skill packages a pinned WSG reference and an assessment crosswalk; read relevant entries progressively rather than putting the entire reference into every prompt.

## Install and run

Follow [installation and your first audit](using/README.md) for the supported checkout setup, harness locations, invocation and proposed plugin experience. See [workflow and artifacts](using/workflow.md) for the collection-to-report handoffs. The same review roles can run sequentially or as authorized subagents.

The [evaluation project](evaluation/README.md) distinguishes skill execution from evidence that skills improve results. Current skill changes do not rewrite the frozen copies used in historical campaigns.

## Discovery and maintenance

The documentation publishes complete skill folders under `.well-known/agent-skills/`, with an index and AI Catalog metadata. These are discovery resources, not an installable Agent Plugin. Catalog-aware clients may use them; a checkout remains necessary for the collectors.

See [skill maintenance](contributing/skills.md) for source layout, versioning, catalog formats and publishing checks.
