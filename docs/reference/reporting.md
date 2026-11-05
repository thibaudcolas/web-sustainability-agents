# Per-site reports and chart data

Each audited origin gets its own report. The [report index](../reports/README.md) separates current examples from earlier experiments. A later comparison can reference reports without merging their evidence, scores, or denominators.

The structure adapts the local claude-seo audit's summary, prioritized findings, category detail, and structured envelope. Its SEO category weights do not transfer to sustainability. Source: [claude-seo audit skill](https://github.com/AgriciDaniel/claude-seo/blob/6be93f45064ffbadced572b5d5c95f55fd263af0/skills/seo-audit/SKILL.md).

## Reading order

1. **Overall assessment and key measures:** scoped score and coverage, initial transfer, eligible Digital Carbon Ratings, estimated annual footprint and measured energy when available, sample size, and a plain explanation of measurement completeness.
2. **Top five findings:** useful changes, experiments, and existing optimizations worth preserving. Do not invent five defects or imply equal priority.
3. **Quantitative evidence:** measurements and calculations with units, profile, denominator, and uncertainty.
4. **Qualitative review:** purpose, user needs, technology context, disclosure interpretation, and source corroboration.
5. **Further checks and readable evidence:** a compact outcome index linking to named observations and useful follow-ups. Technical artifact downloads are optional reproduction detail.
6. **Next steps for auditing:** additional public tests, source/internal evidence, applicability decisions, and owner validation needed to increase coverage.
7. **Methodology and reproducibility:** versioned rubric, evidence and skill hashes, model settings, capture profiles, calculation assumptions, commands, and limitations.

The [scoped audit score](../knowledge-base/audit-scoring.md) is now implemented as passing guideline groups divided by all attempted applicable or unresolved groups. Show pass/fail/unknown counts and checked/71 coverage beside the number. A page-load carbon band, measured joules, annual emissions scenario and full-guideline conformance are separate quantities; do not average them into this score.

## Reader-facing detail

Describe the site and the audit performed; keep methodology development, skill experiments, owner feedback and report revision history in project documentation and provenance artifacts. Prefix check-outcome wording with consistent status symbols, hidden from assistive technology because the visible wording supplies their meaning.

Show each WSG area's passing percentage and count, checked guideline groups out of the area total, and unresolved count. Link the area names to corresponding subsections of Detailed findings; keep the top priorities together near the start. The denominator follows the overall conservative score: pass, fail and unknown, excluding untested and inapplicable. These are results for partial checks, not verified full guidelines.

Use the first recorded initial visit for transfer headlines. A median requires three complete visits under matching conditions; accept/reject and warm/cold-cache runs cannot be pooled. Use one Page measurements table with a row per page: first-load transfer, cumulative cookie-choice/wait and scroll transfers, estimated gCO₂e, Digital Carbon Rating, browser energy and network energy. Label accept/reject visits within their cells. Link column labels to methodology subsections at the end, where units, selection rules and limitations belong. Join GreenFrame results by exact URL; retain its separate median client-device and network estimates, sample coverage and distinct browser protocol. No energy reading is inferred from transfer alone. Display footprint estimates to two decimal places with a minimum of 0.01 gCO₂e for positive estimates; calculations and carbon ratings retain full precision.

Guideline links include their titles and pinned-description tooltips. Tooltips appear on hover or keyboard focus, remain open when hovered and dismiss with Escape without moving focus. Detailed findings also show the summary as visible text for touch, print and readers who prefer it. Screenshot captions describe the visible point; capture metadata stays in methodology and the manifest. Source excerpts come from captured file text checked against its digest, with both the currently checked-out branch link and an immutable commit link. A branch can move and does not prove deployment identity.

## Implemented data export

The `sustainability-report` skill now owns the editorial pass: plain finding titles, observations, consequences, actions, readable evidence and optional screenshots. It packages a writing guide, editorial schema and report template. The agent writes a separate editorial file bound to the original review digest; `audit/render_review.py` validates that binding, every check and the original priority order before rendering. Explicit owner feedback can revise priority and ordering through a separate review-bound presentation supplement, with a rationale for each change. The report writer cannot silently replace the scored judgments.

