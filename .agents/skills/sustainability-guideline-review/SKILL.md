---
name: sustainability-guideline-review
description: Judge scoped WSG checks from evidence and a versioned rubric, preserving applicability, unknowns, coverage limits, and actionable follow-up work.
license: MIT
metadata:
  version: "0.3.0"
---

# Sustainability guideline review

Read the supplied rubric, requested scope, and evidence before assigning outcomes. A rubric expectation is the test being judged; its WSG mapping supplies context, not permission to claim the entire guideline is satisfied.

Read the relevant guideline and success criteria in [the pinned WSG reference](references/wsg.json), plus [the assessment crosswalk](references/assessment-crosswalk.json) when planning additional checks. The reference is context for interpreting the criteria, not a claim that every criterion has an implemented collector. Match by meaning and canonical fragments: the older assessment uses different numbering. Distinguish automated observations, manual quantitative tasks that agents can execute, and qualitative judgments requiring task context. Public evidence can support all three; organizational execution may still need records or owner evidence. A manual label is not a reason to exclude a check.

When the packet selects `qualitative-context-review` checks, load the frozen `sustainability-context-review` skill and its reference. Read `context.json` records and requests alongside browser evidence. Public operational examples may support scoped judgments without internal access; a policy, future intention or successful auditor walkthrough cannot establish performed governance or representative-user testing. Missing records remain explicit unknowns, not failures. Preserve the narrower guidance-only scope of `service-end-of-life` and the distinct expectations when two checks map to one guideline.

For each requested guideline group, return its ID, outcome, evidence IDs, rationale, confidence, and next evidence needed. Use `pass` only when every declared expectation is supported for the declared sample; `fail` for a demonstrated contradiction; `cantTell` for missing observations or unresolved applicability; `inapplicable` only with an applicability reason; and `untested` when the check was not attempted. When several rules map to one guideline, any demonstrated failure takes precedence, otherwise unresolved expectations remain `cantTell`; all applicable rules must pass for a scoped pass. Do not multiply a guideline's weight by its number of rules or pages.

The project score is `100 × passed / (passed + failed + cantTell)`, after grouping by guideline. Inapplicable and untested groups are displayed separately. Unknowns earn no points but are not reported as defects. The optional impact-weighted variant uses the same groups and declared WSG Impact Ratings weights; it is a project convention, not an official W3C site score. Keep coverage out of all 71 guidelines adjacent to either score. A zero checked denominator is unavailable, not zero or 100.

Do not infer full-guideline conformance from passing narrow tests. A language attribute check cannot establish semantic quality; a policy route cannot establish policy contents or operational implementation; an initial theme probe cannot establish response to an in-page preference change. Read linked-file alternatives before concluding a resource is absent. Assess remediation prerequisites and user value before prioritizing a missing optional feature.

If the request supplies an external evaluation schema, use that schema. For claim-validation questions, follow its declared semantics: “unsupported” includes insufficient evidence and need not mean a site defect. Keep direct state uncertainty distinct from whether evidence supports a claim.
