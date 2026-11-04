# Web sustainability benchmark with Harbor

Design update: November 4, 2026. **Use Harbor as the primary benchmark runner and task format.** Establish one versioned web sustainability benchmark with separate knowledge, evidence-review, and end-to-end audit tracks. Use narrower skill evaluations to diagnose failures and improve components without changing the overall benchmark's meaning.

This page defines the broader benchmark to build, with a [machine-readable seed plan](assets/benchmark-plan.json). The [first executable slice](first-slice.md) implements six development cases covering part of this design. The twelve families below remain expansion specifications. The [evaluation methodology](../feasibility-study/evaluation.md) remains the source for metrics, labeling, and release gates.

The [test-site shortlist](test-sites.md) maps this design to concrete material: adapted STAR examples, a pinned Wagtail bakerydemo, and a separately reported real-world sample. One site can supply several case families; a published example is not automatically a reviewed reference answer.

## Benchmark structure

| Track                     | Input and task                                                                 | Main score dimensions                                                         | Why separate it                                        |
| ------------------------- | ------------------------------------------------------------------------------ | ----------------------------------------------------------------------------- | ------------------------------------------------------ |
| Knowledge and methodology | Answer bounded questions from a pinned WSG/STAR/SWDM/DCR source pack           | Correct distinctions, citations, calculations, appropriate uncertainty        | Exposes methodology errors without browser variability |
| Evidence review           | Produce findings from frozen captures, policies, and optional source           | Finding precision/recall, evidence support, applicability, unsupported passes | Compares reviewers on the same observations            |
| Audit execution           | Inspect a controlled running site and produce an evidence-linked report        | Collection coverage, valid findings, task completion, bounded actions         | Tests the whole workflow and harness                   |
| Context-assisted audit    | Repeat selected cases with matching, stale, or contradictory internal evidence | Better diagnosis, feasible fixes, justified resolution of unknowns            | Measures whether local context actually helps          |

For knowledge, prioritize open-book application of supplied authoritative sources over recall of current draft numbers. An optional closed-book diagnostic can reveal model familiarity, but it should not drive the main ranking. Correct interpretation of a pinned draft is more useful than memorizing a moving publication.

Use frozen sites for the reproducible execution track and a separately reported live-site validation set. A live website's deployment, traffic, geography, and third parties can change between runs. Do not mix those changes into a model leaderboard as though each system saw the same task.

## Initial twelve case families

Start with a small vertical slice before expanding to the earlier 60–100-case development corpus. Each family should eventually have clean, failing, incomplete, and misleading variants as applicable.

| ID    | Case family                     | Required behavior                                                                       |
| ----- | ------------------------------- | --------------------------------------------------------------------------------------- |
| `K01` | DCR and WSG scope               | Reject the claim that an A rating establishes WSG conformance                           |
| `K02` | Rating versions and boundaries  | Use SWDM v4 thresholds and classify unrounded boundary values correctly                 |
| `K03` | Policy versus operation         | Distinguish a stated retention rule from evidence that deletion runs                    |
| `K04` | Carbon and measurement          | Distinguish modeled page emissions, measured bytes, and attributed inference energy     |
| `R01` | Personalized cache exception    | Preserve justified privacy controls while finding cacheable static resources            |
| `R02` | Deferred media                  | Judge network behavior rather than accepting a lazy-loading attribute as proof          |
| `R03` | Partial capture                 | Report incomplete evidence instead of a clean audit or A+ rating                        |
| `R04` | Conflicting internal evidence   | Retain runtime observations and flag stale or contradictory configuration               |
| `A01` | Cold/warm journey               | Execute the declared states and identify invalid cache instrumentation                  |
| `A02` | Consent and third parties       | Compare bounded consent states and avoid inferring necessity from hostnames             |
| `A03` | Media recommendation            | Propose a change while preserving keyboard access and alternatives                      |
| `A04` | Prompt injection and completion | Ignore instructions embedded in evidence and produce a valid completed/partial artifact |

These are public development cases. Do not label them held out after publishing their expected behavior. Create an independent hidden release set later, split by site/template and evidence family, with all paired context variants kept together. Have another reviewer adjudicate reference findings and exceptions before using scores to select a model.

## Harbor task design

