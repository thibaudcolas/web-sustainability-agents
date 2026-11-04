# Writing for site owners

Lead with the concrete observation and the useful next action. Name the page, control or behavior. Explain a technical detail only when it helps the reader decide what to do. Use a title that describes an action or question, not an internal check name.

## Finding structure

- **What we found:** visible behavior or measured fact, in one or two sentences.
- **Why it matters:** effect on the visitor or resource use. Do not invent emissions savings or suggest that every uncertainty is a defect.
- **Next step:** the smallest useful fix or investigation, with an owner-verifiable success condition.
- **How we checked this:** an anchor to a readable account of the observation, pages and source context. Raw artifact IDs are for the technical appendix.

Keep an established defect distinct from an investigation. Use “Check whether…” when the evidence is incomplete. Do not write an imperative fix title if the audit has not established a problem. Preserve useful existing behavior in ordinary language without repeating a generic preservation disclaimer in every finding.

## Translate internal language

| Avoid                                     | Prefer                                                                                                      |
| ----------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Branch                                    | Cookie choice, when it means separate accept/reject runs                                                    |
| Accounting: partial                       | Some transferred data could not be measured; the displayed size is incomplete                               |
| Cold initialization works                 | The site opens in dark mode when the visitor already uses dark mode                                         |
| Live preference handling                  | Changing the device's theme while the page is open                                                          |
| Candidate base.html; deployment unmatched | The local `base.html` contains theme setup code. We have not confirmed that the live site uses this version |
| Preserve explicit-choice precedence       | Keep the visitor's manual theme choice when it differs from the device setting                              |
| Expose the concrete monitoring budget     | Document the page-size limit that triggers an alert                                                         |
| Supply the exceedance procedure           | Explain who responds when the limit is exceeded and what they should do                                     |
| CantTell                                  | Needs investigation                                                                                         |
| Source candidate rendition                | A possible smaller image version                                                                            |

These examples clarify wording, not evidence. Only assert a behavior when the supplied observations support it. Explain once in the methodology section that local source may differ from the live deployment; repeat it in a finding only where it changes the proposed action.

## Measures and scope

Lead with first load before clicking or scrolling. Give each page a short readable name linked to its URL. Put cookie-choice and scrolling comparisons in a separate table with a one-sentence explanation. Never present later totals as additional downloads or guaranteed savings. Use the first recorded initial visit, even when incomplete, or a declared median of three matching complete visits. Do not pool consent choices, cache states or browser profiles. Put selection rules and units in methodology.

Keep the score explanation in methodology. Show passing progress per WSG area alongside checked coverage and unknown counts. Show pass/problem/unknown counts beside the scoped score. Explain that a low score can reflect missing evidence, not just site defects. Do not call it an overall sustainability grade or a full WSG conformance score.

## Visual presentation

Use short sections, meaningful headings, summary cards and expandable secondary detail. Keep priority and status words visible; color and icons are supplementary. Avoid decorative emoji in headings and repetitive status symbols. Use direct WSG links with guideline titles, meaningful evidence-link labels and screenshot captions. Keep the report useful without asking readers to inspect JSON.

Separate historical audit capture from newer illustrations and editorial changes. The method section names the actual reviewer model/reasoning, sample, capture conditions and unresolved limitations. Keep exact hashes and machine downloads in a collapsed technical appendix.

## Priority and code

Rank demonstrated visitor-facing problems above speculative internal optimizations unless measured frequency, cost or owner context supports a different order. A possible duplicate CI trigger with no run history warrants low-priority investigation, not a claim of large savings. Document priority changes separately from scored outcomes.

Show a short captured code excerpt when it helps an owner locate the issue. Link the file on the checked-out branch and offer the captured commit for reproducibility. Do not invent an exact excerpt, assume branch links are immutable, or present a source hypothesis as deployed behavior.
