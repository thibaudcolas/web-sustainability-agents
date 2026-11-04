# Energy and traffic enrichment experiment

The audit has separate adapters for GreenFrame resource-model estimates, co2-runner CPU-package counters, and a CrUX lookup. These answer different questions and must retain their measurement boundaries. Sitespeed.io's hardware-energy path has been inspected but has not been executed. See [methodology and sources](../knowledge-base/energy-and-traffic.md).

## Fresh GreenFrame estimates

The fresh report supplement captured six pages on November 4, 2026, from 22:38:59 to 22:41:40 UTC. All 18 repetitions completed successfully. Each row summarizes three independent browser scenarios; the range is observed variation, not a confidence interval.

| Page                          | Client-device median | Client-device range | Network median |
| ----------------------------- | -------------------: | ------------------: | -------------: |
| Guide homepage                |            12.00 mWh |     10.38–13.85 mWh |       0.76 mWh |
| Guide: manage images          |            11.15 mWh |     10.52–14.50 mWh |       2.80 mWh |
| Guide: new in Wagtail 8.1     |            10.72 mWh |     10.67–11.04 mWh |       4.19 mWh |
| Wagtail.org homepage          |            12.08 mWh |     11.23–12.58 mWh |      11.65 mWh |
| Wagtail.org: Wagtail 8.1 blog |            16.41 mWh |     15.48–18.00 mWh |      25.26 mWh |
| Wagtail.org: sustainability   |            13.84 mWh |     10.66–14.96 mWh |       7.51 mWh |

The [guide manifest](../reports/assets/report-refinement/guide/energy/manifest.json) and [Wagtail.org manifest](../reports/assets/report-refinement/wagtail/energy/manifest.json) retain exact Wh values, individual repetitions, component estimates, timestamps and artifact digests. Their adjacent page directories publish raw Docker counters, full-precision model output and the executed scenario/bridge. Each bundle includes `plan.json` and `reproduction.json`; sibling `energy.json` files are exact manifest copies for report rendering. These later captures supplement the scored reports without changing their original evidence or judgments.

