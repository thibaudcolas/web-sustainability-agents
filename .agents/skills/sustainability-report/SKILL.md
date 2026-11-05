---
name: sustainability-report
description: Turn a scored sustainability audit into a readable per-site report with clear priorities, illustrated findings, and a human-readable evidence appendix. Use after evidence review and scoring, or when revising report presentation.
license: MIT
metadata:
  version: "0.2.2"
---

# Sustainability report

Help a site owner understand what to change, what is already working, and what still needs investigation. Describe the site and the audit performed, without narrating methodology development, skill experiments, owner feedback or report revisions. Put development history in project documentation and provenance artifacts. Read [the writing guide](references/writing.md) and use [the report template](assets/report-template.md). Keep measurement, judgment and editorial work distinct: rewriting a finding does not change its outcome, evidence, or score. Recalibrate priority only through an explicit, review-bound presentation supplement with a reason.

Use the audit checkout's `audit/render_review.py` with the scored session and a separate editorial JSON file matching [the editorial schema](references/editorial.schema.json). Read the original review, relevant evidence and rubric before writing. Bind the editorial file to the original review's SHA-256; supply every check exactly once and preserve top-finding order and IDs. The renderer calculates displayed measures and evidence links. Do not hand-edit those numbers or invent supporting observations.

Write for the site owner first. Put explanations and useful actions in the report body, then link to named evidence sections. Technical artifacts belong in an optional reproduction appendix. Use decimal kB (1,000 bytes) and MB (1,000,000 bytes); reserve KiB for binary units. Explain an incomplete measurement in everyday language, including its effect on ratings. Display footprint estimates to two decimal places, with 0.01 gCO₂e as the minimum positive display value. Retain full precision for calculations and ratings.

Use 1–3 screenshots when they clarify a finding. Run `audit/screenshots.py` for explicitly selected views, inspect the actual images, and provide useful alternative text and captions. Record URL, viewport, state, capture time and file digest. A later screenshot illustrates a finding; it does not retroactively prove a prior measurement. Do not use a screenshot as proof of transferred bytes, semantics, successful interaction, or energy savings. Omit failed or irrelevant captures.

For new Sol 6.1 audit and report-writing runs use high reasoning unless the owner specifies otherwise; DeepSeek V4.1 Flash remains high. Record actual settings separately for the audit judgment and editorial pass. Existing low-reasoning judgments stay labeled as such. A presentation revision is not evidence that higher reasoning improved audit accuracy.

Render the Markdown, preview the themed page at desktop and narrow widths, and check internal evidence links, image captions, readable tables and keyboard access to expandable sections. Use the existing MkDocs theme and semantic HTML before adding a separate report application. Preserve the source session; publish only inspected editorial and illustration artifacts.

Use the first recorded initial visit for transfer headlines, retaining incomplete status; use a median only for three complete repetitions under matching conditions. Do not pool consent or cache states. Put unit definitions and capture provenance in methodology. Use one Page measurements table with a row per page: first load, cumulative cookie/wait and scroll totals, estimated gCO₂e, Digital Carbon Rating, browser energy and network energy. Label separate cookie choices within cells. Join separately collected energy by exact URL; state missing coverage plainly. Link column labels to methodology subsections at the end; keep units, selection rules and model boundaries there. Never add GreenFrame energy, SWDM emissions and hardware counters into a common total.

Prefix check-outcome wording with status symbols (✅ pass, ❌ problem, ❓ investigation, ➖ inapplicable, ⚪ untested). Keep the wording visible and hide decorative symbols from assistive technology. Show per-area passing counts and percentages alongside the number of guideline groups checked and unknowns. Use the same denominator as the overall score; distinguish partial checks from full guideline conformance. Link each area to its corresponding subsection in Detailed findings; retain named evidence anchors and keep top priorities together near the start. Show guideline titles beside WSG numbers, with pinned-reference summaries in focus/hover tooltips and visible in the evidence appendix. Tooltips must dismiss with Escape and remain open when hovered. Do not hide essential descriptions in hover-only tooltips.

Keep screenshot captions short and descriptive; capture time, dimensions and limitations belong in methodology and the manifest. For useful source findings, show a short exact captured excerpt and link both the checked-out branch and captured commit. Validate the excerpt against the captured file digest and line range. Source availability does not establish the deployed revision.

A `--presentation` JSON supplement may bind caption replacements, priority changes, order and source excerpts to the original review SHA-256. Record each priority change's rationale. `--energy` accepts a separate `greenframe-energy-v2` experiment for the same origin. Keep both outside the original frozen session, link them through `--supplement-prefix`, and preserve a reproduction command. No hidden hand-edited report numbers.
