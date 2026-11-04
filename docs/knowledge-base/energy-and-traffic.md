# Browser energy and traffic scenarios

Transfer size, browser energy, and audience size answer different questions. Keep their units, populations, and uncertainty separate before combining them in any impact model.

## Hardware energy versus modeled carbon

The existing SWDM calculation models emissions from transferred data. It does not directly measure browser energy. Sitespeed.io's sustainability plugin also uses CO2.js; enabling that plugin is not equivalent to hardware profiling. [Sitespeed.io sustainability documentation](https://www.sitespeed.io/documentation/sitespeed.io/sustainable/).

Co2-runner drives Playwright Firefox and reads Mozilla Profiler power counters. On this Linux machine, the selected counter covers the whole processor package, including unrelated background work, browser startup, and shutdown. Separate cores, integrated GPU, and system counters overlap and must not be summed. Separate DRAM and the rest of the device are outside the package boundary. [Mozilla RAPL documentation](https://firefox-source-docs.mozilla.org/performance/tools_power_rapl.html).

Counter values are interval picoWatt-hours: multiply their sum by `1e-9` for mWh or `3.6e-9` for joules. Missing counters, unsupported schema, empty samples, invalid values, and failed journeys are explicit unavailable results. A valid all-zero series still needs a plausibility check.

Sitespeed.io has a distinct Firefox power path: `--firefox.geckoProfiler`, `--firefox.geckoProfilerParams.features js,stackwalk,cpu,power`, and `--firefox.powerConsumption true`. Browsertime exposes `powerConsumption` in Wh. Its inspected implementation skips the first sample; the local co2-runner includes it. Matching tool names or units is insufficient for a matched experiment. [Configuration](https://www.sitespeed.io/documentation/sitespeed.io/configuration/), [Browsertime implementation](https://github.com/sitespeedio/browsertime/blob/main/lib/firefox/geckoProfiler.js).

Do not add measured CPU energy to a complete SWDM result: that mixes boundaries and can double-count modeled device energy. A replacement or hybrid model needs an explicit accounting design. Repeat measurements sequentially under controlled conditions before making causal or cross-site efficiency claims.

## CrUX lookup without credentials

The canonical source is Google's monthly BigQuery dataset. Popularity is a coarse origin-level bucket, not an exact position or disclosed pageview count. Scheme and full hostname matter; `guide.wagtail.org` and `wagtail.org` are separate origins. CrUX eligibility and its Chrome population also limit interpretation. [BigQuery structure](https://developer.chrome.com/docs/crux/bigquery/), [CrUX methodology](https://developer.chrome.com/docs/crux/methodology/).

For a simple public lookup, use the [monthly CrUX dumps](https://github.com/crissyfield/crux-dumps), pin their repository commit and month, and scan compressed bucket files for exact origins. The mirror is a third-party export, not a Google API. Record file digests and searched coverage. The [top-million CSV mirror](https://github.com/zakird/crux-top-lists) is another convenient option, but neither current audit target appeared within the first million buckets of the inspected dataset; stopping there would miss both.

An absent result means not found within the searched dataset and scope. It does not establish zero traffic, a global rank, or the reason for CrUX exclusion. Prefer a Google BigQuery query when a configured project and direct-source verification are available.

## Rank-to-pageviews scenarios

The supplied [ranking-to-pageviews project](https://github.com/thibaudcolas/ranking-to-pageviews) maps rank buckets to annual pageview medians derived from US government analytics. Its local revision `e36613ef9dd2f7cee5557ea794d238af31acbaf7` uses 2025 traffic and December 2025 ranks. The copied mapping is CC0; its digest is recorded with each scenario. The README also gives a power-law extrapolation for unranked sites; missing lookup does not justify assigning that value.

Apply bucket medians as cohort-based scenarios, not actual analytics, forecasts, or statistical bounds. Audience, geography, month, and content type can differ substantially. A high fit to aggregate bucket medians does not establish low error for an individual site. Owner-supplied analytics and held-out calibration are the next validation step.

Annual emissions additionally require the right population, page mix, cache/revisit behavior, and compatible carbon assumptions. Do not multiply one cold homepage result by a rank-derived pageview point and label the product the site's measured footprint.

A clearly labeled annual estimate can use explicit proxy assumptions where real analytics are unavailable. The [implemented scenario](../initial-implementation/skill-audit-workflow.md#annual-footprint-scenarios) uses an equal mix of sampled pages and first visits only, retains partial-input status, and publishes sampled-page sensitivities rather than confidence bounds. Refine those assumptions when owner data becomes available.
