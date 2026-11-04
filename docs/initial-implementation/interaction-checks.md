# Interaction and interpretation checks

The interaction collector supplies public-site observations for twelve scoped WSG reviews. It accepts the audit agent's per-site plan rather than assuming Wagtail URLs. It records facts for qualitative interpretation; it does not turn a quiet page, a missing optional feature, or a successful selector lookup into a guideline pass.

Run it after choosing the sample and meaningful visitor tasks:

```sh
uv run --locked --script audit/probes.py \
  --plan .audit-work/site-plan.json \
  --output .audit-work/site-probes.json
```

The [agent-triggered workflow](agent-driven-audits.md) coordinates this evidence with initial-load measurements, disclosures, and source review. This collector runs separately from headline byte and energy measurement. Its instrumentation and repeated states must not be counted as ordinary page traffic.

## Repeatable observations

For each planned page, the collector loads a fresh Chromium context at 1280 × 800 CSS pixels and waits 500 ms after the load event. It records bounded visible text, headings, navigation, link names, form labels, controls, overlays, media, images, fonts, Resource Timing entries, and initial code execution observations. It then resizes the same document to 360 pixels, changes the reduced-motion preference, and emulates print. A separate fresh context loads the page with JavaScript disabled.

The narrow viewport is a layout probe, not a complete mobile-device emulation. The reduced-motion state checks a preference change on the existing page, not initialization with that preference. The print state exposes visibility and layout observations; it does not render a paginated PDF or assess a downloaded document's accessibility. The no-JavaScript state captures content availability, not task completion. These distinctions follow the separation between [Playwright viewport, device, and media emulation](https://playwright.dev/python/docs/emulation).

The output retains truncation flags and limits: 20,000 text characters, 300 links and resource timing entries, 150 controls and images, and smaller bounded lists for headings, media, and overlays. Observations concern the main document; embedded frames are listed but not traversed. Accessible-name fields are ingredients for review, not an implementation of the full accessible-name computation. Resource Timing's zero sizes can reflect restrictions or cache reuse; they are not evidence of zero transferred bytes.

Initial JavaScript coverage uses the [Chrome DevTools Protocol Profiler](https://chromedevtools.github.io/devtools-protocol/tot/Profiler/). CSS observations use [CSS rule usage tracking](https://chromedevtools.github.io/devtools-protocol/tot/CSS/). The artifact preserves bounded source-offset ranges. It does not convert source positions to network bytes or promise that unexecuted code can be removed: a later task, breakpoint, or preference can need it. Instrumentation also counts calls to `Notification.requestPermission` through a wrapper that delegates to the original API. That count says nothing about unvisited states or whether a user actually saw a browser prompt.

## Declared journeys

The agent can add up to ten journeys with a task description, starting URL, explicit `click`, `fill`, or `press` actions, and an optional completion selector. Each journey uses a fresh browser context. The collector preserves before/after observations, each action's status, and whether the supplied completion selector is visible. A failed action stops subsequent actions; missing optional controls are recorded separately.

```json
{
  "id": "search-help",
  "url": "https://example.com/help/",
  "task": "Find guidance about images",
  "actions": [
    { "type": "fill", "selector": "input[name=q]", "value": "images" },
    { "type": "press", "selector": "input[name=q]", "key": "Enter" }
  ],
  "successSelector": "main .search-results"
}
```

This example requires selectors discovered on the audited site. A visible results container is only one piece of task evidence: the reviewer must inspect relevance, empty results, recovery, keyboard behavior, and unnecessary steps. The collector does not discover or submit forms on its own. Actions that submit information require a plan consistent with the authorized audit scope.

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

These are narrow expectations, not complete guideline tests. An agent can gather more evidence interactively, inspect supplied source, or ask an owner about audience and task priorities. Record the added procedure, observed state, evidence identity, and remaining uncertainty so the next audit can repeat it.

## Reproducibility and validation

The plan has one origin, 1–20 pages, and at most ten journeys with twenty actions each. Page collection is bounded to 50 seconds, the separate no-JavaScript load to 30 seconds, each journey to 90 seconds, and context cleanup to five seconds. Evidence checkpoints preserve completed pages when later work fails. The output records the plan hash, browser version, timestamps, states, errors, and check definitions. Raw output permissions are private because page text and supplied input values can need review before publication.

The localhost fixture tests exercise actual Chromium behavior: desktop versus narrow overflow, print navigation visibility, reduced-motion changes, no-JavaScript fallback content, labels, download links, unused function observations, explicit search completion, and stopping after a failed action. They verify the collector contract, not the correctness of an LLM's qualitative judgments. The [methodology benchmark](methodology-benchmark.md) remains a separate frozen campaign; changes to skills and check definitions need their own evaluation inputs and results.
