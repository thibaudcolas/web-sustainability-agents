# Scoring a scoped sustainability audit

A useful score needs a declared test scope, explicit outcomes, and a visible coverage denominator. The implemented approach reports passing scoped checks grouped by WSG guideline. It does not equate a narrow automated test with a whole guideline, or a percentage with conformance.

## What the supporting standards provide

[ACT Rules Format 1.1](https://www.w3.org/TR/act-rules-format/) distinguishes passed, failed, inapplicable, unresolved, and untested outcomes. Its outcome mapping explains why passing a rule may still require further testing of the underlying requirement. This is a useful design precedent for our evidence model; ACT does not supply a general weighted website-sustainability score, and our rules are not approved ACT rules.

[WSG Impact Ratings](https://www.w3.org/TR/wsg-ir/) assigns guideline priority points using people, planet, prosperity, and timeframe ratings. The points characterize potential impact and timing, not a site's implementation quality or estimated carbon savings. The draft says ratings are individual, not compounded, and zero-rated items must not be omitted from assessment. Using those points as score weights is our experimental aggregation convention, not a formula prescribed by W3C.

[STAR](https://w3c.github.io/sustainableweb-ig/docs/star.html) discusses tool-specific scoring and weighting additional sustainability achievements, but the inspected document does not define one universal pass-percentage formula. Its evaluation method also requires scope and reporting context. We therefore make the local aggregation rule explicit and version it instead of presenting a project-defined score as an official STAR rating.

## Implemented score

The `scoped-wsg-v1` rubric declares one bounded expectation for each supported guideline group. Multiple observations or rules within a group count once:

1. Any evidenced failure makes the group `fail`.
2. Otherwise, an unresolved expectation or a mix of tested and untested applicable expectations makes it `cantTell`.
3. All applicable expectations must pass for a scoped `pass`.
4. Groups with no attempted checks stay `untested`; `inapplicable` requires a reason.

The headline score is:

```text
checked = passed + failed + cantTell
scoped audit score = 100 × passed / checked
```

Unresolved checks earn no points, but are not counted or described as failures. Inapplicable and untested groups remain visible outside the score denominator. An empty denominator produces an unavailable score. A report must also show `checked / 71`, the full guideline register, and the number of complete guidelines verified. At present, complete-guideline verification remains zero.

For example, two passes, one failure, and one unresolved check produce **50/100**, with **2/4 passing scoped checks**. This describes the evidence established under the rubric. It does not mean half the site is unsustainable, or that the unresolved check is a defect. Expanding the sample can lower the score by discovering unresolved work; track coverage and resolution alongside it.

The secondary impact-weighted score uses each checked guideline's published impact points once:

```text
100 × sum(weights of passing groups) / sum(weights of checked groups)
```

Do not multiply weights by the number of pages, resources, rules, or findings. A zero weight remains in the unweighted counts and coverage. An all-zero weighted denominator is unavailable. The project freezes all 71 weights with the inspected draft URL and HTML digest in `audit/impact-weights.json`.

## Interpretation and validation

The primary score is intentionally simple and auditable. The weighted variant is exploratory: impact points are ordinal priorities, so their numerical aggregation is not a calibrated measure of environmental harm. Neither score substitutes for Digital Carbon Ratings, estimated annual emissions, task success, or hardware-energy measurements.

Passing a metadata-presence check does not establish metadata quality; passing a dark-initialization check does not establish live preference handling; a published policy does not establish execution. The rubric records those boundaries. Optional missing files or descriptions do not automatically fail a guideline. Full conformance remains a separate criterion-level question.

Only compare scores with matching rubric versions, applicability decisions, sampling plans, and collection profiles. Preserve old judgments when the rubric changes. Independently review expectations and useful recommendations, then add counterexamples and held-out cases. The [current workflow and coverage](../initial-implementation/skill-audit-workflow.md) reports what has actually been evaluated and what evidence would increase coverage.