Harbor tasks package an instruction, environment, configuration, and verifier. Its current integrations include Codex, Claude Code, OpenCode, and pi, with skill support across these integrations. Pin Harbor and the installed agent versions; the capability list is not a guarantee that every adapter/provider combination works. [Task overview](https://docs.harborframework.com/tasks/overview), [pre-integrated agents](https://docs.harborframework.com/agents/pre-integrated-agents).

Proposed layout for each implemented task:

```text
task-id/
  task.toml
  instruction.md
  environment/
    Dockerfile
    skills/
    inputs/
  tests/
    Dockerfile
    test.sh
    reference.json
  solution/
    solve.sh
```

Mount only the permitted input tier. In a public-only browser case, run the fixture application in a separate service without exposing its source to the agent. Hiding source in a different folder in the same unrestricted container is not a public-only condition. In source-assisted variants, deliberately provide the corresponding snapshot and revision metadata.

Use a separate verifier environment with protected reference labels and tests. Transfer only declared report/evidence artifacts into it. Harbor's separate-verifier support starts a fresh environment rather than inheriting arbitrary agent filesystem changes; explicit artifact declarations determine what reaches grading. [Separate verifier](https://docs.harborframework.com/tasks/separate-verifier), [artifact contract](https://docs.harborframework.com/tasks/artifacts).

An illustrative configuration fragment, to validate against the pinned Harbor release during implementation:

```toml
artifacts = ["/app/output/report.json", "/app/output/evidence"]

[environment]
skills_dir = "/skills"

[agent]
timeout_sec = 600

[verifier]
environment_mode = "separate"
timeout_sec = 120
```

The environment must actually contain the skills at `/skills`; setting `skills_dir` alone does not upload them. Harbor can also inject job-level skills, allowing controlled skill/no-skill comparisons. Keep the fixture and grading rules fixed while changing the skill package. [Task skills](https://docs.harborframework.com/tasks/skills), [job skills](https://docs.harborframework.com/jobs/skills).

Use network policy to permit the fixture services and required inference endpoints while restricting arbitrary answer retrieval. Model API traffic must remain possible even when the task is otherwise offline. Inspect the chosen agent integration's routing and allowlisting rather than assuming one environment variable works everywhere. [Base URL management](https://docs.harborframework.com/agents/base-url-management), [network policies](https://docs.harborframework.com/tasks/network-policies).

## Grading and comparable scores

Grade exact fields, units, evidence references, and scenario outcomes in code. Human-reviewed rubrics handle context and recommendation validity. A model judge can assist on bounded questions, but it must be calibrated against reviewers and must not be the sole authority for its own provider's outputs.

Match findings by rule, target/state, underlying issue, and cited evidence. Penalize unsupported extra findings as well as missed findings; otherwise an agent can maximize recall by listing every possible problem. Accept equivalent wording and more than one valid fix. Preserve individual dimensions instead of hiding unsafe advice behind an average score.

Report per-track results, macro-averages across case families, completion/error rates, and serious-error counts. If an overall number is needed, preregister its weights and show the component scores alongside it. Correctly reporting unknown is a valid outcome when evidence is unavailable. A missing required report is a task failure; a broken environment or verifier is an infrastructure error with its own count. Do not silently exclude failed trials from the only published denominator.

First run the reference solution and a no-operation agent. The reference should satisfy the rubric; the no-operation run should not pass. Add deliberately fabricated citations, malformed reports, contradictory findings, and excessive generic recommendations as negative grader tests. This validates the evaluator before spending on model comparisons.

## Required comparison matrix

Every model-bearing benchmark campaign should include a **Neuralwatt DeepSeek V4.1 Flash arm and a Codex arm**, as requested. Deterministic fixture and grader checks need no inference. A narrow diagnostic can run alone during development, but a release comparison must include both required arms or be labeled incomplete.

Separate three comparisons:

1. **Model comparison:** use the same reviewer adapter, evidence, prompts, output contract, and budgets. Compare DeepSeek with the selected OpenAI model on generative tasks, and Jev/Clef on typed decisions.
2. **Harness comparison:** hold the model/provider fixed where supported and compare skill loading, tool execution, evidence collection, and report quality across hosts.
3. **System comparison:** compare useful complete configurations, such as Codex plus rules versus OpenCode/DeepSeek plus rules and Clef. Name every differing component; this measures systems, not an isolated model effect.

Start with a sequential single-reviewer baseline. Then test shared skills, optional internal evidence, decision-model review, and delegated specialists as separate additions. Do not run the full cross-product of all models, harnesses, evidence modes, and prompts before finding which factors matter. Repeat stochastic trials, pair cases, report uncertainty, and include all retries and escalation costs.

The [model/provider plan](model-comparison.md) gives the Neuralwatt and TypeSafe adapter details and energy accounting requirements.

## Inspect AI and Promptfoo

Use Inspect AI if its model-level analysis, scorers, or logging make the frozen-evidence and knowledge tracks easier to investigate. Its OpenAI-compatible provider supports custom endpoint configuration. The `inspect_harbor` bridge can reuse Harbor tasks, but the reviewed bridge documentation warns that some features are unsupported or ignored, including task skill-directory handling and multi-step tasks. Do not assume equivalent isolation, skills, artifacts, and errors without an adapter parity test. [Inspect providers](https://inspect.aisi.org.uk/providers.html), [Inspect Harbor task mapping](https://meridianlabs-ai.github.io/inspect_harbor/tasks.html).

Promptfoo is optional for quick prompt/criteria regressions. Its Python provider can call the same decision adapter used elsewhere. Keep labels, evidence fixtures, and scoring functions canonical so a Promptfoo experiment does not become a second inconsistent benchmark. Do not require all three runners in the initial implementation. [Promptfoo Python provider](https://www.promptfoo.dev/docs/providers/python/).

The smallest initial stack is Harbor plus shared Python grading/provider utilities. Add Inspect or Promptfoo only for a specific analysis they improve. Preserve runner-specific behavior in the run manifest, and test any claimed parity on the same small corpus.

## Versioning and progression

Version task inputs, source pack, labels, graders, skills, collectors, browser/container images, provider adapters, and requested/served models. Preserve reports, evidence, observable action traces, usage records, and errors. Use separate identifiers for the benchmark release and audit methodology release.

Regrade saved artifacts when only the verifier changes, and rerun inference when the task, evidence, prompt, or model meaning changes. Harbor supports separate-verifier regrading, but a new score still needs an explanation and comparison against the previous rubric. [Harbor regrading](https://docs.harborframework.com/jobs/regrade).

Build the twelve-family vertical slice, validate the grader and two required execution arms, then expand coverage and establish an independently reviewed release set. The [validation roadmap](validation-roadmap.md) states the evidence needed before choosing the production orchestration or making reliability claims.
