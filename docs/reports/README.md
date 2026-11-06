---
search:
  boost: 2
---

# Example audit reports

## Wider content sample

- [Tate](tate.md): seven gallery, exhibition, editorial and policy pages, including its website sustainability statement.
- [NHS](nhs.md): seven public health-information pages, including exercise videos and analytics choices. No diagnosis, account or booking tasks.
- [Google Blog](google-blog.md): six editorial, media and newsletter pages, including reduced-motion behavior and corporate sustainability claims.
- [W3C](w3c.md): seven standards, accessibility and organizational pages, with a catalogue-to-WCAG reading task.
- [Low-tech Magazine](lowtech.md): seven solar-powered publishing pages, including an illustrated guide and historical design decisions.

These audits cover 34 pages with public contextual evidence, separate evidence/guideline/claims reviews, and report-writing agents. All reviewers used GPT-6.1 Sol with high reasoning. Four reports include a separate two-page GreenFrame sample with three repetitions per page; W3C's energy attempts failed and remain unavailable. Each report includes a CrUX-based annual footprint scenario, with its assumptions and limits.

This is broader live experience, not a validated benchmark or site league table. The sites have different purposes, selected checks and evidence periods. In particular, Low-tech Magazine's historical design and governance evidence does not establish current operating practice. Transactional completion, multilingual tasks and representative user research remain outside this sample.

## Wagtail examples

- [guide.wagtail.org](guide.md): the Wagtail editor guide.
- [wagtail.org](wagtail.md): the Wagtail project website.
- [docs.wagtail.org](wagtail-docs.md): nine pages of developer documentation, public maintenance records and a three-page energy sample.
- [Draft.js exporter](draftjs-exporter.md): seven documentation pages under a shared GitHub Pages host, with a homepage energy sample.

Each report records its own sample, measurements, specialist reviews and available context. It leads with a scoped score, results by WSG area, first-load transfers and a separately bounded GreenFrame energy sample, then priorities, evidence, next auditing steps and reproducibility. None is a whole-site sustainability certification. See [how to read the score](../knowledge-base/audit-scoring.md) and [current check coverage](../reference/checks.md).

The developer-documentation reports include selected contextual checks in their scores and use public evidence without source checkouts. Some automated navigations encountered network errors, rate limits or security challenges; those gaps remain explicit unknowns. The Guide and Wagtail.org reports use the earlier check scope with a separate contextual preview. Their scores are not directly comparable measures of site quality.

For feedback, identify the site and check ID, then explain whether the problem is the observed fact, missing evidence, interpretation, priority or proposed fix. We can trace that feedback to a collector, skill, rubric or eval case.

Earlier audit drafts have been removed. Historical experiments and their frozen evidence remain in the [implementation project](../initial-implementation/README.md); previous report text remains in Git history. Their samples and methods differ from these reports, so their scores are not a site-improvement trend.

To create a report, use [the audit guide](../using/README.md). To judge the audit system itself, use [the evaluation project](../evaluation/README.md).
