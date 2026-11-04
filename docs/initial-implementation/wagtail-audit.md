# Wagtail.org: WIP sustainability audit

!!! note "Work in progress"

    Transfer measurements cover the homepage and sustainability page; metadata and preference probes cover seven content pages and one missing path. Traffic accounting remains partial, and organizational coverage is incomplete.

**Overall assessment: preserve caching and video deferral; investigate analytics choices and reconcile a public emissions average.**

| Key measure                         | Result                                                          |
| ----------------------------------- | --------------------------------------------------------------- |
| Homepage initial load               | **944.4 KB** observed; partial accounting                       |
| Sustainability page initial load    | **590.5 KB** observed; partial accounting                       |
| Additional traffic during scrolling | **163.3 KB / 42.8 KB** in the accept trajectories               |
| Initial Digital Carbon Ratings      | **Unavailable** while accounting is incomplete                  |
| Published homepage estimate         | 0.06 gCO2e/view; a separate mobile profile and reporting period |
| Scoped WSG audit score              | **58.8/100 — 10/17 passing scoped checks**                      |
| Estimated annual browsing footprint | **65.1 kgCO2e/year**, under the declared proxy scenario         |

Initial figures precede cookie interaction. Reported failed requests remain part of the site as found; a Plausible error is contextual, not a primary sustainability recommendation.

The `scoped-wsg-v1` score comprises **10 passes, 4 failures, and 3 unresolved checks**. Checked coverage is **17/71 guidelines (23.9%)**; 54 remain untested. The experimental impact-weighted score is **61.8/100**. Unknowns remain in the score denominator but are not failures. A pass satisfies the declared narrow check, not every criterion of its WSG guideline; **zero full guidelines are verified**. See the [scoring method](../knowledge-base/audit-scoring.md) and [evidence-linked judgments](assets/scored-audits.json).

## Top five findings

| Priority                | Finding                                                                | Next action                                                             |
| ----------------------- | ---------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| High review value       | **F01: Analytics loads before a choice**                               | Reconcile observed opt-out behavior with intended purpose and controls. |
| Editorial clarification | **F03: Public average does not reconcile**                             | Confirm denominator/units and correct or explain the average.           |
| Preserve                | **F06: Video is deferred until intent**                                | Retain deferral and verify playback accessibility separately.           |
| Editorial clarification | **F14: Privacy statement has unclear site scope**                      | Confirm whether Torchbox-specific wording describes Wagtail.org.        |
| Corroborate             | **F12: Footprint and infrastructure claims need operational evidence** | Compare published assumptions with a matched measurement profile.       |

## Quantitative evidence

| Page and branch        | Initial load | After cookie choice | After scrolling | Added during scroll window |
| ---------------------- | -----------: | ------------------: | --------------: | -------------------------: |
| Homepage, accept       |     944.4 KB |            944.4 KB |         1.11 MB |                   163.3 KB |
| Homepage, reject       |     944.8 KB |            944.8 KB |         1.11 MB |                   163.4 KB |
| Sustainability, accept |     590.5 KB |            590.5 KB |        633.3 KB |                    42.8 KB |
| Sustainability, reject |     589.7 KB |            589.7 KB |        632.7 KB |                    42.9 KB |

All four runs reached the bottom and completed their configured cookie clicks. No extra traffic was measured in the post-choice window; this does not prove that consent was enforced or that future behavior is identical. Branches use fresh contexts, so their different initial totals are single-run variation. Scroll-window deltas include background activity and late completions; they are not automatically avoidable savings.

[Per-site structured report](assets/reports/https-wagtail-org-fa043133d284.json) and [metric rows for charts](assets/reports/https-wagtail-org-fa043133d284.csv) preserve exact values and provenance. Charts must label partial accounting and avoid stacking cumulative phase totals. See the [reporting contract](reporting.md).

### Additional quantitative context

A separate three-run Firefox experiment measured a median **77.86 J** of whole-system CPU-package energy during homepage load, a three-second wait, startup, and shutdown. This shared-workstation measurement is exploratory and is not added to the SWDM calculation. The September 2026 CrUX **5-million bucket** yields a cohort-based scenario of approximately **573,000 annual pageviews**, not measured analytics. See the [energy and traffic experiment](energy-traffic-experiment.md) for provenance, ranges, differing profiles, and limits.

### Estimated annual footprint

