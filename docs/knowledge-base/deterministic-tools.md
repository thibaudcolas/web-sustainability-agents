# Deterministic tools for sustainability audits

Research date: November 4, 2026. This extends the [initial local project review](local-projects.md). Tool capabilities were checked against source code and primary documentation; no comparative browser benchmark was run.

**Recommendation: own the capture protocol, evidence format, and WSG rule mappings; reuse established measurement engines.** Start with a small Playwright collector for representative journeys, axe-core for accessibility safeguards, and imported Lighthouse diagnostics. Add other engines only when they answer a question the initial stack cannot. Keep agent-browser and a Jev-driven browser as experimental discovery and journey-authoring options.

“Deterministic” describes a calculation or rule applied to supplied observations. It does not make the web, timing measurements, or a tool's interpretation deterministic. Preserve the observation separately from the rule result, and distinguish a failed capture from a failed check.

The [initial implementation](../initial-implementation/README.md) records which components have actually been built and tested. The recommendations here remain a reusable tooling reference.

## What to adopt, adapt, and build

| Component                             | Proposed use                                                          | Ownership decision                            | Important limit                                                |
| ------------------------------------- | --------------------------------------------------------------------- | --------------------------------------------- | -------------------------------------------------------------- |
| Playwright                            | Script journeys; collect requests, responses, DOM facts, and state    | Build a small collector on its APIs           | Browser conditions and instrumentation affect observations     |
| Lighthouse and Lighthouse CI          | Performance diagnostics, budgets, repeat runs, regression reports     | Import raw results and selected audits        | Performance scores do not establish sustainability             |
| Unlighthouse                          | Discover and sample many routes for Lighthouse                        | Optional breadth pass                         | Route sampling can miss important states and journeys          |
| Sitespeed.io and Browsertime          | Established journey measurement, repeated runs, performance artifacts | Alternative measurement backbone              | Adds a separate browser automation stack and operational cost  |
| axe-core                              | Detect accessibility regressions around proposed optimizations        | Run inside the captured browser state         | Automated checks cover only part of accessibility              |
| CO2.js and Greencheck                 | Explicitly labeled estimates and hosting evidence                     | Optional versioned enrichment                 | Neither establishes actual energy use of a request             |
| GreenIT-Analysis and EcoIndex tooling | Additional ecodesign signals and comparison                           | Import selected facts or reports after review | Their indicators and grades are not WSG conformance            |
| Creedengo                             | Source-code efficiency diagnostics where code is available            | Optional repository analysis                  | Public-URL audits cannot supply the required source context    |
| Green Metrics Tool                    | Measure controlled workloads on owned infrastructure                  | Later laboratory investigation                | Host measurements have a specific hardware and system boundary |
| agent-browser                         | Bounded exploration and creation of candidate journeys                | Compare with scripted collection              | An agent choosing commands is a separate source of variability |

