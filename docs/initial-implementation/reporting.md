# Per-site reports and chart data

Each audited origin gets its own report: [guide.wagtail.org](guide-audit.md) and [wagtail.org](wagtail-audit.md). A later comparison can reference them without merging their evidence, scores, or denominators.

The structure adapts the local claude-seo audit's summary, prioritized findings, category detail, and structured envelope. Its SEO category weights do not transfer to sustainability. Source: [claude-seo audit skill](https://github.com/AgriciDaniel/claude-seo/blob/6be93f45064ffbadced572b5d5c95f55fd263af0/skills/seo-audit/SKILL.md).

## Reading order

1. **Overall assessment and key measures:** initial transfer, eligible Digital Carbon Ratings, measured energy when available, sample size, and accounting status.
2. **Top five findings:** useful changes, experiments, and existing optimizations worth preserving. Do not invent five defects or imply equal priority.
3. **Quantitative evidence:** measurements and calculations with units, profile, denominator, and uncertainty.
4. **Qualitative review:** purpose, user needs, technology context, disclosure interpretation, and source corroboration.
5. **Detailed findings and coverage:** evidence-linked explanations, proposed checks, and unknowns.

An overall WSG score remains explicitly unscored until a validated scoring contract exists. A page-load carbon band, evidence coverage count, measured joules, and an organizational assessment are different quantities. Do not average them into a health score.

## Implemented data export

`audit/report.py` reads the frozen staged bundle and writes one JSON envelope and one CSV per origin under `docs/initial-implementation/assets/reports/`. Run:

```sh
uv run --locked --script audit/report.py
```

Exact base units remain in machine data; human traffic tables use decimal KB or MB. Each observation records site, page URL, run, branch, phase, capture time, metric, category, unit, status, evidence ID, and source digest. Carbon calculations remain separate, labeled `modeled`, with their original trace. Unknown values must be null or absent with a reason, never converted to zero.

The initial chart contracts cover phase traffic, incremental traffic, and resource composition. They specify dimensions and aggregation before any rendering implementation. Cumulative phases must not be stacked. Resource categories can be stacked only within the same run and phase. Fresh accept/reject branches are separate trajectories. Partial accounting stays visible in tables and chart descriptions.

## Energy and traffic series

The exporter also reads the energy and traffic artifacts when available. Energy rows retain one observation per repetition, including joules, scope, protocol, duration, counter category, and validity. The linked energy artifact supplies full hardware/browser provenance. Show individual runs plus median and range; a range is not a confidence interval. Do not align a whole Firefox session with a Chromium phase as if they were equivalent measurements.

Traffic rows retain origin, rank bucket, dataset month, estimated annual pageviews, and a `scenario` basis, with source hashes linking to lookup scope and mapping provenance. Missing lookup is not zero traffic or a known unranked bucket. Site analytics can replace the scenario only with matching scope and period. An annual impact calculation additionally needs a defensible page mix and repeat-visit model; a homepage multiplied by guessed traffic is not a measured annual footprint.

For future charts, preserve trial and protocol IDs rather than only aggregate values. This enables distributions, before/after comparisons, per-template breakdowns, and error bars once repeated matched observations exist. Accessible labels, equivalent tables, and downloadable data belong to the later presentation implementation.
