---
name: sustainability-report
description: Turn a scored sustainability audit into a readable per-site report with clear priorities, illustrated findings, and a human-readable evidence appendix. Use after evidence review and scoring, or when revising report presentation.
license: MIT
metadata:
  version: "0.1.1"
---

# Sustainability report

Help a site owner understand what to change, what is already working, and what still needs investigation. Read [the writing guide](references/writing.md) and use [the report template](assets/report-template.md). Keep measurement, judgment and editorial work distinct: rewriting a finding does not change its outcome, priority, evidence, or score.

Use the audit checkout's `audit/render_review.py` with the scored session and a separate editorial JSON file matching [the editorial schema](references/editorial.schema.json). Read the original review, relevant evidence and rubric before writing. Bind the editorial file to the original review's SHA-256; supply every check exactly once and preserve top-finding order and IDs. The renderer calculates displayed measures and evidence links. Do not hand-edit those numbers or invent supporting observations.

Write for the site owner first. Put explanations and useful actions in the report body, then link to named evidence sections. Technical artifacts belong in an optional reproduction appendix. Use decimal kB (1,000 bytes) and MB (1,000,000 bytes); reserve KiB for binary units. Explain an incomplete measurement in everyday language, including its effect on ratings.

Use 1–3 screenshots when they clarify a finding. Run `audit/screenshots.py` for explicitly selected views, inspect the actual images, and provide useful alternative text and captions. Record URL, viewport, state, capture time and file digest. A later screenshot illustrates a finding; it does not retroactively prove a prior measurement. Do not use a screenshot as proof of transferred bytes, semantics, successful interaction, or energy savings. Omit failed or irrelevant captures.

For new Sol 6.1 audit and report-writing runs use high reasoning unless the owner specifies otherwise; DeepSeek V4.1 Flash remains high. Record actual settings separately for the audit judgment and editorial pass. Existing low-reasoning judgments stay labeled as such. A presentation revision is not evidence that higher reasoning improved audit accuracy.

Render the Markdown, preview the themed page at desktop and narrow widths, and check internal evidence links, image captions, readable tables and keyboard access to expandable sections. Use the existing MkDocs theme and semantic HTML before adding a separate report application. Preserve the source session; publish only inspected editorial and illustration artifacts.
