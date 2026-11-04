# Audit workflow and artifacts

The agent controls scope, invokes deterministic collectors, applies review skills, and renders a report. `audit/workflow.py` implements the file-based handoffs. For installation and a copyable agent request, start with [Run a sustainability audit](README.md).

## 1. Define the scope

Run from the audit checkout. The agent creates a plan, then refines the pages, visitor tasks, consent branches and journey completion conditions:

```sh
uv run --locked --script audit/workflow.py init \
  --origin https://example.org --page https://example.org/ \
  --plan .audit-work/example-plan.json
```

Reuse the owner's supplied context. Ask only about missing decisions that change the work, and record answers, assumptions and unresolved questions in the plan. Required unanswered questions block collection; optional questions do not prevent independent public exploration.

A plan covers one exact origin. Select pages by content and functional diversity, not just URL count. A journey's `success` can specify URL, selector and expected text; all supplied postconditions and required actions must succeed. Discover consent selectors on the actual site. See [browser probes](../reference/browser-probes.md) for supported actions and states.

An empty `checks` list selects the current default catalog: 25 public checks in 24 guideline groups, or 33 checks in 32 groups when `sourceFiles` is nonempty. This does not select every WSG criterion. To include source evidence, declare `sourceRoots` and select individual `{root, path}` records as described in the [check reference](../reference/checks.md).

## 2. Collect and inspect

```sh
uv run --locked --script audit/workflow.py collect \
  --plan .audit-work/example-plan.json --session .audit-work/example-run-1
```

The session must be new. Collection freezes the plan and skills, runs the staged browser measurements, Wappalyzer scan, supplementary probes, disclosure interpretation and selected source capture, then assembles a review packet. Wappalyzer's separate scan is excluded from page-load totals.

Inspect command exit codes and page-level errors. A completed command can contain failed selectors, missing states or incomplete accounting. Keep those limits in the review. Preserve initial, consent and scroll observations separately; only initial-load figures lead the report.

| Artifact                                                        | Purpose                                                      |
| --------------------------------------------------------------- | ------------------------------------------------------------ |
| `plan.json`, `receipt.json`                                     | Scope, assumptions, invocation and implementation provenance |
| `skills/`, `checks.json`, `rubric.json`, `impact-weights.json`  | Frozen review instructions and scoring expectations          |
| `staged.json`, `probes.json`, `disclosures.json`, `source.json` | Measurements and scoped supplementary evidence               |
| `packet.json`                                                   | Review inventory with evidence IDs and artifact hashes       |
| `review-template.json`                                          | Required row-level judgment structure                        |

Source files are supplemental evidence, not deployment attestation. A carbon.txt declaration helps identify claims and supporting documents; it does not itself prove sustainable hosting. Keep additional evidence in a new traceable packet rather than silently amending a frozen session.

Optional [GreenFrame measurements](../knowledge-base/greenframe.md) and hardware-energy experiments need their own validated runner and protocol. Run them separately while other workloads are idle. They are not automatic components of the public baseline.

## 3. Review with the skills

Give the reviewer the frozen packet, relevant raw evidence, rubric and skill resources. Apply the quantitative evidence, guideline and claims review roles from the [skill catalog](../agent-skills.md). Use sequential roles or authorized subagents; the output contract is the same.

Write `review.json` from the session's template. Every selected check needs an outcome, actual evidence IDs, rationale, confidence and next evidence needs. Record the actual harness, model and reasoning settings. An unknown is a valid result; a cited node is not automatically sufficient support for a claim. Read relevant WSG criteria progressively from the guideline skill's pinned reference.

The workflow has no built-in model API call. The agent supplies these qualitative judgments; the next command calculates the score.

## 4. Calculate and render

```sh
uv run --locked --script audit/workflow.py score \
  --session .audit-work/example-run-1 \
  --review .audit-work/example-run-1/review.json
uv run --locked --script audit/render_review.py \
  --session .audit-work/example-run-1 \
  --artifact-prefix . \
  --output .audit-work/example-run-1/report.md
```

The scorer verifies packet and evidence hashes, requires the selected checks, and groups judgments once per guideline. Unknowns remain in the attempted denominator. The renderer supports the current `agent-breadth-v2` rubric and validates scored inputs before producing Markdown. It does not invent or rejudge findings.

The report uses `--artifact-prefix` to link its evidence files. The example keeps the report next to those files. This development renderer still includes campaign-specific methodology wording, a publication-manifest link and relative documentation links from the repository examples. The agent must adapt those passages to the actual run and create or omit publication-only links before sharing; rendering alone does not create a sanitized publication bundle. General report packaging remains part of the DX work.

See [reporting reference](../reference/reporting.md) for chart data, denominators and expected sections. Review the resulting priorities, recommendations and limits before sharing.

## Reproduce and extend a run

Recalculating from preserved reviews and inputs needs no new model calls. Recollecting a live site or rerunning a reviewer can change the evidence or judgments and requires a new campaign. Scores from different samples or rubrics are not before/after comparisons.

The [example reports](../reports/README.md) link their exact evidence bundles and reproduction commands. Earlier two-page pilots and their failed journeys remain in the [implementation evidence record](../initial-implementation/sources.md#original-agent-pilot-reproduction) and historical reports; the latest three-page runs have completed declared journeys.
