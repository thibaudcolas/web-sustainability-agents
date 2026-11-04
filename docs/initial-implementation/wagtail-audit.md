# Wagtail sites: WIP sustainability audit

**The sampled guide pages have a small transfer footprint and effective repeat-visit reuse. The clearest Wagtail.org review priorities are analytics loading and opt-out behavior, a broken analytics script, and an inconsistent public emissions average.** Guide image loading and JavaScript fallback behavior offer narrower improvement opportunities. Several existing optimizations deserve to be preserved.

This is a reviewable audit report of a **bounded sample**, not a declaration that either site passes or fails WSG as a whole. Findings below have stable IDs for owner feedback. They combine deterministic observations, coordinator review, and source corroboration. Model-generated reviews are a separate experiment described in the [model and audit checkpoint](review-checkpoint.md); this report was not produced by an already validated autonomous audit system.

## Scope and evidence

The owner selected these content-focused sites and supplied their repositories. Prior sustainability work informs the review context but does not determine outcomes. The sample comprises the guide homepage, its image-management article, the Wagtail homepage, and the sustainability page. The linked ecosystem footprint article was read to check a public numerical claim; it was not included in the page-load measurements.

Each sampled page received a cold and warm desktop capture, a separate desktop and mobile scroll observation, and a desktop observation without JavaScript. Two desktop journeys were exercised: search for image-management guidance and follow the homepage footer link to sustainability. Follow-ups checked the guide's search control without JavaScript, Wagtail's horizontal overflow, typography, and analytics after opting out. No feedback forms were submitted. Video playback, authenticated pages, other languages, other browsers, backend operation, and the full content inventory remain outside this sample.

The [evidence bundle](assets/wagtail-review-evidence.json) contains capture timestamps, browser/version settings, selected headers, request phases, DOM observations, journey outcomes, source excerpts and hashes, and the arithmetic check. Evidence IDs below refer to its objects. Query strings and fragments are removed from published URLs to exclude analytics identifiers. Full private observations stay in ignored `.audit-work/`. Source excerpts come only from named tracked files in public repositories.

The methodology follows STAR's scope, evidence, sampling, and reporting structure, with an explicit departure from a comprehensive site evaluation: these four selected pages are a development sample, without a complete site inventory or representative random sample. The [WSG draft](https://www.w3.org/TR/web-sustainability-guidelines/), [STAR](https://w3c.github.io/sustainableweb-ig/docs/star.html), and [impact ratings](https://www.w3.org/TR/wsg-ir/) guide interpretation. The priorities here are practical review priorities, not copied WSG impact scores or measured carbon savings.

### Measurement summary

Decimal bytes below are **received network bytes including protocol-reported overhead**, not decoded body sizes. “Complete” means complete within the initial-load collector's protocol. Scrolling observations are separate and do not extend these carbon calculations.

