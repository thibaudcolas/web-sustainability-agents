# Sources and research method

This ledger supports the [research overview](README.md); nearby citations in the topic pages identify the evidence for individual claims.

## Scope and method

The investigation combined primary-source web research, direct inspection of public source files, and read-only inspection of `local/claude-seo` and `local/accessibility-agents`. Both local working trees were clean at inspection. Their commit IDs appear in [the local project review](../knowledge-base/local-projects.md).

The work included:

- Reading the published WSG draft, its conformance provisions, impact ratings, STAR methodology, and representative techniques.
- Fetching WSG/STAR JSON and repository trees, counting records, comparing identifiers with the published HTML, and checking selected fixture URLs.
- Inspecting three STAR fixture bodies and the local projects' orchestration, structured outputs, and evaluation code.
- Reading current TypeSafe API, primitive, confidence, model, image, and cookbook documentation, plus Cloudflare's deployment documentation and model card.
- Reviewing relevant measurement tools and evaluation methodology to develop a proposed architecture and experimental plan.

The research does not include an exhaustive semantic mapping of all 197 criteria, execution of every STAR fixture, live website audits, paid model calls, model accuracy measurements, or validation of organizational sustainability claims. Recommendations and numerical pilot targets are explicitly proposals.

## WSG and supporting sources

