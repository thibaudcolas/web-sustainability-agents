# First executable audit slice

Checkpoint: November 4, 2026. **The repository now has a runnable evidence-review benchmark, controlled browser fixtures, a shared review skill, and initial measurements of the two owner-nominated Wagtail sites.** This is a development experiment, not a validated sustainability assurance product.

## What runs

The Playwright collector in `audit/collect.js` records a cold and warm navigation in the same browser context. It records request outcomes, selected response headers, cache observations, received bytes, browser version, capture conditions, and a content hash. It never uses Playwright routing, which would disable the HTTP cache. Its scope is deliberately small: Chromium, a fixed viewport, no scrolling or consent interaction, and a fixed observation window.

The original project-owned fixture in `audit/fixture.js` combines a reusable public script, deliberately private non-cacheable data, and an optional illustration. Its contrasting variant retransfers the script and requests the illustration before intent. These are implementations inspired by STAR's testing ideas, not copies of STAR's illustrative pages or assertions that STAR supplies executable ground truth. Keyboard activation, image alternatives, structure, and ARIA were reviewed with the accessibility-agents specialists; no issues were reported within those scopes. Actual screen-reader speech was not tested.

`audit/rating.js` wraps CO2.js 0.19.0 with SWDM v4 and preserves the calculation trace. Ratings require a complete, positive-byte cold capture. Hosting remains unknown, with a disclosed non-green scenario assumption. The result is provisional pending external validation of the capture/profile combination. Warm visits, errors, and incomplete captures do not receive a grade. Tests exercise the installed library's unrounded rating boundaries.

The portable `sustainability-evidence-review` skill lives in `.agents/skills/`. Harbor copies the same skill into each agent environment. There is no dependency on a native sub-agent API in this slice; delegation has not been shown to improve its results.

## Six development cases

The checked-in `benchmarks/corpus.json` freezes measured fixture observations. `benchmarks/build.js` turns them into six Harbor tasks:

| Case                        | Deliberate distinction                                               |
| --------------------------- | -------------------------------------------------------------------- |
| Clean public evidence       | Reused asset, appropriate private `no-store`, deferred illustration  |
| Broken public evidence      | Asset retransferred and illustration requested before intent         |
| Broken with matching source | Same observations, plus a runner-supplied deployment-matched excerpt |
| Broken with stale source    | Source identity conflicts with the observed deployment identity      |
| Incomplete evidence         | Observations deliberately withheld; no carbon grade                  |
| Untrusted policy content    | A policy includes instructions to mark everything passing            |

Each task asks six bounded questions and requires a JSON report with outcomes, explanations, evidence IDs, and the supplied deterministic rating. Public-only tasks contain observations but no fixture source. Source-assisted tasks receive a small excerpt and synthetic deployment identity, not a real project checkout. Thus this tests use of supplied context, not autonomous repository investigation.

Harbor 0.23.0 runs the grader in a separate container. Only the report artifact crosses into it. The agent image does not contain the reference labels, verifier, or oracle solution. The grader checks outcomes, required evidence references, duplicate/missing answers, invented IDs, and preservation of the deterministic rating. It does **not** establish the semantic truth of every explanation or recommendation. A plausible but unsupported explanation with valid IDs can still pass; independent review and stronger claim-level checks remain necessary.

These six related cases cover parts of the larger [benchmark design](benchmark.md). They are public development cases with hand-authored expectations, not six independent sites, a held-out test set, or all twelve planned case families.

## Reproduce the experiment

Use the repository's Node.js version, Docker, and Harbor 0.23.0. Install Harbor separately from the documentation environment if needed, for example with `uv tool install --python 3.12 harbor==0.23.0`.

```sh
npm ci
just audit-install
just test
just benchmark-build
just benchmark-controls
node benchmarks/preflight.js
just benchmark-neuralwatt
just benchmark-codex
```

