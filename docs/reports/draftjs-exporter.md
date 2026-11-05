# Draft.js exporter for Python (draftjs_exporter): sustainability audit

**Audit scope:** [https://wagtail.github.io/draftjs_exporter/](https://wagtail.github.io/draftjs_exporter/). Findings apply to this service and its sampled pages, not other projects on the same host.

## At a glance

<div class="grid cards" markdown="1">

- **33.3/100** — scoped audit score<br>8 passing, 2 with problems, 14 needing more evidence.
- **7 pages** reviewed<br>1 visitor journey; public-site evidence.
- **24 of 71 guideline groups** scored<br>45 untested; 2 not applicable. Tests cover selected aspects of each guideline.

</div>

This public-site audit covers seven selected Draft.js exporter documentation pages under /draftjs_exporter/ and a search-to-installation task. Other projects on `wagtail.github.io` are outside scope. Seven initial loads were attempted; five succeeded with incomplete transfer accounting. Failed loads are unavailable, and carbon ratings are withheld. Missing page states and interaction evidence limit the scoped score and leave substantial uncertainty.

The clearest small fix is to correct sitemap requests from four nested pages that return 404. The observed setup task successfully reached installation and a complete first-render example without account or payment barriers. System fonts, a small shared logo, compression and cache policies are useful strengths; search-index deferral still needs investigation.

## Results by WSG area

<div class="audit-table-scroll" tabindex="0" role="region" aria-label="Selected checks by WSG area">
<table>
<caption>Selected checks by WSG area</caption>
<thead><tr><th scope="col">Area</th><th scope="col">Passing</th><th scope="col">Guideline groups checked</th><th scope="col">Needs evidence</th></tr></thead>
<tbody>
<tr><th scope="row"><a href="#findings-2">User experience design</a></th><td>45% (5/11)</td><td>11 of 17</td><td>6</td></tr>
<tr><th scope="row"><a href="#findings-3">Web development</a></th><td>12% (1/8)</td><td>8 of 16</td><td>5</td></tr>
<tr><th scope="row"><a href="#findings-4">Hosting, infrastructure and systems</a></th><td>67% (2/3)</td><td>3 of 12</td><td>1</td></tr>
<tr><th scope="row"><a href="#findings-5">Business strategy and product management</a></th><td>0% (0/2)</td><td>2 of 26</td><td>2</td></tr>
</tbody></table></div>

Passing percentages apply to the selected checks. Full-guideline conformance has not been established.

## Page measurements

<div class="audit-table-scroll" tabindex="0" role="region" aria-label="Page measurements">
<table>
<caption>Page measurements</caption>
<thead><tr><th scope="col">Page</th><th scope="col"><a href="#measure-first-load">First load</a></th><th scope="col"><a href="#measure-after-choice">After waiting</a></th><th scope="col"><a href="#measure-scroll">After scrolling</a></th><th scope="col"><a href="#measure-carbon">Estimated footprint</a></th><th scope="col"><a href="#measure-carbon">Carbon rating</a></th><th scope="col"><a href="#measure-energy">Browser energy</a></th><th scope="col"><a href="#measure-energy">Network energy</a></th></tr></thead>
<tbody>
<tr><th scope="row"><a href="https://wagtail.github.io/draftjs_exporter/">Draft.js exporter for Python (draftjs_exporter)</a></th><td>142.7 kB · <a href="#measure-completeness">partial</a></td><td>142.7 kB · <a href="#measure-completeness">partial</a></td><td>142.7 kB · <a href="#measure-completeness">partial</a></td><td>Withheld</td><td>Withheld</td><td>11.42 mWh</td><td>2.06 mWh</td></tr>
<tr><th scope="row"><a href="https://wagtail.github.io/draftjs_exporter/getting-started/">Getting started</a></th><td>Unavailable (navigation failed)</td><td>Unavailable (navigation failed)</td><td>Unavailable (navigation failed)</td><td>Withheld</td><td>Withheld</td><td>Not sampled</td><td>Not sampled</td></tr>
<tr><th scope="row"><a href="https://wagtail.github.io/draftjs_exporter/content-state/">Content state</a></th><td>148.3 kB · <a href="#measure-completeness">partial</a></td><td>148.3 kB · <a href="#measure-completeness">partial</a></td><td>148.3 kB · <a href="#measure-completeness">partial</a></td><td>Withheld</td><td>Withheld</td><td>Not sampled</td><td>Not sampled</td></tr>
<tr><th scope="row"><a href="https://wagtail.github.io/draftjs_exporter/reference/configuration/">Configuration</a></th><td>147.3 kB · <a href="#measure-completeness">partial</a></td><td>147.3 kB · <a href="#measure-completeness">partial</a></td><td>147.3 kB · <a href="#measure-completeness">partial</a></td><td>Withheld</td><td>Withheld</td><td>Not sampled</td><td>Not sampled</td></tr>
<tr><th scope="row"><a href="https://wagtail.github.io/draftjs_exporter/reference/api/">API</a></th><td>190.1 kB · <a href="#measure-completeness">partial</a></td><td>190.1 kB · <a href="#measure-completeness">partial</a></td><td>190.1 kB · <a href="#measure-completeness">partial</a></td><td>Withheld</td><td>Withheld</td><td>Not sampled</td><td>Not sampled</td></tr>
<tr><th scope="row"><a href="https://wagtail.github.io/draftjs_exporter/guides/alternative-engines/">Alternative engines</a></th><td>145.2 kB · <a href="#measure-completeness">partial</a></td><td>145.2 kB · <a href="#measure-completeness">partial</a></td><td>145.2 kB · <a href="#measure-completeness">partial</a></td><td>Withheld</td><td>Withheld</td><td>Not sampled</td><td>Not sampled</td></tr>
<tr><th scope="row"><a href="https://wagtail.github.io/draftjs_exporter/migration-guide/">Migration guide</a></th><td>Unavailable (navigation failed)</td><td>Unavailable (navigation failed)</td><td>Unavailable (navigation failed)</td><td>Withheld</td><td>Withheld</td><td>Not sampled</td><td>Not sampled</td></tr>
</tbody></table></div>

## Estimated annual footprint

Annual impact is unavailable: CrUX ranks describe the whole origin, including other projects. Pageviews for this audited path are unknown. Obtain traffic limited to this service before projecting either SWDM emissions or client electricity.

## Priorities

### 1. Resolve sitemap requests from nested documentation pages

<div class="audit-finding" markdown="1">

**Low priority** · Problem found · <a class="audit-guideline" href="https://www.w3.org/TR/web-sustainability-guidelines/#use-sustainable-javascript-and-apis" title="Write efficient JavaScript and use APIs that minimize processing, data use, and energy consumption.">WSG 3.11: Use sustainable JavaScript and APIs</a>

**What we found.** The root sitemap at /draftjs_exporter/sitemap.xml returns XML with HTTP 200. Four nested pages—Content state, configuration, API and alternative engines—each request their own page-relative sitemap.xml and receive roughly 3.9 kB of 404 HTML. This is a small, observed request-path defect.

**Why it matters.** These completed error responses transfer data without supplying the requested sitemap. The evidence does not quantify backend cost, emissions savings or an effect on task completion, so this is a low-priority repair.

**Next step.** Resolve the sitemap URL against the documentation root. Verify that home and all four nested pages retrieve the intended XML and that useful search and release requests still work.

[How we checked this: Resolve sitemap requests from nested documentation pages](#evidence-api-requests)

</div>

### 2. Check whether deferring the search index improves first load

<div class="audit-finding" markdown="1">

**Low priority** · Needs investigation · <a class="audit-guideline" href="https://www.w3.org/TR/web-sustainability-guidelines/#modularize-bandwidth-heavy-components" title="Split large components into smaller, on-demand modules to improve loading efficiency while balancing maintainability and caching performance.">WSG 3.3: Modularize bandwidth-heavy components</a>

**What we found.** The successful homepage run loads a roughly 64 kB compressed search index during initial loading. Search was useful in the completed setup task. The audit has not demonstrated safe on-demand activation, and search-worker transfer accounting is incomplete.

**Why it matters.** Deferral could change when data is loaded, but its value depends on actual search use and result readiness. The captured index size does not establish removable bytes or an achievable saving.

**Next step.** Treat this as a low-priority investigation if first-load transfer matters. Compare on-demand activation with current behavior under matched conditions, including immediate typing, complete worker accounting, offline search and responsiveness. Adopt a change only after showing a useful measured improvement.

[How we checked this: Check whether deferring the search index improves first load](#evidence-components)

</div>

### 3. Document release-linked review of useful migration guidance

<div class="audit-finding" markdown="1">

**Low priority** · Needs investigation · <a class="audit-guideline" href="https://www.w3.org/TR/web-sustainability-guidelines/#promote-responsible-data-practices" title="Respect user data rights and manage data lifecycle through minimized collection, user control, portability, deletion, and content archiving.">WSG 5.18: Promote responsible data practices</a>

**What we found.** The migration guide provides concrete compatibility advice and retained upgrade paths. The captured public material does not identify an explicit review schedule, responsible owner or applied review record.

**Why it matters.** A lightweight release-linked review record would help maintainers keep current advice accurate while retaining instructions that readers on older versions still need. The evidence gap does not establish absent maintenance.

**Next step.** Record who reviews documentation with a release, when that review is due, and one actual review decision. Preserve historical upgrade guidance and label its relationship to current configuration. This is low-priority follow-up.

[How we checked this: Document release-linked review of useful migration guidance](#evidence-content-lifecycle)

</div>

## Further checks

These outcomes apply to the selected checks and sample. Open a check's explanation for the observation, limitations and useful follow-up.

??? note "Browse all check outcomes"

    <div class="audit-table-scroll" tabindex="0" role="region" aria-label="All selected check outcomes">
    <table>
    <caption>All selected check outcomes</caption>
    <thead><tr><th scope="col">Check</th><th scope="col">Outcome</th></tr></thead>
    <tbody>
    <tr><th scope="row"><a href="#evidence-distraction">Check the remaining reading states for interruptions</a></th><td><span aria-hidden="true">❓</span> Needs investigation</td></tr>
    <tr><th scope="row"><a href="#evidence-choice">No consequential accept-or-reject choice was in scope</a></th><td><span aria-hidden="true">➖</span> Not relevant here</td></tr>
    <tr><th scope="row"><a href="#evidence-comprehension">Keep the direct route from purpose to working example</a></th><td><span aria-hidden="true">✅</span> Passed this check</td></tr>
    <tr><th scope="row"><a href="#evidence-consistency">Keep shared navigation names consistent</a></th><td><span aria-hidden="true">✅</span> Passed this check</td></tr>
    <tr><th scope="row"><a href="#evidence-motion">Check motion during the missing states and interactions</a></th><td><span aria-hidden="true">❓</span> Needs investigation</td></tr>
    <tr><th scope="row"><a href="#evidence-notifications">Complete the check for unsolicited alerts</a></th><td><span aria-hidden="true">❓</span> Needs investigation</td></tr>
    <tr><th scope="row"><a href="#evidence-documents">Inspect a real print preview before changing print styles</a></th><td><span aria-hidden="true">❓</span> Needs investigation</td></tr>
    <tr><th scope="row"><a href="#evidence-unused-code">Exercise interactive features before removing code</a></th><td><span aria-hidden="true">❓</span> Needs investigation</td></tr>
    <tr><th scope="row"><a href="#evidence-components">Check whether search-index deferral would help readers</a></th><td><span aria-hidden="true">❓</span> Needs investigation</td></tr>
    <tr><th scope="row"><a href="#evidence-layout">Exercise search and navigation at narrow widths</a></th><td><span aria-hidden="true">❓</span> Needs investigation</td></tr>
    <tr><th scope="row"><a href="#evidence-impact-choice">No consequential environmental choice was established</a></th><td><span aria-hidden="true">➖</span> Not relevant here</td></tr>
    <tr><th scope="row"><a href="#evidence-journeys">The observed search-to-installation task completed</a></th><td><span aria-hidden="true">✅</span> Passed this check</td></tr>
    <tr><th scope="row"><a href="#evidence-media-delivery">Keep the small shared logo proportionate</a></th><td><span aria-hidden="true">✅</span> Passed this check</td></tr>
    <tr><th scope="row"><a href="#evidence-font-delivery">Retain readable system-font delivery</a></th><td><span aria-hidden="true">✅</span> Passed this check</td></tr>
    <tr><th scope="row"><a href="#evidence-semantic-forms">Keep meaningful page structure and control names</a></th><td><span aria-hidden="true">✅</span> Passed this check</td></tr>
    <tr><th scope="row"><a href="#evidence-metadata">Maintain descriptive metadata for published documentation paths</a></th><td><span aria-hidden="true">✅</span> Passed this check</td></tr>
    <tr><th scope="row"><a href="#evidence-preference-behavior">Establish the intended theme behavior</a></th><td><span aria-hidden="true">❓</span> Needs investigation</td></tr>
    <tr><th scope="row"><a href="#evidence-no-js-content">Complete the no-JavaScript reading comparison</a></th><td><span aria-hidden="true">❓</span> Needs investigation</td></tr>
    <tr><th scope="row"><a href="#evidence-api-requests">Resolve sitemap requests from nested documentation pages</a></th><td><span aria-hidden="true">❌</span> Problem found</td></tr>
    <tr><th scope="row"><a href="#evidence-public-cache-policy">Retain the observed public caching and validation policy</a></th><td><span aria-hidden="true">✅</span> Passed this check</td></tr>
    <tr><th scope="row"><a href="#evidence-text-compression">Keep compression on successful text responses</a></th><td><span aria-hidden="true">✅</span> Passed this check</td></tr>
    <tr><th scope="row"><a href="#evidence-keyboard-path">Verify focus through search and the complete task</a></th><td><span aria-hidden="true">❓</span> Needs investigation</td></tr>
    <tr><th scope="row"><a href="#evidence-disclosure-scope">Identify any exporter-specific impact statement</a></th><td><span aria-hidden="true">❓</span> Needs investigation</td></tr>
    <tr><th scope="row"><a href="#evidence-carbon-discovery">Coordinate carbon.txt discovery with the origin owner if useful</a></th><td><span aria-hidden="true">❌</span> Problem found</td></tr>
    <tr><th scope="row"><a href="#evidence-hosting-evidence">Match hosting claims to this documentation service</a></th><td><span aria-hidden="true">❓</span> Needs investigation</td></tr>
    <tr><th scope="row"><a href="#evidence-service-necessity">Document the bounded decision to maintain the exporter capability</a></th><td><span aria-hidden="true">❓</span> Needs investigation</td></tr>
    <tr><th scope="row"><a href="#evidence-access-barriers">Keep installation guidance openly reachable</a></th><td><span aria-hidden="true">✅</span> Passed this check</td></tr>
    <tr><th scope="row"><a href="#evidence-content-lifecycle">Record review of useful migration and compatibility guidance</a></th><td><span aria-hidden="true">❓</span> Needs investigation</td></tr>
    </tbody></table></div>

## Next steps for auditing

1. Complete missing paired normal, narrow, preference and no-JavaScript states, especially the API and configuration reading comparisons. Treat navigation transport errors as unavailable observations.
2. Verify visible focus and the complete keyboard search-to-installation route; exercise narrow menu and search controls and check long code content in a real mobile task if device coverage is required.
3. Obtain complete search-worker transfer accounting and clean linked initial visits before comparing page weights, assigning carbon ratings or evaluating a search-loading change. Repeat the automated installation route if measured completion and timing are needed.
4. If further owner context would be useful, add represented-user research, one bounded exporter continuation decision, and a release-linked documentation review rule with an applied maintenance record. Retain useful historical upgrade guidance.
5. For any future annual project estimate, obtain path-specific visits or an evidenced origin-to-project allocation; keep transfer-based emissions and separately modeled client energy distinct.
6. The audit checks selected aspects of 24 of 71 guideline groups; full criteria and STAR conformance remain outside this review. Broaden qualitative coverage beyond the selected service, access and lifecycle checks using public records or concrete owner examples.

The sample covers selected pages and visitor tasks, not every page on the site. Expand it where the checks above identify an untested template, interaction or audience need.

## Detailed findings

This appendix explains the evidence in ordinary language. This audit used public-site evidence without a source checkout. Unavailable documents or internal records do not establish that the organization has none.

### User experience design {#findings-2}

<h4 id="evidence-distraction">Check the remaining reading states for interruptions</h4>

**Needs investigation** · <a class="audit-guideline" href="https://www.w3.org/TR/web-sustainability-guidelines/#design-to-assist-and-not-to-distract" title="Give users control over notifications and focus, prioritize task-relevant content, and avoid designs that distract or unnecessarily extend engagement.">WSG 2.5: Design to assist and not to distract</a>

_Give users control over notifications and focus, prioritize task-relevant content, and avoid designs that distract or unnecessarily extend engagement._

The captured installation, Content state, API and migration reading states show no autoplay or active animation. Search supports documentation discovery, and the completed installation walkthrough encountered no extra account or payment steps. Missing normal page observations prevent a conclusion across the full sample.

**Next step:** Capture the missing normal reading states, then check whether any prompts interrupt the documentation task.

**Where we looked:**

- Browser observations for [Getting started](https://wagtail.github.io/draftjs_exporter/getting-started/).
- Browser observations for [Content state](https://wagtail.github.io/draftjs_exporter/content-state/).
- Browser observations for [Api](https://wagtail.github.io/draftjs_exporter/reference/api/).
- Browser observations for [Migration guide](https://wagtail.github.io/draftjs_exporter/migration-guide/).
- Recorded visitor task starting at [Draftjs_exporter](https://wagtail.github.io/draftjs_exporter/).

<h4 id="evidence-choice">No consequential accept-or-reject choice was in scope</h4>

**Not relevant here** · <a class="audit-guideline" href="https://www.w3.org/TR/web-sustainability-guidelines/#avoid-being-manipulative-or-deceptive" title="Avoid deceptive patterns, clearly label ads, respect consent for tracking, and ensure search, sharing, and discoverability practices prioritize user needs over optimization or manipulation.">WSG 2.6: Avoid being manipulative or deceptive</a>

_Avoid deceptive patterns, clearly label ads, respect consent for tracking, and ensure search, sharing, and discoverability practices prioritize user needs over optimization or manipulation._

The sampled task involves reading and search, with no observed consent, subscription, purchase or personal-data submission choice. Technical engine recommendations do not create a comparable transaction choice.

**Next step:** Review wording, defaults and visual prominence if consequential consent or payment choices are introduced.

**Where we looked:**

- Recorded visitor task starting at [Draftjs_exporter](https://wagtail.github.io/draftjs_exporter/).
- Captured public evidence for [Draftjs_exporter](https://wagtail.github.io/draftjs_exporter/).
- Browser observations for [Content state](https://wagtail.github.io/draftjs_exporter/content-state/).

<h4 id="evidence-comprehension">Keep the direct route from purpose to working example</h4>

**Passed this check** · <a class="audit-guideline" href="https://www.w3.org/TR/web-sustainability-guidelines/#make-deliverables-understandable-and-reusable" title="Create discoverable, maintainable, and reusable documentation and code resources that support long-term understanding, reuse, and sustainability.">WSG 2.7: Make deliverables understandable and reusable</a>

_Create discoverable, maintainable, and reusable documentation and code resources that support long-term understanding, reuse, and sustainability._

The homepage explains Python ContentState-to-HTML conversion and points newcomers to Content state and Getting started. Installation includes the package command and complete first-render example; engine and migration guidance explain concrete tradeoffs and upgrade actions. This supports the sampled Python-developer audience.

**Next step:** If the audience broadens, check these explanations with developers unfamiliar with Draft.js and its data model.

**Where we looked:**

- Recorded visitor task starting at [Draftjs_exporter](https://wagtail.github.io/draftjs_exporter/).
- Captured public evidence for [Draftjs_exporter](https://wagtail.github.io/draftjs_exporter/).
- Captured public evidence for [Alternative engines](https://wagtail.github.io/draftjs_exporter/guides/alternative-engines/).
- Captured public evidence for [Migration guide](https://wagtail.github.io/draftjs_exporter/migration-guide/).
- Browser observations for [Content state](https://wagtail.github.io/draftjs_exporter/content-state/).
- Browser observations for [Configuration](https://wagtail.github.io/draftjs_exporter/reference/configuration/).
- Browser observations for [Api](https://wagtail.github.io/draftjs_exporter/reference/api/).

<h4 id="evidence-consistency">Keep shared navigation names consistent</h4>

**Passed this check** · <a class="audit-guideline" href="https://www.w3.org/TR/web-sustainability-guidelines/#use-a-design-system-for-interface-consistency" title="Use design systems and established patterns to ensure consistent, efficient, and sustainable interfaces through reusable components and clear maintenance practices.">WSG 2.8: Use a design system for interface consistency</a>

_Use design systems and established patterns to ensure consistent, efficient, and sustainable interfaces through reusable components and clear maintenance practices._

Clean captured states across the seven pages use shared navigation names and consistent Search and Clear controls. This supports consistency within the sample; it does not establish a documented design system or every interaction state.

**Next step:** Use the existing navigation names and control labels when extending the documentation.

**Where we looked:**

- Browser observations for [Getting started](https://wagtail.github.io/draftjs_exporter/getting-started/).
- Browser observations for [Content state](https://wagtail.github.io/draftjs_exporter/content-state/).
- Browser observations for [Api](https://wagtail.github.io/draftjs_exporter/reference/api/).
- Browser observations for [Migration guide](https://wagtail.github.io/draftjs_exporter/migration-guide/).
- Browser observations for [Configuration](https://wagtail.github.io/draftjs_exporter/reference/configuration/).
- Browser observations for [Draftjs_exporter](https://wagtail.github.io/draftjs_exporter/).
- Browser observations for [Alternative engines](https://wagtail.github.io/draftjs_exporter/guides/alternative-engines/).

<h4 id="evidence-motion">Check motion during the missing states and interactions</h4>

**Needs investigation** · <a class="audit-guideline" href="https://www.w3.org/TR/web-sustainability-guidelines/#ensure-animation-is-proportionate-and-easy-to-control" title="Use animation sparingly and efficiently, only when it supports understanding, while limiting performance impact and giving users control over motion.">WSG 2.10: Ensure animation is proportionate and easy to control</a>

_Use animation sparingly and efficiently, only when it supports understanding, while limiting performance impact and giving users control over motion._

No active animation or media playback appears in the successful desktop, narrow and reduced-motion reading observations. Short quiet observations and missing normal page states leave transitions and later interactions unresolved.

**Next step:** Complete the missing normal states and exercise any actual motion before judging its purpose, controls or reduced-motion behavior.

**Where we looked:**

- Browser observations for [Getting started](https://wagtail.github.io/draftjs_exporter/getting-started/).
- Browser observations for [Content state](https://wagtail.github.io/draftjs_exporter/content-state/).
- Browser observations for [Api](https://wagtail.github.io/draftjs_exporter/reference/api/).
- Browser observations for [Migration guide](https://wagtail.github.io/draftjs_exporter/migration-guide/).

<h4 id="evidence-notifications">Complete the check for unsolicited alerts</h4>

**Needs investigation** · <a class="audit-guideline" href="https://www.w3.org/TR/web-sustainability-guidelines/#avoid-unwanted-notifications" title="Send only user-requested notifications and provide clear, accessible controls for managing preferences, opt-in, and account and contact settings.">WSG 2.12: Avoid unwanted notifications</a>

_Send only user-requested notifications and provide clear, accessible controls for managing preferences, opt-in, and account and contact settings._

The observed states recorded no notification permission requests or unsolicited notification flow. Permission was denied in the browser, and some normal page observations are missing, so this does not cover every possible notification state.

**Next step:** Check alerts and permission requests in the remaining normal states and document their user purpose if any appear.

**Where we looked:**

- Browser observations for [Getting started](https://wagtail.github.io/draftjs_exporter/getting-started/).
- Browser observations for [Content state](https://wagtail.github.io/draftjs_exporter/content-state/).
- Browser observations for [Api](https://wagtail.github.io/draftjs_exporter/reference/api/).
- Browser observations for [Migration guide](https://wagtail.github.io/draftjs_exporter/migration-guide/).

<h4 id="evidence-documents">Inspect a real print preview before changing print styles</h4>

**Needs investigation** · <a class="audit-guideline" href="https://www.w3.org/TR/web-sustainability-guidelines/#reduce-the-impact-of-downloadable-and-physical-documents" title="Reduce paper use through digital-first workflows, optimize and reuse accessible downloadable documents, and provide clear, user-controlled document previews and formats.">WSG 2.13: Reduce the impact of downloadable and physical documents</a>

_Reduce paper use through digital-first workflows, optimize and reuse accessible downloadable documents, and provide clear, user-controlled document previews and formats._

No downloadable document links were recorded in the observed states. Print emulation preserves installation text and removes its navigation, while API and migration states retain navigation regions. Without a paginated preview, these regions do not establish wasted pages, clipping or duplication.

**Next step:** Inspect API and migration print previews with real content, checking code and upgrade steps before adjusting print styles.

**Where we looked:**

- Browser observations for [Getting started](https://wagtail.github.io/draftjs_exporter/getting-started/).
- Browser observations for [Content state](https://wagtail.github.io/draftjs_exporter/content-state/).
- Browser observations for [Api](https://wagtail.github.io/draftjs_exporter/reference/api/).
- Browser observations for [Migration guide](https://wagtail.github.io/draftjs_exporter/migration-guide/).

<h4 id="evidence-journeys">The observed search-to-installation task completed</h4>

**Passed this check** · <a class="audit-guideline" href="https://www.w3.org/TR/web-sustainability-guidelines/#design-efficient-and-streamlined-user-journeys" title="Design clear, efficient journeys that help users complete tasks and find content with minimal effort.">WSG 2.4: Design efficient and streamlined user journeys</a>

_Design clear, efficient journeys that help users complete tasks and find content with minimal effort._

The timestamped setup walkthrough entered getting started in search, selected its result and reached the installation command plus complete first-render example. The later automated measurement stopped at initial navigation with ERR_NETWORK_CHANGED before any search action, leaving measured timing and completion unavailable.

**Next step:** Repeat the same route in a clean linked measurement if completion reliability or timing is needed; keep navigation transport errors distinct from search behavior.

**Where we looked:**

- Recorded visitor task starting at [Draftjs_exporter](https://wagtail.github.io/draftjs_exporter/).
- Browser observations for [Draftjs_exporter](https://wagtail.github.io/draftjs_exporter/).

<h4 id="evidence-media-delivery">Keep the small shared logo proportionate</h4>

**Passed this check** · <a class="audit-guideline" href="https://www.w3.org/TR/web-sustainability-guidelines/#optimize-media-to-reduce-resource-use" title="Include media only when it supports user needs. Manage, optimize, and load media efficiently. Ensure users have control over playback and data use.">WSG 2.9: Optimize media to reduce resource use</a>

_Include media only when it supports user needs. Manage, optimize, and load media efficiently. Ensure users have control over playback and data use._

Clean reading states use the same small PNG logo without heavy article images or video. The observed logo is a modest shared resource; the absence of responsive image variants does not establish a worthwhile optimization.

**Next step:** Check any future article images at their intended display sizes and pixel densities. The present logo is a low-value optimization target.

**Where we looked:**

- Browser observations for [Getting started](https://wagtail.github.io/draftjs_exporter/getting-started/).
- Browser observations for [Content state](https://wagtail.github.io/draftjs_exporter/content-state/).
- Browser observations for [Api](https://wagtail.github.io/draftjs_exporter/reference/api/).
- Captured public evidence for [Draftjs_exporter](https://wagtail.github.io/draftjs_exporter/).
- Browser observations for [Draftjs_exporter](https://wagtail.github.io/draftjs_exporter/).
- Browser observations for [Configuration](https://wagtail.github.io/draftjs_exporter/reference/configuration/).
- Browser observations for [Alternative engines](https://wagtail.github.io/draftjs_exporter/guides/alternative-engines/).
- Browser observations for [Migration guide](https://wagtail.github.io/draftjs_exporter/migration-guide/).

<h4 id="evidence-font-delivery">Retain readable system-font delivery</h4>

**Passed this check** · <a class="audit-guideline" href="https://www.w3.org/TR/web-sustainability-guidelines/#use-optimized-web-typography" title="Use font strategies that minimize downloads and complexity while supporting required languages and dynamic content.">WSG 2.11: Use optimized web typography</a>

_Use font strategies that minimize downloads and complexity while supporting required languages and dynamic content._

Observed typography uses system fonts with Helvetica, Arial and sans-serif fallbacks. FontFace lists are empty and the successful homepage resource sample contains no web-font responses, supporting delivery without external font downloads for the sampled English text.

**Next step:** Check fallback readability and character coverage if supported languages or typography requirements change.

**Where we looked:**

- Browser observations for [Draftjs_exporter](https://wagtail.github.io/draftjs_exporter/).
- Browser observations for [Getting started](https://wagtail.github.io/draftjs_exporter/getting-started/).
- Browser observations for [Content state](https://wagtail.github.io/draftjs_exporter/content-state/).
- Browser observations for [Api](https://wagtail.github.io/draftjs_exporter/reference/api/).
- Captured public evidence for [Draftjs_exporter](https://wagtail.github.io/draftjs_exporter/).

<h4 id="evidence-no-js-content">Complete the no-JavaScript reading comparison</h4>

**Needs investigation** · <a class="audit-guideline" href="https://www.w3.org/TR/web-sustainability-guidelines/#provide-cross-platform-compatibility-support" title="Document compatibility, avoid unnecessary obsolescence, and test across devices, systems, and network conditions.">WSG 2.17: Provide cross-platform compatibility support</a>

_Document compatibility, avoid unnecessary obsolescence, and test across devices, systems, and network conditions._

Fresh no-JavaScript states retain reading text, headings and navigation for home, installation, Content state, alternative engines and migration. Configuration and API navigations encountered ERR_NETWORK_CHANGED, leaving those comparisons unavailable rather than demonstrating a JavaScript dependency.

**Next step:** Capture clean no-JavaScript configuration and API pages and compare their full reading content and navigation with matching normal states.

**Where we looked:**

- Browser observations for [Draftjs_exporter](https://wagtail.github.io/draftjs_exporter/).
- Browser observations for [Getting started](https://wagtail.github.io/draftjs_exporter/getting-started/).
- Browser observations for [Content state](https://wagtail.github.io/draftjs_exporter/content-state/).
- Browser observations for [Configuration](https://wagtail.github.io/draftjs_exporter/reference/configuration/).
- Browser observations for [Api](https://wagtail.github.io/draftjs_exporter/reference/api/).
- Browser observations for [Alternative engines](https://wagtail.github.io/draftjs_exporter/guides/alternative-engines/).
- Browser observations for [Migration guide](https://wagtail.github.io/draftjs_exporter/migration-guide/).

<h4 id="evidence-disclosure-scope">Identify any exporter-specific impact statement</h4>

**Needs investigation** · <a class="audit-guideline" href="https://www.w3.org/TR/web-sustainability-guidelines/#identify-assess-disclose-review-and-mitigate-sustainability-impacts" title="Assess and report the planet, people, and prosperity impacts of digital projects, and plan measurable reductions to the real-world effects of their activity.">WSG 2.1: Identify, assess, disclose, review, and mitigate sustainability impacts</a>

_Assess and report the planet, people, and prosperity impacts of digital projects, and plan measurable reductions to the real-world effects of their activity._

The homepage explains the library purpose but supplies no captured sustainability impact or mitigation statement. Bounded origin discovery also found no usable statement at its sampled routes. This leaves a service-linked disclosure unresolved and does not establish that no policy exists elsewhere.

**Next step:** If disclosure is intended, provide a public statement explicitly covering /draftjs_exporter/ and explaining its web-service impact and mitigation scope.

**Where we looked:**

- Disclosure discovery for the origin `https://wagtail.github.io`.
- Captured public evidence for [Draftjs_exporter](https://wagtail.github.io/draftjs_exporter/).

### Web development {#findings-3}

<h4 id="evidence-unused-code">Exercise interactive features before removing code</h4>

**Needs investigation** · <a class="audit-guideline" href="https://www.w3.org/TR/web-sustainability-guidelines/#minify-and-remove-unused-code" title="Minify code and data, and remove unused characters to reduce file size and improve loading efficiency and maintainability.">WSG 3.2: Minify and remove unused code</a>

_Minify code and data, and remove unused characters to reduce file size and improve loading efficiency and maintainability._

Initial-load coverage includes unexecuted JavaScript ranges and unused CSS rules. These source positions do not represent removable download bytes, and later search, navigation and code-copy tasks were not covered sufficiently to justify removal.

**Next step:** Capture representative search, navigation and code-copy interactions and establish which code they need before proposing a smaller bundle.

**Where we looked:**

- Browser observations for [Content state](https://wagtail.github.io/draftjs_exporter/content-state/).
- Browser observations for [Api](https://wagtail.github.io/draftjs_exporter/reference/api/).
- Browser observations for [Migration guide](https://wagtail.github.io/draftjs_exporter/migration-guide/).
- Captured public evidence for [Draftjs_exporter](https://wagtail.github.io/draftjs_exporter/).

<h4 id="evidence-components">Check whether search-index deferral would help readers</h4>

**Needs investigation** · <a class="audit-guideline" href="https://www.w3.org/TR/web-sustainability-guidelines/#modularize-bandwidth-heavy-components" title="Split large components into smaller, on-demand modules to improve loading efficiency while balancing maintainability and caching performance.">WSG 3.3: Modularize bandwidth-heavy components</a>

_Split large components into smaller, on-demand modules to improve loading efficiency while balancing maintainability and caching performance._

The homepage initially loads a roughly 64 kB compressed search index alongside the documentation bundle. Search successfully supported the setup task. Incomplete worker transfer accounting and the absence of a tested on-demand alternative leave safe deferral and any savings unproven.

**Next step:** If first-load transfer is a priority, compare search activation and immediate typing under matched conditions with complete worker accounting; check result readiness, offline search and responsiveness before adopting a change.

**Where we looked:**

- Captured public evidence for [Draftjs_exporter](https://wagtail.github.io/draftjs_exporter/).
- Browser observations for [Content state](https://wagtail.github.io/draftjs_exporter/content-state/).
- Recorded visitor task starting at [Draftjs_exporter](https://wagtail.github.io/draftjs_exporter/).

<h4 id="evidence-layout">Exercise search and navigation at narrow widths</h4>

**Needs investigation** · <a class="audit-guideline" href="https://www.w3.org/TR/web-sustainability-guidelines/#ensure-layouts-work-for-different-devices-and-requirements" title="Use responsive, progressively enhanced, and carbon-aware design to ensure accessible, adaptable functionality across devices and interaction methods while managing resource use.">WSG 3.10: Ensure layouts work for different devices and requirements</a>

_Use responsive, progressively enhanced, and carbon-aware design to ensure accessible, adaptable functionality across devices and interaction methods while managing resource use._

Captured installation, Content state, API and migration pages retain their headings and reading content without reported document overflow at desktop and narrow widths. Narrow menu and search controls were not exercised, and paired states are missing for some pages.

**Next step:** Complete desktop/narrow comparisons, exercise narrow navigation and search, and inspect long API and code content; use a real mobile task before making device-compatibility claims.

**Where we looked:**

- Browser observations for [Getting started](https://wagtail.github.io/draftjs_exporter/getting-started/).
- Browser observations for [Content state](https://wagtail.github.io/draftjs_exporter/content-state/).
- Browser observations for [Api](https://wagtail.github.io/draftjs_exporter/reference/api/).
- Browser observations for [Migration guide](https://wagtail.github.io/draftjs_exporter/migration-guide/).

<h4 id="evidence-semantic-forms">Keep meaningful page structure and control names</h4>

**Passed this check** · <a class="audit-guideline" href="https://www.w3.org/TR/web-sustainability-guidelines/#ensure-code-follows-good-semantic-practices" title="Use standards-compliant HTML and web platform features, and avoid unnecessary complexity or non-standard code.">WSG 3.6: Ensure code follows good semantic practices</a>

_Use standards-compliant HTML and web platform features, and avoid unnecessary complexity or non-standard code._

Each sampled page has at least one clean state with English language metadata, one main region and a descriptive primary heading. Search and Clear have explicit labels, navigation sections are named, and copy buttons have a Copy to clipboard title. This bounded structure-and-naming check is not a full accessibility assessment.

**Next step:** For a broader assessment, verify copy-control names in the accessibility tree and inspect the API heading hierarchy and complete interactions.

**Where we looked:**

- Browser observations for [Draftjs_exporter](https://wagtail.github.io/draftjs_exporter/).
- Browser observations for [Getting started](https://wagtail.github.io/draftjs_exporter/getting-started/).
- Browser observations for [Content state](https://wagtail.github.io/draftjs_exporter/content-state/).
- Browser observations for [Configuration](https://wagtail.github.io/draftjs_exporter/reference/configuration/).
- Browser observations for [Api](https://wagtail.github.io/draftjs_exporter/reference/api/).
- Browser observations for [Alternative engines](https://wagtail.github.io/draftjs_exporter/guides/alternative-engines/).
- Browser observations for [Migration guide](https://wagtail.github.io/draftjs_exporter/migration-guide/).

<h4 id="evidence-metadata">Maintain descriptive metadata for published documentation paths</h4>

**Passed this check** · <a class="audit-guideline" href="https://www.w3.org/TR/web-sustainability-guidelines/#structure-metadata-for-machine-readability" title="Include essential document metadata and structured data to improve usability, accessibility, and machine readability.">WSG 3.8: Structure metadata for machine readability</a>

_Include essential document metadata and structured data to improve usability, accessibility, and machine readability._

Clean states provide content-specific titles, purpose-specific descriptions and absolute self-canonical URLs under /draftjs_exporter/. No structured-data blocks were declared. These observations apply to the sampled exporter pages.

**Next step:** Keep canonical URLs aligned with published paths and validate any structured data introduced later.

**Where we looked:**

- Browser observations for [Draftjs_exporter](https://wagtail.github.io/draftjs_exporter/).
- Browser observations for [Getting started](https://wagtail.github.io/draftjs_exporter/getting-started/).
- Browser observations for [Content state](https://wagtail.github.io/draftjs_exporter/content-state/).
- Browser observations for [Configuration](https://wagtail.github.io/draftjs_exporter/reference/configuration/).
- Browser observations for [Api](https://wagtail.github.io/draftjs_exporter/reference/api/).
- Browser observations for [Alternative engines](https://wagtail.github.io/draftjs_exporter/guides/alternative-engines/).
- Browser observations for [Migration guide](https://wagtail.github.io/draftjs_exporter/migration-guide/).

<h4 id="evidence-preference-behavior">Establish the intended theme behavior</h4>

**Needs investigation** · <a class="audit-guideline" href="https://www.w3.org/TR/web-sustainability-guidelines/#use-media-queries-that-support-sustainability-goals" title="Support user preferences via media queries for color, motion, contrast, data use, and related settings to improve accessibility and efficiency.">WSG 3.9: Use media queries that support sustainability goals</a>

_Support user preferences via media queries for color, motion, contrast, data use, and related settings to improve accessibility and efficiency._

Successful desktop and dark-preference states remain light while retaining reading content. No active motion was observed. The evidence does not establish an offered dark theme or a requirement to follow the device setting, so the fixed light appearance alone does not demonstrate a defect.

**Next step:** Establish the intended theme policy and controls; if device-theme following is intended, verify both initial loading and changes while a page remains open.

**Where we looked:**

- Browser observations for [Getting started](https://wagtail.github.io/draftjs_exporter/getting-started/).
- Browser observations for [Content state](https://wagtail.github.io/draftjs_exporter/content-state/).
- Browser observations for [Api](https://wagtail.github.io/draftjs_exporter/reference/api/).
- Browser observations for [Migration guide](https://wagtail.github.io/draftjs_exporter/migration-guide/).

<h4 id="evidence-api-requests">Resolve sitemap requests from nested documentation pages</h4>

**Problem found** · <a class="audit-guideline" href="https://www.w3.org/TR/web-sustainability-guidelines/#use-sustainable-javascript-and-apis" title="Write efficient JavaScript and use APIs that minimize processing, data use, and energy consumption.">WSG 3.11: Use sustainable JavaScript and APIs</a>

_Write efficient JavaScript and use APIs that minimize processing, data use, and energy consumption._

The documentation-root sitemap returns XML successfully. Content state, configuration, API and alternative-engine pages each request a page-relative sitemap.xml and receive roughly 3.9 kB of 404 HTML. These four completed error requests are a demonstrated local request defect; visitor-task impact and backend cost were not measured.

**Next step:** Resolve sitemap fetching against /draftjs_exporter/ and verify root and nested pages retrieve the intended XML without new failed requests.

**Where we looked:**

- Captured public evidence for [Draftjs_exporter](https://wagtail.github.io/draftjs_exporter/).
- Captured public evidence for [Content state](https://wagtail.github.io/draftjs_exporter/content-state/).
- Captured public evidence for [Configuration](https://wagtail.github.io/draftjs_exporter/reference/configuration/).
- Captured public evidence for [Api](https://wagtail.github.io/draftjs_exporter/reference/api/).
- Captured public evidence for [Alternative engines](https://wagtail.github.io/draftjs_exporter/guides/alternative-engines/).
- Browser observations for [Content state](https://wagtail.github.io/draftjs_exporter/content-state/).

<h4 id="evidence-keyboard-path">Verify focus through search and the complete task</h4>

**Needs investigation** · <a class="audit-guideline" href="https://www.w3.org/TR/web-sustainability-guidelines/#ensure-code-follows-good-semantic-practices" title="Use standards-compliant HTML and web platform features, and avoid unnecessary complexity or non-standard code.">WSG 3.6: Ensure code follows good semantic practices</a>

_Use standards-compliant HTML and web platform features, and avoid unnecessary complexity or non-standard code._

Short Tab traces reach skip/home links, Search where initialized, the repository link and task navigation in a meaningful sequence. Search focus styling and an intermediate dialog state were not captured well enough to verify discernible focus. A complete keyboard route or trap was not established.

**Next step:** Visually verify focus on the skip link, Search input and dialog controls, then complete the installation route with forward and reverse keyboard traversal.

**Where we looked:**

- Browser observations for [Getting started](https://wagtail.github.io/draftjs_exporter/getting-started/).
- Browser observations for [Content state](https://wagtail.github.io/draftjs_exporter/content-state/).
- Browser observations for [Api](https://wagtail.github.io/draftjs_exporter/reference/api/).
- Browser observations for [Migration guide](https://wagtail.github.io/draftjs_exporter/migration-guide/).

<h4 id="evidence-carbon-discovery">Coordinate carbon.txt discovery with the origin owner if useful</h4>

**Problem found** · <a class="audit-guideline" href="https://www.w3.org/TR/web-sustainability-guidelines/#include-expected-and-beneficial-files" title="Include standard website metadata and configuration files to support discoverability, transparency, and operational best practices.">WSG 3.13: Include expected and beneficial files</a>

_Include standard website metadata and configuration files to support discoverability, transparency, and operational best practices._

The sampled origin-root and well-known carbon.txt routes returned 404, with no captured discovery or delegation relationship. A parseable service-related file could not be established through those routes. This scoped absence provides no conclusion about emissions levels or other projects on the origin.

**Next step:** If useful, coordinate a correctly scoped carbon.txt relationship with the origin owner and validate its declared version, schema and supporting evidence.

**Where we looked:**

- Disclosure discovery for the origin `https://wagtail.github.io`.

### Hosting, infrastructure and systems {#findings-4}

<h4 id="evidence-public-cache-policy">Retain the observed public caching and validation policy</h4>

**Passed this check** · <a class="audit-guideline" href="https://www.w3.org/TR/web-sustainability-guidelines/#optimize-caching-and-support-offline-access" title="Use caching and offline capabilities to reduce network load, improve resilience, and balance performance with sustainability.">WSG 4.2: Optimize caching and support offline access</a>

_Use caching and offline capabilities to reduce network load, improve resilience, and balance performance with sustainability._

Successful reusable first-party scripts, styles, images and search-index responses expose ten-minute cache lifetimes and ETags. Public GitHub API responses expose a one-minute public cache lifetime and ETags. These headers support bounded reuse or validation; warm reuse and offline behavior were not measured.

**Next step:** Use matched warm-load observations before claiming saved transfer. Consider longer lifetimes only where versioned assets and hosting controls support them.

**Where we looked:**

- Captured public evidence for [Draftjs_exporter](https://wagtail.github.io/draftjs_exporter/).
- Captured public evidence for [Content state](https://wagtail.github.io/draftjs_exporter/content-state/).
- Captured public evidence for [Configuration](https://wagtail.github.io/draftjs_exporter/reference/configuration/).
- Captured public evidence for [Api](https://wagtail.github.io/draftjs_exporter/reference/api/).
- Captured public evidence for [Alternative engines](https://wagtail.github.io/draftjs_exporter/guides/alternative-engines/).

<h4 id="evidence-text-compression">Keep compression on successful text responses</h4>

**Passed this check** · <a class="audit-guideline" href="https://www.w3.org/TR/web-sustainability-guidelines/#reduce-data-transfer-with-compression" title="Compress server responses and media files to reduce bandwidth, storage use, and delivery overhead while balancing processing costs.">WSG 4.3: Reduce data transfer with compression</a>

_Compress server responses and media files to reduce bandwidth, storage use, and delivery overhead while balancing processing costs._

Successful material HTML, CSS, JavaScript, search-index JSON and GitHub API responses use gzip. Worker accounting gaps and failed page navigations limit the scope of this finding; they do not establish a compression defect.

**Next step:** Check unobserved successful responses if expanding the claim; no specific compression repair is established by this sample.

**Where we looked:**

- Captured public evidence for [Draftjs_exporter](https://wagtail.github.io/draftjs_exporter/).
- Captured public evidence for [Content state](https://wagtail.github.io/draftjs_exporter/content-state/).
- Captured public evidence for [Configuration](https://wagtail.github.io/draftjs_exporter/reference/configuration/).
- Captured public evidence for [Api](https://wagtail.github.io/draftjs_exporter/reference/api/).
- Captured public evidence for [Alternative engines](https://wagtail.github.io/draftjs_exporter/guides/alternative-engines/).

<h4 id="evidence-hosting-evidence">Match hosting claims to this documentation service</h4>

**Needs investigation** · <a class="audit-guideline" href="https://www.w3.org/TR/web-sustainability-guidelines/#use-sustainable-hosting" title="Select and manage infrastructure using sustainability metrics, prioritizing low-carbon energy use and low-impact hosting and domain choices in selection, and extending hardware lifespan and minimising emissions in management.">WSG 4.1: Use sustainable hosting</a>

_Select and manage infrastructure using sustainability metrics, prioritizing low-carbon energy use and low-impact hosting and domain choices in selection, and extending hardware lifespan and minimising emissions in management._

The `github.io` origin and response routes identify the delivery context. No retrieved service-specific sustainability record or independent operational evidence establishes renewable-energy, hardware or emissions performance for the exporter documentation.

**Next step:** If making a sustainable-hosting claim, supply a dated provider record with independently corroborated operational scope and a clear relationship to this origin and project path.

**Where we looked:**

- Disclosure discovery for the origin `https://wagtail.github.io`.
- Captured public evidence for [Draftjs_exporter](https://wagtail.github.io/draftjs_exporter/).

### Business strategy and product management {#findings-5}

<h4 id="evidence-impact-choice">No consequential environmental choice was established</h4>

**Not relevant here** · <a class="audit-guideline" href="https://www.w3.org/TR/web-sustainability-guidelines/#communicate-the-environmental-impact-of-user-choices" title="Empower users, allowing them to make decisions when their choices can influence the environmental impact they have.">WSG 5.4: Communicate the environmental impact of user choices</a>

_Empower users, allowing them to make decisions when their choices can influence the environmental impact they have._

The scoped visitor reads installation and usage guidance. No high-transfer media setting, bulk export or comparable web-service choice was established. Engine guidance explains software tradeoffs without a measured environmental comparison.

**Next step:** Reassess if the service introduces consequential resource-use choices; support any environmental comparison with a common workload and scope.

**Where we looked:**

- Recorded visitor task starting at [Draftjs_exporter](https://wagtail.github.io/draftjs_exporter/).
- Captured public evidence for [Alternative engines](https://wagtail.github.io/draftjs_exporter/guides/alternative-engines/).
- Browser observations for [Getting started](https://wagtail.github.io/draftjs_exporter/getting-started/).

<h4 id="evidence-service-necessity">Document the bounded decision to maintain the exporter capability</h4>

**Needs investigation** · <a class="audit-guideline" href="https://www.w3.org/TR/web-sustainability-guidelines/#evaluate-if-a-digital-product-or-service-is-necessary" title="Assess alignment with sustainability goals, validate product need, and reduce barriers to access, usability, and fairness.">WSG 5.13: Evaluate if a digital product or service is necessary</a>

_Assess alignment with sustainability goals, validate product need, and reduce barriers to access, usability, and fairness._

The homepage explains a Python/Wagtail/Django conversion need, and alternative-engine guidance describes dependencies, speed, sanitization and output stability. This supports purpose and technical tradeoffs. It does not complete a documented evaluation of user desirability, ongoing viability and credible capability-level alternatives or reuse.

**Next step:** If resolving this check is useful, supply one creation or continuation decision connecting user need, maintenance resources, feasibility and considered alternatives to the chosen exporter capability.

**Assessed scope:** The documented creation/continuation rationale for the Python Draft.js ContentState-to-HTML exporter capability, limited to the current homepage purpose statement and published alternative-engine tradeoffs. Assess whether these public records establish desirability, feasibility, viability and alternatives; do not infer unpublished business decisions or a site-wide necessity judgment.

**Where we looked:**

- Captured public evidence for [Draftjs_exporter](https://wagtail.github.io/draftjs_exporter/).
- Captured public evidence for [Alternative engines](https://wagtail.github.io/draftjs_exporter/guides/alternative-engines/).

<h4 id="evidence-access-barriers">Keep installation guidance openly reachable</h4>

**Passed this check** · <a class="audit-guideline" href="https://www.w3.org/TR/web-sustainability-guidelines/#evaluate-if-a-digital-product-or-service-is-necessary" title="Assess alignment with sustainability goals, validate product need, and reduce barriers to access, usability, and fairness.">WSG 5.13: Evaluate if a digital product or service is necessary</a>

_Assess alignment with sustainability goals, validate product need, and reduce barriers to access, usability, and fairness._

The observed anonymous English desktop task used keyboard text entry and pointer result selection to reach installation and the first-render example without an account, payment, personal-data submission or external navigation. This is one successful bounded task, excluding keyboard-only, assistive-technology, geographic and representative-user claims.

**Next step:** Obtain a clean linked run for measured reliability. Extend to other represented users and constraints only when broadening the declared assessment scope.

**Assessed scope:** Anonymous English-reading desktop Chromium visitor, 1280 × 800 CSS pixels, using keyboard text entry and pointer selection: search from the documentation homepage for getting started, reach the installation command and complete first-render example without account creation, payment or submission. Keyboard-only traversal, assistive technologies, other countries and representative-user testing are outside this task scope.

**Where we looked:**

- Recorded visitor task starting at [Draftjs_exporter](https://wagtail.github.io/draftjs_exporter/).
- Browser observations for [Draftjs_exporter](https://wagtail.github.io/draftjs_exporter/).
- Browser observations for [Getting started](https://wagtail.github.io/draftjs_exporter/getting-started/).

<h4 id="evidence-content-lifecycle">Record review of useful migration and compatibility guidance</h4>

**Needs investigation** · <a class="audit-guideline" href="https://www.w3.org/TR/web-sustainability-guidelines/#promote-responsible-data-practices" title="Respect user data rights and manage data lifecycle through minimized collection, user control, portability, deletion, and content archiving.">WSG 5.18: Promote responsible data practices</a>

_Respect user data rights and manage data lifecycle through minimized collection, user control, portability, deletion, and content archiving._

The migration guide retains concrete upgrade instructions from earlier releases alongside current compatibility guidance. This is useful applied maintenance content. Date labels and release sections do not establish an explicit review schedule, ownership or a recorded review decision.

**Next step:** Document a release-linked review rule, responsible owner and one applied review decision, keeping historical upgrade paths discoverable and clearly distinguished from current configuration.

**Assessed scope:** Public Draft.js exporter documentation under /draftjs_exporter/ as captured for this audit: assess the documented update/review lifecycle and applied compatibility guidance in the current migration guide, including retained upgrade instructions for earlier releases. Date labels alone do not establish a review schedule; repository maintenance and unpublished processes are outside scope.

**Where we looked:**

- Captured public evidence for [Migration guide](https://wagtail.github.io/draftjs_exporter/migration-guide/).
- Captured public evidence for [Draftjs_exporter](https://wagtail.github.io/draftjs_exporter/).
- Browser observations for [Migration guide](https://wagtail.github.io/draftjs_exporter/migration-guide/).

## Methodology and reproducibility

The browser measurements were captured from **2026-11-05T07:45:55.240102+00:00** to **2026-11-05T07:46:56.155980+00:00**. Initial-load tests used a 1280 × 800 desktop viewport and a 3-second observation window. Cookie choices and scrolling were recorded afterward. Supplementary tests covered narrow layouts, color and motion preferences, print, JavaScript availability and bounded keyboard navigation.

**Audit judgments:** Codex native subagent, gpt-6.1-sol, **high reasoning**. **Report wording:** Codex native subagent, gpt-6.1-sol, **high reasoning**.

The scoring method is `agent-breadth-v3`. A guideline group counts once even if it has several checks. Observed problems take precedence over unresolved checks in that group. 2 groups were excluded as not applicable; 45 were untested. Unknowns remain in the passing-percentage denominator; untested and inapplicable groups do not. Area percentages use the same rule as the overall score.

### First load {#measure-first-load}

Data downloaded before clicking or scrolling, using the first recorded initial visit for each URL, including its completeness limit. Decimal kB = 1,000 bytes; MB = 1,000,000 bytes.

### Cookie choices and waiting {#measure-after-choice}

No cookie banner was observed in this sample. The intermediate checkpoint waits without clicking. Later columns show **cumulative totals**, including the initial load of that visit. They are not additional amounts to add together or guaranteed savings.

### Scrolling {#measure-scroll}

Cumulative downloads after scrolling to the bottom, following the cookie-choice or waiting checkpoint of the same visit. Compare accept and reject values within their own visit; do not subtract the first-load headline from a different visit.

### Partial measurements {#measure-completeness}

A partial result means some requests failed or did not finish in the observation window, so their transferred size is uncertain. The site is measured as it behaved; a failed analytics request is context, not automatically a priority fix. Failed document loads and HTTP error responses are shown as unavailable, since their bytes do not represent the requested page. Carbon estimates and ratings are withheld for failed or incomplete initial captures. Unmarked transfer figures are complete within the test conditions, not a measure of every possible download.

### Estimated footprint and Digital Carbon Rating {#measure-carbon}

Both use the same initial visit as the first-load column. Footprints are estimates in grams of carbon dioxide equivalent (gCO₂e) per first visit. They display two decimal places, with a minimum of 0.01 gCO₂e for positive estimates. Digital Carbon Ratings use unrounded estimates from the fixed comparison model. Recorded model: Sustainable Web Design Model version 4 through `@tgwf/co2@0.19.0`, assuming 100% first visits. The comparison gives no green-hosting credit. These are model assumptions, not verified electricity-supply facts. Ratings remain provisional because the capture protocol has not been independently validated; they do not establish whole-site sustainability.

### Browser and network energy {#measure-energy}

Energy is shown in milliwatt-hours (mWh = 0.001 Wh). Browser energy includes modeled CPU, memory, disk and display use. Not sampled means no energy experiment was supplied for that page; unavailable means a supplied experiment did not yield a usable result. Neither means zero energy.

**Energy method:** GreenFrame 2.0.1 uses separately recorded browser scenarios, with three fresh-context visits per page, page load followed by a three-second wait, and no cookie interaction or scrolling. The median client-device estimate and median network estimate are reported separately; their medians must not be added to derive a total. This is a resource-use model, not metered whole-device electricity. Browser startup and the collector warm-up are excluded; browser close is included.

The pinned container uses Chromium 110 and a fixed Chrome 89 user-agent, independently of the transfer collector. The model assumes a 14 W display; that assumption contributes substantially to these short visits. CPU, memory and disk estimates use the collection host's properties. Background activity on this shared workstation was not independently isolated. These figures support repeat experiments under the same conditions, not device-independent rankings. GreenFrame network energy and SWDM carbon estimates overlap in scope and are not added together.

Illustrations were captured separately from the transfer measurements. Their capture dates, viewports, URLs and file hashes are retained in the screenshot manifest. No source checkout was included in this audit.

??? note "Technical files for reproducing this report"

    The report above can be read without these files. They retain exact evidence, original judgments and calculation inputs for independent reproduction.

    - [Audit scope and tasks](assets/draftjs-exporter/plan.json)
    - [Collector commands and versions](assets/draftjs-exporter/receipt.json)
    - [Original judgments](assets/draftjs-exporter/review.json)
    - [Score calculation](assets/draftjs-exporter/scores.json)
    - [Scoring implementation and calculation provenance](assets/draftjs-exporter/score-receipt.json)
    - [Evidence index](assets/draftjs-exporter/packet.json)
    - [Recorded transfers and disclosures](assets/draftjs-exporter/staged.json)
    - [Browser observations](assets/draftjs-exporter/probes.json)
    - [Selected source evidence](assets/draftjs-exporter/source.json)
    - [Energy protocol, samples and provenance](assets/draftjs-exporter/energy/manifest.json)
    - [Specialist reviews and reconciliation](assets/draftjs-exporter/review-handoffs.json)
    - [Chart-ready measurements and scoring data](assets/draftjs-exporter/chart-data.json)
    - [Measurement table for charts](assets/draftjs-exporter/chart-data.csv)
    - [Frozen session, skill snapshots and reproduction instructions](assets/draftjs-exporter/session.zip)
    - [Publication hashes](assets/draftjs-exporter/manifest.json)
    - [Report wording and check explanations](assets/draftjs-exporter/editorial.json)
    - [Editorial model and input provenance](assets/draftjs-exporter/editorial-receipt.json)

    Original review SHA-256: `046e37618c4b1303237bdbc90ffebbc6625dcdc8169f8e589bc81d38ee82953d`. Recalculate with `audit/assess.py` using the preserved reviews, rubric, weights and evidence. New collection or model review requires a new session; it can produce different results.