| Page                                                                       | Cold received bytes | Warm received bytes | Calculation status                                  |
| -------------------------------------------------------------------------- | ------------------: | ------------------: | --------------------------------------------------- |
| [Guide homepage](https://guide.wagtail.org/en/)                            |              58,917 |                 450 | Provisional A+, 0.00873 gCO2e per sampled cold load |
| [Manage images](https://guide.wagtail.org/en/how-to-guides/manage-images/) |             232,252 |              17,435 | Provisional A+, 0.03442 gCO2e per sampled cold load |
| [Wagtail homepage](https://wagtail.org/)                                   |             943,914 |              38,962 | Partial accounting; rating withheld                 |
| [Sustainability](https://wagtail.org/sustainability/)                      |             603,775 |              36,786 | Partial accounting; rating withheld                 |

The guide calculations use CO2.js 0.19.0, SWDM v4, a first-visit-only scenario, and unknown hosting represented by the non-green scenario. They are modeled estimates, not measured energy, annual emissions, or whole-site Digital Carbon Ratings. The capture/profile combination still needs external validation. Wagtail captures contain failed requests, including a Plausible 404 and an aborted analytics response, so the pipeline correctly withholds a rating. Warm visits also receive no grade under this protocol. See the [rating implementation and limitations](first-slice.md#what-runs).

### Source provenance

| Repository                                                                                          | Inspected revision                         | Relationship to production                   |
| --------------------------------------------------------------------------------------------------- | ------------------------------------------ | -------------------------------------------- |
| [Wagtail guide](https://github.com/wagtail/guide/tree/31a4547eb1f6de55baea84269723313784f6b544)     | `31a4547eb1f6de55baea84269723313784f6b544` | Supplied checkout; deployed revision unknown |
| [Wagtail.org](https://github.com/wagtail/wagtail.org/tree/9fa65385f27c15b83c86a4f6e0e3ac18d4784609) | `9fa65385f27c15b83c86a4f6e0e3ac18d4784609` | Supplied checkout; deployed revision unknown |

Every published excerpt matches its committed file. Existing untracked screenshots and accessibility histories were left untouched and excluded. Runtime/source agreement identifies plausible implementation locations; it does not establish that the whole checkout is deployed. CMS content, production environment values, and GTM container configuration are not supplied by these excerpts.

## Findings to act on or investigate

### F01 — Review analytics loading and the meaning of opt-out

**Priority: high review value. Outcome: confirmed loading behavior; necessity and collection semantics unresolved.** Related WSG area: 3.5, third-party services.

The cold Wagtail homepage requested three Google scripts totaling 346,983 received bytes: GTM, `gtag/js`, and `analytics.js`. The sustainability page requested the same three script families totaling 347,006 bytes. These requests occurred before any interaction. This is a concrete resource cost even if a tracking configuration limits the data collected. Evidence: `wagtail-home-cold`, `wagtail-sustainability-cold`.

In a fresh context, the “Opt out” control was visible. After selecting it and reloading, the banner stayed dismissed, but the three Google scripts and `j/collect` requests still occurred. The `g/collect` request observed before the choice was absent from the recorded post-choice window. Thus it would be inaccurate to say the choice had no effect, or that no analytics traffic remained. Request payloads and consent-mode semantics were not inspected. Evidence: `wagtail-opt-out`.

**Source contribution:** `wagtail-gtm` locates conditional GTM injection in `patterns/base_page.html`. `wagtail-cookie-control` shows the banner writing a preference cookie. These are candidate places to trace control flow; neither includes the remote GTM container's rules. The source therefore narrows the investigation without proving a consent implementation defect or a legal conclusion.

**Recommended next action:** identify which integrations are still needed, how the preference is consumed, and whether nonessential scripts can be omitted before activation and after opt-out. Test fresh, opt-in, opt-out, and returning sessions against the intended contract. Do not remove all analytics solely because this audit observes their cost. No annual saving can be estimated without traffic and a validated counterfactual.

### F02 — Resolve the repeatedly failing Plausible script

**Priority: straightforward investigation. Outcome: confirmed request failure in this environment.** Related WSG areas: 2.15 and 3.5.

Both sampled Wagtail pages requested `https://plausible.io/js/pa-ngavQ28VQSDP3hrszIVgI.js`, which returned HTTP 404 in cold and warm captures. The browser reported the script as aborted. Its missing byte count is unknown, not zero. Evidence: the four `wagtail-*-cold` and `wagtail-*-warm` captures.

**Source contribution:** `wagtail-plausible` contains the same URL and initialization in [the shared base template](https://github.com/wagtail/wagtail.org/blob/9fa65385f27c15b83c86a4f6e0e3ac18d4784609/wagtailio/project_styleguide/templates/patterns/base.html#L30). That is a strong candidate location to check. Confirm the intended Plausible deployment and repeat from another network before deciding whether to correct the URL or remove an obsolete integration. Treat the coexistence of Plausible and Google as an inventory question, not proof that their purposes duplicate each other.

### F03 — Reconcile the public per-site emissions average

**Priority: editorial correction or clarification. Outcome: arithmetic inconsistency under the stated common-population interpretation.** Related WSG area: 5.5, environmental calculations.

The sustainability page reports 5,173 tonnes per year across 6,431 sites and an average of 12 tonnes per site per year. Dividing the total by the count yields approximately **0.8044 tonnes per site per year**, not 12. The linked footprint article identifies the same total and site count for 2025. Evidence: `sustainability-average`, `footprint-total`, `average-check`. [Sustainability page](https://wagtail.org/sustainability/), [footprint article](https://wagtail.org/blog/wagtails-2025-carbon-footprint/).

Confirm whether the average was carried over from another estimate, uses another population, or has a different unit. Then correct it or label the distinct denominator. This check does not validate the underlying emissions model or imply that 0.8044 is a measured average for every Wagtail site.

**Source contribution:** the inspected templates do not contain this CMS-authored sentence. The likely edit is in page content, but no exact CMS block or database record was established. An agent should not invent a source-file patch for it. A useful regression check would reconcile displayed totals, populations, units, and years against the approved dataset.

### F04 — Test deferred and responsive guide screenshots

**Priority: measured optimization experiment. Outcome: confirmed eager requests; savings and acceptable rendition sizes unmeasured.** Related WSG areas: 2.9 and 3.7.

On the image-management page at 390 CSS pixels wide, all four screenshots were requested in the initial phase, before scrolling. They have `loading="auto"`, no `srcset` or `sizes`, 900-pixel intrinsic widths, and approximately 350-pixel rendered widths. Their top positions were 928, 1,418, 2,153, and 2,698 pixels, below the 844-pixel viewport. Desktop capture counted 177,126 received bytes for the four responses. Evidence: `guide-images-mobile`, `guide-images-cold`.

Despite `.png` filenames, the response headers identify **WebP** bodies. Recommending a PNG-to-WebP conversion based on filenames would be a false positive. Nor does a 900-to-350 width ratio alone prove waste: screenshot legibility, zoom, and device pixel ratio matter. The mobile profile here uses device scale factor 1 and is not a representative high-density phone.

**Source contribution:** `guide-image-format` sets the full-width rendition to `width-900` in [the image-format configuration](https://github.com/wagtail/guide/blob/31a4547eb1f6de55baea84269723313784f6b544/apps/custom_media/image_formats.py). It is a candidate starting point, not the entire HTML generation path. Trace rich-text rendering and any cached or imported content before changing it.

Experiment with deferring later screenshots and responsive renditions while preserving a readable full-size view. Recheck initial and full-journey traffic, layout stability, and image legibility at higher pixel densities. Native lazy loading may still fetch nearby offscreen images; do not write an acceptance test that assumes every offscreen image must wait for scrolling.

### F05 — Preserve caching and negotiated compression

**Priority: retain as a regression check. Outcome: positive within the sampled states.** Related WSG areas: 4.2 and 4.3.

Guide warm captures transfer substantially less data, with the main static script reused. The image article still transfers its HTML; that alone does not justify caching all HTML indefinitely. Wagtail static CSS, JavaScript, and fonts use long-lived immutable caching, and sampled HTML is Brotli-compressed. Guide JavaScript is gzip-compressed. Evidence: the eight cold/warm captures and their resource headers.

These observations support narrow findings about delivery and repeat visits. They do not establish backend cache hit rates, correct invalidation, authenticated cache safety, offline availability, or a complete compression policy. The source's cache-related settings and template fragments suggest further places to inspect, but running infrastructure was not measured. Keep privacy-sensitive `no-store` separate from reusable public asset caching.

### F06 — Preserve user-controlled video loading

**Priority: retain and complete interaction testing. Outcome: positive pre-playback behavior.** Related WSG area: 2.9.

The Wagtail homepage exposes native video controls, `preload="none"`, and no autoplay attribute. No media request occurred during the initial desktop/mobile observations or incremental scrolling. Evidence: `wagtail-home-desktop`, `wagtail-home-mobile`. `wagtail-video` corroborates that implementation in [the homepage template](https://github.com/wagtail/wagtail.org/blob/9fa65385f27c15b83c86a4f6e0e3ac18d4784609/wagtailio/project_styleguide/templates/patterns/pages/home/home_page.html#L50).

Some lower-page images did load on scrolling, so the initial page weight is not the full reading-journey weight. Video activation, keyboard operation, captions, alternative content, duration information, and actual transferred video bytes remain untested. Do not turn the positive pre-playback observation into a pass for the whole media guideline.

### F07 — Keep the successful search journey, test its edge cases

**Priority: retain as a journey regression. Outcome: successful for one query and typing pattern.** Related WSG areas: 2.4 and 3.11.

Opening guide search, typing “images” with 80 ms between keys, and selecting the result reached the expected article. One search JSON request was observed. The Wagtail homepage footer link also reached the sustainability page. Evidence: `guide-search-images`, `wagtail-find-sustainability`.

**Source contribution:** `guide-search` shows a 150 ms debounce, consistent with one request for this typing pattern. That is more useful than a generic recommendation to debounce search that already does so. Slower typing, interrupted requests, no-results handling, stale response ordering, keyboard-only completion, and screen-reader usability have not been evaluated. Do not infer user satisfaction or population-wide task success from these two journeys.

### F08 — Offer a usable search fallback when JavaScript is unavailable

**Priority: targeted resilience improvement. Outcome: confirmed limitation in the tested state.** Related WSG area: 2.17.

Without JavaScript, the guide retains the sampled main text and a visible navigation link to image management. Its search button remains visible, but clicking it does not reveal the hidden search input. Evidence: `guide-home-no-js` and follow-up `guide-no-js`. This is a search limitation, not evidence that the whole guide is unusable without JavaScript.

`guide-search-template` contains a GET search form within the hidden modal, providing a plausible reuse path. Expose a non-modal form or link when JavaScript is absent, then verify actual results and keyboard navigation. The direct server search response was not exercised in this audit; the template alone does not prove it works.

### F09 — Review typography under constrained loading

**Priority: lower-priority investigation. Outcome: source and stylesheet observation, without measured user delay.** Related WSG area: 2.11.

Wagtail serves WOFF2 fonts from its own origin with long cache lifetimes. The inspected font rules use `font-display: block` for regular Kumbh Sans and omit an explicit display value for two other weights. Evidence: `wagtail-font-css`, `wagtail-fonts`, and cold resource headers.

Test text visibility on a constrained connection before recommending `swap`, `fallback`, or a system-font alternative. We did not measure font-blocking duration, layout shifts, readability, or brand requirements. Self-hosting is an existing positive; changing fonts is not automatically the highest-value sustainability action.

### F10 — Investigate small horizontal overflow without overstating it

**Priority: low, pending user-impact validation. Outcome: reproducible 10-pixel horizontal scroll range.** Related WSG area: 3.10.

The homepage had a 400-pixel document at a 390-pixel viewport and a 1,290-pixel document at 1,280 pixels. A programmatic horizontal scroll reached 10 pixels. The candidate-element list also includes intentionally hidden off-canvas navigation, so blindly reporting every out-of-bounds element would be wrong. Evidence: `wagtail-mobile`, `wagtail-desktop`.

Visual inspection of the mobile screenshot showed readable primary content; it did not establish a blocked task. Identify the element responsible, verify touch/keyboard and zoom behavior, and fix only a demonstrated layout issue. The report does not assign an emissions saving or an accessibility conformance failure to this observation.

## Unresolved coverage

### F11 — Public sustainability reporting does not establish organizational implementation

The sustainability page and linked methodology provide useful transparency and explicit uncertainty about ecosystem estimates. That is positive evidence of public reporting. Neither those pages nor the inspected source establishes procurement criteria, retention/deletion execution, workforce practices, supplier assurance, disaster recovery, or all other organizational WSG requirements. These remain **not assessed or inconclusive**, not automatic failures and not passes inferred from a policy page.

The [guideline coverage register](assets/wsg-review-coverage.json) accounts for all 71 guidelines in the inspected WSG draft. It records where this report provides partial evidence and leaves the rest unassessed. Partial evidence is not a guideline pass; no conformance percentage is calculated. An owner-reviewed service inventory and relevant operational records would determine the next sample and which organizational questions are applicable.

### F12 — Infrastructure and annual impact remain unknown

The capture does not measure origin CPU, database work, storage, build pipelines, electricity supply, hardware lifespan, or actual annual traffic. A CDN hostname and source caching configuration cannot establish these. Hosting therefore remains unknown in the scenario calculation. Source access could enable targeted query profiling and deployment inspection, but the checkout alone does not supply live operational evidence.

### F13 — Collection validity is a pipeline finding

The Wagtail resource errors prevent a complete carbon calculation under the current conservative gate. A 204 analytics response reported as aborted is not itself proof of a broken user experience. Validate byte accounting against another collector, distinguish expected response behavior from network failures, and account for child frames and service workers before changing the gate. Do not suppress inconvenient resources merely to produce a grade.

## What source access changed

The public evidence alone supports analytics-loading observations, the Plausible error, the arithmetic discrepancy, screenshot behavior, cache reuse, and video deferral. Source access adds candidate implementation locations, identifies an existing search debounce, and explains why a template edit cannot necessarily correct CMS-authored content. It does **not** change a runtime failure into a pass, prove the deployed revision, or reveal remote GTM rules.

This audit demonstrates source-assisted investigation by the coordinator. The paired model trials receive selected excerpts; they do not autonomously explore the entire repositories. Measuring whether autonomous source discovery improves recommendations still requires a separate task, access boundary, and owner-reviewed expected locations.

## Turn feedback into pipeline changes

Reply with a finding ID and the disputed observation, interpretation, priority, or proposed fix. A correction to one does not automatically invalidate the others. For example, “F04: retain 900-pixel screenshots for zoom, but defer the last two” changes recommendation prerequisites while preserving the observed request timing.

| Finding or feedback                                                    | Component to change                                      | Regression to add after owner review                                                    |
| ---------------------------------------------------------------------- | -------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| F01: intended consent behavior or analytics purpose differs            | Scenario collection and evidence-review rubric           | Fresh/opt-in/opt-out/returning cases, with expected requests and legitimate exceptions  |
| F02: failure is network-specific or an obsolete integration            | Resource-error classification and source corroboration   | Independent reproduction, valid script, missing script, and uncertain network cases     |
| F03: figures have different populations or units                       | Numerical extraction, arithmetic checks, semantic review | Same-denominator mismatch plus a legitimate different-denominator example               |
| F04: image detail, pixel density, or content format changes the advice | Media evidence contract and recommendation checks        | MIME type versus extension; screenshot readability; initial versus full-journey traffic |
| F05–F07: an existing optimization is missed                            | Deterministic evidence and exception handling            | Warm-cache reuse, deferred video, and an already-debounced search                       |
| F08: fallback is unnecessary or another route exists                   | Journey scope and usability review                       | JavaScript-disabled search success or an explicit justified scope exception             |
| F09–F10: low-priority observations are distracting                     | Prioritization and report presentation                   | Require user-impact evidence before escalating source-only or cosmetic concerns         |
| F11–F12: relevant records were available but missed                    | Evidence discovery and coverage tracking                 | Find supplied records; distinguish policy, implementation, and missing evidence         |
| F13: byte totals or completeness are wrong                             | Collector and rating eligibility                         | Independent accounting checks; expected aborts; frames and service workers              |
| Source location or deployment claim is wrong                           | Source provenance checks                                 | Matching, unknown, stale, and contradictory deployment identities                       |

Accepted corrections should become versioned expectations before rerunning both model arms. Preserve the original report, label changes, inputs, and disagreements. Keep a future held-out set separate from these owner-reviewed development cases; repeated tuning on this report is not independent evidence of model improvement.

## Reproduce the checkpoint

```sh
node audit/site-review.js
node audit/site-followups.js
node audit/publish-site-review.js
just benchmark-build
node benchmarks/build-site-review.js
```

Recollection observes changing live sites; it will not reproduce identical bytes. Use the committed evidence and frozen task inputs for model comparisons. See the [checkpoint](review-checkpoint.md) for model settings, Harbor commands, results, and limitations.
