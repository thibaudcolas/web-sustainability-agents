# Interaction and interpretation checks

The interaction collector supplies public-site observations for 22 scoped WSG reviews in catalog `interaction-probes-v2`. It accepts the audit agent's per-site plan rather than assuming Wagtail URLs. It records facts for qualitative interpretation; it does not turn a quiet page, a missing optional feature, or a successful selector lookup into a guideline pass.

Run it after choosing the sample and meaningful visitor tasks:

```sh
uv run --locked --script audit/probes.py \
  --plan .audit-work/site-plan.json \
  --output .audit-work/site-probes.json
```

The [agent-triggered workflow](../using/workflow.md) coordinates this evidence with initial-load measurements, disclosures, and source review. This collector runs separately from headline byte and energy measurement. Its instrumentation and repeated states must not be counted as ordinary page traffic.

## Repeatable observations

For each planned page, the collector loads a fresh Chromium context at 1280 × 800 CSS pixels and waits 500 ms after the load event. It records bounded visible text, headings, navigation, link names, form labels, controls, overlays, media, images, fonts, Resource Timing entries, and initial code execution observations. It then resizes the same document to 360 pixels, changes reduced-motion and dark preferences, and emulates print. After resetting to screen/light/no-preference, it records twelve real Tab movements without activating controls. Separate fresh contexts load the page with JavaScript disabled and with dark/reduced-motion preferences established before navigation.

The narrow viewport is a layout probe, not a complete mobile-device emulation. The `reduced_motion` and `live_dark` states change preferences on the existing page. The separate `cold_dark` state covers initialization with both dark and reduced-motion preferences. Compare observable content, colors and movement rather than using the media-query result alone as a pass. The print state exposes visibility and layout observations; it does not render a paginated PDF or assess a downloaded document's accessibility. The no-JavaScript state captures content availability, not task completion. These distinctions follow the separation between [Playwright viewport, device, and media emulation](https://playwright.dev/python/docs/emulation).

The output also includes canonical/description/viewport metadata, structured-data JSON syntax, main/heading/form observations, intrinsic image dimensions and responsive-image declarations. Font descriptors retain loading status and display strategy; no constrained-font-loading test is implied.