The renderer uses the existing [Material cards](https://squidfunk.github.io/mkdocs-material/reference/grids/), [admonitions](https://squidfunk.github.io/mkdocs-material/reference/admonitions/) and [PyMdown expandable details](https://facelessuser.github.io/pymdown-extensions/extensions/details/). Findings have explicit headings and text priority labels. Evidence links target readable sections in the same report. Raw JSON downloads appear only in the collapsed technical appendix. A separate bespoke HTML application is unnecessary for this version; the MkDocs output already supplies themed HTML and accessible native disclosure controls.

For an existing scored session, the renderer accepts `--session`, `--editorial`, `--artifact-prefix` and `--output`. Optional `--screenshots` and `--image-prefix` attach a separately validated screenshot manifest. `--presentation` accepts caption replacements, reasoned priority/order changes and captured source excerpts. `--energy` adds a separate GreenFrame experiment for the same origin; `--annual` and `--traffic` add validated annual scenarios, recomputed against the supplied transfer, energy and traffic inputs; `--supplement-prefix` links these additions in the technical appendix. The original scored session remains unchanged. The [agent workflow](../using/workflow.md) coordinates these handoffs; normal users ask the agent for an audit rather than running each command themselves.

Screenshots come from `audit/screenshots.py`, with a bounded plan, exact origin, viewport, state, capture timestamp and file digest. Captions and alternative text describe inspected images. A later screenshot illustrates current appearance without changing the older scored capture. The renderer rejects wrong-origin, altered or unrecognized-check images. It does not use screenshots as proof of network size, semantic accessibility or energy savings.

`audit/report.py` separately exports chart-ready JSON and CSV. Always provide the current session's inputs and optional enrichment paths so its historical defaults cannot attach an older campaign's data:

```sh
uv run --locked --script audit/report.py \
  --input .audit-work/example-run-1/staged.json \
  --assessments .audit-work/example-run-1/scores.json \
  --energy .audit-work/example-run-1/energy.json \
  --traffic .audit-work/example-run-1/traffic.json \
  --annual .audit-work/example-run-1/annual.json \
  --output .audit-work/example-run-1/charts
```

The three optional energy, traffic and annual files may be absent; absent files contribute no enrichment. Supply them only when their scope and protocol match the intended report. Running the exporter without arguments instead reproduces the older published report-data experiment under `docs/initial-implementation/assets/reports/`.

Exact base units remain in machine data; human traffic tables use decimal **kB** or **MB** (1,000 and 1,000,000 bytes). Use **KiB** only for 1,024-byte units; lowercase `k` is the SI prefix for kilo. [NIST prefix reference](https://www.nist.gov/pml/owm/metric-si-prefixes). Historical benchmark unit labels remain frozen rather than changing old task contracts.

Each observation records site, page URL, run, branch, phase, capture time, metric, category, unit, status, evidence ID, and source digest. The human report translates `branch` to the actual cookie choice and `accountingStatus` to measurement completeness. Carbon calculations remain separate, labeled `modeled`, with their original trace. Unknown values must be null or absent with a reason, never converted to zero.

The initial chart contracts cover phase traffic, incremental traffic, and resource composition. They specify dimensions and aggregation before any rendering implementation. Cumulative phases must not be stacked. Resource categories can be stacked only within the same run and phase. Fresh accept/reject branches are separate trajectories. Partial accounting stays visible in tables and chart descriptions.

## Energy and traffic series

The exporter also reads the energy and traffic artifacts when available. Energy rows retain one observation per repetition, including joules, scope, protocol, duration, counter category, and validity. The linked energy artifact supplies full hardware/browser provenance. Keep individual runs in the artifacts. The human report uses one visit or a median of three comparable repetitions, not a range. Do not align a whole Firefox session with a Chromium phase as if they were equivalent measurements.

Traffic rows retain origin, rank bucket, dataset month, estimated annual pageviews, and a `scenario` basis, with source hashes linking to lookup scope and mapping provenance. Missing lookup is not zero traffic or a known unranked bucket. Site analytics can replace the scenario only with matching scope and period. The [annual calculator](../using/workflow.md#estimate-annual-impact) uses an explicitly assumed page mix and first-visit model when actual analytics are unavailable. A clearly labeled estimate is allowed; it is not a measured annual footprint.

The exporter also includes `scoped_audit_score` and `annual_browsing_footprint` series. Score rows retain rubric and checked/total coverage. Annual rows retain partial-input status and low/high sampled-page sensitivities, which must not be rendered as confidence intervals. Both link to exact source digests. Measured package energy remains a separate series and is never added to SWDM.

For future charts, preserve trial and protocol IDs rather than only aggregate values. This enables distributions, before/after comparisons, per-template breakdowns, and error bars once repeated matched observations exist. Accessible labels, equivalent tables, and downloadable data belong to the later presentation implementation.

## Annual footprint and improvement scale

Keep this section in every report, with an explicit unavailable explanation when traffic is missing. The default compares SWDM v4 annual browsing emissions with a separate client-only GreenFrame projection; their overlapping boundaries prevent adding them. The current annual calculator uses the report's first recorded initial visit per URL, equal sampled-page weights and unrounded model values. Partial transfer inputs remain labeled; they do not gain a Digital Carbon Rating. Legacy branch-mean calculations can still be reproduced with `--visit-selection branch-mean`, but the current renderer requires `first`.

The client projection uses each energy URL's median of three repetitions, then equally weights those sampled URLs. It scales initial-load Wh by estimated annual pageviews and divides by 1,000 for kWh. Operational emissions multiply kWh by an explicit gCO₂e/kWh factor and divide by 1,000. The default 494 is the [SWDM v4 comparison factor](https://sustainablewebdesign.org/estimating-digital-emissions/), not audience-specific electricity data. Report the smaller energy sample, laboratory duration and device assumptions; exclude later reading, network, servers and embodied emissions from this client-only result.

A hypothetical 10% reduction shows the scale of an improvement at unchanged traffic. It does not predict the savings from a recommended fix. Validate changes with matched before/after scenarios and scale the measured difference only to affected pageviews. The [agent workflow](../using/workflow.md#estimate-annual-impact) runs the lookup and calculator; the owner does not need to operate them.
