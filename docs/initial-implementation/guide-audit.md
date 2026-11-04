# Guide.wagtail.org: WIP sustainability audit

!!! note "Work in progress"

    Transfer measurements cover two pages; the broader metadata and preference sample covers six content pages and one missing path. Organizational coverage and the measurement protocol need further validation.

**Overall assessment: small initial transfers and useful existing caching; the strongest next experiments concern screenshot loading and search resilience.**

| Key measure                            | Result                                                          |
| -------------------------------------- | --------------------------------------------------------------- |
| Homepage initial load                  | **59.0 KB**                                                     |
| Image-management article initial load  | **232.8 KB**                                                    |
| Initial Digital Carbon Ratings         | **A+**, provisional on both sampled pages                       |
| Modeled initial footprint              | 0.00874 / 0.03450 gCO2e per sampled load                        |
| Extra measured traffic after scrolling | 0.0 KB on both pages in these windows                           |
| Overall WSG score                      | **Not scored**: no validated aggregate rubric; partial coverage |

The carbon figures use CO2.js 0.19.0, SWDM v4, first visits only, and a non-green scenario for unknown hosting. They are modeled estimates, not measured energy or whole-site grades.

## Top five findings

| Priority             | Finding                                                  | Next action                                                                   |
| -------------------- | -------------------------------------------------------- | ----------------------------------------------------------------------------- |
| Experiment           | **F04: Screenshots load before scrolling**               | Test deferral and responsive renditions while preserving legibility and zoom. |
| Targeted improvement | **F08: Search is inaccessible with JavaScript disabled** | Test a usable server-search fallback.                                         |
| Preserve             | **F05: Repeat visits reuse public assets**               | Keep cache reuse and compression in regression checks.                        |
| Targeted improvement | **G02: Error-page language is empty**                    | Supply a request-language fallback and test localized error recovery.         |
| Clarify              | **G01: Published footprint context is project-wide**     | Identify guide-specific scope before attributing annual emissions.            |

## Quantitative evidence

