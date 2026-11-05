# Project assessment

**The project demonstrates a useful agent-led sustainability audit, but it is still a developer-operated preview.** The strongest parts are evidence preservation, deterministic calculations, specialist review contracts and readable reports. The next milestone is making that workflow reliably usable from an installed skill, with less coordinator repair and better evidence for qualitative conclusions.

The goal remains the experience of claude-seo or accessibility-agents: install, supply a URL, answer relevant scope questions, and receive an actionable audit. WSG supplies the subject matter; STAR informs the evaluation process. Measurements support the audit, while agents investigate context and interpret requirements that cannot be reduced to numeric thresholds.

This assessment inspects implementation, skills, tests, published reports and benchmark artifacts at [revision a9c952b](https://github.com/thibaudcolas/web-sustainability-agents/tree/a9c952b6d99b21c26488af27fbb8781bc75cdceb). It also revisits the reference projects and current methodology documents. It does not run new live audits, paid model comparisons or a clean installation in another harness. Recommendations below are engineering judgments, not new benchmark results.

## Fit against the goals

| Goal                                           | Current evidence                                                                                              | Assessment                                                                                             |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Ask an agent for an audit                      | One discovery skill, progressive role loading, plugin manifests and a project installer                       | Implemented entry point; clean installation through final delivery is unvalidated                      |
| Deterministic evidence plus LLM interpretation | Browser measurements, interactions, disclosures, source capture, three review roles and deterministic scoring | Working architecture; collection completeness is the main immediate weakness                           |
| WSG breadth beyond performance                 | 43 scoped checks across 40 guideline groups, including ten contextual checks                                  | Meaningful breadth, but every method is partial and criterion mapping is incomplete                    |
| STAR-informed evaluation                       | Scope, page selection, task definitions, frozen evidence and reproducibility details                          | Partial process support; current small samples do not meet STAR's broader sampling advice              |
| Specialist skills and subagents                | Setup, collection, evidence, guidelines, claims and reporting instructions; native review handoffs            | Real use in reports; domain expertise remains concentrated in one guideline reviewer                   |
| Harness independence                           | Shared files and CLI, native Claude descriptors, sequential fallback, four installer targets                  | Portable contracts; no demonstrated end-to-end equivalence across hosts                                |
| Public-first, source-assisted auditing         | Two public-only reports and two reports with selected source evidence                                         | Working modes; no matched comparison establishes the benefit of source access                          |
| Evaluation-driven improvement                  | Harbor campaigns, controls, high-reasoning Sol and Neuralwatt DeepSeek results                                | Good development infrastructure; limited independent labels and no complete current-workflow benchmark |
| Jev/Clef decisions                             | Research, candidate tasks and an offline request preview                                                      | No operational integration or sustainability-domain inference results                                  |

## What is worth keeping

The separation of observation, judgment, calculation and writing is sound. A reviewer cites captured evidence; a scorer computes outcomes; a report writer explains them. Public evidence, candidate source code, modeled carbon and client-energy estimates retain distinct meanings. These boundaries are more valuable than adding another measurement tool without a clear question.

The latest reports demonstrate actual Sol/high specialist reviews and contextual evidence, rather than merely documenting a proposed workflow. Four reports now cover different content services, including a project hosted below a shared origin. They exercise useful edge cases, but all belong to the Wagtail ecosystem and are predominantly documentation or content sites. This is development diversity, not broad external validation. [Reports and evidence](../reports/README.md)

The implementation already adopts the reference projects' central patterns: one coordinator, progressively loaded instructions, bounded specialist outputs and deterministic report generation. The inspected claude-seo audit additionally routes to domain specialists according to site features. Accessibility-agents provides structured findings and defect-oriented evaluation examples. We should adopt those behaviors selectively; their crawl sizes, scores and domain accuracy do not transfer to sustainability. [Audit-project comparison](../knowledge-base/local-projects.md), [orchestration comparison](../knowledge-base/agent-orchestration.md)

## Coverage: what the numbers actually mean

The current catalog contains **22 browser checks, three disclosure/hosting checks, eight source checks and ten contextual checks**. With all contextual checks selected, the public-only catalog offers **35 checks across 32 guideline groups**; adding source checks yields **43 across 40 groups**. Actual audits select a subset. The broader 46/71 figure in older coverage summaries combines historical and current methods and should not be used as the current product's coverage headline. [Check reference](../reference/checks.md)

No complete guideline has been verified. Ten contextual expectations identify criterion IDs; the other 33 expectations primarily map to guideline groups. Until each expectation names the clauses it assesses, we cannot calculate an honest implemented-criterion percentage.

The separate inventory classifies all **197 criteria**: 3 static analysis, 6 automated, 48 manual quantitative, 50 manual qualitative and 90 consulting. These are project planning classes. They show why a browser-performance scanner alone cannot achieve the goal; they do not establish that the classified techniques have been implemented. Agents can investigate all five classes when appropriate evidence exists. [Current auditability inventory](../knowledge-base/assessment-crosswalk.md)

Published results illustrate the difference between breadth and resolved evidence:

| Report                                              | Pages selected | Scoped groups checked / 71 | Pass | Problem | Unknown |
| --------------------------------------------------- | -------------: | -------------------------: | ---: | ------: | ------: |
| [Wagtail guide](../reports/guide.md)                |              6 |                         31 |   16 |       3 |      12 |
| [Wagtail.org](../reports/wagtail.md)                |              7 |                         32 |   15 |       4 |      13 |
| [Wagtail documentation](../reports/wagtail-docs.md) |              9 |                         26 |    4 |       2 |      20 |
| [Draft.js exporter](../reports/draftjs-exporter.md) |              7 |                         24 |    8 |       2 |      14 |

These are different samples and rubric selections, not comparable site rankings. In particular, the documentation score of 15.38/100 reflects four passes, two problems and twenty unknowns. It is largely an evidence-resolution result, not evidence of unusually poor sustainability. Keep the existing formula reproducible, but test whether owners understand the counts and coverage beside it before giving the percentage more visual authority. [Score semantics](../knowledge-base/audit-scoring.md)

### STAR needs a more explicit boundary

STAR covers scope, exploration, sampling, evaluation and reporting. Its sampling advice recommends evaluating all pages/states where feasible, particularly below 1,000 pages; otherwise it describes random samples of 10–20%. Our 5–10 deliberately selected pages are a useful bounded diagnostic, not implementation of that sampling advice. STAR also emphasizes interactions and remedies that do not interfere with other requirements. [STAR evaluation methodology](https://w3c.github.io/sustainableweb-ig/docs/star.html)

Keep the small default. Record template/task/state coverage and describe it as a scoped audit. Add a separate, deliberately planned comprehensive evaluation mode only when needed. A count of links to STAR techniques would not establish process coverage. The [WSG draft](https://www.w3.org/TR/web-sustainability-guidelines/) also addresses people and organizational decisions, so traffic and energy reductions cannot stand in for its wider scope.

## Where the workflow still depends on its developer

### Deterministic tools have distinct jobs

| Tool or component                               | Current role                                                           | Main limit                                                                              |
| ----------------------------------------------- | ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Custom Playwright collectors                    | Transfer phases, page states, task actions and screenshots             | Incomplete requests, challenges and readiness still need coordinator interpretation     |
| PyPI Wappalyzer                                 | Technology hints for contextual advice                                 | A fingerprint does not establish deployment versions or justify a fix                   |
| Disclosure discovery and carbon.txt interpreter | Find statements and preserve declared relationships                    | No full carbon.txt schema certification or independent operational hosting verification |
| CO2.js, SWDM v4 and Digital Carbon Ratings      | Reproducible transfer-based estimates and eligible ratings             | Models depend on complete, correctly scoped inputs                                      |
| GreenFrame and co2-runner                       | Optional resource-model estimates and separate CPU-package experiments | Different boundaries; sitespeed.io protocol comparison remains backlog work             |

The [tool reference](../knowledge-base/deterministic-tools.md) distinguishes candidate tools from integrated collectors. The immediate need is reliable observations and justified interpretation, not a larger tool list.

### Collection and recovery

The latest captures exposed security challenges, navigation failures, uncertain search readiness and incomplete worker-transfer accounting. These limits were preserved correctly, but they left many checks unknown. More pages under the same conditions would mostly produce more incomplete evidence.

The next collector work should distinguish intended content from a challenge/error document, establish task readiness, capture worker traffic correctly and recover through bounded, recorded attempts. Recovery must preserve the original first visit. Validate these on controlled fixtures before expanding live crawling. The existing source checks and contextual records should remain usable even when a browser branch fails. **B01/B15/B35** in the [backlog](backlog.md).

GreenFrame is implemented and used, but normally on only 1–3 selected pages with three repetitions. It estimates client and network energy from a resource model; co2-runner's CPU-package counter has a different boundary. Neither makes all report rows measured electricity, and they are not interchangeable with SWDM. Matched energy protocols, realistic page mixes and traffic calibration remain open. Optional energy work should not block a useful baseline audit. [Measurement reference](../knowledge-base/energy-and-traffic.md), [GreenFrame](../knowledge-base/greenframe.md)

### Orchestration and installation

The shared CLI is the right boundary. It lets each host use its own agent capabilities while retaining the same evidence and result formats. There is no need to select another orchestration framework before testing it.

However, the implemented orchestration tool governs **three review tasks**, not the whole audit. Its `status` reports review acceptance; it does not describe setup, collection, supplements, report delivery or recovery. Setup and report agents have instructions, but not equivalent validated lifecycle contracts. Partial work and retries rely substantially on coordinator discipline. [Orchestration implementation](https://github.com/thibaudcolas/web-sustainability-agents/blob/a9c952b6d99b21c26488af27fbb8781bc75cdceb/audit/orchestrate.py)

There is also a concrete enforcement gap: `workflow score` validates the final review and frozen evidence, but does not require accepted specialist results or reconciliation. The reconciliation receipt records responses to issues without binding the resulting final review. This is reasonable for a low-level calculation tool, but the full audit needs a completion gate that distinguishes a reconciled audit from an independently supplied review. Metadata stating a model or execution mode is not proof of the actual execution. **B36**. [Scoring implementation](https://github.com/thibaudcolas/web-sustainability-agents/blob/a9c952b6d99b21c26488af27fbb8781bc75cdceb/audit/workflow.py#L754-L827)

Installation resolves paths independently of the working directory, which is good. But `prepare` installs the workspace's development environment and npm dependencies in the runtime checkout; `doctor` checks executable locations and directory presence, not a successful browser launch. The project installer points to a retained checkout, and reinstalling conflicts with its no-overwrite behavior. Update, removal, cache replacement and minimal-runtime installation need a tested lifecycle. **B28**. [Runtime helper](https://github.com/thibaudcolas/web-sustainability-agents/blob/a9c952b6d99b21c26488af27fbb8781bc75cdceb/.agents/skills/sustainability-audit/scripts/runtime.py), [installer](https://github.com/thibaudcolas/web-sustainability-agents/blob/a9c952b6d99b21c26488af27fbb8781bc75cdceb/scripts/install_audit.py)

The latest reports also needed coordinator-owned archive publication and an explicitly separate scoring campaign after a scorer fix. That preserved provenance, but required repository knowledge. Packaging, portable report links and version-aware recomputation should be normal CLI operations. **B29/B37**. Keep the current host-native design; validate Codex and Claude Code first, then OpenCode/pi. Installer options are not a support matrix of completed audits.

## Qualitative review needs deeper tasks, not dozens of new agents

The three review roles primarily separate **guideline judgment, measurement scrutiny and claim scrutiny**. Only one worker owns all selected guideline outcomes. The contextual skill improves evidence selection and scopes, but is not a specialist in every domain it covers.

Two focused review modules are worth testing next:

- **Experience and content:** task completion, navigation, content usefulness, media necessity, constrained access and the tradeoffs of proposed changes. Evidence should include completed tasks and specific content, not only DOM features.
- **Governance and lifecycle:** distinguish commitments, performed reviews, resulting decisions and progress; investigate content/data lifecycle and service retirement within a defined service and period.

Start as task-specific references under the existing roles. Compare them with the current general review and a no-skill baseline on the same evidence and budget. Promote them to optional specialists when the comparison shows useful gains. Keep one authoritative outcome per check, with claims/evidence reviewers able to challenge it. **B32/B33/B34**.

The next qualitative failure to solve is often **finding the right evidence**, not interpreting an already selected paragraph. Test public records, missing records, contradictory records and supplied internal context. A walkthrough cannot replace research with affected users; a missing public document cannot establish that an organization lacks the practice. Conversely, a requirement for a published statement should not be inflated into proof of operational execution. [Qualitative evaluation design](../evaluation/design.md#next-qualitative-validation)

## Put Jev/Clef to work in one bounded experiment

There is no decision-model adapter in the audit pipeline and no completed Jev/Clef campaign. The existing jevotron preview validates request construction only. Its useful pattern is cached, traceable review of structured records; jev-ultrafast demonstrates constrained action selection with independent execution checks. Neither project's results establish WSG accuracy. [Decision-model source review](../feasibility-study/decision-model-examples.md)

**First experiment: check whether a proposed finding is supported by its cited evidence.** Supply the exact claim, criterion clause, declared scope, evidence spans and collection limitations. Return `supported`, `contradicted` or `insufficient`, preserving all probabilities. Check hashes, pointers and exact quotations in code first. TypeSafe's [citation-check example](https://docs.typesafe.ai/cookbooks/citation_check.md) provides this decomposition; its [confidence documentation](https://docs.typesafe.ai/confidence.md) explains why a concentrated answer distribution does not itself establish correctness. Clef also exposes typed decisions, but its provider contract must be checked separately. [Clef contract](https://developers.cloudflare.com/workers-ai/models/clef/)

Run this alongside the existing reviews, with no authority to change outcomes or suppress checks. Use TypeSafe Jev and Neuralwatt Clef, plus the required Sol/high and Neuralwatt DeepSeek/high baselines. Include policy-versus-practice, wrong service scope, challenge pages, incomplete measurements and unsupported source/deployment claims. Independently label examples before inference; do not reuse ambiguous recommendation labels unchanged.

Measure unsupported claims missed, supported claims incorrectly flagged, abstention, calibration and total reviewer cost/time. Keep service errors distinct from insufficient evidence. A well-formed answer is not success, and a confidence threshold must earn its use on held-out cases. This experiment can start alongside workflow repairs; it need not wait for every audit feature. **B10**.

Second, consider evidence relevance ranking, testing what the shortlist misses. Adaptive browser actions come later: stabilize scripted readiness and recovery first, then compare drivers with the same tasks and independent success checks. The fast browser demo's existing-profile measurements are not automatically a cold-load sustainability protocol.

## The next benchmark should exercise the product

The four later benchmark families contain **57 development cases**; six original tasks are separate. The latest nineteen-case comparison gives both Sol/high and DeepSeek/high **16/19** complete reports satisfying the strict reference contract. The same three disagreements include known contract ambiguities. Four cases per arm exercise frozen-bundle collection, not the complete live audit. These results do not yet establish superior recommendations, skill benefit, harness parity or robust evidence discovery. [Evaluation results](../evaluation/README.md)

Build one small complete task before a large new comparison. It should start from an installed skill in an unrelated project directory, require one useful scope clarification, explore a controlled website, encounter a recoverable collection failure, complete reviews and deliver a report that opens outside this repository. Then extend to the three execution tasks in the existing evaluation plan.

Use Harbor with the two required high-reasoning model arms. Grade evidence discovery, unsupported findings, useful recommendations, complete artifacts, recovery and user effort separately. Add an externally reviewed hidden set split by site/template; public examples remain development material. After contract repairs, compare skills and source access independently, then repeat a complete task under another harness. A new framework or another large synthetic case count would not answer these questions. **B07/B16/B17/B20/B22/B27/B32/B38**.

## Recommended next milestone

Deliver **one reproducible install-to-report audit** with bounded recovery, a portable output bundle and a truthful completion status. In parallel, map existing checks to criterion clauses and run the small decision-model experiment. Defer a larger crawl, a mandatory new orchestration framework and additional general-purpose evaluators.

The [roadmap](validation-roadmap.md) defines acceptance gates. The [backlog](backlog.md) owns individual changes and distinguishes implemented foundations from unfinished validation. No new architecture choice is needed from the owner to start this work.

## Verification of this assessment

Counts were checked against the current catalogs, published plans/scores and benchmark case files. The pinned WSG reference validator, 171 Python tests and nine JavaScript tests passed. Linting, local links, checked external sources and the strict documentation build passed. `doctor` resolved this checkout and its existing prerequisites; that is a local smoke check, not a clean-install result. Existing site evidence, scores and benchmark results remain unchanged.
