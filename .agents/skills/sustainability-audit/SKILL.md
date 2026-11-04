---
name: sustainability-audit
description: Coordinate a per-site sustainability audit using measurement evidence, scoped WSG review, footprint scenarios, and an explicit plan for increasing audit coverage.
license: MIT
metadata:
  version: "0.1.0"
---

# Sustainability audit

Define one origin, relevant paths/states, available source or internal documents, and the audit purpose. Begin with existing evidence and its collection dates before recollecting. Follow the repository's reproducible collector commands when available; separate hardware-energy runs from other workloads.

Use bounded review roles rather than asking one prompt to discover, measure, judge, and score everything:

- Quantitative evidence: apply `sustainability-evidence-review` to phases, completeness, units, cache/consent profiles, and technology context.
- Guideline judgments: apply `sustainability-guideline-review` to a versioned rubric and the exact sample. Return row-level outcomes and evidence needs, not an intuitive grade.
- Claims and recommendations: apply `sustainability-claims-review` to disclosures, annual scenarios, source corroboration, and recommendation usefulness.

When the harness supports subagents and the task authorizes delegation, assign these as independent bounded reviews with the same evidence inventory. Give each worker the relevant skill and output contract, then reconcile disagreements explicitly. Otherwise execute the same roles sequentially. Workers need not share a proprietary orchestration API. Do not treat reviewer agreement as new site evidence.

Use repository calculation tools to aggregate judgments and annual scenarios. Publish one report with key measures and score, top priorities, quantitative evidence, qualitative interpretation, and detailed findings. A score must identify rubric version, pass/failed/unknown counts, checked and total guideline coverage, and excluded inapplicable/untested checks. Keep DCR, scoped audit score, and hardware energy distinct.

End with “Next steps for auditing” and “Methodology and reproducibility.” Separate fixes to the site from work needed to improve audit confidence. Explain which additional public journeys, source evidence, internal records, or owner judgments would increase coverage; record what remains outside the current method. Link WSG areas directly. Preserve evidence hashes, source revisions, model/skill settings, commands, and limitations so another harness can reproduce the work.