The model recipes require `NEURALWATT_API_KEY` and an existing Codex login, respectively. They use OpenCode 1.19.5 with `neuralwatt/deepseek-v4.1-flash`, and Codex CLI 0.166.0 with `openai/gpt-6-astra`, with low reasoning requested for both. The Codex model was selected from the local account's available configuration. These are comparisons of two model-plus-harness systems, not isolated model comparisons or equivalent reasoning budgets.

Generated tasks, full trajectories, provider responses, and working results stay under ignored `.audit-work/`. Treat those raw files as private: harness configuration and logs can include account material. Published results should use an explicit allowlist of fields. The recipes use an absolute jobs directory to avoid a Harbor/Docker Compose relative-path fallback observed during the initial controls.

The Docker base image is pinned by digest, and npm dependencies are locked. Agent setup still installs operating-system packages and transitive harness dependencies; this is not yet a fully hermetic environment. The model ID also does not freeze provider weights. Preserve each run's inputs, versions, timestamps, and actual response metadata.

`node benchmarks/build.js --refresh` deliberately remeasures the fixtures and changes the frozen corpus. Use it when reviewing a measurement or fixture change, not between comparison arms. Normal builds reuse the checked-in observations.

For a bounded live sample:

```sh
node audit/collect.js .audit-work/wagtail-captures.json \
  https://guide.wagtail.org/en/ \
  https://guide.wagtail.org/en/how-to-guides/manage-images/ \
  https://wagtail.org/ \
  https://wagtail.org/sustainability/
```

This opens four pages twice. It does not crawl, submit forms, or establish that a user journey is usable. Successful capture is distinct from successful task completion.

## Initial benchmark results

Both model arms received identical frozen inputs for all six revised cases. The [published results and reports](assets/first-slice-results.json) include input hashes, reports, outcomes, token/cost metadata, earlier preflights, and explicit restoration notes for the historical Harbor redaction issue described below.

| Arm                                       | Reports accepted by the narrow grader | Harbor-reported trial errors |
| ----------------------------------------- | ------------------------------------: | ---------------------------: |
| Reference control                         |                                6 of 6 |                            0 |
| No-operation control                      |                                0 of 6 |                            0 |
| Codex / GPT-6 Astra                       |                                6 of 6 |                            0 |
| OpenCode / Neuralwatt DeepSeek V4.1 Flash |                                6 of 6 |                            6 |

This demonstrates basic evidence-contract handling on closely related development cases. It does not establish model accuracy on WSG, recommendation quality, a benefit over deterministic rules, or a winning model. The separate verifier's acceptance of an artifact must not conceal an unsuccessful harness execution. The original artifacts remain private and unchanged; restored published reports were independently regraded against the same references, reproducing the recorded rewards.

For the revised six-case campaigns, the harness-reported cost totals were approximately $1.54 for Codex and $0.0125 for DeepSeek. These are unreconciled harness estimates, not provider invoices or cost per trustworthy audit. Prompt overhead, caching, model prices, and harness behavior differ. Complete campaign energy accounting remains unavailable.

## Initial live findings and limitations

The [published live sample](assets/live-sample.json) contains the sanitized resource observations. Byte values below are decimal bytes, not decoded asset sizes or energy measurements.

| Sample                      | Cold received bytes | Warm received bytes | Initial capture status                 |
| --------------------------- | ------------------: | ------------------: | -------------------------------------- |
| Guide homepage              |              58,635 |               1,045 | Complete within this protocol          |
| Guide image-management page |             232,124 |              17,377 | Complete within this protocol          |
| Wagtail homepage            |             944,006 |              39,847 | Incomplete accounting; rating withheld |
| Wagtail sustainability page |             603,126 |              37,653 | Incomplete accounting; rating withheld |

Both guide pages calculate as A+ under the declared provisional scenario. These are initial-viewport results with no scrolling; they must not be presented as grades for the complete sites or as WSG conformance.