A bounded [CDP Network ledger](https://chromedevtools.github.io/devtools-protocol/tot/Network/#event-responseReceived) retains at most 300 request records and 300 responses, with total counts exposing truncation. Response headers use an explicit cache/compression allowlist and exclude cookies and authorization. Policy headers do not demonstrate warm-cache reuse; repeated API URLs do not demonstrate redundancy or backend energy.

The [keyboard trace](https://playwright.dev/python/docs/api/class-keyboard#keyboard-press) records actual focused elements, geometry, scroll position and focus-style clues. It does not activate controls, test reverse traversal or establish accessible names. A missing outline can coexist with a useful border/shadow indicator; review the rendered indicator before asserting failure.

The output retains truncation flags and limits: 20,000 text characters, 300 links and resource timing entries, 150 controls and images, and smaller bounded lists for headings, media, and overlays. Observations concern the main document; embedded frames are listed but not traversed. Accessible-name fields are ingredients for review, not an implementation of the full accessible-name computation. Resource Timing's zero sizes can reflect restrictions or cache reuse; they are not evidence of zero transferred bytes.

Initial JavaScript coverage uses the [Chrome DevTools Protocol Profiler](https://chromedevtools.github.io/devtools-protocol/tot/Profiler/). CSS observations use [CSS rule usage tracking](https://chromedevtools.github.io/devtools-protocol/tot/CSS/). The artifact preserves bounded source-offset ranges. It does not convert source positions to network bytes or promise that unexecuted code can be removed: a later task, breakpoint, or preference can need it. Instrumentation also counts calls to `Notification.requestPermission` through a wrapper that delegates to the original API. That count says nothing about unvisited states or whether a user actually saw a browser prompt.

## Declared journeys

The agent can add up to ten journeys with a task description, starting URL, explicit `click`, `fill`, or `press` actions, an optional viewport, and explicit completion conditions. Each journey uses a fresh browser context. The collector preserves before/after observations, each action's status, and whether all declared URL, unique visible selector and text conditions hold after successful actions. The legacy `successSelectorVisible` field remains an observation; it never establishes task completion by itself. A failed action stops subsequent actions; missing optional controls are recorded separately.

```json
{
  "id": "search-help",
  "url": "https://example.com/help/",
  "task": "Find guidance about images",
  "actions": [
    { "type": "fill", "selector": "input[name=q]", "value": "images" },
    { "type": "press", "selector": "input[name=q]", "key": "Enter" }
  ],
  "viewport": { "width": 360, "height": 800 },
  "success": {
    "url": "https://example.com/help/search/?q=images",
    "selector": "main .search-results",
    "text": "Managing images"
  }
}
```

This example requires selectors, an exact result URL and result text discovered on the audited site. A missing postcondition is `not_declared`; a failed action or unmet condition is `not_satisfied`, including when a generic heading remains visible. A satisfied postcondition is a bounded observable result, not a usability score. A visible results container is only one piece of task evidence: the reviewer must inspect relevance, empty results, recovery, keyboard behavior, and unnecessary steps. The collector does not discover or submit forms on its own. Actions that submit information require a plan consistent with the authorized audit scope.

## Scoped review catalog

`audit/probe-checks.json` is the versioned review catalog. Agents should read its exact expectations together with the pinned WSG reference and cite the relevant page/state or journey JSON Pointer. Additional evidence can be necessary even when collection succeeds.

| Check              | WSG area                                                                                                                | Interpretation and necessary follow-up                                                                                                       |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Distraction        | [2.5](https://www.w3.org/TR/web-sustainability-guidelines/#design-to-assist-and-not-to-distract)                        | Relate observed prompts and motion to the visitor task; useful guidance is not automatically distraction.                                    |
| Choice             | [2.6](https://www.w3.org/TR/web-sustainability-guidelines/#avoid-being-manipulative-or-deceptive)                       | Review choice wording and controls, then exercise both paths and inspect visual prominence before judging manipulation.                      |
| Comprehension      | [2.7](https://www.w3.org/TR/web-sustainability-guidelines/#make-deliverables-understandable-and-reusable)               | Judge sampled wording against the declared audience; an LLM is not a substitute for evidence from that audience.                             |
| Consistency        | [2.8](https://www.w3.org/TR/web-sustainability-guidelines/#use-a-design-system-for-interface-consistency)               | Compare repeated navigation and controls; consistent samples do not prove an organizational design system exists.                            |
| Motion             | [2.10](https://www.w3.org/TR/web-sustainability-guidelines/#ensure-animation-is-proportionate-and-easy-to-control)      | Assess purpose, playback controls, and actual preference response. Follow up on initialization and triggered motion.                         |
| Notifications      | [2.12](https://www.w3.org/TR/web-sustainability-guidelines/#avoid-unwanted-notifications)                               | Assess the usefulness and control of observed alerts and requests; none observed is limited to this sample.                                  |
| Documents          | [2.13](https://www.w3.org/TR/web-sustainability-guidelines/#reduce-the-impact-of-downloadable-and-physical-documents)   | Check print visibility and download labels, then retrieve representative documents before asserting optimization or equivalent alternatives. |
| Unused code        | [3.2](https://www.w3.org/TR/web-sustainability-guidelines/#minify-and-remove-unused-code)                               | Treat initial execution gaps as investigation candidates. Check representative journeys or source before recommending deletion.              |
| Components         | [3.3](https://www.w3.org/TR/web-sustainability-guidelines/#modularize-bandwidth-heavy-components)                       | Relate early resources to actual component use and deferred activation; script counts alone do not establish a splitting opportunity.        |
| Layout             | [3.10](https://www.w3.org/TR/web-sustainability-guidelines/#ensure-layouts-work-for-different-devices-and-requirements) | Compare overflow and content, then operate affected controls. Intentional scroll regions can be appropriate.                                 |
| Impact information | [5.4](https://www.w3.org/TR/web-sustainability-guidelines/#communicate-the-environmental-impact-of-user-choices)        | Identify consequential choices first; assess relevant, supported information rather than requiring labels everywhere.                        |
| Journeys           | [2.4](https://www.w3.org/TR/web-sustainability-guidelines/#design-efficient-and-streamlined-user-journeys)              | Check task completion and efficiency with declared actions; selector visibility alone is insufficient.                                       |

The second catalog version adds ten checks backed by the expanded observations:

| Check                 | WSG area                                                                                                        | Evidence and interpretation                                                                                                                     |
| --------------------- | --------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Media delivery        | [2.9](https://www.w3.org/TR/web-sustainability-guidelines/#optimize-media-to-reduce-resource-use)               | Compare rendered/intrinsic dimensions, DPR, formats and responsive declarations; validate legibility and task value before changing renditions. |
| Font delivery         | [2.11](https://www.w3.org/TR/web-sustainability-guidelines/#use-optimized-web-typography)                       | Review loaded families/variants and fallback strategy; constrained loading and language requirements can remain unresolved.                     |
| Semantics and forms   | [3.6](https://www.w3.org/TR/web-sustainability-guidelines/#ensure-code-follows-good-semantic-practices)         | Check sampled language, heading/main structure and control labeling; presence is not full semantic validity.                                    |
| Metadata              | [3.8](https://www.w3.org/TR/web-sustainability-guidelines/#structure-metadata-for-machine-readability)          | Check meaningful title/canonical and declared JSON syntax, respecting optional metadata and page purpose.                                       |
| Preference behavior   | [3.9](https://www.w3.org/TR/web-sustainability-guidelines/#use-media-queries-that-support-sustainability-goals) | Compare live changes with fresh initialization and actual visible state.                                                                        |
| No-JavaScript content | [2.17](https://www.w3.org/TR/web-sustainability-guidelines/#provide-cross-platform-compatibility-support)       | Compare core reading/navigation content, keeping interaction and full compatibility claims separate.                                            |
| API requests          | [3.11](https://www.w3.org/TR/web-sustainability-guidelines/#use-sustainable-javascript-and-apis)                | Investigate repeated requests against task freshness needs; repetition alone does not establish waste.                                          |
| Public cache policy   | [4.2](https://www.w3.org/TR/web-sustainability-guidelines/#optimize-caching-and-support-offline-access)         | Assess public reusable assets separately from private responses; warm reuse needs a separate test.                                              |
| Text compression      | [4.3](https://www.w3.org/TR/web-sustainability-guidelines/#reduce-data-transfer-with-compression)               | Inspect material text responses and encoding, allowing tiny/already-compressed/error-response exceptions.                                       |
| Keyboard path         | [3.6](https://www.w3.org/TR/web-sustainability-guidelines/#ensure-code-follows-good-semantic-practices)         | Review twelve forward Tab observations and focus visibility; no full keyboard or WCAG conformance claim.                                        |

These are narrow expectations, not complete guideline tests. An agent can gather more evidence interactively, inspect supplied source, or ask an owner about audience and task priorities. Record the added procedure, observed state, evidence identity, and remaining uncertainty so the next audit can repeat it.

## Reproducibility and validation

The plan has one origin, 1–20 pages, and at most ten journeys with twenty actions each. Page collection is bounded to 50 seconds, each separate no-JavaScript and cold-dark load to 30 seconds, each journey to 90 seconds, and context cleanup to five seconds. Evidence checkpoints preserve completed pages when later work fails. The output records the plan hash, browser version, timestamps, states, errors, and check definitions. Raw output permissions are private because page text and supplied input values can need review before publication.

The localhost fixture tests exercise actual Chromium behavior: desktop versus narrow overflow, print navigation visibility, reduced-motion changes, no-JavaScript fallback content, labels, download links, unused function observations, explicit search completion, strong postconditions despite a visible generic heading, optional journey viewport, metadata, preference initialization, real Tab movement, bounded header filtering, and stopping after a failed action. They verify the collector contract, not the correctness of an LLM's qualitative judgments. The [methodology benchmark](../initial-implementation/methodology-benchmark.md) remains a separate frozen campaign; changes to skills and check definitions need their own evaluation inputs and results.

The fixture received a focused keyboard-specialist review. Its dark-theme focus indicator was adjusted to preserve contrast; deliberate narrow overflow and motion remain controlled test conditions. The review and browser assertions do not substitute for an accessibility audit of live sites.
