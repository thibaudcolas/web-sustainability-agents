# Agent-triggered audit workflow

Use this repository's checkout as the tool directory; installing the skill does not install collectors. Run `uv run --locked --script audit/workflow.py --help` there to verify availability. The workflow uses files and ordinary subprocesses, independent of a harness's model API.

## Choose scope with the owner

First reuse explicit preferences, known origins and existing context. Ask only questions that materially change the audit. Useful questions are: which visitor tasks matter most; whether this is a public-only audit or supplied source/internal evidence is available; and whether there are support requirements or restricted flows to include. Group related questions. Offer a public, anonymous, bounded baseline while optional answers are pending. A required unanswered question blocks the dependent work, not independent public exploration.

Record answers, remaining questions and assumptions in the plan. An empty question list means no further clarification was necessary; it does not mean the owner answered every possible question. Initial above-the-fold bytes are the headline. Consent choices and scrolling are additional states. Include accept and reject branches when present, and record selector discovery rather than assuming the Wagtail selectors work elsewhere. Read `audit/run.py --help` and its target examples for supported actions. A declared source root is a search location, not proof of deployment identity.

```sh
uv run --locked --script audit/workflow.py init \
  --origin https://example.org --page https://example.org/ \
  --plan .audit-work/example-plan.json
```

Edit the plan before collection: meaningful page tasks, purposeful pages across templates, journeys with explicit actions and completion evidence, consent branches, public disclosure hints and relevant check IDs. Use `audit/probe-checks.json`, `audit/source-checks.json` and the disclosure expectations in `audit/workflow.py` as the current review catalog. Empty `checks` selects public checks and adds source checks only when `sourceFiles` is nonempty. It does not select all WSG criteria. Declare journey `success` with a destination URL, relevant selector and expected text; every supplied postcondition must match. A generic heading or completed click alone is not task completion. Keep the sample bounded; add a new campaign when exploration justifies widening it. Record omitted paths and functional diversity so small samples are not mistaken for whole-site coverage.

## Run and inspect evidence

The agent runs these commands; do not merely instruct the human to do so when tools are available and the task authorizes collection.

```sh
uv run --locked --script audit/workflow.py collect \
  --plan .audit-work/example-plan.json --session .audit-work/example-run-1
```

The collector creates a new session with a frozen plan, skill resources, scoped rubric, exact command receipts, locked-script hashes, first-load/consent/scroll measurements, supplemental browser probes, and `packet.json`. Inspect exit statuses **and** per-page errors, unresolved actions, redirects and missing state data. A zero exit code can still include failed probes. Check final origins before making origin-level claims. Data collection is separate from judging its usefulness.

Collection already runs `audit/disclosures.py` and indexes `disclosures.json` for normalized carbon.txt relationships. For a standalone historical capture, the equivalent command is `audit/disclosures.py --input <capture.json> --output <new-derived.json>`. Do not overwrite an artifact after its review packet is frozen. This is an interpretation of retrieved evidence, not a new measurement or independent verification. Read its claims and follow the smallest relevant public proof links when needed. If supplementary evidence changes a judgment, retain it with capture details and add it to a new packet instead of citing an unrecorded browser session.

For optional client-side GreenFrame runs, read `audit/greenframe.py --help` and the GreenFrame knowledge-base page. Run hardware/energy experiments separately while other workloads are idle. Do not mix them with LLM campaigns, and do not add their results to SWDM estimates. No energy tool is required for a public baseline audit.

## Review and calculate

Give the review agent the session's `packet.json`, frozen skills, scoped rubric and raw evidence. Read only the relevant entries from the guideline skill's WSG reference. The session contains `review-template.json`; write a new `review.json`, preserving every check ID. Quantitative observations, qualitative interpretations and further evidence needs remain distinct. Cite the supplied evidence IDs and specific observations. Record the actual model, reasoning and harness; do not copy example model settings if different.

If source is available, investigate plausible findings in the supplied checkout and documents: record revision/dirty status, file identity, relationship to the site and whether deployment is verified. Source evidence can corroborate a recommendation or reveal a tradeoff; it cannot erase a contradictory live observation. To include source in the scored packet, set `sourceRoots` and explicitly select `sourceFiles` as `{root, path}` objects. `audit/source.py` snapshots up to thirty named text files, including identity and repository state. Files up to 64 KB include text; files up to 2 MB can supply identity metadata only. Larger, unavailable or non-text files remain unresolved. No repository code is executed. Inspect selected files before publication. Source-only checks are omitted from the default public baseline when no files are selected. Declarations, installed dependencies, deployed versions and operational execution remain distinct.

```sh
uv run --locked --script audit/workflow.py score \
  --session .audit-work/example-run-1 --review .audit-work/example-run-1/review.json
```

The scorer requires every selected check, resolves evidence references, verifies artifact/rubric hashes, groups once per guideline and preserves unknowns. A pass means only the scoped expectations passed. The new session rubric is distinct from the historical two-site rubric; scores are not comparable across different check selections or samples.

Write one report per origin. Include the first-load metrics, scoped score and coverage, up to five useful priorities, quantitative observations, qualitative findings and direct WSG links. Finish with next auditing steps and reproducibility: plan, commands, captures, evidence hashes, skill/model versions, limitations, internal evidence availability and remaining WSG/STAR scope. Preserve the private session; publish only inspected, sanitized evidence. Raw text and screenshots can contain personal information even on public pages.
