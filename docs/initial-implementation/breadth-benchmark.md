# Broader audit interpretation benchmark

This family adds **16 controlled cases**, **32 supported/unsupported claims**, **16 numeric or unavailable-value requests**, and **16 single-operation recommendations**. Four cases also require a collection artifact produced from a separate frozen evidence bundle. The cases map to 23 WSG guideline groups; those mappings describe the evaluation topics, not complete guideline coverage.

Together with the earlier 12 evidence cases and ten methodology cases, there are now **38 cases across these three development families**. The original six browser-fixture tasks are a separate family. Historical cases, skill snapshots and results remain unchanged.

The [complete public case book](assets/breadth-benchmark-cases.json) includes every input, expected answer and recommendation. This is intentionally reviewable development material. The [frozen task manifest](assets/breadth-benchmark-manifest.json) records exact input, reference, instruction, collector, verifier and skill-resource hashes. These are coordinator-authored cases reviewed for consistency before freezing, not independent owner labels or a held-out accuracy estimate.

## Cases to review

| Case                                | Main distinction                                                                                                | Expected recommendation                                         |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| `journey-false-success`             | A visible generic heading cannot override an unchanged URL and failed task action                               | Investigate the selector and task-specific completion condition |
| `consent-visual-equivalence`        | Separate working accept/reject controls and matching dimensions do not establish equal visual prominence        | Investigate visual presentation and post-rejection collection   |
| `print-document-scope`              | Retained print sections and hidden navigation do not establish pagination or downloadable-document optimization | Preserve demonstrated navigation hiding                         |
| `motion-initial-live`               | Reduced motion on initialization can work while a live preference change fails an explicit requirement          | Fix the live-change behavior                                    |
| `instructional-image-context`       | Below-fold position does not remove a screenshot's instructional purpose or legibility needs                    | Reject removal based solely on position                         |
| `font-language-fallback`            | A Latin font subset cannot replace the fallback rendering the captured Greek text                               | Preserve the required fallback                                  |
| `carbon-delegated-presence`         | A root 404 can coexist with a working exact-host header delegation                                              | Reject green-hosting inference from provider names alone        |
| `carbon-schema-not-proof`           | Schema validity and historical disclosure are different from verified current energy claims                     | Investigate current provider evidence                           |
| `source-deployment-conflict`        | An undeployed local lazy-loading template cannot override runtime requests                                      | Investigate deployment and visitor-task requirements            |
| `dependency-declared-not-installed` | Manifest minimum versions are not deployed versions                                                             | Reject an immediate upgrade based on that assumption            |
| `cache-private-public`              | Observed reuse of public CSS does not justify publicly caching personal statements                              | Preserve private response protection                            |
| `governance-policy-execution`       | A published role and target do not establish staffing or achieved reductions                                    | Investigate implementation records                              |
| `form-validation-task`              | A useful associated error and allowed paste do not prove valid submission or keyboard recovery                  | Investigate the untested task path                              |
| `download-choice-relevance`         | A verified equivalent HTML option can satisfy a reading task without its larger optional PDF                    | Preserve the HTML option                                        |
| `energy-boundary-greenframe`        | Modeled scenario energy, CPU-package observations and SWDM overlap                                              | Reject addition of package observations to SWDM                 |
| `scope-clarification-injection`     | Page instructions cannot authorize an administrative deletion outside the owner's scope                         | Defer the restricted flow                                       |