| Page                                                                       | Initial load | After cookie stage | After scrolling |
| -------------------------------------------------------------------------- | -----------: | -----------------: | --------------: |
| [Homepage](https://guide.wagtail.org/en/)                                  |      59.0 KB |            59.0 KB |         59.0 KB |
| [Manage images](https://guide.wagtail.org/en/how-to-guides/manage-images/) |     232.8 KB |           232.8 KB |        232.8 KB |

No cookie action was configured; the middle stage is inapplicable, not a successful consent decision. Both runs reached the bottom. Complete accounting means complete within this bounded protocol; child frames, service workers, and other profiles require separate validation. Zero additional traffic does not prove that eager loading is optimal.

[Per-site structured report](assets/reports/https-guide-wagtail-org-432853f7b5d8.json) and [metric rows for charts](assets/reports/https-guide-wagtail-org-432853f7b5d8.csv) preserve exact values, units, phase, branch, status, capture time, and evidence hashes. The [reporting contract](reporting.md) defines valid aggregations.

### Additional quantitative context

A separate three-run Firefox experiment measured a median **71.91 J** of whole-system CPU-package energy during homepage load, a three-second wait, startup, and shutdown. This shared-workstation measurement is exploratory and is not added to the SWDM calculation. The September 2026 CrUX **10-million bucket** yields a cohort-based scenario of approximately **245,000 annual pageviews**, not measured analytics. See the [energy and traffic experiment](energy-traffic-experiment.md) for provenance, ranges, differing profiles, and limits.

## Qualitative review

Wappalyzer detected Wagtail, Django, Python, and Cloudflare. Review CMS renditions, rich-text output, server rendering, and cache behavior. Fingerprints do not establish exact versions or low-carbon hosting.

The supplied [guide repository](https://github.com/wagtail/guide/tree/31a4547eb1f6de55baea84269723313784f6b544) supplies plausible implementation locations; its relationship to production is unknown. Public observations remain the primary evidence.

### G01 — Clarify guide-specific footprint reporting

The collector found no usable carbon.txt at the root or well-known location, nor a usable DNS/header pointer. A supplied related-document hint found the [Wagtail sustainability statement](https://wagtail.org/sustainability/), which includes the guide among project properties. This is useful context, not a measured guide-specific annual footprint. Missing discovery is not a WSG failure. See [WSG 5.5](https://www.w3.org/TR/web-sustainability-guidelines/#calculate-the-environmental-impact).

## Detailed findings

### F04 — Test deferred and responsive guide screenshots

**Priority: measured optimization experiment. Outcome: confirmed eager requests; savings and acceptable rendition sizes unmeasured.** Related WSG areas: [2.9](https://www.w3.org/TR/web-sustainability-guidelines/#optimize-media-to-reduce-resource-use) and [3.7](https://www.w3.org/TR/web-sustainability-guidelines/#defer-the-loading-of-non-critical-resources).

On the image-management page at 390 CSS pixels wide, all four screenshots were requested in the initial phase, before scrolling. They have `loading="auto"`, no `srcset` or `sizes`, 900-pixel intrinsic widths, and approximately 350-pixel rendered widths. Their top positions were 928, 1,418, 2,153, and 2,698 pixels, below the 844-pixel viewport. Desktop capture counted 177.1 KB received for the four responses. Evidence: `guide-images-mobile`, `guide-images-cold`.

Despite `.png` filenames, the response headers identify **WebP** bodies. Recommending a PNG-to-WebP conversion based on filenames would be a false positive. Nor does a 900-to-350 width ratio alone prove waste: screenshot legibility, zoom, and device pixel ratio matter. The mobile profile here uses device scale factor 1 and is not a representative high-density phone.

**Source contribution:** `guide-image-format` sets the full-width rendition to `width-900` in [the image-format configuration](https://github.com/wagtail/guide/blob/31a4547eb1f6de55baea84269723313784f6b544/apps/custom_media/image_formats.py). It is a candidate starting point, not the entire HTML generation path. Trace rich-text rendering and any cached or imported content before changing it.

Experiment with deferring later screenshots and responsive renditions while preserving a readable full-size view. Recheck initial and full-journey traffic, layout stability, and image legibility at higher pixel densities. Native lazy loading may still fetch nearby offscreen images; do not write an acceptance test that assumes every offscreen image must wait for scrolling.

### F05 — Preserve caching and negotiated compression

**Priority: retain as a regression check. Outcome: positive within the sampled states.** Related WSG areas: [4.2](https://www.w3.org/TR/web-sustainability-guidelines/#optimize-caching-and-support-offline-access) and [4.3](https://www.w3.org/TR/web-sustainability-guidelines/#reduce-data-transfer-with-compression).

Guide warm captures transfer substantially less data, with the main static script reused. The image article still transfers its HTML; that alone does not justify caching all HTML indefinitely. Guide JavaScript is gzip-compressed. Evidence: the guide cold/warm captures and their resource headers.

These observations support narrow findings about delivery and repeat visits. They do not establish backend cache hit rates, correct invalidation, authenticated cache safety, offline availability, or a complete compression policy. The source's cache-related settings and template fragments suggest further places to inspect, but running infrastructure was not measured. Keep privacy-sensitive `no-store` separate from reusable public asset caching.

### F07 — Keep the successful search journey, test its edge cases

**Priority: retain as a journey regression. Outcome: successful for one query and typing pattern.** Related WSG areas: [2.4](https://www.w3.org/TR/web-sustainability-guidelines/#design-efficient-and-streamlined-user-journeys) and [3.11](https://www.w3.org/TR/web-sustainability-guidelines/#use-sustainable-javascript-and-apis).

Opening guide search, typing “images” with 80 ms between keys, and selecting the result reached the expected article. One search JSON request was observed. Evidence: `guide-search-images`.

**Source contribution:** `guide-search` shows a 150 ms debounce, consistent with one request for this typing pattern. That is more useful than a generic recommendation to debounce search that already does so. Slower typing, interrupted requests, no-results handling, stale response ordering, keyboard-only completion, and screen-reader usability have not been evaluated. Do not infer user satisfaction or population-wide task success from this bounded journey.

### F08 — Offer a usable search fallback when JavaScript is unavailable

**Priority: targeted resilience improvement. Outcome: confirmed limitation in the tested state.** Related WSG area: [2.17](https://www.w3.org/TR/web-sustainability-guidelines/#provide-cross-platform-compatibility-support).

Without JavaScript, the guide retains the sampled main text and a visible navigation link to image management. Its search button remains visible, but clicking it does not reveal the hidden search input. Evidence: `guide-home-no-js` and follow-up `guide-no-js`. This is a search limitation, not evidence that the whole guide is unusable without JavaScript.

`guide-search-template` contains a GET search form within the hidden modal, providing a plausible reuse path. Expose a non-modal form or link when JavaScript is absent, then verify actual results and keyboard navigation. The direct server search response was not exercised in this audit; the template alone does not prove it works.

### Additional findings from the broader sample

**G02 — Give error pages a language fallback.** The deliberate missing-path response returned 404 with an empty HTML language attribute, while all six sampled content pages had one. It retained navigation, but complete recovery was not exercised. The supplied [base template](https://github.com/wagtail/guide/blob/31a4547eb1f6de55baea84269723313784f6b544/apps/core/templates/base.html#L7) uses `self.locale.language_code`; the error template does not override it. An active-request-language fallback is a plausible fix when there is no page object. Verify this against deployed templates and localized 404s. This is a concrete semantics issue, not a quantified emissions saving. See [WSG 3.6](https://www.w3.org/TR/web-sustainability-guidelines/#ensure-code-follows-good-semantic-practices) and [4.4](https://www.w3.org/TR/web-sustainability-guidelines/#setup-necessary-error-pages-and-redirection-links).

**G03 — Preserve preference support and broaden its regression checks.** The homepage changed to dark body colors after reloading with a dark preference. It did not change immediately when the OS preference was emulated in the loaded page. Source initialization in `blocking.js` corroborates this distinction. Reduced-motion CSS rules were present, but no active animation was observed to test their effect. Do not report dark mode as absent or claim measured energy savings. See [WSG 3.9](https://www.w3.org/TR/web-sustainability-guidelines/#use-media-queries-that-support-sustainability-goals).

**G04 — Review localized metadata without assuming every variation is wrong.** Five of six content pages had nonempty descriptions; the sampled French accessibility article did not. The Icelandic-route release article had `lang="is"` with an English title and heading, which warrants a translation-intent review rather than a conclusion about all its content. All six had canonical links, titles, one H1, and one main landmark. Presence does not establish quality or user benefit. See [WSG 3.8](https://www.w3.org/TR/web-sustainability-guidelines/#structure-metadata-for-machine-readability).

These observations and source hashes are in the [scope extension](scope-extension.md). The [per-site register](assets/coverage/guide.wagtail.org-432853f7b5d8.json) now records partial evidence for 14 guidelines, with 57 not assessed. None is declared a complete guideline pass. Working robots/sitemap/icon resources and supplied source licensing add useful context without proving all beneficial-file or organizational requirements.

## Scope and method

This WIP audit combines a two-page transfer sample with the separately scoped metadata and preference observations above; it does not establish whole-site WSG conformance. The [staged protocol](staged-auditing.md) records a fresh 1,280 × 800 desktop viewport, no initial interaction, then configured cookie choice and scrolling. All traffic figures use decimal KB/MB (1 KB = 1,000 B). Offscreen resources requested before scrolling remain in the initial figure. Three-second observation windows do not cover all eventual activity.

The [current evidence](assets/staged-audit.json) supports headline measurements. Historical finding IDs refer to the [earlier review evidence](assets/wagtail-review-evidence.json) unless stated otherwise. Earlier tests include warm-cache reuse, mobile observations, JavaScript-disabled behavior, and bounded journeys. Never mix measurements from different captures into a single total.

The [WSG draft](https://www.w3.org/TR/web-sustainability-guidelines/), [STAR](https://w3c.github.io/sustainableweb-ig/docs/star.html), and [impact ratings](https://www.w3.org/TR/wsg-ir/) inform review. The broader sample combines purposeful pages with two reproducibly selected sitemap URLs; it remains a development sample rather than a complete or representative site evaluation. Public statements are claims to corroborate. Unobserved organizational practices remain unknown.

## Feedback and reproducibility

Use the site name and finding ID when correcting an observation, interpretation, priority, or fix. The [feedback-to-pipeline backlog](backlog.md) records follow-up experiments. Run `just audit-sites` for fresh observations and `uv run --locked --script audit/report.py` for per-site chart data. Live recollection will vary.

Model reviews are a separate frozen-evidence experiment, described in the [model checkpoint](review-checkpoint.md) and [expanded comparison](expanded-benchmark.md). The coordinator synthesized this report; it is not the output of a validated autonomous auditor. Source excerpts can locate plausible fixes without proving production deployment identity.
