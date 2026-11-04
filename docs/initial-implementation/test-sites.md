# Demo sites and benchmark targets

**Start with adapted STAR fixtures and a pinned local Wagtail bakerydemo, then validate on a small set of real websites.** Finding public sites is straightforward. Establishing correct expected findings, realistic exceptions, and deployment-linked internal evidence is where project-owner input is most valuable.

## What WSG and STAR supply

The published WSG draft supplies requirements and implementation references, rather than a complete labeled collection of audited websites. Its status section states that no preliminary interoperability or implementation reports exist. STAR provides techniques, procedures, examples, and a linked test suite. Its PASS/FAIL table describes whether a test could be performed, not the sustainability verdict for an arbitrary site. [WSG draft](https://www.w3.org/TR/web-sustainability-guidelines/), [STAR](https://w3c.github.io/sustainableweb-ig/docs/star.html).

Rechecking the STAR repository returned the same revision as the earlier research: `393ed62a16580968e2de8af77c68fe9a2e2c675d`. Its JSON lists 116 technique test URLs; 113 correspond to files in that tree, and three paths are missing. The directory contains 119 HTML files overall, including `_template.html` and five additional pages not referenced by those JSON URLs. These counts describe source files, not validated tests or automated WSG coverage. [Pinned JSON](https://github.com/w3c/sustainableweb-ig/blob/393ed62a16580968e2de8af77c68fe9a2e2c675d/docs/star.json), [test directory](https://github.com/w3c/sustainableweb-ig/tree/393ed62a16580968e2de8af77c68fe9a2e2c675d/docs/test-suite).

The [earlier inventory](../knowledge-base/wsg-and-star.md) lists the missing paths. Do not silently substitute similarly named files without reviewing whether they test the intended requirement.

### Useful examples, with adaptation required

| STAR example                                                                                                    | Source observation                                                              | Proposed benchmark adaptation                                                                            |
| --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| [Lazy loading/video facade](https://w3c.github.io/sustainableweb-ig/docs/test-suite/lazy-loading.html)          | Links a YouTube thumbnail to a video; includes an expected-result sentence      | Use local media and compare requests before/after activation; add eager and keyboard-accessible variants |
| [Server compression](https://w3c.github.io/sustainableweb-ig/docs/test-suite/server-side-compression.html)      | Describes a header check; the HTML does not configure its server                | Serve the same body with controlled compressed/uncompressed responses                                    |
| [Public documents](https://w3c.github.io/sustainableweb-ig/docs/test-suite/public-documents.html)               | Policy headings and report links use placeholder destinations                   | Compare empty claims, substantive documents, stale targets, and corroborating records                    |
| [Third-party preferences](https://w3c.github.io/sustainableweb-ig/docs/test-suite/third-party-preferences.html) | Consent buttons have no handlers or controlled resource-loading behavior        | Implement a local third-party service and verify request differences between states                      |
| [Refresh frequency](https://w3c.github.io/sustainableweb-ig/docs/test-suite/refresh-frequency.html)             | Sets cookies without explicit expiry attributes and presents a retention policy | Test whether an auditor distinguishes policy text, browser storage, and actual deletion evidence         |

These observations come from source inspection, not browser execution. The [consent source](https://github.com/w3c/sustainableweb-ig/blob/393ed62a16580968e2de8af77c68fe9a2e2c675d/docs/test-suite/third-party-preferences.html) and [retention source](https://github.com/w3c/sustainableweb-ig/blob/393ed62a16580968e2de8af77c68fe9a2e2c675d/docs/test-suite/refresh-frequency.html) are especially useful examples of why an evaluator must check behavior rather than trust the visible claim. Session cookies lacking explicit expiry do not, by themselves, prove indefinite retention or a backend policy violation.

Treat upstream assertions as test-author intent to review. Build paired correct, defective, exempt, and incomplete versions. For blind evaluations, remove answer-bearing test titles, assertions, comments, and explanatory sentences from the agent-visible variant; preserve provenance and expected outcomes in the protected verifier. Keep ordinary policy claims in the page when judging those claims is the task.

Host assets and supporting services locally so YouTube availability or a remote hosting configuration does not determine the expected answer. Use a server capable of controlling response headers and state; a static HTML archive alone cannot provide compression, cache, consent, polling, and backend-retention ground truth.

## A realistic controlled application

**Wagtail bakerydemo is the first application candidate.** It provides a runnable CMS example with content pages, images, galleries, search, forms, and source code, with documented local/Docker setup. That supports the same audit task with and without access to implementation details. This is a proposal based on its documented features, not a claim that its existing implementation is a known-good or known-bad sustainability reference. [Bakerydemo](https://github.com/wagtail/bakerydemo).

Pin a revision, dependencies, database/media seed, and production-like serving configuration. Define a short journey such as finding a bread, opening its detail page, and locating a store. Record known observations, then introduce one reviewed defect at a time in benchmark-only variants: an oversized image, eager offscreen media, repeated requests, or an incorrect cache policy. Include legitimate exceptions and clean controls to expose over-reporting.

For the public-only variant, expose the running application over the fixture network but keep its source outside the agent container. For source-assisted variants, mount the matching checkout; add stale configuration and conflicting documentation deliberately in separate cases. Never expose the injected-defect manifest or reference findings to the agent.

The [headless bakerydemo](https://github.com/wagtail/bakerydemo-headless) is a useful later addition for a Next.js frontend over the CMS API. Use it to diversify implementation patterns; do not assume that a headless architecture is intrinsically better or worse. Compare equivalent content, functionality, and serving modes before attributing differences to architecture.

The existing [Wagtail bakerydemo archive](https://github.com/thibaudcolas/wagtail-bakerydemo-archive) offers static snapshots across versions. It could help frozen DOM, accessibility, and presentation reviews. A static snapshot does not preserve the original server behavior or all interactions, so it cannot replace the runnable app for network and task-completion tests.

## Real-world validation candidates

The owner selected **guide.wagtail.org and wagtail.org**. They know both sites well and report prior sustainability-focused improvements. Prioritize these two content-focused sites for false-positive review and practical feedback; do not convert that history into passing labels. The [first executable slice](first-slice.md) records the initial bounded sample.

Real sites help reveal missing assumptions; they do not arrive with reliable sustainability answer keys. Keep live-site results separate from the frozen benchmark and review findings before treating them as labels.

| Candidate                                                                       | Proposed small sample                                                       | Research value                                                                                                 |
| ------------------------------------------------------------------------------- | --------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| [LOW←TECH Magazine](https://solar.lowtechmagazine.com/about/the-solar-website/) | About page and two articles                                                 | Explicitly documented design/hosting choices; assess nuanced tradeoffs without presuming all requirements pass |
| [GOV.UK](https://www.gov.uk/renew-adult-passport)                               | A public guidance journey through related information pages                 | Task-oriented information, links, and a clear user purpose; stop before the transactional service              |
| This documentation project                                                      | Locally served production build, homepage, research page, search/navigation | Source is available and controlled; verify framework behavior and test source-assisted diagnosis               |
| The two owner-nominated Wagtail sites                                           | Homepage, an important content/product page, and a real user task           | Owner knowledge can validate necessity, deployment identity, and proposed fixes                                |

LOW←TECH documents its static design and solar hosting, including possible offline periods. Treat availability as a capture outcome, and its descriptions as claims to corroborate within the available evidence. A sustainability-oriented site is a useful contrast case, not a universal passing control. [Website explanation](https://solar.lowtechmagazine.com/about/the-solar-website/).

For each live target, save the sample rationale, capture date, locale, viewport, consent/cache state, URLs, task, and successful-completion condition. Use a few bounded journeys rather than a full crawl. A collection error must not become a negative sustainability judgment. Repeated load testing or transactional interactions are unnecessary for this initial validation.

## Recommended first corpus

1. **Six to eight controlled cases:** adapt STAR ideas for media, compression, caching, consent, policy evidence, and incomplete collection. Each has a reviewed expected result and at least one contrasting variant.
2. **One pinned application:** bakerydemo, with a short public journey and matched source-assisted evidence. Reuse those variants across the relevant twelve benchmark families.
3. **Two initial live targets:** guide.wagtail.org and wagtail.org, starting with the guide homepage/image-management instructions and the Wagtail homepage/sustainability page. Other candidates can diversify a later sample.

The case counts are an initial proposal, not a statistically sufficient release benchmark. The twelve benchmark families cover different questions; they do not require twelve distinct websites. Execute model-bearing comparisons through Harbor with the required Neuralwatt/DeepSeek and Codex arms once the fixtures and graders are ready.

No extra URLs are needed to begin. The most valuable optional contribution is one or two sites whose purpose and implementation the project owner knows, plus an important user journey and any known exceptions or past audit findings. Public-only sites are sufficient; a matching code snapshot or a few internal documents would additionally enable the paired-context experiment.

The subsequent [executable slice](first-slice.md) implements original controlled fixtures and measures the two selected Wagtail sites. Bakerydemo remains a later application candidate. Live observations are not benchmark answer keys.
