# Decision models before, during, and after collection

Research date: November 4, 2026. This page reviews the newly available local copies of jevotron and jev-ultrafast and extends the [Jev/Clef assessment](decision-models.md).

**The examples suggest two complementary roles: review structured evidence in batches, and select bounded browser actions when discovery needs interpretation.** A decision model can therefore help acquire evidence as well as judge it. Code still defines allowed actions, executes them, checks outcomes, and determines which claims the evidence can support.

These are source-informed design proposals. The research executed an offline jevotron request preview, but no inference, adaptive browser benchmark, or sustainability audit.

## jevotron: structured evidence review

The inspected version was commit `300a67b332dbb6bb6a18fc39532dffcb18fe8055`. jevotron's `jt` CLI reads structured records, asks field-level questions with the whole entry as context, and produces probabilities, reports, and cached results. Its default task is anomaly detection, but configuration supports custom labels and criteria. [Repository at the inspected commit](https://github.com/thi-bot/jevotron/tree/300a67b332dbb6bb6a18fc39532dffcb18fe8055), [configuration](https://github.com/thi-bot/jevotron/blob/300a67b332dbb6bb6a18fc39532dffcb18fe8055/src/jevotron/config.py), [request construction](https://github.com/thi-bot/jevotron/blob/300a67b332dbb6bb6a18fc39532dffcb18fe8055/src/jevotron/requests.py).

For sustainability, an entry could contain one claim, the relevant WSG/STAR requirement, evidence spans, observation scope, source versions, and collection completeness. A selected field could ask whether the claim is supported. Another dataset could contain recommendations and the constraints they must preserve. Deterministic code should prefilter cases where no semantic question remains.

An entry is assessed independently. A model reviewing a resource cannot infer site-wide necessity from other rows it has not received. Include the necessary task context and summaries in that entry, or explicitly construct a larger case. This matters for third-party necessity, retention policies, and repeated findings across templates.

### What was tested offline

The existing local installation successfully generated requests for two synthetic evidence records with three labels: `SUPPORTED`, `CONTRADICTED`, and `INSUFFICIENT`. The process ran without an API key in a temporary working directory. It created two requests with one Choice question each. No predictions were obtained.

Download the [generated request preview](assets/decision-preview.json). It records the command, source commit, model identifier, exact state, and criteria. The relevant command was:

```sh
jt preview evidence.jsonl --config review.py --id-column id --field /claim --limit 2
```

The configuration used this structure:

```python title="review.py"
from jevotron.config import Config

config = Config(
    labels=["SUPPORTED", "CONTRADICTED", "INSUFFICIENT"],
    criteria={
        "SUPPORTED": (
            "The evidence supports every material part of the selected claim "
            "within its scope."
        ),
        "CONTRADICTED": (
            "The evidence explicitly conflicts with a material part of the claim."
        ),
        "INSUFFICIENT": (
            "The evidence is incomplete, ambiguous, absent, or only aspirational."
        ),
    },
    anomaly_label="CONTRADICTED",
    model="jev-1.13.0",
    guidance=(
        "Assess claim support using only the provided evidence and scope. "
        "A policy statement is not proof of operational implementation."
    ),
)
```

The first record claims that inactive accounts are deleted after 24 months, with evidence saying only that retention will be reviewed next year. The intended label is `INSUFFICIENT`. The second claims that a policy _states_ a 24-month limit, supported by that exact policy assertion. Its intended label is `SUPPORTED`, within the scope of what the document says. Neither record proves the service implements deletion.

This validates request construction for the proposed task, not classification quality. Choosing `CONTRADICTED` as the anomaly label is a CLI configuration requirement; do not use anomalies-only reporting for an audit, because it could hide insufficient evidence. Preserve the complete distribution and explicit result state. Also, the generated question still uses the generic wording “correctness”; test whether a purpose-built support question improves performance before choosing the production adapter.

### Cache and batching lessons