This is a proposed selection, not a ranking established by testing. The [source ledger](../feasibility-study/sources.md#deterministic-tool-follow-up) records the reviewed versions and documentation.

The next design update adds [Digital Carbon Ratings through a pinned CO2.js adapter](digital-carbon-ratings.md). Optional repository/source analysis belongs in the [source-assisted audit mode](../feasibility-study/portable-audits.md), where code findings are corroborated against the deployed observations rather than assumed to describe production.

### Existing performance engines

Lighthouse CI already provides URL lists, repeated collection, assertions, budgets, and report storage. Reuse those capabilities instead of rebuilding a performance dashboard. Retain audit details, browser and Lighthouse versions, and individual measurements; an aggregate score can hide the exact tradeoff being investigated. [Lighthouse CI configuration](https://googlechrome.github.io/lighthouse-ci/docs/configuration.html).

Lighthouse user flows support navigation, timespan, and snapshot audits. This is useful for interactions beyond a landing page, but the documented Node integration uses Puppeteer. It is not a ready-made Playwright adapter: choose an integration boundary explicitly, such as importing reports from a separate, identically specified journey. [Lighthouse user flows](https://github.com/GoogleChrome/lighthouse/blob/main/docs/user-flows.md).

Unlighthouse adds route discovery and bulk analysis, with CI budgets and JSON reporting. Use it to identify templates and candidate problems, then audit selected journeys under the controlled protocol. A crawl with sampling enabled is not a complete site inventory. [Unlighthouse CI](https://unlighthouse.dev/integrations/ci).

Sitespeed.io deserves a practical comparison before expanding a custom collector. Its scripting interface supports multi-step journeys, and Browsertime supplies browser measurement and artifacts. If repeated measurement, reporting, and historical analysis become the main work, adapting this established harness may cost less than maintaining the equivalent ourselves. Its Selenium-style scripts would be another integration to maintain alongside Playwright. [Sitespeed.io scripting](https://www.sitespeed.io/documentation/sitespeed.io/scripting/), [Browsertime introduction](https://www.sitespeed.io/documentation/browsertime/introduction/).

The Sitespeed.io sustainability plugin can combine transfer observations and hosting information into emissions estimates. Keep the model version, inputs, assumptions, and output units together. Compare this with a direct CO2.js adapter before building a second estimation pipeline. These estimates must stay separate from measured bytes and physical energy readings. [Sustainability plugin](https://www.sitespeed.io/documentation/sitespeed.io/sustainable/), [CO2.js overview](https://developers.thegreenwebfoundation.org/co2js/overview/).

### Ecodesign and energy tools

[GreenIT-Analysis](https://github.com/cnumr/GreenIT-Analysis) combines browser observations with ecodesign checks and EcoIndex. The [Lighthouse EcoIndex plugin](https://github.com/cnumr/lighthouse-plugin-ecoindex) is another integration option. Inspect each underlying rule before mapping it to WSG: a request count or DOM-size indicator is useful evidence, but a grade is a methodology-specific interpretation. Review the license of the exact code, rules, and documentation being reused; for example, the [EcoIndex website repository](https://github.com/cnumr/EcoIndex) carries a noncommercial, no-derivatives content license. Do not assume all related components share a license.

[Creedengo JavaScript](https://github.com/green-code-initiative/creedengo-javascript) offers source analysis through ESLint and Sonar integration. It could detect implementation candidates that browser observations cannot explain. Treat those as source findings requiring reachability and workload context; code that looks wasteful may never execute in the tested journey. Its GPL licensing also merits review before distributing an integrated derivative.

[Green Metrics Tool](https://github.com/green-coding-solutions/green-metrics-tool) is relevant to a later controlled experiment, especially when the application and infrastructure are available. It supports different metric providers, including hardware energy sources and resource counters. Record which provider actually ran: CPU energy, a whole-machine power reading, and a software-derived estimate have different boundaries. It does not reveal the energy use of an arbitrary remote origin simply by browsing it. Check current AGPL/commercial terms for the intended integration. [Measurement introduction](https://docs.green-coding.io/docs/prologue/introduction/).

## What the local projects actually provide

### claude-seo

The November 4 inspection used commit `6be93f45064ffbadced572b5d5c95f55fd263af0`. These are executable scripts and reusable engineering patterns, rather than a ready-made WSG engine.

| Local component                         | Useful behavior                                                                      | Adaptation needed                                                               |
| --------------------------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------- |
| `fetch_page.py`, `url_safety.py`        | Bounded fetching, URL checks, shared safety controls                                 | Preserve retrieval failures and distinguish document bytes from journey traffic |
| `sitemap_discovery.py`                  | Robots and sitemap discovery with bounded responses                                  | Add representative journey and state selection                                  |
| `parse_html.py`                         | Structured HTML facts, including lazy-loading indicators                             | Distinguish declared markup from observed resource behavior                     |
| `render_page.py`                        | Browser rendering, raw/rendered content, accessibility tree, partial-result metadata | Add a controlled measurement protocol and full network evidence                 |
| `pagespeed_check.py`, `crux_history.py` | Lighthouse/PSI diagnostics and field-data retrieval                                  | Keep field data separate from lab captures; preserve unavailable data           |
| `unlighthouse_run.py`                   | Pinned CLI invocation and normalized route results                                   | Retain underlying reports and verify adapter compatibility                      |
| `drift_baseline.py`                     | Stored observations and baseline comparison                                          | Extend identity to scenario, state, method, and instrumentation versions        |

Sources: [fetching and parsing scripts](https://github.com/AgriciDaniel/claude-seo/tree/6be93f45064ffbadced572b5d5c95f55fd263af0/scripts), [browser renderer](https://github.com/AgriciDaniel/claude-seo/blob/6be93f45064ffbadced572b5d5c95f55fd263af0/scripts/render_page.py), [Unlighthouse wrapper](https://github.com/AgriciDaniel/claude-seo/blob/6be93f45064ffbadced572b5d5c95f55fd263af0/scripts/unlighthouse_run.py).

The renderer's partial/truncation reporting is especially worth adopting. Its auto-rendering decision is optimized for extracting content from sparse application shells. Sustainability checks involving runtime requests, polling, or media need a browser even when server-rendered HTML is already complete. Optional image or font blocking also changes the thing being measured; a discovery capture using those options cannot serve as an unmodified resource baseline.

There is a subtle cache issue: the renderer installs request routing. Playwright documents that enabling routing disables HTTP caching. Reusing this renderer unchanged would therefore undermine a realistic warm-cache test. Retain the security goal of guarded browsing, but design a compatible egress mechanism or declare a separate cache-disabled profile. Do not silently remove network safeguards to make a benchmark look realistic. [Renderer source](https://github.com/AgriciDaniel/claude-seo/blob/6be93f45064ffbadced572b5d5c95f55fd263af0/scripts/render_page.py), [BrowserContext routing](https://playwright.dev/docs/api/class-browsercontext#browser-context-route).

The Unlighthouse wrapper pins `unlighthouse@0.13.5`; it is not an unpinned shell command. Its normalized output emphasizes route scores. Preserve the full reports for diagnostic evidence, and treat an unrecognized output structure as an adapter error rather than zero findings.

Do not reuse the preload score as a sustainability rule. It rewards hints including speculation and preloading, which may trade latency for additional traffic. Its source also contains advice that `no-store` disqualifies back/forward caching; Chrome now permits some such pages under specific conditions. HTTP caching, back/forward caching, privacy requirements, and speculative fetching need separate tests. [Preload checker](https://github.com/AgriciDaniel/claude-seo/blob/6be93f45064ffbadced572b5d5c95f55fd263af0/scripts/preload_check.py), [Chrome's current back/forward cache behavior](https://developer.chrome.com/docs/web-platform/bfcache-ccns).

Similarly, lexical “content quality” heuristics do not establish that content is unnecessary or AI-written. Reuse extraction and evidence provenance; independently validate any judgment used to recommend deletion. [Content-quality script](https://github.com/AgriciDaniel/claude-seo/blob/6be93f45064ffbadced572b5d5c95f55fd263af0/scripts/content_quality.py).

### accessibility-agents

This follow-up inspected commit `7597f1a2cd315f144bc6a212ecceabf0268ea044`, which is newer than the snapshot in the initial review. Its MCP server contains executable Playwright tools for axe, accessibility snapshots, keyboard probing, contrast, and viewport behavior. The broader tool catalog also includes supplied-markup checks and document inspection. [Playwright tools](https://github.com/thi-bot/accessibility-agents/blob/7597f1a2cd315f144bc6a212ecceabf0268ea044/mcp-server/tools/playwright-tools.js), [tool metadata](https://github.com/thi-bot/accessibility-agents/blob/7597f1a2cd315f144bc6a212ecceabf0268ea044/mcp-server/tool-metadata.js).

These provide valuable safeguards: an image optimization must preserve text alternatives; simplifying a page must preserve keyboard operation; changing a downloadable document must preserve its accessibility. They are related quality evidence, not measures of environmental improvement.

Several implementation details matter before reuse:

- Individual browser tools launch and navigate separately. Running axe in our existing captured state would reduce duplicate browsing and state differences.
- The structured axe violation mapping retains only the first affected node per violation. Detailed incomplete results are not retained in the violation branch. Preserve raw axe output, including all nodes and incomplete checks, before normalizing it.
- The keyboard tool assigns `trapped = focusOrder.length < 3` inside a branch requiring `focusOrder.length > 2`. That assignment cannot identify a trap. This is a source-level finding, not a runtime reproduction; its “no trap” output should not be inherited as assurance.
- A missing CSS outline is not sufficient to establish a missing focus indicator; borders or shadows can provide one. Likewise, repeated focus targets and small target sizes need contextual interpretation.

The separate [high-impact Playwright script](https://github.com/thi-bot/accessibility-agents/blob/7597f1a2cd315f144bc6a212ecceabf0268ea044/mcp-server/scripts/playwright-high-impact-check.mjs) combines responsive checks, axe, and interaction probes. It is useful as a design reference, but its probes change state and its heuristics need individual validation.

The Lighthouse and scanner bridges are skills directing an agent to interpret and merge reports. They are not deterministic report parsers merely because the upstream scanner is deterministic. Build a schema-validated adapter for repeatable merging. Two reports containing the same underlying axe finding are correlated evidence, not two independent confirmations. [Lighthouse bridge](https://github.com/thi-bot/accessibility-agents/blob/7597f1a2cd315f144bc6a212ecceabf0268ea044/skills/lighthouse-bridge/SKILL.md), [merge implementation](https://github.com/thi-bot/accessibility-agents/blob/7597f1a2cd315f144bc6a212ecceabf0268ea044/skills/a11y-core/scripts/merge-findings.mjs).

## Playwright, agent-browser, or an existing harness?

| Approach                 | Best fit                                                      | What we still need to own                                                 |
| ------------------------ | ------------------------------------------------------------- | ------------------------------------------------------------------------- |
| Playwright scripts       | Small, explicit journeys and detailed assertions              | Capture schema, measurement windows, aggregation, fixtures                |
| Sitespeed.io/Browsertime | Repeated performance experiments and historical reporting     | WSG mapping, scenario specification, evidence integration                 |
| agent-browser commands   | Agent-friendly exploration, snapshots, and candidate journeys | Planner evaluation, outcome verification, repeatable measurement protocol |
| Jev-ultrafast pattern    | Typed decisions over a restricted browser action space        | Model evaluation, supported-widget coverage, independent outcome checks   |

[Playwright network APIs](https://playwright.dev/docs/network) provide a strong foundation for collecting network evidence close to a scripted action. [Request sizes](https://playwright.dev/docs/api/class-request#request-sizes) distinguish encoded response-body bytes from other fields. Preserve definitions and collection failures rather than substituting decoded HTML length. Cross-origin Resource Timing can hide sizes, and a zero `transferSize` is not alone proof of a cache hit. Prefer explicit cache/source evidence and reconcile multiple measurement surfaces. [Resource Timing specification](https://w3c.github.io/resource-timing/), [transferSize behavior](https://developer.mozilla.org/en-US/docs/Web/API/PerformanceResourceTiming/transferSize).

[agent-browser](https://agent-browser.dev/) exposes compact accessibility snapshots, element references, browser actions, HAR capture, and profiling. Its current documentation describes a native Rust implementation; it should not be assumed to be a Playwright wrapper. It could replace much hand-written browser glue for exploratory agents, but the CLI does not make the caller's planning deterministic. [Snapshots](https://agent-browser.dev/snapshots), [network and HAR](https://agent-browser.dev/network), [profiler](https://agent-browser.dev/profiler).

HAR and trace export make agent-browser a credible collection candidate, not just a navigation tool. First compare its artifacts against known fixtures and the Playwright collector. Verify redirects, cached responses, service-worker behavior, failures, and requests after interactions. A timeline trace can explain activity but does not directly measure energy. Benchmark trace overhead separately.

Use an isolated browser profile for measurements. agent-browser's named sessions can isolate browser state when launching separate browsers, but attaching different sessions to the same existing CDP browser shares its profile. A different tab is not a clean cookie or cache boundary. [Session documentation](https://agent-browser.dev/sessions).

The initial recommendation is therefore **scripted Playwright for the small pilot, with a time-boxed Sitespeed.io comparison before building extensive reporting**. Use agent-browser or the [Jev-ultrafast approach](../feasibility-study/decision-model-examples.md) to discover and propose journeys; validate those journeys, then replay stable scenarios for comparisons. Evaluate adaptive collection separately where a fixed script is genuinely inadequate.

## Candidate checks and their evidence boundaries

The following are proposed implementation units, not an authoritative mapping to every WSG criterion. Attach each to the pinned WSG/STAR identifiers only after reviewing applicability and the full test procedure.

| Check                    | Deterministic observation                                         | Judgment still required                                         |
| ------------------------ | ----------------------------------------------------------------- | --------------------------------------------------------------- |
| Transfer budget          | Encoded bytes and request counts by phase and origin              | Appropriate budget for the successful task                      |
| Compression              | Response encoding, content type, size, and status                 | Whether compressing this resource is beneficial and feasible    |
| Caching                  | Headers, revalidation, observed cold/warm behavior                | Correct freshness, personalization, and privacy requirements    |
| Images                   | Requested dimensions/formats, rendered size, timing, alternatives | Visual quality, content role, and appropriate delivery strategy |
| Media                    | Autoplay declarations, actual playback, bytes before/after action | Whether the experience needs that behavior                      |
| Third parties            | Origin, initiator, bytes, timing, consent-state differences       | Ownership, necessity, contractual and user requirements         |
| Idle activity            | Requests and activity during a fixed observation window           | Whether polling or background work serves the task              |
| Documents                | Download size/type plus accessibility diagnostics                 | Whether an equivalent accessible format meets user needs        |
| Accessibility regression | Raw axe findings and explicit interaction assertions              | Manual checks and user impact beyond automation                 |
| Policy evidence          | Document retrieval, dates, evidence spans, links                  | What the statement establishes and whether practice matches it  |

A deterministic result can be as narrow as “this image was requested before scrolling in this state.” Whether that violates an applicable sustainability requirement is a separate decision. Conversely, a missing header is sometimes directly testable without any model call. The [architecture](../feasibility-study/architecture.md) explains how to retain both facts and criterion-level conclusions.

## Capture protocol before more tools

Define a scenario as a task, starting state, actions, checkpoints, success assertion, and bounded observation window. Specify browser/build, device and viewport, network settings, locale, authentication, consent, cache, service workers, and the test environment. Include the methodology and collector revisions in the run identity.

For the pilot, compare at least these states where applicable:

1. A fresh profile and cold initial visit.
2. A repeat visit in the same profile, preserving the intended cache state.
3. The same task with optional consent declined and accepted.
4. Explicit scroll or interaction that reveals deferred content or starts media.
5. A fixed idle interval after the task completes.

Do not equate `networkidle` with task completion or wait forever for analytics. Use explicit application assertions and bounded settling rules. Record timeouts, blocked resources, aborted requests, unsupported browser features, and unavailable measurements as collection outcomes.

Instrumentation can change the result. Routing can disable caching; service-worker blocking changes application behavior; screenshot stabilization can suppress animation; injected libraries add traffic; focus emulation can keep a background tab active. Separate the unmodified measurement run from diagnostic probes when needed. Record which artifacts came from which run instead of joining them as if they were simultaneous observations.

Separate request bytes attributable to the application from collector-introduced traffic, while retaining both totals. Use fixed observation windows to compare application behavior: inference latency in an adaptive journey otherwise changes how long polling runs. Report the adaptive agent's actual duration and resource use separately as part of the auditor's cost.

Capture once per required state and let skills consume the resulting artifacts. A network specialist, media reviewer, and policy reviewer should not each repeat the same page load. Raw artifacts may contain credentials or personal content, so store a restricted original where needed and generate a sanitized review bundle with stable evidence references.

## Collector acceptance checks

A useful collector should supply a capture manifest, request records, selected DOM facts, raw accessibility diagnostics, and a report distinguishing observations, findings, and unknowns. Add adapters for imported Lighthouse results before adding another crawler. Use JSON Schema validation and explicit adapter versions; a missing report, incompatible schema, or empty sample must never become a pass.

Build controlled fixtures for compressed/uncompressed resources, cache reuse/revalidation, delayed images, autoplay, consent-dependent requests, persistent polling, redirects, and service-worker responses. Include a fixture in which instrumentation changes behavior, so that invalid measurement profiles are detected. Check expected requests and state transitions first; exact wall-clock timing is not a stable fixture assertion.

Then run the same small set of journeys through Playwright and one alternative. Compare capture completeness, repeated-run variability, task completion, failures, maintenance effort, browser launches, transferred bytes, runtime, and artifact size. Review disagreements against the fixture or application evidence. Only after that comparison should we claim that a tool is accurate enough for a particular check. The [evaluation plan](../feasibility-study/evaluation.md) separates these collection tests from model quality and WSG interpretation.
