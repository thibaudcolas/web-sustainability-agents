---
tags:
  - sustainability
  - agents
  - research
search:
  boost: 2
---

# Agentic audits for web sustainability

Initial research: November 3, 2026. Tooling, benchmark, provider, portability, and carbon-rating updates: November 4, 2026.

**Recommendation: build an evidence-based audit assistant around a versioned methodology, with deterministic checks first and bounded model reviews where interpretation is necessary.** This looks useful for finding improvements, assembling evidence, and maintaining an audit over time. Its suitability for autonomous sustainability assurance is unproven.

!!! note "Research and proposed design"

    This research inspected primary sources, four local projects, and WSG/STAR data, and generated an offline decision-request preview. It did not run a sustainability audit, benchmark models, or implement an audit engine. The architecture, evaluation targets, and pilot below are proposals, not demonstrated results.

## Why this is promising

An audit combines several kinds of work: discovering relevant pages and documents, measuring behavior, interpreting requirements, identifying missing evidence, and explaining changes. Models can help with the discovery and interpretation steps. Ordinary software can keep measurements, calculations, evidence references, and reporting reproducible.

The Web Sustainability Guidelines (WSG) cover user experience, development, hosting, and business practices across planet, people, and prosperity. Their current published version is a **Group Note Draft**, not a W3C Recommendation. Sustainable Tooling And Reporting (STAR) supplies supporting methodology and techniques. This scope makes an audit assistant more useful than a page-weight score, but also means that a public URL alone cannot establish every result. [WSG draft](https://www.w3.org/TR/web-sustainability-guidelines/), [STAR](https://w3c.github.io/sustainableweb-ig/docs/star.html).

The strongest initial product would answer: **“What can we substantiate, what should we investigate, and what should we change next?”** Each answer should identify its evidence, scope, methodology version, and uncertainty.

The accepted direction is a public-site audit that also uses supplied source code and internal documents when relevant. Use Harbor for the benchmark, with Neuralwatt DeepSeek V4.1 Flash and Codex in model-bearing release comparisons. Share skills across Codex, Claude Code, OpenCode, and pi through small host adapters. Add Digital Carbon Ratings as a distinct deterministic reporting layer. The [validation roadmap](validation-roadmap.md) identifies what to establish before expanding implementation.

## Read the research

| Document                                                              | Purpose                                                                                     |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| [WSG and STAR](../knowledge-base/wsg-and-star.md)                     | Standards status, methodology, data inspection, and measurement limits                      |
| [Digital Carbon Ratings](../knowledge-base/digital-carbon-ratings.md) | SWDM v4 ratings, calculation profiles, thresholds, and reporting limits                     |
| [Local audit projects](local-projects.md)                             | Concrete patterns from claude-seo and accessibility-agents                                  |
| [Deterministic tools](deterministic-tools.md)                         | Executable local tools, existing measurement engines, Playwright, and agent-browser         |
| [Audit architecture](architecture.md)                                 | Division of work, candidate checks, sub-agents, skills, evidence, and reporting             |
| [Portable audits and project evidence](portable-audits.md)            | Shared skills, harness adapters, public-only and internally assisted audits                 |
| [Decision models](decision-models.md)                                 | Jev/Clef suitability, narrow judgments, escalation, and model comparison                    |
| [Decision-model examples](decision-model-examples.md)                 | jevotron evidence review, Jev-ultrafast browser decisions, and an offline request preview   |
| [Evaluation plan](evaluation.md)                                      | Datasets, baselines, metrics, release gates, and methodology changes                        |
| [Harbor benchmark](benchmark.md)                                      | Overall tracks, twelve initial case families, grader design, and optional Inspect/Promptfoo |
| [Model and provider comparisons](model-comparison.md)                 | DeepSeek/Neuralwatt, Codex, Clef/Jev, API contracts, and energy accounting                  |
| [Validation roadmap](validation-roadmap.md)                           | Implementation sequence and evidence needed for the next decisions                          |
| [Sources and research method](sources.md)                             | Dated sources, pinned repositories, reproducible observations, and limitations              |

## Where to use each method

| Method                 | Strongest role                                                                        | Main limit                                                                           |
| ---------------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| Deterministic checks   | Parse headers, count bytes, compare budgets, validate records                         | Measurements depend on capture conditions; a proxy may not establish the requirement |
| Decision models        | Classify evidence, judge a narrow relationship, route uncertain cases                 | Typed output and concentrated probabilities do not establish truth                   |
| Generative LLM reviews | Investigate ambiguous cases, explain tradeoffs, draft evidence-linked recommendations | Can invent explanations or overgeneralize from incomplete observations               |
| People                 | Establish intent, verify organizational practice, resolve consequential ambiguity     | Time and expertise must be budgeted                                                  |

Use a fixed workflow for known checks. Allow agents to investigate only bounded gaps with an explicit stopping condition. Anthropic's workflow/agent distinction supports this starting point; it is design guidance, not evidence that this particular audit will work. [Building effective agents](https://www.anthropic.com/research/building-effective-agents).

## Recommended pilot

1. **Reconcile the methodology.** Pin the WSG publication, STAR commit, and a small mapping of criteria to tests. Resolve the identifier and missing-fixture issues documented in the knowledge base.
2. **Build the evidence baseline.** Capture a few representative journeys once. Implement roughly ten narrow checks spanning media, caching, compression, third parties, budgets, and policy evidence. Include honest unknown results for inaccessible infrastructure and governance.
3. **Build and validate the benchmark.** Implement the twelve initial Harbor case families and validate their graders before expanding to 60–100 deliberately varied development cases. Include public/source-assisted pairs, ambiguity, and adversarial inputs; reserve independent sites for later validation.
4. **Compare methods.** Start with rules, Neuralwatt DeepSeek V4.1 Flash, and Codex. Evaluate Jev/Clef on the same semantic cases, then test escalation and specialist delegation. Separate model, harness, and complete-system comparisons.
5. **Decide on measured value.** Keep the extra machinery only if it improves finding quality or reduces review effort at acceptable cost, latency, and resource use. Use separate gates for false reassurance and harmful recommendations.

Avoid starting with one agent per WSG criterion. A small set of specialists sharing captured evidence is easier to evaluate and less likely to duplicate browsing. Make a multi-agent design earn its complexity against a single-reviewer baseline.

The tooling follow-up recommends a small Playwright collector, axe-core safeguards, and imported Lighthouse diagnostics, with Sitespeed.io evaluated before building extensive measurement infrastructure. Use agent-browser or typed browser decisions for bounded discovery and journey authoring, then replay validated scenarios for comparisons. Measure collection quality independently from review quality. See the [tool selection and capture protocol](deterministic-tools.md).

## Decisions to defer until the pilot

- Which semantic tasks benefit from Jev or Clef rather than ordinary rules or one LLM call?
- How often does additional evidence resolve uncertainty, compared with calling a larger model?
- Which domain judgments do reviewers agree on well enough to automate?
- Can the audit reduce human review effort without increasing unsupported passes?
- Do recommended changes improve resource use per successful user task while preserving accessibility and usability?
- Does the value of repeated auditing justify its own collection and inference costs?

No credible percentage of “WSG automated” or expected carbon savings follows from the research alone. The useful next milestone is a reproducible, independently reviewed pilot report.