jevotron keys successful assessments by the endpoint and canonical request content. It persists completed results and records request provenance. Changing guidance, criteria, model, or evidence creates different requests; changing output sorting or a reporting threshold can reuse existing judgments. This is a strong pattern for evaluating methodology changes without paying to recompute unchanged work. [Cache guide](https://github.com/thi-bot/jevotron/blob/300a67b332dbb6bb6a18fc39532dffcb18fe8055/docs/guides/cache.md).

There are several audit-specific qualifications:

- Include relevant scope and source versions in the request itself. A filename or row position is not a sufficient identity or context boundary.
- `--refresh` replaces a matching cached assessment. Maintain a separate append-only evaluation archive when comparing repeated trials or model revisions.
- A stable model alias can point to changed weights while returning an old cached assessment. Pin an exposed version and record the provider revision where available.
- Shared-state batching changes the prompt layout and neighboring questions. Test whether it changes judgments; it is an experimental factor, not merely a transport optimization.
- `--where`, thresholds, and output ordering operate after assessment. They do not avoid inference costs. Prefilter records or select fields before submission when the goal is to reduce work.
- The entry's maximum field anomaly probability is a triage statistic, not a calibrated probability that any field is wrong.

Sources: [request construction](https://github.com/thi-bot/jevotron/blob/300a67b332dbb6bb6a18fc39532dffcb18fe8055/src/jevotron/requests.py), [batching](https://github.com/thi-bot/jevotron/blob/300a67b332dbb6bb6a18fc39532dffcb18fe8055/src/jevotron/batching.py), [report guide](https://github.com/thi-bot/jevotron/blob/300a67b332dbb6bb6a18fc39532dffcb18fe8055/docs/guides/reports.md).

Keep incomplete runs explicit. A streaming report may contain useful completed assessments while the run fails later; that is a partial result, not a completed audit. The cache's ability to resume should not obscure which records remain unassessed.

jevotron also contains an [agent-trace assessment example](https://github.com/thi-bot/jevotron/blob/300a67b332dbb6bb6a18fc39532dffcb18fe8055/analysis/agent-traces/README.md). It reports step-level labeled evaluation and variation between domains. That is a useful evaluation pattern for audit actions, but its reported performance is not evidence of sustainability-review accuracy. Reuse the separation between task labels, predictions, and error analysis, rather than transferring its thresholds.

## jev-ultrafast: decisions that acquire evidence

The inspected version was commit `544b0b1d5db220c663d4ba41e217d122435a1054`. The core loop captures browser state, constructs indexed candidates, asks Jev to select an operation and relevant target, validates the decision, executes the action, and observes again. A generative text model is used when text entry needs generation. [Project overview](https://github.com/thi-bot/jev-ultrafast/blob/544b0b1d5db220c663d4ba41e217d122435a1054/README.md), [agent loop](https://github.com/thi-bot/jev-ultrafast/blob/544b0b1d5db220c663d4ba41e217d122435a1054/jev_ultrafast/agent.py).

Operation selection and operation-specific target questions can share a request. Code consumes only the target answer for the selected branch. This illustrates a useful alternative to asking a generative agent to emit arbitrary browser code. For an audit, candidate operations might include inspecting a supplied policy link, scrolling to reveal deferred media, or selecting an explicitly allowed consent control. The caller should provide the task, observed candidates, and stopping rules.

The implementation checks allowed identifiers and probability validity, and validates selected answers against their distributions. The agent checks state freshness around execution and has bounded action/model-call budgets. Adopt that separation between semantic selection and mechanical validation. A correctly shaped answer can still choose the wrong control, so independently verify the resulting state. In particular, `DONE` is a decision to verify, not proof of task completion. [Model adapter](https://github.com/thi-bot/jev-ultrafast/blob/544b0b1d5db220c663d4ba41e217d122435a1054/jev_ultrafast/model.py).

### Limits relevant to measurement

The browser integration uses BrowserHarness/CDP with a tab in an existing browser profile, focus emulation, a specified viewport, and short action-specific waits. It is optimized for responsive interaction, not automatically for clean-profile, cold/warm sustainability experiments. The documented supported surface also excludes several complex browser cases, including frames and shadow roots. Treat unsupported widgets as collection limitations. [Browser implementation](https://github.com/thi-bot/jev-ultrafast/blob/544b0b1d5db220c663d4ba41e217d122435a1054/jev_ultrafast/browser.py), [documented scope](https://github.com/thi-bot/jev-ultrafast/blob/544b0b1d5db220c663d4ba41e217d122435a1054/README.md).

Its accessibility module combines static facts, axe, focus probes, disclosure interactions, media observations, and an optional generative review. This is close to the layered audit shape we want, but its instrumentation changes the page: axe is downloaded from a CDN; focus probing injects CSS disabling animations and transitions; keyboard and disclosure probes mutate interaction state. The source's “read-only” description does not mean behavior is unmodified. Keep these diagnostics separate from baseline animation, media, and network measurements. [Accessibility collector](https://github.com/thi-bot/jev-ultrafast/blob/544b0b1d5db220c663d4ba41e217d122435a1054/jev_ultrafast/accessibility.py).

The default model alias is `jev-latest`; pin a version for comparative evaluation. Its small latency experiments are useful development evidence, but do not establish general browser reliability, sustainability savings, or superiority over another harness. Evaluate the full task distribution we expect, including unsuccessful and unsupported cases.

## A combined workflow

The following is a proposed orchestration using skills and bounded sub-agents, rather than an implementation already present in this repository.

| Stage                   | Deterministic responsibility                              | Possible decision-model contribution                           | Output                                       |
| ----------------------- | --------------------------------------------------------- | -------------------------------------------------------------- | -------------------------------------------- |
| Plan scope              | Enumerate URLs, documents, templates, and known scenarios | Select representative candidates or relevant policy passages   | Reviewable sample with inclusion reasons     |
| Explore gaps            | Expose allowed operations and validate current targets    | Select the next useful evidence-gathering action               | Action log and observed outcome              |
| Capture baseline        | Replay validated scenarios with fixed conditions          | Usually none                                                   | Versioned evidence bundle                    |
| Run checks              | Compute metrics, validate schemas, apply exact rules      | Usually none                                                   | Facts, narrow results, and unresolved cases  |
| Review evidence         | Construct complete cases and enforce evidence references  | Judge support, relevance, or a bounded contextual relationship | Probabilities and proposed labels            |
| Investigate uncertainty | Apply budgets and preserve missing-evidence states        | Route to another evidence source or specialist                 | Additional evidence or explicit unknown      |
| Report and compare      | Apply scope, deduplicate, render, compare versions        | Optional explanation drafting with separate verification       | Evidence-linked report and evaluation record |

Skills should describe inputs, allowed tools, required evidence, stopping conditions, and output schemas. A capture skill can call deterministic collectors; a policy-review skill can call a decision adapter; an investigation skill can use an adaptive browser under a bounded plan. Sub-agents consume shared artifacts, and the coordinator prevents duplicate captures and merges only validated results. The model provider remains behind an adapter so the same cases can compare Jev, Clef, and a generative baseline.

Useful follow-up experiments include selecting among extracted policy passages instead of generating quotations, routing a case to the specialist most likely to resolve it, and deciding which missing observation would distinguish competing interpretations. Each needs an explicit no-match or insufficient-evidence outcome. Do not let an adaptive planner redefine the audit's requirements to fit what it found.

## Evaluate collection and review independently

Run two experiments before combining them:

1. Give all reviewers the same frozen evidence. Compare rules, a generative reviewer, Jev/Clef judgments, and escalation cascades on correctness, unsupported passes, abstention, calibration, cost, and review effort.
2. Give collection methods the same task and success assertions. Compare scripted Playwright, an agent-browser planner, and a Jev-ultrafast-style driver on completion, evidence coverage, forbidden or irrelevant actions, retries, variability, and resources consumed.

Then compare the combined systems. A smarter reviewer cannot repair evidence never collected; a broader collector may create more work without improving conclusions. Preserve action traces, request/response records, and evidence lineage so failures can be assigned to selection, collection, rule interpretation, or reporting.

Test prompt layout and batching separately from model upgrades. Include contradictory evidence, unrelated neighboring records, adversarial page instructions, stale element targets, inaccessible controls, and misleading completion messages. Use independent outcome assertions and human adjudication for the cases where code cannot establish the answer. The [evaluation plan](evaluation.md) supplies the broader release gates and methodology-version strategy.