The estimated annual browsing footprint is **65.1 kgCO2e/year**, using **572,851 estimated annual pageviews** and an equal mix of the homepage and sustainability page. Accept/reject captures are averaged within each page before weighting pages. Representing all views with only the lighter or heavier sampled page yields **50.1–80.2 kgCO2e/year**. Transfer accounting remains **partial**, so this estimate does not qualify the pages for DCR badges. These are scenario sensitivities, not confidence bounds. The estimate assumes first visits only, an unknown real page mix, and non-green hosting in SWDM v4. It includes modeled operational and embodied browsing emissions, not a complete organizational footprint or a measured calendar-year total. Scrolling, playback, actual repeat visits and unsampled content can change it. See the [annual scenario artifact](assets/annual-footprints.json) and [reproduction details](skill-audit-workflow.md#methodology-and-reproducibility).

## Qualitative review

[Carbon.txt](https://wagtail.org/carbon.txt) declares syntax version 0.4 and links [digital-emissions documentation](https://wagtail.org/digital-emissions/). That statement describes a 0.06 gCO2e homepage view from an April 2026 mobile Lighthouse profile, 507 KB for first-time visitors, an annual footprint range, and monitoring practices. Its profile and grid assumptions differ from this desktop capture. The difference is not evidence of a regression.

Wappalyzer detected Wagtail, Django, Python, Cloudflare, Google analytics/tag-manager, Plausible, and PWA fingerprints. These guide investigation; they do not establish exact deployment versions, successful integrations, low-carbon hosting, or offline support. Plausible being fingerprinted despite a failed request illustrates the distinction.

The supplied [Wagtail.org source](https://github.com/wagtail/wagtail.org) provides candidate implementation locations. Deployment identity remains unknown, and CMS-authored content or remote tag-manager rules may not be represented in source.

## Detailed findings

### F01 — Review analytics loading and the meaning of opt-out

**Priority: high review value. Outcome: confirmed loading behavior; necessity and collection semantics unresolved.** Related WSG area: [3.5](https://www.w3.org/TR/web-sustainability-guidelines/#treat-third-parties-the-same-as-first-parties), third-party services.

The cold Wagtail homepage requested three Google scripts totaling 347.0 KB received: GTM, `gtag/js`, and `analytics.js`. The sustainability page requested the same three script families totaling 347.0 KB. These requests occurred before any interaction. This is a concrete resource cost even if a tracking configuration limits the data collected. Evidence: `wagtail-home-cold`, `wagtail-sustainability-cold`.

In a fresh context, the “Opt out” control was visible. After selecting it and reloading, the banner stayed dismissed, but the three Google scripts and `j/collect` requests still occurred. The `g/collect` request observed before the choice was absent from the recorded post-choice window. Thus it would be inaccurate to say the choice had no effect, or that no analytics traffic remained. Request payloads and consent-mode semantics were not inspected. Evidence: `wagtail-opt-out`.

**Source contribution:** `wagtail-gtm` locates conditional GTM injection in `patterns/base_page.html`. `wagtail-cookie-control` shows the banner writing a preference cookie. These are candidate places to trace control flow; neither includes the remote GTM container's rules. The source therefore narrows the investigation without proving a consent implementation defect or a legal conclusion.

**Recommended next action:** identify which integrations are still needed, how the preference is consumed, and whether nonessential scripts can be omitted before activation and after opt-out. Test fresh, opt-in, opt-out, and returning sessions against the intended contract. Do not remove all analytics solely because this audit observes their cost. No annual saving can be estimated without traffic and a validated counterfactual.

### F03 — Reconcile the public per-site emissions average

**Priority: editorial correction or clarification. Outcome: arithmetic inconsistency under the stated common-population interpretation.** Related WSG area: [5.5](https://www.w3.org/TR/web-sustainability-guidelines/#calculate-the-environmental-impact), environmental calculations.

The sustainability page reports 5,173 tonnes per year across 6,431 sites and an average of 12 tonnes per site per year. Dividing the total by the count yields approximately **0.8044 tonnes per site per year**, not 12. The linked footprint article identifies the same total and site count for 2025. Evidence: `sustainability-average`, `footprint-total`, `average-check`. [Sustainability page](https://wagtail.org/sustainability/), [footprint article](https://wagtail.org/blog/wagtails-2025-carbon-footprint/).

Confirm whether the average was carried over from another estimate, uses another population, or has a different unit. Then correct it or label the distinct denominator. This check does not validate the underlying emissions model or imply that 0.8044 is a measured average for every Wagtail site.

**Source contribution:** the inspected templates do not contain this CMS-authored sentence. The likely edit is in page content, but no exact CMS block or database record was established. An agent should not invent a source-file patch for it. A useful regression check would reconcile displayed totals, populations, units, and years against the approved dataset.

### F06 — Preserve user-controlled video loading

**Priority: retain and complete interaction testing. Outcome: positive pre-playback behavior.** Related WSG area: [2.9](https://www.w3.org/TR/web-sustainability-guidelines/#optimize-media-to-reduce-resource-use).

The Wagtail homepage exposes native video controls, `preload="none"`, and no autoplay attribute. No media request occurred during the initial desktop/mobile observations or incremental scrolling. Evidence: `wagtail-home-desktop`, `wagtail-home-mobile`. `wagtail-video` corroborates that implementation in [the homepage template](https://github.com/wagtail/wagtail.org/blob/9fa65385f27c15b83c86a4f6e0e3ac18d4784609/wagtailio/project_styleguide/templates/patterns/pages/home/home_page.html#L50).

Some lower-page images did load on scrolling, so the initial page weight is not the full reading-journey weight. Video activation, keyboard operation, captions, alternative content, duration information, and actual transferred video bytes remain untested. Do not turn the positive pre-playback observation into a pass for the whole media guideline.

### F09 — Review typography under constrained loading

**Priority: lower-priority investigation. Outcome: source and stylesheet observation, without measured user delay.** Related WSG area: [2.11](https://www.w3.org/TR/web-sustainability-guidelines/#use-optimized-web-typography).

Wagtail serves WOFF2 fonts from its own origin with long cache lifetimes. The inspected font rules use `font-display: block` for regular Kumbh Sans and omit an explicit display value for two other weights. Evidence: `wagtail-font-css`, `wagtail-fonts`, and cold resource headers.

Test text visibility on a constrained connection before recommending `swap`, `fallback`, or a system-font alternative. We did not measure font-blocking duration, layout shifts, readability, or brand requirements. Self-hosting is an existing positive; changing fonts is not automatically the highest-value sustainability action.

### F12 — Corroborate infrastructure and annual-impact claims

The capture does not measure origin CPU, database work, storage, build pipelines, electricity supply, hardware lifespan, or actual annual traffic. The newly discovered carbon.txt names infrastructure services, and the digital-emissions statement publishes an annual estimate and methodology. Keep these as attributed context awaiting corroboration. A CDN fingerprint and source caching configuration cannot independently establish the operational facts, so hosting remains unknown in our calculation scenario. Source access could enable targeted profiling, but the checkout alone does not supply live operational evidence.

### F02 — Note the Plausible loading failure in the as-is capture

**Priority: contextual observation. Outcome: confirmed request failure in this environment.** Related WSG areas: [2.15](https://www.w3.org/TR/web-sustainability-guidelines/#audit-and-test-for-bugs-or-issues-requiring-resolution) and [3.5](https://www.w3.org/TR/web-sustainability-guidelines/#treat-third-parties-the-same-as-first-parties).

Both sampled Wagtail pages requested `https://plausible.io/js/pa-ngavQ28VQSDP3hrszIVgI.js`, which returned HTTP 404 in cold and warm captures. The browser reported the script as aborted. Its missing byte count is unknown, not zero. Evidence: the four `wagtail-*-cold` and `wagtail-*-warm` captures.

**Source contribution:** `wagtail-plausible` contains the same URL and initialization in [the shared base template](https://github.com/wagtail/wagtail.org/blob/9fa65385f27c15b83c86a4f6e0e3ac18d4784609/wagtailio/project_styleguide/templates/patterns/base.html#L30). This corroborates the observed request origin, but the sustainability audit measures the site as found. Do not repair, block, or substitute this script to obtain a cleaner measurement. Note the failure and any accounting limitation without making configuration troubleshooting a priority. If the owner separately wants to investigate it, the template is a candidate starting point. The coexistence of Plausible and Google does not prove their purposes duplicate each other.

### F10 — Investigate small horizontal overflow without overstating it

**Priority: low, pending user-impact validation. Outcome: reproducible 10-pixel horizontal scroll range.** Related WSG area: [3.10](https://www.w3.org/TR/web-sustainability-guidelines/#ensure-layouts-work-for-different-devices-and-requirements).

The homepage had a 400-pixel document at a 390-pixel viewport and a 1,290-pixel document at 1,280 pixels. A programmatic horizontal scroll reached 10 pixels. The candidate-element list also includes intentionally hidden off-canvas navigation, so blindly reporting every out-of-bounds element would be wrong. Evidence: `wagtail-mobile`, `wagtail-desktop`.

Visual inspection of the mobile screenshot showed readable primary content; it did not establish a blocked task. Identify the element responsible, verify touch/keyboard and zoom behavior, and fix only a demonstrated layout issue. The report does not assign an emissions saving or an accessibility conformance failure to this observation.

### F05 — Preserve caching and compression

Sampled static CSS, JavaScript, and fonts use long-lived caching, and HTML uses Brotli. These are useful delivery optimizations; they do not establish backend cache efficiency or safe invalidation. Keep them in regression checks. See [WSG 4.2](https://www.w3.org/TR/web-sustainability-guidelines/#optimize-caching-and-support-offline-access) and [4.3](https://www.w3.org/TR/web-sustainability-guidelines/#reduce-data-transfer-with-compression).

### F14 — Clarify the privacy statement's site scope

**Priority: editorial clarification and operational corroboration.** The sampled [privacy page](https://wagtail.org/privacy/) repeatedly describes Torchbox and says its policy applies to the Torchbox website. That is ambiguous on Wagtail.org. Confirm the intended site and organization scope, then align the description with the actual collection and retention practices. The earlier analytics observations identify useful questions; they do not by themselves establish a contradiction in personal-data handling or a legal violation. See [WSG 5.18](https://www.w3.org/TR/web-sustainability-guidelines/#promote-responsible-data-practices).

### F15 — Preserve preference, metadata, and recovery support

The broader sample's seven content pages returned 200 and each had a title, canonical link, language, one H1, and one main landmark. The digital-emissions page lacked a nonempty description; review whether a useful summary would improve discovery. These checks do not validate semantic quality. See [WSG 3.6](https://www.w3.org/TR/web-sustainability-guidelines/#ensure-code-follows-good-semantic-practices) and [3.8](https://www.w3.org/TR/web-sustainability-guidelines/#structure-metadata-for-machine-readability).

The homepage adopted dark body colors after reloading with a dark preference, although changing the preference in the loaded page did not change those colors immediately. Runtime CSS included reduced-motion, forced-colors, and print queries. Source initialization and print styles provide plausible corroboration. Verify usable print output, contrast, and active-motion behavior before claiming comprehensive preference support or savings. See [WSG 3.9](https://www.w3.org/TR/web-sustainability-guidelines/#use-media-queries-that-support-sustainability-goals).

Robots, sitemap, icon, security.txt, carbon.txt, and the homepage's declared manifest were retrievable. The manifest uses a hashed static path: the root-path 404 is not an absent-manifest finding. One deliberate missing path returned 404 with an explanatory heading and search form; successful recovery still needs a journey test. See [WSG 3.13](https://www.w3.org/TR/web-sustainability-guidelines/#include-expected-and-beneficial-files) and [4.4](https://www.w3.org/TR/web-sustainability-guidelines/#setup-necessary-error-pages-and-redirection-links). Evidence and protocol: [scope extension](scope-extension.md).

### F16 — Test deferral of below-fold customer logos

**Priority: bounded optimization experiment. Outcome: failed scoped deferral check, medium confidence.** Related WSG area: [3.7](https://www.w3.org/TR/web-sustainability-guidelines/#defer-the-loading-of-non-critical-resources).

The skill reviewer identified customer logos at approximately 3,198 CSS pixels below the top of the desktop page, with `loading="auto"` and requests in the initial unscrolled capture. The sampled Oxfam and NHS logo responses transferred **7.1 KB** and **3.7 KB**, respectively, already as WebP. Evidence: `wagtail-home-desktop` and resources `1067177.7`/`1067177.8` in `wagtail-home-cold`.

The reviewer judged these customer logos non-critical to the initial view, unlike instructional screenshots whose reading/legibility prerequisites remain unresolved. This judgment is explicit and reviewable, not a measured saving. Test lazy loading for the logo row against request timing and usable on-scroll display; browser distance thresholds may still fetch nearby content. Preserve modern formats and the existing video deferral. Do not extrapolate these two response sizes into annual savings without a validated counterfactual and journey mix.

## Unresolved coverage

### F11 — Public sustainability reporting does not establish organizational implementation

The sustainability page, linked methodology, and newly discovered site-specific digital-emissions statement provide useful transparency and uncertainty about estimates. That is positive evidence of public reporting. Neither those pages nor the inspected source establishes procurement criteria, retention/deletion execution, workforce practices, supplier assurance, disaster recovery, or all other organizational WSG requirements. These remain **not assessed or inconclusive**, not automatic failures and not passes inferred from a policy page.

The [per-site coverage register](assets/coverage/wagtail.org-fa043133d284.json) records partial evidence for 17 of the 71 guidelines, with 54 not assessed. The [historical combined register](assets/wsg-review-coverage.json) remains available for the earlier cross-site review. Partial evidence is not a guideline pass; no conformance percentage is calculated. An owner-reviewed service inventory and relevant operational records would determine the next sample and which organizational questions are applicable.

### F13 — Collection validity is a pipeline finding

Unresolved Wagtail request accounting prevents a complete carbon calculation under the current gate, while the observed as-is bytes remain headline evidence. A fully measured HTTP error response does not itself invalidate the new protocol. A 204 analytics response reported as aborted is not itself proof of a broken user experience. Validate byte accounting against another collector, distinguish expected response behavior from network failures, and account for child frames and service workers before changing the gate. Do not suppress inconvenient resources merely to produce a grade.

## Expanded agent review

A separate [agent-triggered pilot](agent-driven-audits.md) tested 15 scoped expectations on the homepage and sustainability page. Its [review](assets/agent-sessions/wagtail/review.json) and [score](assets/agent-sessions/wagtail/scores.json) have **5 passes, 1 failure and 9 unknowns**: **33.3/100**, with 15/71 groups attempted. This is the new `agent-public-v1` investigation rubric, not a decline from the headline `scoped-wsg-v1` score. The two rubrics and samples must not be merged into an apparent trend.

The new [capture](assets/agent-sessions/wagtail/staged.json) observed initial loads of 944.5–945.5 KB for the homepage and 590.7–591.3 KB for the statement across accept/reject branches. Scroll totals reached 1.108–1.109 MB and 633.7–634.3 KB. All remain partial; no DCR was calculated. These are separate repeated captures, and do not replace the inputs of the annual scenario above.

- **Carbon.txt:** the root file returns 200 and declares version 0.4, four disclosures and four upstream service relationships. The [normalized interpretation](assets/agent-sessions/wagtail/disclosures.json) connects retrieved statements, exact-host declarations, periods and provider roles. Cloudflare, Heroku, AWS and GitHub remain self-declared relationships; none alone verifies renewable hosting. Past reporting validity dates do not invalidate the reports as historical evidence. See [WSG 4.1](https://www.w3.org/TR/web-sustainability-guidelines/#use-sustainable-hosting).
- **Comprehension:** an independent reviewer rediscovered the published arithmetic inconsistency: 5,173 tons across 6,431 sites implies about 0.804 tons per site, not 12. Confirm the intended statistic and population before editing. This also affects comprehensibility under [WSG 2.7](https://www.w3.org/TR/web-sustainability-guidelines/#make-deliverables-understandable-and-reusable), in addition to the footprint-reporting finding above.
- **Print and choices:** print states hide navigation while retaining task content. Both consent buttons have matching measured dimensions and their staged clicks work, but those facts do not establish equal visual prominence or absence of manipulation. Choice and impact-information reviews remain unresolved.
- **Journeys and motion:** the homepage-to-statement selector matched three links, so the collector did not complete the task. Reduced-motion observations also need a specific triggered-animation/control experiment. Neither is reported as a proven site defect.

## Next steps for auditing

The original rubric supports bounded checks in 21/71 guideline groups; this report attempted 17. It has no complete criterion-level guideline coverage. The broader sample covers seven of 525 sitemap-listed content URLs, plus one missing path. The five STAR stages are represented, but selected-page states, complete interactions, non-interference and organizational evidence remain incomplete.

Failed scoped checks concern [script response success](https://www.w3.org/TR/web-sustainability-guidelines/#audit-and-test-for-bugs-or-issues-requiring-resolution), [logo deferral](https://www.w3.org/TR/web-sustainability-guidelines/#defer-the-loading-of-non-critical-resources), [disclosure arithmetic](https://www.w3.org/TR/web-sustainability-guidelines/#calculate-the-environmental-impact), and [privacy-statement scope](https://www.w3.org/TR/web-sustainability-guidelines/#promote-responsible-data-practices). The script error remains contextual rather than a high-priority sustainability recommendation. Unresolved checks concern [font readability](https://www.w3.org/TR/web-sustainability-guidelines/#use-optimized-web-typography), [third-party purposes/preferences](https://www.w3.org/TR/web-sustainability-guidelines/#treat-third-parties-the-same-as-first-parties), and [layout task impact](https://www.w3.org/TR/web-sustainability-guidelines/#ensure-layouts-work-for-different-devices-and-requirements).

1. Complete search/404 recovery and accessible video activation, captions and playback measurements. Broaden page templates, mobile states, keyboard and assistive use; test whether the small overflow disrupts tasks.
2. Obtain the deployed tag inventory and intended preference contract, then test before-choice, accept, reject and returning sessions. Measure text visibility under constrained font loading and validate any logo-deferral experiment.
3. Independently verify partial transfer accounting. Refine the annual estimate with matched-origin analytics and a page/state/revisit mix; perform matched sitespeed.io/co2-runner energy comparisons.
4. Review footprint arithmetic and policy applicability with the owner. Production source identity and internal hosting, retention/deletion, supplier and governance records would enable deeper organizational checks.

See the [coverage roadmap](skill-audit-workflow.md#current-score-and-expected-wsg-coverage) and [ordered backlog](backlog.md). More automation alone cannot establish the missing operational facts or recommendation usefulness.

## Methodology and reproducibility

This WIP audit combines a two-page transfer sample with the separately scoped metadata and preference observations above; it does not establish whole-site WSG conformance. The [staged protocol](staged-auditing.md) records a fresh 1,280 × 800 desktop viewport, no initial interaction, then configured cookie choice and scrolling. All traffic figures use decimal KB/MB (1 KB = 1,000 B). Offscreen resources requested before scrolling remain in the initial figure. Three-second observation windows do not cover all eventual activity.

The [current evidence](assets/staged-audit.json) supports headline measurements. Historical finding IDs refer to the [earlier review evidence](assets/wagtail-review-evidence.json) unless stated otherwise. Earlier tests include warm-cache reuse, mobile observations, JavaScript-disabled behavior, and bounded journeys. Never mix measurements from different captures into a single total.

The [WSG draft](https://www.w3.org/TR/web-sustainability-guidelines/), [STAR](https://w3c.github.io/sustainableweb-ig/docs/star.html), and [impact ratings](https://www.w3.org/TR/wsg-ir/) inform review. The broader sample combines purposeful pages with two reproducibly selected sitemap URLs; it remains a development sample rather than a complete or representative site evaluation. Public statements are claims to corroborate. Unobserved organizational practices remain unknown.

Use the site name and finding ID when correcting an observation, interpretation, priority, or fix. The [feedback-to-pipeline backlog](backlog.md) records follow-up experiments. Run `just audit-sites` for fresh observations and `uv run --locked --script audit/report.py` for per-site chart data. Live recollection will vary.

The current score uses an independent GPT-6.1 Sol/low skill review of the raw artifacts, followed by coordinator inspection and deterministic aggregation. The [skill workflow](skill-audit-workflow.md) records rubric/skill versions, source hashes, review packets and commands. Historical [model comparisons](expanded-benchmark.md) and the [methodology benchmark](methodology-benchmark.md) are separate development evaluations. This report is not a validated autonomous conformance audit; source excerpts locate candidate fixes without proving deployment identity.

To recalculate from published evidence, run `uv run --locked --script audit/assess.py`, `uv run --locked --script audit/annual.py`, then `uv run --locked --script audit/report.py`. The annual calculator uses CO2.js 0.19.0/SWDM v4 and the pinned September 2026 rank dataset/mapping; its output records input and dependency hashes. New live observations or LLM judgments require a new campaign, rather than silently changing this score’s evidence.

The expanded pilot preserves its [plan](assets/agent-sessions/wagtail/plan.json), [command receipt](assets/agent-sessions/wagtail/receipt.json), [evidence manifest](assets/agent-sessions/wagtail/manifest.json), raw observations and exact review inputs. Separate Sol/low reviewers used frozen skills without reading earlier report conclusions. The public packet omits private logs and skill copies but preserves their hashes; deterministic scores can be reproduced using the commands in the [agent workflow](agent-driven-audits.md#pilot-reproduction). No GreenFrame result or new paired-model benchmark is claimed.
