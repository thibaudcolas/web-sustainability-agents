# Energy and traffic enrichment experiment

The audit now runs a Python adapter for the supplied co2-runner and a separate CrUX lookup adapter. Sitespeed.io's hardware-energy path has been inspected but has not been executed in this checkpoint. Its role is the next independent cross-tool comparison. See [methodology and sources](../knowledge-base/energy-and-traffic.md).

## Executed energy measurements

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

The [traffic artifact](assets/traffic-scenarios.json) contains exact mapping values, dataset month, mirror commit, compressed-file digests, searched buckets, and mapping digest. These are **scenarios based on a different population and period**, not observed site traffic. No annual emissions total is calculated. The guide's scenario must not be replaced by Wagtail.org's bucket or combined as if origins were interchangeable.

## Reproduce

```sh
# Uses the supplied checkout and its installed Node/Firefox dependencies.
uv run --locked --script audit/energy.py
# Reads public monthly dumps; no CrUX or BigQuery key required.
uv run --locked --script audit/traffic.py --month 202609
```

The Python entry points have executable shebangs, inline requirements, and script lockfiles. `audit/rank-pageviews.csv` freezes the supplied mapping. New measurements have different timestamps and may differ numerically. Keep Harbor/model work separate from hardware-energy collection.

## Next validation

Run a matched, repeated sitespeed.io/co2-runner comparison on a controlled fixture, including first-sample handling and journey duration. Calibrate traffic scenarios against owner analytics with matching origin and period. Both are tracked in the [backlog](backlog.md); neither uncertainty is hidden by adding a score.
