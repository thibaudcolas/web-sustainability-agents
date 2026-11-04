---
tags:
  - sustainability
  - agents
  - research
search:
  boost: 2
---

# Feasibility study

**Recommendation: build an evidence-based audit assistant around a versioned methodology, with deterministic checks first and bounded model reviews where interpretation is necessary.** This looks useful for finding improvements, assembling evidence, and maintaining an audit over time. Its suitability for autonomous sustainability assurance is unproven.

!!! note "Research and proposed design"

    This study assesses the suitability of agentic web sustainability audits. Its architecture and evaluation targets are proposals. Executed experiments, results, and the development roadmap are documented separately under [initial implementation work](../initial-implementation/README.md).

## Why this is promising

An audit combines several kinds of work: discovering relevant pages and documents, measuring behavior, interpreting requirements, identifying missing evidence, and explaining changes. Models can help with the discovery and interpretation steps. Ordinary software can keep measurements, calculations, evidence references, and reporting reproducible.

The Web Sustainability Guidelines (WSG) cover user experience, development, hosting, and business practices across planet, people, and prosperity. Their current published version is a **Group Note Draft**, not a W3C Recommendation. Sustainable Tooling And Reporting (STAR) supplies supporting methodology and techniques. This scope makes an audit assistant more useful than a page-weight score, but also means that a public URL alone cannot establish every result. [WSG draft](https://www.w3.org/TR/web-sustainability-guidelines/), [STAR](https://w3c.github.io/sustainableweb-ig/docs/star.html).

The strongest initial product would answer: **“What can we substantiate, what should we investigate, and what should we change next?”** Each answer should identify its evidence, scope, methodology version, and uncertainty.

The accepted direction is a public-site audit that also uses supplied source code and internal documents when relevant. Use Harbor for the benchmark, with Neuralwatt DeepSeek V4.1 Flash and Codex in model-bearing release comparisons. Share skills across Codex, Claude Code, OpenCode, and pi through small host adapters. Add Digital Carbon Ratings as a distinct deterministic reporting layer. The [validation roadmap](../initial-implementation/validation-roadmap.md) identifies what to establish before expanding implementation.

## Read the study

| Document                                                   | Purpose                                                                        |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------ |
| [Proposed audit architecture](architecture.md)             | Workflow, candidate checks, skills, sub-agents, and evidence contracts         |
| [Portable audits and project evidence](portable-audits.md) | Shared skills, harness adapters, and optional source/internal context          |
| [Decision models](decision-models.md)                      | Jev/Clef suitability, narrow judgments, uncertainty, and escalation            |
| [Decision-model examples](decision-model-examples.md)      | Lessons from jevotron and jev-ultrafast, including the offline request preview |
| [Evaluation approach](evaluation.md)                       | Reference judgments, controlled comparisons, metrics, and release gates        |
| [Sources and research method](sources.md)                  | Dated sources, inspected revisions, inventory reproduction, and limitations    |

For reusable methodology and tool references, use the [knowledge base](../knowledge-base/README.md). For runnable components, benchmark plans, test sites, and observed results, use [initial implementation work](../initial-implementation/README.md).

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

The tooling follow-up recommends a small Playwright collector, axe-core safeguards, and imported Lighthouse diagnostics, with Sitespeed.io evaluated before building extensive measurement infrastructure. Use agent-browser or typed browser decisions for bounded discovery and journey authoring, then replay validated scenarios for comparisons. Measure collection quality independently from review quality. See the [tool selection and capture protocol](../knowledge-base/deterministic-tools.md).

## Decisions to defer until the pilot

- Which semantic tasks benefit from Jev or Clef rather than ordinary rules or one LLM call?
- How often does additional evidence resolve uncertainty, compared with calling a larger model?
- Which domain judgments do reviewers agree on well enough to automate?
- Can the audit reduce human review effort without increasing unsupported passes?
- Do recommended changes improve resource use per successful user task while preserving accessibility and usability?
- Does the value of repeated auditing justify its own collection and inference costs?

No credible percentage of “WSG automated” or expected carbon savings follows from the research alone. The useful next milestone is a reproducible, independently reviewed pilot report.
