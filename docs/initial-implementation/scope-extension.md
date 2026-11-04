# Broader WSG and STAR evidence

The expanded audit adds sitemap inventory, a reproducible page sample, metadata, preference states, expected files, error recovery, and public-policy review. It follows the [expanded model comparison](expanded-benchmark.md); its new observations have not themselves been through another model campaign. The coordinator reviewed them for the earlier audit drafts, which have since been removed. This page retains the experiment’s original observations; [current reports](../reports/README.md) use separate fresh captures.

## Scope and sampling

The [published collection](assets/scope-extension.json) records URLs, selection reasons, response status, browser version, snapshots, excerpts, source hashes, and collection limits. This is a metadata and behavior probe, not a new transfer or energy measurement.

| Evidence                                                 | Guide | Wagtail.org |
| -------------------------------------------------------- | ----: | ----------: |
| URLs advertised by retrieved sitemap inventory           |   156 |         525 |
| Purposefully selected content pages                      |     4 |           5 |
| Additional pseudo-random content pages                   |     2 |           2 |
| Missing-path probes                                      |     1 |           1 |
| Successful content-page responses                        |     6 |           7 |
| DOM state snapshots, including error pages               |    15 |          17 |
| Guidelines with partial evidence, including earlier work |    14 |          17 |
| Guidelines not assessed                                  |    57 |          54 |

The [guide register](assets/coverage/guide.wagtail.org-432853f7b5d8.json) and [Wagtail.org register](assets/coverage/wagtail.org-fa043133d284.json) each enumerate all 71 guidelines in the inspected draft. Counts describe evidence availability, not passes, coverage of every criterion, or a sustainability score. Each row links directly to its guideline and states its evidence boundary. The draft version and source hashes are retained.

The purposeful guide sample covers the homepage, image management, page management, and the Wagtail 8.1 release article. The additional hash-ordered sample selected an Icelandic-route Wagtail 7.3 article and a French accessibility article. Wagtail.org's purposeful sample covers the homepage, sustainability, digital emissions, privacy, and accessibility; the additional sample selected the 2025 roundup and Google Summer of Code sustainability articles. Full URLs and the deterministic seed are in the artifact. Random selection is without replacement from same-origin sitemap URLs allowed by robots.txt, excluding purposeful selections.