The WSG topics include [efficient journeys](https://www.w3.org/TR/web-sustainability-guidelines/#design-efficient-and-streamlined-user-journeys), [media](https://www.w3.org/TR/web-sustainability-guidelines/#optimize-media-to-reduce-resource-use), [typography](https://www.w3.org/TR/web-sustainability-guidelines/#use-optimized-web-typography), [documents](https://www.w3.org/TR/web-sustainability-guidelines/#reduce-the-impact-of-downloadable-and-physical-documents), [dependencies](https://www.w3.org/TR/web-sustainability-guidelines/#use-dependencies-sparingly-and-maintain-them), [hosting](https://www.w3.org/TR/web-sustainability-guidelines/#use-sustainable-hosting), [caching](https://www.w3.org/TR/web-sustainability-guidelines/#optimize-caching-and-support-offline-access), and [organizational goals](https://www.w3.org/TR/web-sustainability-guidelines/#define-clear-organizational-sustainability-goals-and-metrics). The fixture facts are synthetic and do not assert new facts about either Wagtail site.

## Collection handoff cases

The journey, delegated-carbon, source-deployment and caching cases place their evidence in `/app/bundle.json`, with no facts in `input.json`. The task explicitly directs the agent to run:

```sh
python3 /app/collect.py
```

The collector writes `/app/output/collection.json`, containing the source-file SHA-256, exact origin and facts. The agent reads that artifact before writing its report. Harbor transfers both artifacts to a separate verifier. The oracle runs the same collector; a no-operation agent cannot pass by leaving an empty report.

This checks a concrete collection-to-review handoff, including source identity and site scope. It does **not** prove that a specific command executed: an agent able to reconstruct the expected artifact could write it directly. Trajectory inspection is needed to establish actual command use. The controlled collector does not launch a browser, exercise live scope clarification, or replace the need for future end-to-end site tasks.

The collector is a stdlib Python script with uv metadata and a lockfile. It supports Python 3.11–3.14 so the pinned Node/Bookworm agent image can use its installed interpreter without adding another runtime download. The isolated verifier remains on the pinned Python 3.14 image. This compatibility exception is explicit; production browser collectors keep their existing Python requirements.

## Grading boundaries

Questions use claim-validation semantics: `pass` means supported, and `fail` means unsupported, including insufficient evidence. This does not automatically mean a website defect. Numeric requests specify units and bases; unavailable values must remain null. Recommendations name one operation to reduce the ambiguity found in the [previous methodology campaign](methodology-benchmark.md#completed-model-comparison).

The breadth verifier adds collection-artifact validation to the existing numeric, label, evidence-ID and explanation-presence checks. It rejects missing or altered collection artifacts, wrong origins, changed source hashes and invented evidence. It does not semantically grade prose, calibrate recommendation usefulness or establish that the supplied reference labels are correct. Full reports remain available for owner review.

## Reproduce

```sh
uv run --locked --script benchmarks/build_expanded.py --breadth
harbor run -p .audit-work/breadth-tasks-v1 -a oracle -n 2 \
  --jobs-dir "$PWD/.audit-work/jobs"
harbor run -p .audit-work/breadth-tasks-v1 -a nop -n 2 \
  --jobs-dir "$PWD/.audit-work/jobs"
CODEX_AUTH_JSON_PATH="${CODEX_AUTH_JSON_PATH:-${CODEX_HOME:-$HOME/.codex}/auth.json}" \
  harbor run -c benchmarks/codex.json -p .audit-work/breadth-tasks-v1 \
  --jobs-dir "$PWD/.audit-work/jobs"
harbor run -c benchmarks/neuralwatt.json -p .audit-work/breadth-tasks-v1 \
  --jobs-dir "$PWD/.audit-work/jobs"
```

The required model arms remain GPT-6.1 Sol/low and Neuralwatt DeepSeek V4.1 Flash/high using the existing Codex harness configuration. Current review skills and all their references are copied into the tasks at build time. Do not rebuild or edit them during a campaign. The builder refuses a nonempty output directory.

Publish completed campaigns with `benchmarks/publish_expanded.py --breadth <job directories...>`. The publisher regrades saved reports and collection artifacts, verifies the unchanged base/breadth graders, and compares all task/skill/collector hashes across model arms. It exports allowlisted reports, diagnostics, usage and collection-artifact status without provider transcripts or credentials. Model results must be reported separately from oracle controls, setup failures and retries.
