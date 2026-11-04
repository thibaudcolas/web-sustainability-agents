---
tags:
  - sustainability
  - methodology
---

# WSG and STAR as an audit foundation

Reviewed November 3, 2026. This page separates source observations from recommendations for an audit implementation.

WSG and impact-rating links use their latest published `/TR/` addresses, rechecked November 4. Both still identified the October 16 draft at that check. These URLs can advance; retain publication dates, content digests, and pinned supporting data when reproducing an assessment. See the [source inventory](assets/source-inventory.json).

## Documents and authority

| Source                                                                                                              | Role                                                  | Version reviewed                                                              |
| ------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- | ----------------------------------------------------------------------------- |
| [WSG](https://www.w3.org/TR/web-sustainability-guidelines/)                                                         | Guidelines and success criteria                       | Group Note Draft, October 16, 2026                                            |
| [WSG impact ratings](https://www.w3.org/TR/wsg-ir/)                                                                 | Relative impact and timeframe guidance                | Group Note Draft, October 16, 2026                                            |
| [STAR](https://w3c.github.io/sustainableweb-ig/docs/star.html)                                                      | Evaluation methodology, techniques, and test examples | Editor-maintained supporting document; repository pinned in the source ledger |
| [WSG JSON](https://github.com/w3c/sustainableweb-wsg/blob/eb8f8af2178ddce3d28226f90a6e691ccc6af3c8/guidelines.json) | Machine-readable inventory                            | Declares `lastModified: 2026-08-25`                                           |
| [STAR JSON](https://github.com/w3c/sustainableweb-ig/blob/393ed62a16580968e2de8af77c68fe9a2e2c675d/docs/star.json)  | Techniques, procedures, and test URLs                 | Declares `lastModified: 2026-08-04`                                           |
| [Supporting resources](https://w3c.github.io/sustainableweb-ig/docs/resources.html)                                 | Further research and implementation references        | Living resource collection                                                    |

WSG's conformance section is explicitly work in progress. It describes claims at different scopes, including success criteria and guidelines. An audit should identify the exact requirements and scope behind a claim. The draft does not supply a universal numerical certification grade. [WSG conformance](https://www.w3.org/TR/web-sustainability-guidelines/#conformance).

**Implementation recommendation:** call the result a “WSG-aligned assessment” with explicit coverage until the methodology and claim have been reviewed. A useful optimization finding does not require claiming full conformance.

[Digital Carbon Ratings](digital-carbon-ratings.md) provides an additional estimate-based page rating. Keep it separate from WSG conclusions and WSG impact ratings: these describe different things and have different calculation and evidence requirements.

## STAR methodology and its limits

STAR organizes evaluation around scope, exploration, testing or sampling, auditing, and reporting. It addresses page states, third parties, internal information, and non-interference with other requirements. Its techniques are informative: a technique test is not automatically a complete criterion test. [STAR methodology and techniques](https://w3c.github.io/sustainableweb-ig/docs/star.html).

Two details need explicit implementation decisions. STAR suggests whole-site evaluation where feasible, especially below 1,000 pages, and random samples of 10–20% for larger sites. It also discusses missing internal knowledge as a failure point. These are source recommendations, not evidence that a fixed sample percentage guarantees representativeness. [STAR](https://w3c.github.io/sustainableweb-ig/docs/star.html).

For this project's proposed methodology:

- Record inaccessible information as **unknown**, with a separate explanation of whether it prevents a claim. Do not infer that the underlying practice failed merely because an external auditor cannot observe it.
- Sample templates, important journeys, authenticated states, device profiles, consent states, and content types. Add a reproducible random sample to expose overlooked cases.
- Record the sampling seed, exclusions, coverage, and reasons for additional captures. Explain any departure from STAR's sampling advice.
- Keep performance captures sequential or isolated where parallel activity would distort results. Parallelize analysis of saved evidence instead.
- Treat recommendations affecting accessibility, privacy, security, or task completion as requiring cross-checks before adoption.

This is a proposed adaptation, not a claim that STAR already specifies this workflow.

## Inspection of the machine-readable sources

The following are reproducible structural observations from the pinned JSON files, not estimates of how much WSG can be automated:

| Section                         | WSG guidelines | WSG criteria | STAR techniques |
| ------------------------------- | -------------: | -----------: | --------------: |
| User experience                 |             17 |           48 |              35 |
| Development                     |             16 |           45 |              34 |
| Hosting and infrastructure      |             12 |           34 |              17 |
| Business and product management |             26 |           70 |              30 |
| Total                           |             71 |          197 |             116 |

All 116 technique records contain a `testSuite` URL. Of their IDs, 112 exactly match criterion IDs in the WSG JSON. Four differ:

| STAR ID                  | WSG JSON ID           | Published WSG HTML observation |
| ------------------------ | --------------------- | ------------------------------ |
| `avoiding-overburdening` | `avoid-overburdening` | Uses the STAR spelling         |
| `printed-documents`      | `printing-documents`  | Uses the STAR spelling         |
| `optimized-documents`    | `optimize-documents`  | Uses the STAR spelling         |
| `optimized-delivery`     | `optimize-delivery`   | Uses the STAR spelling         |

The dated publication contains 197 success-criterion headings, but these four JSON anchors do not resolve within that publication. Matching counts therefore do not establish interchangeability between JSON and HTML. A human-reviewed alias map should preserve both source identifiers and the chosen canonical identifier.

Three declared fixture paths are absent from the pinned repository tree and returned HTTP 404 on November 3, 2026:

- `docs/test-suite/energy-relevant-apis.html`
- `docs/test-suite/appropriate-implementation.html`
- `docs/test-suite/disclosure-reporting.html`

The [source ledger](../feasibility-study/sources.md#reproducing-the-inventory) provides the method and a downloadable manifest. Exact ID overlap is an integration diagnostic. It does **not** prove semantic equivalence, technique completeness, or reliable automation.

## What the test suite establishes

STAR's table labels whether a test could be produced or performed; its `PASS` cells are not audit results for an arbitrary website. [STAR test suite](https://w3c.github.io/sustainableweb-ig/docs/star.html).

Inspection of three actual fixtures illustrates the engineering work still required:

| Fixture                                                                                                    | Observation                                          | Proposed adaptation                                                                                        |
| ---------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| [Server compression](https://w3c.github.io/sustainableweb-ig/docs/test-suite/server-side-compression.html) | A small page describes checking response encoding    | Capture negotiated headers and bytes; define exemptions and negative examples                              |
| [Public documents](https://w3c.github.io/sustainableweb-ig/docs/test-suite/public-documents.html)          | Example policy headings and placeholder report links | Verify destination content, scope, dates, and supporting records; distinguish a policy from implementation |
| [Lazy loading](https://w3c.github.io/sustainableweb-ig/docs/test-suite/lazy-loading.html)                  | An example video facade and a prose assertion        | Compare network activity before and after activation; also test keyboard and accessible-name behavior      |

These are useful seeds for fixtures, not a complete executable auditor. Do not let a model see their answer-bearing assertions during a blind evaluation. Do not copy their markup as an accessibility reference.

Use an explicit test-rule format. W3C's [ACT Rules Format 1.1](https://www.w3.org/TR/act-rules-format/) provides a relevant precedent: rule inputs, applicability, expectations, assumptions, examples, versioning, and outcome mappings. Its applicability to this project is architectural; adopting that structure would not make sustainability rules W3C-approved ACT rules. The [ACT test design guidance](https://act-rules.github.io/pages/design/test-cases/) also recommends positive and negative cases for each condition.

## Impact, coverage, and measured emissions

The impact-ratings document provides ordinal ratings across planet, people, and prosperity, plus a timeframe and a derived prioritization score. It states that guideline ratings are not compounded. These values are useful planning inputs; they are not measured emissions reductions. [WSG impact ratings](https://www.w3.org/TR/wsg-ir/).

Keep four reporting dimensions separate:

1. **Coverage:** requirements and states examined, with unknowns visible.
2. **Findings:** observed failures or improvement opportunities and their evidence.
3. **Priority:** expected benefit, reach, effort, reversibility, and dependencies.
4. **Measurements:** bytes, requests, runtime, energy where available, and explicitly modeled emissions.

Do not add ordinal impact ratings into an apparent physical savings total. Do not average unsupported organizational results into a reassuring technical score. If a local priority score is helpful, publish its formula and label it as this project's prioritization policy.

## Measurement and tooling options

| Tool or methodology                                                                                    | Useful evidence                                               | Boundary                                                                                  |
| ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| [Lighthouse](https://developer.chrome.com/docs/lighthouse/performance/performance-scoring)             | Performance metrics and diagnostics                           | Score varies with conditions and represents performance, not whole-service sustainability |
| [Sitespeed.io sustainability plugin](https://www.sitespeed.io/documentation/sitespeed.io/sustainable/) | Repeatable browser measurements with emissions estimates      | Preserve its configuration and model version                                              |
| [CO2.js](https://developers.thegreenwebfoundation.org/co2js/overview/)                                 | Modeled carbon associated with data transfer                  | An estimate, not direct measurement of a particular user's device and server              |
| [Greencheck](https://developers.thegreenwebfoundation.org/api/greencheck/v3/check-single-domain/)      | A domain's presence in green-hosting data                     | A lookup cannot establish every hosting or supply-chain practice                          |
| [EcoIndex](https://www.ecoindex.fr/en/how-it-works/)                                                   | Comparative resource-efficiency indicators                    | Keep its methodology separate from WSG assessment                                         |
| [Ecograder](https://ecograder.com/how-it-works)                                                        | Existing combination of website sustainability signals        | Useful comparator; its overall grade is not a WSG outcome                                 |
| [Software Carbon Intensity](https://sci.greensoftware.foundation/)                                     | Emissions per functional unit with a declared system boundary | Requires energy, carbon-intensity, and embodied-emissions inputs or explicit estimates    |

The Sustainable Web Design Model has changed its estimation formula and underlying assumptions over time. A change in an emissions model can therefore alter a reported number without any website change. Preserve raw measurements so both old and new models can be applied to the same evidence. [Green Web Foundation explanation of model changes](https://www.thegreenwebfoundation.org/news/understanding-the-latest-sustainable-web-design-model-update/).

For intervention studies, compare resource use per **successful task**, not only per page view. Report absolute activity as well: lower resource use per transaction can coexist with higher total consumption. Include rendering, transfer, backend work where accessible, and the audit's own resource use in the declared boundary.

## Adjacent methodologies

The [2024 general policy framework for ecodesign of digital services](https://www.arcep.fr/uploads/tx_gspublication/general_policy_framework_for_the_ecodesign_of_digital_services_version_2024.pdf), often called RGESN, offers another structured ecodesign assessment reference. Its [declaration example](https://www.arcep.fr/fileadmin/user_upload/nos-sujets/environnement/rgesn_2024_ecodesign_declaration_example.html) is useful for designing evidence and disclosure outputs. A future crosswalk should compare the exact obligations and evidence, rather than assume that related WSG and RGESN criteria are interchangeable.

The [agentic audit proposal](../feasibility-study/README.md) uses WSG as its primary requirements inventory, STAR as supporting methodology, and these other tools as evidence producers or design references.