[STAR's evaluation methodology](https://w3c.github.io/sustainableweb-ig/docs/star.html) informs scope definition, exploration, sampling, assessment, and reporting. It favors complete evaluation when feasible, especially below 1,000 pages, and suggests a 10–20% random sample for larger or complex sites. Our small development sample deliberately falls short of that guidance. A sitemap is an advertised URL inventory, not proof of all templates, assets, states, or service boundaries. We have not completed all interactions on selected pages or an organizational evaluation.

## Quantitative collection

Fresh Chromium contexts use a 1,280 × 800 viewport, light color scheme, and no reduced-motion preference. After load and 500 ms, the collector records the DOM; it then enables dark/reduced-motion preferences and records another snapshot after 200 ms. Each homepage is also reloaded with those preferences, followed by 300 ms. A 50-second total page deadline and bounded cleanup preserve partial results if a probe fails.

All 13 selected content pages returned 200, and both deliberate missing paths returned 404. Each content page had a nonempty title, canonical URL, language attribute, one H1, one main landmark, and alt attributes on its images. These presence checks do not validate semantic quality, meaningful alternatives, or accessibility conformance. The guide error page had an empty language attribute. The French guide article and Wagtail digital-emissions page lacked nonempty descriptions.

Both homepages retained light body colors after the in-page preference change, then adopted dark body colors after reload. Both sites exposed reduced-motion CSS queries; Wagtail.org also exposed print and forced-colors queries. No running animation was observed at the capture points, so this does not demonstrate that an active animation responds correctly to reduced motion. No display-energy saving was measured.

Robots files, sitemaps, and icons were retrievable for both sites. Wagtail.org also served carbon.txt, security.txt, and its declared manifest at a hashed static URL. A 404 at `/site.webmanifest` therefore does not mean that its manifest is missing. The guide's checked carbon.txt, security.txt, root manifest, and OpenSearch paths returned 404; no manifest or search-description link was detected on its homepage. Applicability requires review rather than automatically failing every missing conventional path. Retrieval does not validate manifest, security.txt, or robots semantics.

## Qualitative review and source contribution

| Review area                                                                                                                       | Evidence and bounded conclusion                                                       | Next useful check                                                                                            |
| --------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| [WSG 3.6: Semantics](https://www.w3.org/TR/web-sustainability-guidelines/#ensure-code-follows-good-semantic-practices)            | Useful basic landmarks on sampled content; guide 404 language is empty                | Add a request-language fallback for non-page responses, then test localized error pages                      |
| [WSG 3.8: Metadata](https://www.w3.org/TR/web-sustainability-guidelines/#structure-metadata-for-machine-readability)              | Most descriptions are present; two sampled content pages have no nonempty description | Review meaningful descriptions and translation intent; do not infer emissions savings                        |
| [WSG 3.9: Preferences](https://www.w3.org/TR/web-sustainability-guidelines/#use-media-queries-that-support-sustainability-goals)  | Reload reveals dark-mode support that a change-only probe misses                      | Preserve initial preference support; test live changes, print output, contrast, and active motion separately |
| [WSG 3.13: Beneficial files](https://www.w3.org/TR/web-sustainability-guidelines/#include-expected-and-beneficial-files)          | Working sitemap/icon resources and declared Wagtail manifest                          | Validate content, maintenance, and applicability before recommending additional files                        |
| [WSG 4.4: Error recovery](https://www.w3.org/TR/web-sustainability-guidelines/#setup-necessary-error-pages-and-redirection-links) | Correct 404 responses; guide retains navigation; Wagtail offers a search form         | Complete keyboard/search recovery rather than treating the form's presence as success                        |
| [WSG 5.18: Data practices](https://www.w3.org/TR/web-sustainability-guidelines/#promote-responsible-data-practices)               | Wagtail privacy page describes Torchbox and scopes itself to the Torchbox website     | Clarify its applicability to Wagtail.org and corroborate actual processing practices                         |
| [WSG 5.25: Open source](https://www.w3.org/TR/web-sustainability-guidelines/#use-and-contribute-to-open-source)                   | Supplied guide source has a redistribution license and contribution guidance          | Keep code licensing separate from content licensing and wider organizational practice                        |

The public sustainability and digital-emissions pages also provide scoped claims relevant to [WSG 2.1](https://www.w3.org/TR/web-sustainability-guidelines/#identify-assess-disclose-review-and-mitigate-sustainability-impacts) and [3.1](https://www.w3.org/TR/web-sustainability-guidelines/#set-goals-based-on-performance-and-energy-impact). Their existence does not verify operational targets or continuous execution.

Source inspection explains two runtime observations. Both projects' `blocking.js` files consult the OS color preference during initialization. The guide base template derives `lang` from `self.locale.language_code`, while the error template inherits it without a language override. This is a plausible cause of the observed empty 404 language; the active request language is a candidate fallback. Wagtail's print stylesheet and error template corroborate print rules and recovery-form markup. The source artifact records revisions, dirty status, and exact inspected-file hashes. Deployment identity remains unknown; these are candidate implementation locations, not verified production fixes.

The automatic register treats retrieved policy routes as candidates requiring this semantic review. Failed observations and redirects to a homepage cannot establish a policy or recovery behavior. Organizational claims remain unverified without operational evidence.

## Reproduce and extend

```sh
uv run --locked --script audit/scope.py \
  --publish docs/initial-implementation/assets/scope-extension.json
npx prettier --write docs/initial-implementation/assets/scope-extension.json
uv run --locked --script audit/coverage.py
```

Formatting the source artifact before generating registers preserves their exact source digest. Raw observations remain under ignored `.audit-work/`; publication removes URL credentials, queries, and fragments. Link-fragment behavior must be checked against raw observations rather than inferred from the sanitized links.

The next expansion should exercise successful recovery and preference interactions, independently verify recommendation usefulness, and select additional templates and mobile/assistive contexts. Procurement, retention/deletion execution, infrastructure utilization, and other organizational questions need supplied records or owner evidence. See the [ordered backlog](backlog.md).