| Source                                                                                                                                                | Use in this research                                                                        |
| ----------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| [WSG, October 16, 2026](https://www.w3.org/TR/web-sustainability-guidelines/)                                                                         | Requirements, publication status, and claim scope                                           |
| [Impact ratings, October 16, 2026](https://www.w3.org/TR/wsg-ir/)                                                                                     | Relative prioritization and non-compounding of ratings                                      |
| [STAR HTML at the inspected commit](https://github.com/w3c/sustainableweb-ig/blob/393ed62a16580968e2de8af77c68fe9a2e2c675d/docs/star.html)            | Evaluation procedure, techniques, and test-table semantics                                  |
| [STAR JSON at the inspected commit](https://github.com/w3c/sustainableweb-ig/blob/393ed62a16580968e2de8af77c68fe9a2e2c675d/docs/star.json)            | Technique inventory and test URLs                                                           |
| [WSG JSON at the inspected commit](https://github.com/w3c/sustainableweb-wsg/blob/eb8f8af2178ddce3d28226f90a6e691ccc6af3c8/guidelines.json)           | Criterion inventory and identifier comparison                                               |
| [STAR test directory at the inspected commit](https://github.com/w3c/sustainableweb-ig/tree/393ed62a16580968e2de8af77c68fe9a2e2c675d/docs/test-suite) | Fixture availability and examples                                                           |
| [Supporting resources](https://w3c.github.io/sustainableweb-ig/docs/resources.html)                                                                   | Discovery of related sustainability evidence; linked material was not exhaustively reviewed |
| [ACT Rules Format 1.1](https://www.w3.org/TR/act-rules-format/) and [test-case design](https://act-rules.github.io/pages/design/test-cases/)          | Proposed rule structure and positive/negative fixtures                                      |
| [RGESN 2024](https://www.arcep.fr/uploads/tx_gspublication/general_policy_framework_for_the_ecodesign_of_digital_services_version_2024.pdf)           | Adjacent ecodesign methodology; no legal applicability analysis performed                   |

## Models and evaluation sources

| Source                                                                                                                                                                                                                        | Use in this research                                           |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| [TypeSafe documentation index](https://docs.typesafe.ai/llms.txt)                                                                                                                                                             | Discover current pages rather than rely on older descriptions  |
| [Models](https://docs.typesafe.ai/models.md), [images](https://docs.typesafe.ai/images.md), and [API](https://docs.typesafe.ai/api.md)                                                                                        | Version, capability, preview, and request-contract checks      |
| [Primitives](https://docs.typesafe.ai/primitives.md), [Choice](https://docs.typesafe.ai/primitives/choice.md), [Score](https://docs.typesafe.ai/primitives/score.md), and [Noul](https://docs.typesafe.ai/primitives/noul.md) | Typed-decision semantics                                       |
| [Confidence](https://docs.typesafe.ai/confidence.md) and [state](https://docs.typesafe.ai/concepts/state.md)                                                                                                                  | Distribution summaries and evidence preparation                |
| [Building guide](https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md) and [citation checking](https://docs.typesafe.ai/cookbooks/citation_check.md)                                                             | Narrow judgment and verification patterns                      |
| [Cloudflare Clef announcement](https://blog.cloudflare.com/clef-decision-models/)                                                                                                                                             | Release and open-weight claims, treated as provider statements |
| [Workers AI Clef contract](https://developers.cloudflare.com/workers-ai/models/clef/) and [model card](https://huggingface.co/Cloudflare/clef)                                                                                | Hosting limits and deployment options                          |
| [Building effective agents](https://www.anthropic.com/research/building-effective-agents)                                                                                                                                     | Workflow versus agent distinction                              |
| [Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)                                                                                                                       | Tasks, trials, graders, and evaluation design                  |

Some TypeSafe Markdown pages were not readable through the web extraction tool. Direct HTTPS retrieval succeeded and supplied the contents reviewed. Search snippets and third-party model comparisons were used for discovery only; the model recommendations rely on the primary documentation listed here.

## Measurement sources

- [Lighthouse performance scoring](https://developer.chrome.com/docs/lighthouse/performance/performance-scoring): performance interpretation and variability.
- [Sitespeed.io sustainability plugin](https://www.sitespeed.io/documentation/sitespeed.io/sustainable/): browser measurements and estimation integration.
- [CO2.js overview](https://developers.thegreenwebfoundation.org/co2js/overview/) and [model-update explanation](https://www.thegreenwebfoundation.org/news/understanding-the-latest-sustainable-web-design-model-update/): estimated emissions and changing assumptions.
- [Greencheck domain API](https://developers.thegreenwebfoundation.org/api/greencheck/v3/check-single-domain/): hosting lookup scope.
- [EcoIndex methodology](https://www.ecoindex.fr/en/how-it-works/) and [Ecograder methodology](https://ecograder.com/how-it-works): existing comparison tools.
- [Software Carbon Intensity specification](https://sci.greensoftware.foundation/): system boundary and functional-unit framing.

These sources describe capabilities and methodologies. No comparative accuracy or sustainability ranking of the tools was established.

## Deterministic-tool follow-up

The follow-up investigation inspected executable collectors, wrappers, report adapters, caches, and model-driven browser code. All four local working trees were clean when inspected. The accessibility-agents checkout had advanced since the initial review; both snapshots are retained in the documentation.

| Local checkout               | Revision inspected                         | Focus                                                                                            |
| ---------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------ |
| `local/claude-seo`           | `6be93f45064ffbadced572b5d5c95f55fd263af0` | Fetching, rendering, URL safety, sitemaps, PSI/CrUX, Unlighthouse, preload heuristics, baselines |
| `local/accessibility-agents` | `7597f1a2cd315f144bc6a212ecceabf0268ea044` | MCP Playwright tools, high-impact checks, bridge skills, finding merge                           |
| `local/jevotron`             | `300a67b332dbb6bb6a18fc39532dffcb18fe8055` | Request/configuration schemas, cache, batching, reports, trace-evaluation example                |
| `local/jev-ultrafast`        | `544b0b1d5db220c663d4ba41e217d122435a1054` | Browser loop, typed choices, state validation, accessibility probes, benchmark scope             |

The [deterministic-tool review](../knowledge-base/deterministic-tools.md) and [decision-model examples](decision-model-examples.md) link each source-level finding to the relevant commit permalink. A source inspection identifies implementation behavior and possible defects; it is not a runtime reproduction or a complete security or quality review of those projects.

Additional primary documentation reviewed:

| Source                                                                                                                                                                                                                                                                                                     | Research use                                                      |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| [Playwright network](https://playwright.dev/docs/network), [routing](https://playwright.dev/docs/api/class-browsercontext#browser-context-route), [request sizes](https://playwright.dev/docs/api/class-request#request-sizes), [accessibility testing](https://playwright.dev/docs/accessibility-testing) | Collection APIs, cache effects, byte definitions, axe integration |
| [Lighthouse CI](https://googlechrome.github.io/lighthouse-ci/docs/configuration.html), [user flows](https://github.com/GoogleChrome/lighthouse/blob/main/docs/user-flows.md)                                                                                                                               | Repeated diagnostics, assertions, journey integration             |
| [Unlighthouse CI](https://unlighthouse.dev/integrations/ci)                                                                                                                                                                                                                                                | Crawl/report/budget integration                                   |
| [Sitespeed.io scripting](https://www.sitespeed.io/documentation/sitespeed.io/scripting/), [Browsertime](https://www.sitespeed.io/documentation/browsertime/introduction/)                                                                                                                                  | Existing journey measurement infrastructure                       |
| [agent-browser](https://agent-browser.dev/), [snapshots](https://agent-browser.dev/snapshots), [network](https://agent-browser.dev/network), [profiler](https://agent-browser.dev/profiler), [sessions](https://agent-browser.dev/sessions)                                                                | Browser commands, HAR/trace collection, state isolation           |
| [GreenIT-Analysis](https://github.com/cnumr/GreenIT-Analysis), [Lighthouse EcoIndex plugin](https://github.com/cnumr/lighthouse-plugin-ecoindex), [EcoIndex repository](https://github.com/cnumr/EcoIndex)                                                                                                 | Adjacent ecodesign tools and component-specific licensing         |
| [Creedengo JavaScript](https://github.com/green-code-initiative/creedengo-javascript)                                                                                                                                                                                                                      | Optional source analysis                                          |
| [Green Metrics Tool](https://github.com/green-coding-solutions/green-metrics-tool), [measurement introduction](https://docs.green-coding.io/docs/prologue/introduction/)                                                                                                                                   | Controlled infrastructure/resource measurements and boundaries    |
| [Resource Timing](https://w3c.github.io/resource-timing/), [transferSize](https://developer.mozilla.org/en-US/docs/Web/API/PerformanceResourceTiming/transferSize)                                                                                                                                         | Visibility limits and cache interpretation                        |
| [Chrome back/forward cache and no-store](https://developer.chrome.com/docs/web-platform/bfcache-ccns)                                                                                                                                                                                                      | Check an outdated assumption in the local preload advice          |

The offline jevotron preview used two synthetic records in a temporary directory, with the API key removed from the process environment. It exited successfully and emitted two requests with the expected three-label Choice schema. The [saved preview](assets/decision-preview.json) contains the requests and reproduction command. This validates local request construction only; there were no inference calls or measured model outputs. No live browser audit or cross-tool performance experiment was performed.

WSG and impact-rating links now point to the canonical latest published addresses requested for this workspace. They still identified the October 16 drafts when rechecked. The inventory records a fresh digest for the canonical WSG response and retains the earlier digest as historical provenance; a moving publication URL is not an immutable version identifier.

## Ratings, benchmark, providers, and portability follow-up

The provider and portability extension follows the requested Harbor/Neuralwatt direction and adds optional project evidence to the audit design. The [validation roadmap](../initial-implementation/validation-roadmap.md) separates accepted design choices from unverified implementation behavior.

| Sources                                                                                                                                                                                                                                                                                                                                                       | Research use                                                                             |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| [Digital Carbon Ratings](https://sustainablewebdesign.org/digital-carbon-ratings/), [SWDM v4](https://sustainablewebdesign.org/estimating-digital-emissions/)                                                                                                                                                                                                 | Rating scope, baseline, version, and estimation boundaries                               |
| [CO2.js at inspected commit](https://github.com/thegreenwebfoundation/co2.js/tree/27cbe8328aeaad0824fb07b3640dc45b72228c7b)                                                                                                                                                                                                                                   | Constructor, trace methods, v4 model, constants, comparison helper, tests, and changelog |
| [Harbor tasks](https://docs.harborframework.com/tasks/overview), [agents](https://docs.harborframework.com/agents/pre-integrated-agents), [skills](https://docs.harborframework.com/tasks/skills)                                                                                                                                                             | Primary benchmark format and documented harness support                                  |
| [Separate verifier](https://docs.harborframework.com/tasks/separate-verifier), [artifacts](https://docs.harborframework.com/tasks/artifacts), [network policies](https://docs.harborframework.com/tasks/network-policies), [routing](https://docs.harborframework.com/agents/base-url-management), [regrading](https://docs.harborframework.com/jobs/regrade) | Proposed task isolation, outputs, provider access, and methodology iteration             |
| [Inspect providers](https://inspect.aisi.org.uk/providers.html), [Inspect Harbor](https://meridianlabs-ai.github.io/inspect_harbor/tasks.html), [Promptfoo Python provider](https://www.promptfoo.dev/docs/providers/python/)                                                                                                                                 | Optional narrower evaluations and bridge limitations                                     |
| [Neuralwatt public catalog](https://api.neuralwatt.com/v1/models), [DeepSeek V4.1 Flash](https://portal.neuralwatt.com/models/deepseek-v4.1-flash), [model changelog](https://portal.neuralwatt.com/changelog?area=models)                                                                                                                                    | Requested model availability in public metadata and revision changes                     |
| [Neuralwatt Clef Flash](https://neuralwatt.com/models/clef-flash), [System One API](https://neuralwatt.com/docs/api/systemone), [Responses API](https://docs.neuralwatt.com/api/responses)                                                                                                                                                                    | Decision versus generative contracts and preview conditions                              |
| [Neuralwatt energy methodology](https://docs.neuralwatt.com/energy-methodology), [usage records](https://docs.neuralwatt.com/api/usage-requests), [OpenCode integration](https://docs.neuralwatt.com/integrations/opencode)                                                                                                                                   | Provider attribution, consumed/billed distinctions, unit verification, and harness route |
| [Agent Skills specification](https://agentskills.io/specification), [Codex skills](https://learn.chatgpt.com/docs/build-skills), [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)                                                                                                                                              | Portable packaging and Codex-specific execution behavior                                 |
| [Claude skills](https://code.claude.com/docs/en/skills), [Claude subagents](https://code.claude.com/docs/en/sub-agents), [OpenCode skills](https://docs.opencode.ai/docs/skills/), [OpenCode agents](https://docs.opencode.ai/docs/agents/)                                                                                                                   | Host-specific discovery and delegation                                                   |
| [pi skills](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md), [pi subagent extension](https://github.com/earendil-works/pi-subagent)                                                                                                                                                                                      | Standard skills support and optional delegation adapter                                  |

Direct HTTPS retrieval supplied Harbor Markdown pages and CO2.js source where web extraction was incomplete. Some Neuralwatt Markdown endpoints returned 403; their ordinary HTML pages were readable. The public model catalog was retrieved without authentication; the [saved excerpt and response digest](../knowledge-base/assets/neuralwatt-model-snapshot.json) identify the observation. The local Codex CLI version/help were inspected before checking the current official documentation.

No credentials were read, no authenticated provider calls were made, and no model comparisons were executed. CO2.js source was inspected but not run. Harbor/Inspect/Promptfoo integrations were researched, not installed or benchmarked. The [benchmark seed plan](../initial-implementation/assets/benchmark-plan.json) contains public development specifications and expected behaviors, not executable tasks or a hidden evaluation set. The workspace-assisted protocol is a proposed design to validate with paired evidence conditions.

## Reproducing the inventory

The [demo/test-site follow-up](../evaluation/test-sites.md) rechecked the STAR repository revision and JSON/tree mapping: 116 declared URLs, 113 corresponding files, and 119 total HTML files in the test directory. It inspected five fixture bodies, including consent and retention examples, and reviewed the primary bakerydemo, headless demo, archive, LOW←TECH, and GOV.UK sources linked on that page. These were source/document inspections, not executed browser tests or audited reference sites.

Download the [source inventory manifest](../knowledge-base/assets/source-inventory.json) for retrieval URLs, SHA-256 digests, repository revisions, counts, and missing paths. The JSON files retrieved from the live sites were byte-identical to their pinned raw GitHub versions. The published HTML was separately inspected; the JSON's declared date is not treated as its publication date.

This Python snippet reproduces the structural counts and unmatched IDs from the pinned sources. It performs read-only network requests and prints derived data; it does not test any website's sustainability.

```python
import json
from urllib.request import urlopen

sources = {
    "wsg": (
        "https://raw.githubusercontent.com/w3c/sustainableweb-wsg/"
        "eb8f8af2178ddce3d28226f90a6e691ccc6af3c8/guidelines.json"
    ),
    "star": (
        "https://raw.githubusercontent.com/w3c/sustainableweb-ig/"
        "393ed62a16580968e2de8af77c68fe9a2e2c675d/docs/star.json"
    ),
}
documents = {}
for name, url in sources.items():
    with urlopen(url, timeout=30) as response:
        documents[name] = json.load(response)

guidelines = [
    guideline
    for category in documents["wsg"]["category"]
    for guideline in category.get("guidelines", [])
]
criteria = [item for guideline in guidelines for item in guideline["criteria"]]
criterion_ids = {item["id"] for item in criteria}
techniques = [
    technique
    for category in documents["star"]["category"]
    for technique in category.get("techniques", [])
]
print(
    "Guidelines, criteria, techniques:", len(guidelines), len(criteria), len(techniques)
)
print("Exact ID matches:", sum(item["id"] in criterion_ids for item in techniques))
print(
    "Unmatched:", [item["id"] for item in techniques if item["id"] not in criterion_ids]
)
```

Expected output: 71 guidelines, 197 criteria, 116 techniques, and 112 exact ID matches. Compare `testSuite` paths with the pinned STAR tree to reproduce the three missing files. Live HTTP status is time-dependent; the observed 404s are dated evidence rather than permanent assertions.

## Interpretation and follow-up

The most significant uncertainty is empirical: there is no WSG benchmark result here establishing that model review improves accuracy, or that sub-agents outperform a single reviewer. The [evaluation plan](evaluation.md) is designed to answer that question without confusing source coverage, plausible text, and demonstrated audit quality.

Useful follow-up research includes a complete criterion/technique crosswalk, reviewer agreement on subjective cases, a broader review of energy-measurement tooling, and independent validation of changes made from audit recommendations. Preserve unresolved methodology questions as research issues rather than silently encoding assumptions into passes.

## Repository verification

The subsequent [first executable slice](../initial-implementation/first-slice.md) records actual browser and provider experiments, their artifacts, and limitations. Earlier verification entries below describe the research stages at the time they were completed.

The documentation work was checked with `just build-docs`, `just test` (11 tests), `just check-links`, and `just check-external-links`; all passed. The inventory reproduction snippet also returned the documented counts and unmatched IDs. Formatting, Ruff, `ty`, and Vale checks passed.

The initial aggregate `just lint` stopped because `mypy .` followed `local/claude-seo` into the separate reference checkout. The tooling follow-up excludes the root `local/` directory from mypy, as requested, and `uv run mypy .` now passes on this repository's four Python files. Reference checkouts were not modified. This change corrects validation scope; it says nothing about either project's audit accuracy.

The first tooling follow-up passed `just lint`, `just build-docs`, `just test` (11 tests), `just check-links`, and `just check-external-links`. The external check reported zero errors and two redirects.

The ratings/benchmark/provider/portability extension passed the same five checks, again with 11 tests. Its external check reported zero errors and four redirects. The benchmark-plan JSON was also checked for twelve unique case families, both required campaign arms, and explicit design-only status. These checks validate repository quality and source-link availability, not the proposed audit methodology or provider integrations.

See the [implementation evidence ledger](../initial-implementation/sources.md) for executed experiments and their validation.
