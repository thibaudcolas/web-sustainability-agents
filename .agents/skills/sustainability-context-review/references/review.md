# Collect and judge contextual evidence

These checks implement selected qualitative review routes from the pinned WSG reference and the 101-row assessment crosswalk. They are partial project expectations. Follow [STAR's evaluation methodology](https://w3c.github.io/sustainableweb-ig/docs/star.html): define scope, explore the service, select a representative sample, evaluate and report the tested scope. A contextual pass applies to the declared sample and expectation; it cannot establish a complete service process or full-guideline conformance.

## Select relevant questions

The setup role selects from `audit/context-checks.json` through the installed tool root. The frozen session copies these definitions into `checks.json` and `packet.json`, so review workers do not depend on a mutable checkout. Read the matching criterion in the snapshot's `sustainability-guideline-review/references/wsg.json`; the crosswalk in the same folder explains legacy qualitative classifications and semantic migration limits.

For new public audits, consider `access-barriers` for a representative visitor task and `data-minimization` when the task collects personal data. Consider `content-lifecycle` for a substantial content collection and `sustainability-goals` or `governance-practice` when impact/progress statements are present. Select `audience-needs`, `inclusive-testing`, `service-necessity`, `impact-business-model` or `service-end-of-life` when a relevant decision, case study, funding explanation or retirement guidance is in scope. Scope by usefulness and available public routes; the owner need not know check IDs. Record why other contextual checks were omitted. Selection without sufficient evidence remains a useful explicit unknown rather than a presumed pass or defect.

Keep a small bounded sample: one named feature decision, one content collection, one data-collecting task, or one declared reporting period per check can be sufficient. State exclusions. Browser collector facts may already answer part of the question; do not duplicate the entire crawl.

Pin the assessment scope before collection in `plan.contextScopes`, with exactly one nonempty entry for each selected contextual check, including those selected through `checks`. For journey checks, state the task, audience, access constraints and completion condition. For organizational checks, identify the service/collection/decision and applicable period. Reviewers must use that declared boundary; source-record scope and whichever observations happen to be available cannot redefine it.

For example, the same successful desktop search-to-guide trace can support an anonymous English desktop task, while leaving completion with keyboard-only navigation unknown when that is the declared constraint. These are different assessments with different scopes. If the plan requires both, incomplete keyboard evidence cannot be converted into a pass by judging only desktop completion. Preserve unknowns or create a linked new session for a scope change.

## Prepare records before freezing

Capture public pages, downloaded policy text, published issue/decision records or anonymized owner documents as UTF-8 text or Markdown. A task-observation record should include the starting URL, task, audience/constraints, actual actions and states, completion evidence, observation time, and limitations. Preserve relevant source wording and dates; an agent's conclusion alone is not a raw observation. Keep independently retrieved documents distinct from an owner summary or auditor interpretation. Do not include participant identities or personal form data.

Add the selected checks and records to the plan:

```json
{
  "contextChecks": ["access-barriers", "content-lifecycle"],
  "contextScopes": {
    "access-barriers": "Anonymous English readers using keyboard-only navigation: search for the guide from the homepage and reach its complete reading content; no account or submission task.",
    "content-lifecycle": "English guide collection and its 2026 release review: inspect the review schedule and one applied update/archive decision, retaining useful historical access."
  },
  "contextEvidence": [
    {
      "id": "archive-example",
      "kind": "public-document",
      "path": "/project/.audit-work/captures/archive-review.md",
      "source": "https://example.com/content-review/",
      "capturedAt": "2026-11-04T10:00:00+00:00",
      "scope": "Published review schedule and the selected archived guide",
      "checkIds": ["content-lifecycle"],
      "limitations": "Publisher self-report; no CMS history or backend deletion verification"
    }
  ]
}
```

`kind` is `public-document`, `owner-record` or `task-observation`. Paths must be absolute and select regular UTF-8 files; the collector reads at most 64 KB per record and accepts at most thirty records. Source can be a document URL or an attributed owner-record identity. `capturedAt` records retrieval/observation time with a timezone, not an inferred publication date. Put publication and execution dates in the captured text. Every record needs its own scope and limitations.

The workflow freezes captured text and its digest into `context.json`. Unavailable, undecodable and oversized records remain explicit; they do not silently become evidence. Selected packet checks and per-check `requests` both retain the declared `assessmentScope`; requests also preserve the evidence needed and whether captured records are available for review. `review-required` means text exists, not that the expectation passes. `unresolved` means no captured record is available; browser evidence could still help. Reviewers cite `context.json:records:<index>` alongside browser or disclosure IDs. A record's `checkIds` are routing hints, not permission to ignore relevant contradictions elsewhere in the packet.

Evidence arriving after collection requires a linked new session. Never revise frozen text or turn an unanswered optional owner question into an answer. Do not contact third parties to obtain records unless authorized.

## Apply the exact expectation

A public case study can support a bounded research or decision check when it describes actual participants or affected groups, findings, dates and resulting action. No internal repository is required. A generic promise to involve users leaves execution unknown. A successful agent walkthrough establishes observed task behavior, not representative-user testing.

For governance, goals and impact models, trace the same service, metric and period across the commitment, observed result, review and response. Distinguish a measured change from a changed measurement boundary. Policy existence, a staff job title, an SDG icon or an isolated badge cannot supply the missing links. Public operational records can be sufficient for a bounded judgment while remaining attributed and unverified beyond their stated scope.

For content and data, check user value before suggesting deletion, fewer fields or fewer steps. Old reference material can remain necessary. Required authentication can protect people. A visible form or purpose explanation says nothing conclusive about backup deletion, retention enforcement or all-system consent propagation. Request a narrowly scoped processing or lifecycle example when those facts matter; do not demand source code as a substitute.

`service-end-of-life` tests guidance, so adequate scoped instructions can pass without an actual shutdown. State that limit explicitly. Other implementation checks need an executed example when their expectation says so.

Use `pass` only for the exact supported sample and expectation, `fail` for a demonstrated contradiction, `cantTell` for missing facts or unresolved applicability, `inapplicable` with an evidenced applicability reason, and `untested` when no review was attempted. Missing public evidence is not proof that a practice is absent. Give the smallest next evidence request, its likely source and validation purpose. The deterministic scorer combines checks by guideline; never add points for multiple checks in the same group or infer complete guideline coverage.
