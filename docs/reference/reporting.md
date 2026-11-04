# Per-site reports and chart data

Each audited origin gets its own report. The [report index](../reports/README.md) separates current examples from earlier experiments. A later comparison can reference reports without merging their evidence, scores, or denominators.

The structure adapts the local claude-seo audit's summary, prioritized findings, category detail, and structured envelope. Its SEO category weights do not transfer to sustainability. Source: [claude-seo audit skill](https://github.com/AgriciDaniel/claude-seo/blob/6be93f45064ffbadced572b5d5c95f55fd263af0/skills/seo-audit/SKILL.md).

## Reading order

1. **Overall assessment and key measures:** scoped score and coverage, initial transfer, eligible Digital Carbon Ratings, estimated annual footprint, measured energy when available, sample size, and accounting status.
2. **Top five findings:** useful changes, experiments, and existing optimizations worth preserving. Do not invent five defects or imply equal priority.
3. **Quantitative evidence:** measurements and calculations with units, profile, denominator, and uncertainty.
4. **Qualitative review:** purpose, user needs, technology context, disclosure interpretation, and source corroboration.
5. **Detailed findings and coverage:** evidence-linked explanations, proposed checks, and unknowns.
6. **Next steps for auditing:** additional public tests, source/internal evidence, applicability decisions, and owner validation needed to increase coverage.
7. **Methodology and reproducibility:** versioned rubric, evidence and skill hashes, model settings, capture profiles, calculation assumptions, commands, and limitations.

The [scoped audit score](../knowledge-base/audit-scoring.md) is now implemented as passing guideline groups divided by all attempted applicable or unresolved groups. Show pass/fail/unknown counts and checked/71 coverage beside the number. A page-load carbon band, measured joules, annual emissions scenario and full-guideline conformance are separate quantities; do not average them into this score.

## Implemented data export

`audit/render_review.py` renders the current session's scored judgments into a Markdown draft. See [the workflow](../using/workflow.md#4-calculate-and-render) for invocation and its remaining portability limits.

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

Exact base units remain in machine data; human traffic tables use decimal KB or MB. Each observation records site, page URL, run, branch, phase, capture time, metric, category, unit, status, evidence ID, and source digest. Carbon calculations remain separate, labeled `modeled`, with their original trace. Unknown values must be null or absent with a reason, never converted to zero.

The initial chart contracts cover phase traffic, incremental traffic, and resource composition. They specify dimensions and aggregation before any rendering implementation. Cumulative phases must not be stacked. Resource categories can be stacked only within the same run and phase. Fresh accept/reject branches are separate trajectories. Partial accounting stays visible in tables and chart descriptions.

## Energy and traffic series

The exporter also reads the energy and traffic artifacts when available. Energy rows retain one observation per repetition, including joules, scope, protocol, duration, counter category, and validity. The linked energy artifact supplies full hardware/browser provenance. Show individual runs plus median and range; a range is not a confidence interval. Do not align a whole Firefox session with a Chromium phase as if they were equivalent measurements.

Traffic rows retain origin, rank bucket, dataset month, estimated annual pageviews, and a `scenario` basis, with source hashes linking to lookup scope and mapping provenance. Missing lookup is not zero traffic or a known unranked bucket. Site analytics can replace the scenario only with matching scope and period. The [annual calculator](../initial-implementation/skill-audit-workflow.md#annual-footprint-scenarios) uses an explicitly assumed page mix and first-visit model when actual analytics are unavailable. A clearly labeled estimate is allowed; it is not a measured annual footprint.

The exporter also includes `scoped_audit_score` and `annual_browsing_footprint` series. Score rows retain rubric and checked/total coverage. Annual rows retain partial-input status and low/high sampled-page sensitivities, which must not be rendered as confidence intervals. Both link to exact source digests. Measured package energy remains a separate series and is never added to SWDM.

For future charts, preserve trial and protocol IDs rather than only aggregate values. This enables distributions, before/after comparisons, per-template breakdowns, and error bars once repeated matched observations exist. Accessible labels, equivalent tables, and downloadable data belong to the later presentation implementation.