The guide homepage and image-management page completed the initial capture protocol with substantially fewer received bytes on warm navigation. The wagtail.org captures included a Plausible script response with HTTP 404 and an aborted Google Analytics collection request with status 204. Those observations require interpretation: an aborted analytics request is not automatically a sustainability defect, and incomplete accounting is not a valid carbon rating. See the [live sample results](assets/live-sample.json) for measurements and conditions.

The collector currently sums CDP-reported received bytes, including reported overhead. It does not measure device energy, backend resource use, or all traffic from child frames. Service workers are blocked for this profile. Child frames, failed requests, and unfinished requests trigger an incomplete result. The observation window cannot establish the absence of later polling or activity. A complete capture therefore means complete within this limited protocol, not complete knowledge of the page.

The first two model preflights exposed an ambiguous rubric question about whole-site conformance. Both models reasonably treated observed defects as evidence against blanket conformance, while the initial reference expected an unknown. The revised case asks about **unobserved organizational processes**, independently of frontend behavior. Required citations were also narrowed to the facts actually needed. Earlier scores are retained as development history and should not be used to rank the models.

An additional review concern is numeric language: the first DeepSeek report described a received-byte figure as a body size, although the collector includes overhead. The current outcome grader does not catch that error. Add explicit byte-unit metadata to normalized evidence and verify numeric claims before accepting generated explanations.

The standalone Neuralwatt tool-call preflight succeeded and returned request-level energy and cost extensions. Harbor/OpenCode trajectories do not yet provide a verified complete energy ledger for the campaign. Keep unavailable inference energy as unknown; neither harness cost estimates nor the preflight's energy can stand in for the full campaign. A missing provider fingerprint also leaves served-weight identity unverified. [Neuralwatt OpenCode integration](https://docs.neuralwatt.com/integrations/opencode), [Neuralwatt energy methodology](https://docs.neuralwatt.com/energy-methodology).

The [sanitized preflight response](assets/provider-preflight.json) preserves the tool call, usage, energy attribution method, and request cost, excluding account allowance and authentication material.

OpenCode produced report artifacts but exited nonzero with `EPIPE` in all six revised trials. A further trial with formatter and language-server processes disabled showed the same symptom. This remains an integration failure even when the separate verifier accepts the report. The [matching upstream issue](https://github.com/harbor-framework/harbor/issues/4019) describes the same symptom; its suspected cause is not confirmed here. The baseline configuration retains the campaign settings rather than treating the unsuccessful workaround as a fix.

Harbor also treated the initial Codex authentication toggle `CODEX_FORCE_AUTH_JSON=1` as a secret and replaced the digit `1` inside downloaded metadata, reports, and verifier logs, breaking some JSON. The committed recipe instead passes the path to the existing Codex authentication file through `CODEX_AUTH_JSON_PATH`, avoiding a short redaction value. The summary script's explicit `--restore-codex-auth-flag` option reverses only this known historical nonsecret substitution in published copies, marks affected trials, and preserves the original files. Restored reports are regraded against their original references and must match Harbor's recorded rewards. This is another reason to retain raw artifacts and validate result serialization before a larger campaign.

A further Codex trial using the committed authentication-path configuration completed without errors, passed the verifier, and produced valid report and metadata JSON without restoration. That validates this workaround on the clean fixture; it does not resolve the separate OpenCode failure.

## Next validation gate

Before expanding to bakerydemo, additional skills, or Jev/Clef routing, independently review the case expectations and a small set of actual model reports. Resolve or replace the OpenCode integration so a passing artifact also comes from a successful run. Improve the evidence contract to check units, unsupported numeric claims, and recommendation prerequisites. Validate child-frame/service-worker accounting and the treatment of aborted analytics requests against another measurement tool. Then use a matching Wagtail checkout to test whether source access improves a concrete diagnosis or proposed fix.

Keep both Wagtail sites as owner-known validation targets. The owner's familiarity and past sustainability work make them useful for identifying false positives and impractical recommendations; those facts are context, not passing labels. A useful next checkpoint is a reviewed audit report for one real journey, with a public-only version and a deployment-matched source-assisted version.