The boundary is **modeled browser-device CPU, memory, disk and screen energy**. Network energy is modeled separately; remote servers are excluded. The unchanged [GreenFrame 2.0.1 model](https://github.com/marmelab/greenframe-cli/blob/v2.0.1/src/model/stat-tools/getConsumption.ts) uses a synthetic 45 W CPU and 14 W screen, with CPU usage normalized by available host CPUs. The screen estimate dominates these client-device results. This is neither measured electricity nor total-device energy, and it must not be added to SWDM or extrapolated directly to annual site impact. The results establish a reproducible sample, not a causal efficiency ranking.

The shared Linux workstation had an Intel Core i5-1145G7 and eight logical CPUs. Docker 29.9.2 ran the pinned `mcr.microsoft.com/playwright:v1.30.0-focal` image, digest `sha256:9e6eddb08b8566076ef778007859096bc90f8984236061c086eaede2fb60430b`, with Chromium 110.0.5481.38. GreenFrame supplies a fixed Chrome 89 user-agent string and `--disable-web-security`; these are experimental limits, not a current-browser compatibility claim. Temperature, power state and ambient activity were uncontrolled; local tests and campaigns were paused during collection.

Each fresh browser context used 1,280 × 800, navigated through `load`, then waited three seconds without consent interaction or scrolling. GreenFrame starts its accounting window after browser startup and a two-second warm-up, and ends after browser close. Modeled counter spans were approximately 3–5 seconds. Repetitions shared a container, so this does not establish cold host caches. The narrow energy sample covers three pages per site, fewer than the browser audit sample.

## Earlier CPU-package measurements

| Target homepage | Valid repetitions | Median CPU-package energy | Observed range |
| --------------- | ----------------: | ------------------------: | -------------: |
| Guide           |                 3 |                   71.91 J |  68.76–72.35 J |
| Wagtail.org     |                 3 |                   77.86 J |  76.65–78.17 J |

The [energy artifact](assets/energy-experiment.json) records each run, counter sample count and span, session duration, source digests, and first-sample sensitivity. These are sequential, round-robin, headed Firefox sessions at 1,280 × 720: navigate through load, wait three seconds, close. No consent interaction or scroll is included. The sessions lasted about 5.7–6.2 seconds including startup/shutdown. The Chromium transfer protocol uses 1,280 × 800 and different instrumentation; the figures are not interchangeable phase measurements.

Linux RAPL permissions and the CPU-package event were already available. No system settings were changed. The shared workstation's temperature, power state, and unrelated activity were not experimentally controlled; no audit tests or model campaigns were deliberately run alongside these measurements. There is no idle subtraction, matched performance baseline, or causal site comparison.

The local co2-runner revision is `cf665f56e0b7db396d0422de1d143559986fa745` with uncommitted changes, including the CPU-package selection fix. The adapter records file hashes in addition to the commit. It leaves the checkout untouched and isolates profiles/HARs under ignored `.audit-work/energy/`. The published artifact excludes those raw files.

The validator accepts one top-level CPU-package series and rejects missing, empty, malformed, nonfinite, negative, or unordered samples. It does not sum overlapping domains. A valid all-zero series is flagged and excluded from the summary. The first sample is included to match co2-runner; excluding it is recorded separately as a sensitivity calculation.

## Executed CrUX lookup

The pinned mirror's September 2026 dataset matched both exact HTTPS origins:

| Origin                      | CrUX rank bucket | Annual pageview scenario |
| --------------------------- | ---------------: | -----------------------: |
| `https://guide.wagtail.org` |       10,000,000 |    approximately 245,000 |
| `https://wagtail.org`       |        5,000,000 |    approximately 573,000 |

The [traffic artifact](assets/traffic-scenarios.json) contains exact mapping values, dataset month, mirror commit, compressed-file digests, searched buckets, and mapping digest. These are **scenarios based on a different population and period**, not observed site traffic. The initial experiment stopped at pageview scenarios; the [annual footprint extension](skill-audit-workflow.md#annual-footprint-scenarios) now combines them with an explicitly assumed sampled-page mix. The guide's scenario must not be replaced by Wagtail.org's bucket or combined as if origins were interchangeable.

## Reproduce

```sh
# Uses the supplied checkout and its installed Node/Firefox dependencies.
uv run --locked --script audit/energy.py --output .audit-work/new-cpu-package-energy.json
# Reads public monthly dumps; no CrUX or BigQuery key required.
uv run --locked --script audit/traffic.py --month 202609
```

The Python entry points have executable shebangs, inline requirements, and script lockfiles. `audit/rank-pageviews.csv` freezes the supplied mapping. New measurements have different timestamps and may differ numerically. Keep Harbor/model work separate from hardware-energy collection.

For the fresh GreenFrame protocol, install CLI 2.0.1 into an isolated local directory and pull the pinned runner image. The captured CLI archive SHA-256 is `fbfbbfd6ba034b2dd7ed35f6a412f32873f2ab0d3d9dbe06a5b590ab0fc1effc`; the stable download URL can change, so verify both version and digest. Use the published plans and new output directories:

```sh
docker pull mcr.microsoft.com/playwright:v1.30.0-focal
uv run --locked --script audit/greenframe.py \
  --plan docs/reports/assets/report-refinement/guide/energy/plan.json \
  --output-dir .audit-work/new-guide-energy \
  --mode run --binary .audit-work/tools/greenframe/bin/greenframe
uv run --locked --script audit/greenframe.py \
  --plan docs/reports/assets/report-refinement/wagtail/energy/plan.json \
  --output-dir .audit-work/new-wagtail-energy \
  --mode run --binary .audit-work/tools/greenframe/bin/greenframe
```

New agent collections record energy readiness by default. `workflow collect --energy run --greenframe-binary <local-binary>` attempts the accepted sample after browser collection; `--energy skip` records an explicit opt-out. Missing prerequisites or invalid counters retain null metrics and a reason. No hardware permissions or global settings are changed.

## Next validation

Run a matched, repeated sitespeed.io/co2-runner comparison on a controlled fixture, including first-sample handling and journey duration. Calibrate traffic scenarios against owner analytics with matching origin and period. Both are tracked in the [backlog](backlog.md); neither uncertainty is hidden by adding a score.
