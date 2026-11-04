# Scope and qualitative case review

These are public controlled development cases, not held-out accuracy labels or live-site findings. Both model arms requested high reasoning through Codex CLI. Read the [campaign method](scope-benchmark.md) for setup failures, controls, provenance and interpretation limits. Every reference is coordinator-authored; disagreement can identify a model error, an ambiguous task or a deficient reference.

The verifier checks structured judgments and explanation presence. It does not grade the usefulness or truth of the prose below. References and rationale were withheld from model environments. No prediction was selected by its score.

| Model                      | Accepted complete reports | Graded reports |
| -------------------------- | ------------------------- | -------------- |
| GPT-6.1 Sol (high)         | 16                        | 19             |
| DeepSeek V4.1 Flash (high) | 16                        | 19             |

## Cases

### energy-measured-modeled-boundaries

Review dimensions: energy-boundary. Frozen collector handoff required: yes.

Supplied evidence:

```json
[
  {
    "id": "e1",
    "value": {
      "localRun": {
        "cpuPackageJoules": 72,
        "durationSeconds": 12,
        "kind": "hardware counter observation",
        "includes": "browser, collector, OS and background processes",
        "idleBaselineMeasured": false
      },
      "siteIsolatedJoules": null
    }
  },
  {
    "id": "e2",
    "value": {
      "greenframe": {
        "energyWh": 0.004,
        "kind": "modeled browser scenario",
        "sameVisit": true
      },
      "swdm": {
        "gramsCO2e": 0.03,
        "kind": "transfer-based model",
        "overlapWithGreenframe": "not reconciled"
      }
    }
  }
]
```

Reference rationale: A real counter observation does not isolate a site; unit conversion does not make a model a measurement.

**q1: The supplied CPU package counter observed 72 J across the local run.**

Reference: pass.

| Model                      | Judgment | Explanation                                                                                                                                                                              |
| -------------------------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | pass     | e1 records an observed CPU package counter total of 72 J across the 12-second local run, without isolating the site contribution. Evidence: e1.                                          |
| DeepSeek V4.1 Flash (high) | pass     | e1 records 72 J for one 12-second local hardware run, supporting the narrow numerical claim; this is a broad CPU package observation rather than an isolated site measure. Evidence: e1. |

**q2: The CPU package observation isolates site-only electricity consumption.**

Reference: fail.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                                                   |
| -------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | fail     | e1 includes browser, collector, OS and background processes, has no measured idle baseline, and explicitly leaves site-isolated joules unavailable, so site-only consumption is unsupported. Evidence: e1.                                                    |
| DeepSeek V4.1 Flash (high) | fail     | e1 records siteIsolatedJoules as null and states that the counter includes browser, collector, OS and background processes with no idle baseline, so the observation does not isolate site-only electricity and the site-only share is unknown. Evidence: e1. |

**q3: Adding the two model outputs and hardware reading establishes a measured site total.**

Reference: fail.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                                    |
| -------------------------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | fail     | e1 is a non-isolated hardware observation and e2 supplies modeled energy and emissions with unreconciled overlap and different units, so adding them cannot establish a measured site total. Evidence: e1, e2.                                 |
| DeepSeek V4.1 Flash (high) | fail     | e1 is a hardware energy counter while e2 provides modeled GreenFrame energy and a transfer-based SWDM carbon estimate with unreconciled overlap, so adding these distinct quantities cannot establish a measured site total. Evidence: e1, e2. |

**m1: GreenFrame scenario energy converted to joules**

Reference: 14.4 J (modeled).

| Model                      | Judgment         | Explanation                                                                                                                                                                                |
| -------------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| GPT-6.1 Sol (high)         | 14.4 J (modeled) | e2 gives modeled GreenFrame scenario energy of 0.004 Wh; multiplying by exactly 3600 J/Wh yields 14.400000 J, a model estimate whose accuracy is not established by the supplied evidence. |
| DeepSeek V4.1 Flash (high) | 14.4 J (modeled) | Calculated from e2's 0.004 Wh GreenFrame same-visit scenario using 3,600 J per Wh gives 14.4 J; this is a modeled conversion, not an observation.                                          |

**m2: Site-only measured energy**

Reference: null J (unavailable).

| Model                      | Judgment             | Explanation                                                                                                                                                                                              |
| -------------------------- | -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | null J (unavailable) | e1 explicitly reports site-isolated joules as null and supplies only a shared CPU package observation without an idle baseline, so site-only measured energy is unavailable, not zero.                   |
| DeepSeek V4.1 Flash (high) | null J (unavailable) | e1 reports siteIsolatedJoules as null and its 72 J package counter includes non-site background activity, so no site-only measured energy is available and null is retained rather than treated as zero. |

**r1: Retain the CPU observation and model estimates with their separate scopes in the report.**

Reference: preserve.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                                                                                      |
| -------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| GPT-6.1 Sol (high)         | preserve | Retain the observed CPU package energy in e1 and the modeled estimates in e2 with their separate scopes and units, because site attribution and model overlap remain unresolved and preclude a combined total. Evidence: e1, e2.                                                                 |
| DeepSeek V4.1 Flash (high) | preserve | e1 supports retaining the 72 J counter only within its broad local-run boundary, while e2's modeled GreenFrame and SWDM results require separate scopes because their overlap is unreconciled, so preserving them separately retains useful evidence without implying a total. Evidence: e1, e2. |

### inference-energy-missing-not-zero

Review dimensions: energy-missing. Frozen collector handoff required: no.

Supplied evidence:

```json
[
  {
    "id": "e1",
    "value": {
      "modelCall": {
        "inputTokens": 2100,
        "outputTokens": 400,
        "energyJoules": null,
        "providerEnergyHeader": null,
        "usageCostUSD": 0
      },
      "localEnergyMeasurement": {
        "packageJoules": 34,
        "boundary": "local browser and harness only; remote inference excluded"
      }
    }
  }
]
```

Reference rationale: Missing provider telemetry remains unknown; local package energy and billing are separate quantities.

**q1: The zero harness cost establishes zero inference energy.**

Reference: fail.

| Model                      | Judgment | Explanation                                                                                                                                                                               |
| -------------------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | fail     | e1 records zero usage cost but null inference-energy fields, so the financial cost does not establish zero remote inference energy, which remains unknown. Evidence: e1.                  |
| DeepSeek V4.1 Flash (high) | fail     | Evidence e1 reports a usage cost of USD 0 but provides neither remote inference joules nor a provider energy header, so zero cost does not establish zero inference energy. Evidence: e1. |

**q2: The remote inference energy is unresolved in the supplied evidence.**

Reference: pass.

| Model                      | Judgment     | Explanation                                                                                                                                                                                                        |
| -------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| GPT-6.1 Sol (high)         | inconclusive | e1 supplies neither remote inference energy nor a provider energy header, and its 34 J local measurement explicitly excludes remote inference, leaving the requested direct energy state unresolved. Evidence: e1. |
| DeepSeek V4.1 Flash (high) | inconclusive | Evidence e1 leaves remote inference energy unresolved because both energyJoules and providerEnergyHeader are null, so the direct state is unknown rather than zero or measured. Evidence: e1.                      |

**m1: Remote inference energy**

Reference: null J (unavailable).

| Model                      | Judgment             | Explanation                                                                                                                                                          |
| -------------------------- | -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | null J (unavailable) | e1 has null remote inference-energy fields and no supplied energy model, so remote inference energy is unavailable rather than zero.                                 |
| DeepSeek V4.1 Flash (high) | null J (unavailable) | Evidence e1 supplies no remote inference energy measurement and no provider energy header, so the unavailable value remains null rather than being inferred as zero. |

**m2: Observed local CPU package energy**

Reference: 34 J (observed).

| Model                      | Judgment        | Explanation                                                                                                                                              |
| -------------------------- | --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | 34 J (observed) | e1 reports 34 J of observed local CPU package energy for the browser and harness only, excluding remote inference and providing no uncertainty estimate. |
| DeepSeek V4.1 Flash (high) | 34 J (observed) | Evidence e1 directly observes 34 J of local browser and harness package energy, with the stated boundary excluding remote inference.                     |

**r1: Publish zero joules for remote inference because no energy field was returned.**

Reference: not_supported.

| Model                      | Judgment      | Explanation                                                                                                                                                                                                               |
| -------------------------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | not_supported | e1 provides missing remote energy fields rather than an observed zero, so publishing zero joules is unsupported and remote inference energy must remain unavailable. Evidence: e1.                                        |
| DeepSeek V4.1 Flash (high) | not_supported | Publishing zero joules is unsupported because evidence e1 has a missing remote energy field rather than an observed zero; the unknown must remain null and require measurement or provider energy evidence. Evidence: e1. |

GPT-6.1 Sol (high) verifier diagnostics: answers/q2: incorrect outcome.

DeepSeek V4.1 Flash (high) verifier diagnostics: answers/q2: incorrect outcome.

### initial-first-visit-and-median-three

Review dimensions: repeat-selection. Frozen collector handoff required: yes.

Supplied evidence:

```json
[
  {
    "id": "e1",
    "value": {
      "protocol": {
        "page": "/",
        "phase": "initial",
        "profile": "fresh anonymous, no consent interaction",
        "viewport": "1280x720",
        "network": "unthrottled",
        "headline": "first successful valid run",
        "repeatStatistic": "median of three matching successful runs"
      },
      "runs": [
        {
          "id": "a",
          "bytes": 900000,
          "status": "success"
        },
        {
          "id": "b",
          "bytes": 1100000,
          "status": "success"
        },
        {
          "id": "c",
          "bytes": 1000000,
          "status": "success"
        }
      ]
    }
  }
]
```

Reference rationale: First headline is run a at 900 kB; the sorted three matching runs have median 1000 kB. These summaries must retain distinct selection rules.

**q1: The first-visit headline and the three-run median are distinct summaries under this protocol.**

Reference: pass.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                                                                                    |
| -------------------------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | pass     | e1 defines separate summaries: the first successful initial run a supplies the 900 kB headline, while the median of matching runs a, b and c is 1,000 kB, within this frozen protocol only. Evidence: e1.                                                                                      |
| DeepSeek V4.1 Flash (high) | pass     | Evidence e1 explicitly defines the headline as the first successful valid run and the repeat statistic as the median of three matching successful runs, and the listed runs make these summaries distinct; no material uncertainty remains within this frozen synthetic capture. Evidence: e1. |

**q2: The minimum of the three is the requested repeat statistic.**

Reference: fail.

| Model                      | Judgment | Explanation                                                                                                                                                                                                |
| -------------------------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | fail     | e1 explicitly requests the three-run median (1,000 kB), so the minimum (900 kB, run a) is unsupported as the repeat statistic even though it coincides with this sample’s headline. Evidence: e1.          |
| DeepSeek V4.1 Flash (high) | fail     | Evidence e1 requests the three-run median, which is run c at 1000000 bytes, whereas the minimum is run a at 900000 bytes, so the claim is contradicted within the frozen synthetic protocol. Evidence: e1. |

**m1: First successful initial-load headline**

Reference: 900 kB (observed).

| Model                      | Judgment            | Explanation                                                                                                                                                                                                                                      |
| -------------------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| GPT-6.1 Sol (high)         | 900.0 kB (observed) | e1 records first successful initial-load run a at 900,000 bytes, exactly 900 kB using decimal conversion, scoped to the supplied fresh anonymous capture.                                                                                        |
| DeepSeek V4.1 Flash (high) | 900.0 kB (observed) | Evidence e1 records run a as the first successful initial-load run with 900000 bytes, equal to 900.00000 decimal kB; this observed value is limited to the frozen fresh anonymous, unthrottled capture and is not a live or broad-site estimate. |

**m2: Median initial-load transfer over the three matching runs**

Reference: 1000 kB (calculated).

| Model                      | Judgment               | Explanation                                                                                                                                                                                                                                              |
| -------------------------- | ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | 1000.0 kB (calculated) | e1 supplies matching successful runs a, b and c at 900,000, 1,100,000 and 1,000,000 bytes; their median is exactly 1,000,000 bytes / 1,000 = 1,000 kB, describing only these three runs.                                                                 |
| DeepSeek V4.1 Flash (high) | 1000.0 kB (calculated) | Evidence e1 lists three successful runs of 900000, 1100000, and 1000000 bytes, whose median is 1000000 bytes, equal to 1000.0000 decimal kB; this calculated result is exact for the frozen sample but is not a confidence bound or population estimate. |

**r1: Preserve both the first-visit headline and labeled median with their run IDs.**

Reference: preserve.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                                                                                           |
| -------------------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | preserve | Preserve the 900 kB first-visit headline labeled run a and the 1,000 kB median labeled runs a, b and c because e1 explicitly distinguishes their purposes, with neither summary establishing performance beyond this sample. Evidence: e1.                                                            |
| DeepSeek V4.1 Flash (high) | preserve | Evidence e1 assigns run IDs a, b, and c and defines two distinct summaries, the first successful run headline and the three-run median, so retaining both with their run IDs preserves demonstrated useful reporting detail; the judgment is limited to this frozen synthetic protocol. Evidence: e1. |

### median-cannot-mix-consent-and-cache

Review dimensions: repeat-selection, consent. Frozen collector handoff required: no.

Supplied evidence:

```json
[
  {
    "id": "e1",
    "value": {
      "requestedStatistic": "median of three fresh anonymous initial visits before consent interaction",
      "runs": [
        {
          "id": "a",
          "bytes": 100000,
          "state": "fresh before consent",
          "valid": true
        },
        {
          "id": "b",
          "bytes": 600000,
          "state": "fresh after accept all",
          "valid": true
        },
        {
          "id": "c",
          "bytes": 20000,
          "state": "warm cached before consent",
          "valid": true
        }
      ],
      "remainingRuns": null
    }
  }
]
```

Reference rationale: Technical run success does not make cache and consent states interchangeable.

**q1: The three successful runs form the requested matching-condition repeat sample.**

Reference: fail.

| Model                      | Judgment | Explanation                                                                                                                                                                                    |
| -------------------------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | fail     | e1 records only run a as fresh before consent; run b follows accept-all and run c uses a warm cache, so successful execution does not establish three matching-condition visits. Evidence: e1. |
| DeepSeek V4.1 Flash (high) | fail     | Only run a is a fresh before-consent visit; run b occurs after accept all and run c is warm cached, so the three runs do not match the requested condition. Evidence: e1.                      |

**q2: Run a supplies a first fresh before-consent observation.**

Reference: pass.

| Model                      | Judgment | Explanation                                                                                                                                                          |
| -------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | pass     | e1 identifies valid run a as fresh before consent with 100000 observed bytes, supporting a first matching observation but not a three-visit statistic. Evidence: e1. |
| DeepSeek V4.1 Flash (high) | pass     | Run a is explicitly recorded as a valid fresh before-consent observation of 100000 bytes. Evidence: e1.                                                              |

**m1: Requested median of three matching fresh before-consent visits**

Reference: null kB (unavailable).

| Model                      | Judgment              | Explanation                                                                                                                                                        |
| -------------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| GPT-6.1 Sol (high)         | null kB (unavailable) | e1 supplies only one matching fresh before-consent visit and no remaining runs, so the requested three-visit median cannot be calculated.                          |
| DeepSeek V4.1 Flash (high) | null kB (unavailable) | A median of three matching fresh before-consent visits cannot be calculated because only run a has that state; b and c have different cache or consent conditions. |

**m2: First fresh before-consent observation**

Reference: 100 kB (observed).

| Model                      | Judgment            | Explanation                                                                                                                                      |
| -------------------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| GPT-6.1 Sol (high)         | 100 kB (observed)   | e1 records 100000 observed bytes for run a, converted using 1000 bytes per decimal kB to 100 kB; this represents one fresh before-consent visit. |
| DeepSeek V4.1 Flash (high) | 100.0 kB (observed) | Run a directly observed 100000 bytes, which converts using decimal units to 100.00000 kB.                                                        |

**r1: Collect two additional fresh before-consent visits under the same conditions before calculating that median.**

Reference: investigate.

| Model                      | Judgment    | Explanation                                                                                                                                                                                                       |
| -------------------------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | investigate | e1 contains only one matching visit, so collecting two additional fresh before-consent visits under the same conditions would complete the requested sample and permit its median to be calculated. Evidence: e1. |
| DeepSeek V4.1 Flash (high) | investigate | Only one observation currently matches the fresh before-consent condition, so two additional matching visits are needed to obtain the requested three-run sample before calculating the median. Evidence: e1.     |

### area-score-known-only-and-coverage

Review dimensions: area-scores, unknown-coverage. Frozen collector handoff required: no.

Supplied evidence:

```json
[
  {
    "id": "e1",
    "value": {
      "rubric": {
        "pass": 1,
        "fail": 0,
        "cantTell": "exclude from score; include applicable coverage denominator",
        "notApplicable": "exclude from both denominators",
        "areaWeighting": "not supplied"
      },
      "areas": {
        "userExperience": ["pass", "fail", "cantTell", "notApplicable"],
        "development": ["pass", "pass", "cantTell", "cantTell"],
        "hosting": ["cantTell", "notApplicable"],
        "business": ["notApplicable"]
      }
    }
  }
]
```

Reference rationale: Known-only denominators and applicable coverage differ; no applicable business checks means undefined coverage, not 0 or 100.

**q1: A hosting score of zero is established by its unknown and not-applicable checks.**

Reference: fail.

| Model                      | Judgment | Explanation                                                                                                                                                                                         |
| -------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | fail     | In e1, hosting has one unknown and one not-applicable check, leaving no known score denominator, so its score is unavailable rather than zero. Evidence: e1.                                        |
| DeepSeek V4.1 Flash (high) | fail     | The rubric excludes unknown checks from the score and not-applicable checks from both denominators, so hosting has no known-score denominator and its score is unavailable, not zero. Evidence: e1. |

**q2: The supplied rubric authorizes an overall score across the four areas.**

Reference: fail.

| Model                      | Judgment | Explanation                                                                                                                                                                       |
| -------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | fail     | The rubric in e1 supplies area-level scoring exclusions but no area weighting or aggregation rule, so it does not authorize an overall score across the four areas. Evidence: e1. |
| DeepSeek V4.1 Flash (high) | fail     | The rubric supplies no area weighting, so it provides no basis for combining the four area results into an authorized overall score. Evidence: e1.                                |

**m1: User experience known-only score**

Reference: 50 percent (calculated).

| Model                      | Judgment                  | Explanation                                                                                                                                                                                           |
| -------------------------- | ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | 50 percent (calculated)   | From e1, the user experience known-only score is calculated as 100 × 1 pass / (1 pass + 1 fail) = 50%, excluding the unknown and not-applicable checks.                                               |
| DeepSeek V4.1 Flash (high) | 50.0 percent (calculated) | From the four user-experience checks in e1, one pass and one fail yield 1/(1+1) = 50.00000000%; the unknown is excluded from this known-only score and the not-applicable check is excluded entirely. |

**m2: User experience assessed-applicable coverage**

Reference: 66.66666666666667 percent (calculated).

| Model                      | Judgment                               | Explanation                                                                                                                                                                                                                          |
| -------------------------- | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| GPT-6.1 Sol (high)         | 66.66666666666667 percent (calculated) | From e1, user experience assessed-applicable coverage is calculated as 100 × 2 known results / 3 applicable checks = 66.66666666666667%, including one unknown in the applicable denominator and excluding one not-applicable check. |
| DeepSeek V4.1 Flash (high) | 66.66666667 percent (calculated)       | Of the three applicable user-experience checks in e1 after excluding one not-applicable check, two are assessed, yielding 2/3 = 66.66666667% coverage.                                                                               |

**m3: Development known-only score**

Reference: 100 percent (calculated).

| Model                      | Judgment                   | Explanation                                                                                                                                                                        |
| -------------------------- | -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | 100 percent (calculated)   | From e1, the development known-only score is calculated as 100 × 2 passes / 2 known results = 100%, while two unknown checks remain outside the score denominator.                 |
| DeepSeek V4.1 Flash (high) | 100.0 percent (calculated) | The two development passes and two unknowns in e1 yield 2/(2+0) = 100.00000000% for the known-only score; the unknowns are excluded and do not establish outcomes on those checks. |

**m4: Development assessed-applicable coverage**

Reference: 50 percent (calculated).

| Model                      | Judgment                  | Explanation                                                                                                                                          |
| -------------------------- | ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | 50 percent (calculated)   | From e1, development assessed-applicable coverage is calculated as 100 × 2 known results / 4 applicable checks = 50%, with two checks still unknown. |
| DeepSeek V4.1 Flash (high) | 50.0 percent (calculated) | In e1 all four development checks are applicable and two are assessed, yielding 2/4 = 50.00000000% assessed-applicable coverage.                     |

**m5: Hosting known-only score**

Reference: null percent (unavailable).

| Model                      | Judgment                   | Explanation                                                                                                                                                                    |
| -------------------------- | -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| GPT-6.1 Sol (high)         | null percent (unavailable) | In e1, hosting has zero known results after excluding its unknown and not-applicable checks, so its known-only score has a zero denominator and is unavailable.                |
| DeepSeek V4.1 Flash (high) | null percent (unavailable) | In e1 hosting has one unknown and one not-applicable check but no pass or fail, so the known-only denominator is zero and the requested score is unavailable (null), not zero. |

**m6: Hosting assessed-applicable coverage**

Reference: 0 percent (calculated).

| Model                      | Judgment                 | Explanation                                                                                                                                                            |
| -------------------------- | ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | 0 percent (calculated)   | From e1, hosting assessed-applicable coverage is calculated as 100 × 0 known results / 1 applicable unknown check = 0%, which does not establish a zero hosting score. |
| DeepSeek V4.1 Flash (high) | 0.0 percent (calculated) | In e1 hosting has one applicable check and none assessed, yielding 0/1 = 0.00000000% assessed-applicable coverage while the hosting score itself remains unavailable.  |

**m7: Business assessed-applicable coverage**

Reference: null percent (unavailable).

| Model                      | Judgment                   | Explanation                                                                                                                                               |
| -------------------------- | -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | null percent (unavailable) | In e1, the sole business check is not applicable, leaving zero applicable checks and therefore unavailable assessed-applicable coverage rather than zero. |
| DeepSeek V4.1 Flash (high) | null percent (unavailable) | In e1 the sole business check is not applicable, so the applicable denominator is zero and coverage is unavailable (null), not zero or 100%.              |

**r1: Report area scores beside applicable coverage and explicit unknown counts.**

Reference: preserve.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                                                                           |
| -------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | fix      | The exclusions in e1 support reporting area scores with applicable coverage and unknown counts (user experience 1, development 2, hosting 1, business 0), marking zero-denominator results unavailable so readers can distinguish known performance from evidence gaps. Evidence: e1. |
| DeepSeek V4.1 Flash (high) | fix      | The rubric's exclusion and coverage rules make area scores unsafe to report without companion coverage and unknown counts, so adding both is justified; whether an existing report already does so is unknown. Evidence: e1.                                                          |

GPT-6.1 Sol (high) verifier diagnostics: recommendations/r1: incorrect action.

DeepSeek V4.1 Flash (high) verifier diagnostics: recommendations/r1: incorrect action.

### ci-priority-requires-applicability-evidence

Review dimensions: priority, applicability. Frozen collector handoff required: no.

Supplied evidence:

```json
[
  {
    "id": "e1",
    "value": {
      "priorityRule": "Include demonstrated applicable failures in CI remediation. cantTell requests evidence. notApplicable is excluded. Consider measured repeated exposure before prioritizing; severity numbers alone do not override applicability.",
      "checks": [
        {
          "id": "video-autoplay",
          "result": "notApplicable",
          "reason": "scoped pages have no video",
          "severity": 10
        },
        {
          "id": "mobile-transfer",
          "result": "fail",
          "reason": "all 3 scoped pages exceed supplied 500 kB budget",
          "severity": 7,
          "repeatedExposure": "all 3 initial visits"
        },
        {
          "id": "database-query",
          "result": "cantTell",
          "reason": "no backend query trace",
          "severity": 9
        }
      ]
    }
  }
]
```

Reference rationale: The explicit queue rule makes priority evidence-dependent; numeric severity cannot promote unknowns or excluded checks into failures.

**q1: The not-applicable autoplay check is a demonstrated CI failure because its severity is highest.**

Reference: fail.

| Model                      | Judgment | Explanation                                                                                                                                                                                                             |
| -------------------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | fail     | e1 explicitly excludes not-applicable checks and records no video on the scoped pages, so the highest severity does not establish an autoplay CI failure within this scope. Evidence: e1.                               |
| DeepSeek V4.1 Flash (high) | fail     | e1 marks the autoplay check notApplicable because the scoped pages contain no video, and its priority rule excludes notApplicable checks while stating that severity alone cannot override applicability. Evidence: e1. |

**q2: The mobile-transfer check is eligible for the supplied CI remediation queue.**

Reference: pass.

| Model                      | Judgment | Explanation                                                                                                                                                                                                        |
| -------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| GPT-6.1 Sol (high)         | pass     | e1 records mobile-transfer budget failure on all three scoped initial visits, satisfying the supplied rule for CI remediation eligibility within that sample. Evidence: e1.                                        |
| DeepSeek V4.1 Flash (high) | pass     | e1 identifies mobile-transfer as the demonstrated applicable failure, exceeding the supplied 500 kB budget on all three scoped initial visits, so it is eligible for the supplied remediation queue. Evidence: e1. |

**q3: The unknown database check establishes inefficient deployed database queries.**

Reference: fail.

| Model                      | Judgment | Explanation                                                                                                                                                                                                       |
| -------------------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | fail     | e1 records cantTell because no backend query trace is available, so inefficient deployed queries are unsupported and actual query efficiency remains unknown. Evidence: e1.                                       |
| DeepSeek V4.1 Flash (high) | fail     | e1 records the database check as cantTell because no backend query trace was supplied, so the frozen evidence supports asking for that trace rather than establishing inefficient deployed queries. Evidence: e1. |

**m1: Demonstrated applicable failing checks in this queue**

Reference: 1 checks (calculated).

| Model                      | Judgment              | Explanation                                                                                                                                                                   |
| -------------------------- | --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | 1 checks (calculated) | Calculated from e1, only mobile-transfer is a demonstrated applicable failing check; autoplay is excluded and the unresolved database check is not counted as a failure.      |
| DeepSeek V4.1 Flash (high) | 1 checks (calculated) | Calculated from e1: only mobile-transfer has result fail; video-autoplay is notApplicable and database-query is cantTell, yielding one demonstrated applicable failing check. |

**r1: Prioritize the demonstrated mobile-transfer budget regression in this CI queue.**

Reference: fix.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                                                       |
| -------------------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | fix      | e1 supports prioritizing the mobile-transfer budget failure affecting all three scoped initial visits to reduce transfer, with any improvement requiring validation against the supplied 500 KB budget because savings are unquantified. Evidence: e1.            |
| DeepSeek V4.1 Flash (high) | fix      | e1 supports prioritizing the mobile-transfer regression because it is an applicable demonstrated failure with repeated exposure across all three scoped visits, though the root cause and post-remediation budget compliance remain to be measured. Evidence: e1. |

**r2: Obtain a scoped backend trace to resolve the database check.**

Reference: investigate.

| Model                      | Judgment    | Explanation                                                                                                                                                                                                                     |
| -------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | investigate | e1 identifies a missing backend query trace, so obtaining a scoped trace is justified to assess query efficiency and resolve the CI check without presuming a deployed defect. Evidence: e1.                                    |
| DeepSeek V4.1 Flash (high) | investigate | e1 records the database check as cantTell specifically because no backend query trace exists, making a scoped trace the smallest appropriate next investigation without yet proving inefficient deployed queries. Evidence: e1. |

### branch-link-not-immutable-source-proof

Review dimensions: source-provenance. Frozen collector handoff required: no.

Supplied evidence:

```json
[
  {
    "id": "e1",
    "value": {
      "sourceRecord": {
        "url": "https://code.example/org/site/blob/main/package.json",
        "ref": "main",
        "retrievedCommit": null,
        "excerpt": "{\"dependencies\":{\"widget\":\"^2.0.0\"}}",
        "retrievedAt": "2026-10-01T10:00:00Z"
      },
      "deploymentCommit": null,
      "lockfile": null
    }
  }
]
```

Reference rationale: A mutable ref and requirement string support a bounded source claim, not reproducible commit/deployment evidence.

**q1: The supplied branch URL is immutable commit-pinned provenance.**

Reference: fail.

| Model                      | Judgment | Explanation                                                                                                                                                              |
| -------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| GPT-6.1 Sol (high)         | fail     | e1 supplies a mutable main-branch URL with no retrieved commit, so immutable commit-pinned provenance is unsupported. Evidence: e1.                                      |
| DeepSeek V4.1 Flash (high) | fail     | Evidence e1 identifies a mutable branch ref (`main`) and records `retrievedCommit` as null, so the supplied URL is not immutable commit-pinned provenance. Evidence: e1. |

**q2: The excerpt establishes a declared widget requirement in the retrieved branch snapshot.**

Reference: pass.

| Model                      | Judgment | Explanation                                                                                                                                                                                              |
| -------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | pass     | e1 explicitly declares widget with requirement ^2.0.0 in the retrieved package.json excerpt, establishing that declaration within the supplied branch snapshot but not a resolved version. Evidence: e1. |
| DeepSeek V4.1 Flash (high) | pass     | Evidence e1's excerpt declares `widget` at `^2.0.0` under dependencies for the retrieved `main` branch snapshot, although the missing commit identity limits reproducibility. Evidence: e1.              |

**q3: The exact deployed widget version is established by the excerpt.**

Reference: fail.

| Model                      | Judgment | Explanation                                                                                                                                                                |
| -------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | fail     | e1 supplies only the declared range ^2.0.0 and no lockfile or deployment commit, so an exact deployed widget version is unsupported. Evidence: e1.                         |
| DeepSeek V4.1 Flash (high) | fail     | Evidence e1 supplies only the ranged requirement `^2.0.0` with no lockfile or deployment commit, so it does not establish the exact deployed widget version. Evidence: e1. |

**m1: Exact deployed widget version**

Reference: null version (unavailable).

| Model                      | Judgment                   | Explanation                                                                                                                                                           |
| -------------------------- | -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | null version (unavailable) | e1 provides a dependency range without a lockfile or deployment linkage, leaving the exact deployed widget version unavailable.                                       |
| DeepSeek V4.1 Flash (high) | null version (unavailable) | The exact deployed widget version is unavailable from e1 because the dependency range permits multiple resolutions and no lockfile or deployment linkage is supplied. |

**r1: Capture the resolved commit, lockfile and deployment linkage before claiming an exact installed version.**

Reference: investigate.

| Model                      | Judgment    | Explanation                                                                                                                                                                                                |
| -------------------------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | investigate | e1 lacks the resolved commit, lockfile and deployment linkage, so capturing and checking those records is justified before claiming an exact installed version, which remains unestablished. Evidence: e1. |
| DeepSeek V4.1 Flash (high) | investigate | Evidence e1 shows that an immutable commit, lockfile, and deployment linkage are absent, so capturing them is the bounded investigation needed before claiming an exact installed version. Evidence: e1.   |

### commit-pin-does-not-repair-snippet-mismatch

Review dimensions: source-provenance, snippet-match. Frozen collector handoff required: no.

Supplied evidence:

```json
[
  {
    "id": "e1",
    "value": {
      "source": {
        "commit": "1111111111111111111111111111111111111111",
        "path": "src/main.js",
        "verifiedBytes": "import { render } from \"./render.js\";\nrender();",
        "snippetClaimedAsExact": "import tracking from \"analytics-vendor\";\ntracking.start();",
        "snippetMatchesVerifiedBytes": false
      },
      "deploymentMatchesCommit": true,
      "networkCapture": null
    }
  }
]
```

Reference rationale: A genuine commit and deployment match do not establish text absent from the verified file; no whole-site absence is asserted.

**q1: Commit-pinned provenance by itself validates the mismatched tracking snippet.**

Reference: fail.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                              |
| -------------------------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | fail     | e1 explicitly records a snippet mismatch, so commit-pinned provenance and a matching deployment do not validate the claimed tracking snippet. Evidence: e1.                                                                              |
| DeepSeek V4.1 Flash (high) | fail     | Evidence e1 shows the deployment matches the pinned commit, but the claimed snippet does not match those commit bytes, so provenance alone does not validate it; the null network capture leaves runtime behavior unknown. Evidence: e1. |

**q2: The supplied source bytes establish that the claimed tracking import is present in this file.**

Reference: fail.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                                                                            |
| -------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | fail     | The verified bytes in e1 contain only the render import and render() call, contradicting the claimed tracking import in this file without establishing behavior elsewhere. Evidence: e1.                                                                                               |
| DeepSeek V4.1 Flash (high) | fail     | Evidence e1 gives verified bytes containing a render import rather than the analytics import and explicitly marks the claimed snippet as nonmatching, so the claim is contradicted for this file; the null network capture leaves tracking outside this file unresolved. Evidence: e1. |

**m1: Tracking imports established in the verified bytes**

Reference: 0 imports (observed).

| Model                      | Judgment             | Explanation                                                                                                                                                     |
| -------------------------- | -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | 0 imports (observed) | e1's supplied verified bytes contain zero tracking imports; this observed count applies only to those bytes and does not establish site-wide tracking behavior. |
| DeepSeek V4.1 Flash (high) | 0 imports (observed) | The verified source bytes in evidence e1 contain no tracking import, although its null network capture leaves tracking outside this file unknown.               |

**r1: Remove the claimed tracking import from this file on the strength of the mismatched snippet.**

Reference: not_supported.

| Model                      | Judgment      | Explanation                                                                                                                                                                                                             |
| -------------------------- | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | not_supported | e1's verified bytes do not contain the proposed removal target, so the mismatched snippet does not justify this edit, and no network capture establishes runtime tracking. Evidence: e1.                                |
| DeepSeek V4.1 Flash (high) | not_supported | Evidence e1 shows the claimed tracking import is absent from the verified bytes, so removing it from this file is not justified by the mismatch; whether such tracking occurs at runtime remains unknown. Evidence: e1. |

### star-qualitative-scope-and-evidence

Review dimensions: STAR, audience-needs, governance-practice, sustainability-goals. Frozen collector handoff required: no.

Supplied evidence:

```json
[
  {
    "id": "e1",
    "value": {
      "reviewScope": {
        "samples": ["public service home", "support page"],
        "orgRecords": "public progress report only",
        "requestedOutput": "qualitative evaluation narrative disclosing scope, sampling, methods, evidence and uncertainties; no rating scale supplied",
        "sampling": {
          "advertisedContentPages": 120,
          "selectedPages": 2,
          "selection": "purposive development sample; no random sample",
          "completeProcessCoverage": false
        }
      },
      "evidence": {
        "strength": "accessible low-data HTML support route completed in 3 tests",
        "tension": "owner targets 20% lower annual transfer but no baseline period supplied",
        "action": "progress report names an owner for baseline definition",
        "reservation": "no staff interviews or procurement records"
      }
    }
  }
]
```

Reference rationale: A bounded evaluation narrative can disclose the supplied scope, evidence and unknowns without claiming a completed STAR evaluation or inventing an official rating scale.

**q1: The evidence supports a bounded qualitative STAR-style discussion with explicit reservations.**

Reference: pass.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                                                                                                                                         |
| -------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | pass     | e1 supports a bounded qualitative STAR-style discussion of the support route completed in three tests, the stated 20% annual-transfer target lacking a baseline period, and the named baseline owner, with explicit reservations about the purposive two-page sample, incomplete process coverage and limited organizational records. Evidence: e1. |
| DeepSeek V4.1 Flash (high) | pass     | The review contract in e1 requests a qualitative narrative and supplies a bounded two-page purposive sample with an observed support strength, a baseline gap, an owner action, and explicit reservations, so the claimed discussion is supported only at that stated scope. Evidence: e1.                                                          |

**q2: A numerical STAR rating of 4 out of 5 is established by the supplied review contract.**

Reference: fail.

| Model                      | Judgment | Explanation                                                                                                                                                               |
| -------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | fail     | e1 requests a qualitative narrative and supplies no rating scale or scoring rubric, so a numerical STAR rating of 4 out of 5 is unsupported. Evidence: e1.                |
| DeepSeek V4.1 Flash (high) | fail     | The supplied contract in e1 specifies a qualitative narrative and no rating scale, so no 4-out-of-5 STAR score is established and the claim is unsupported. Evidence: e1. |

**q3: The public samples establish organization-wide sustainability performance.**

Reference: fail.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                                                                      |
| -------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | fail     | e1 covers two purposively selected pages out of 120 advertised content pages, lacks complete process coverage, and supplies only a public progress report without staff interviews or procurement records, so organization-wide performance remains unestablished. Evidence: e1. |
| DeepSeek V4.1 Flash (high) | fail     | e1 covers 2 purposively selected pages out of 120 advertised pages and lacks random sampling, complete process coverage, staff interviews, and procurement records, so the public samples cannot establish organization-wide performance. Evidence: e1.                          |

**m1: Numeric STAR rating**

Reference: null score (unavailable).

| Model                      | Judgment                 | Explanation                                                                                                                                                   |
| -------------------------- | ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | null score (unavailable) | e1 supplies no numerical STAR scale, rubric or scoring method, so a numeric rating is unavailable and cannot be calculated from the qualitative observations. |
| DeepSeek V4.1 Flash (high) | null score (unavailable) | e1 states that no rating scale was supplied and requests a qualitative narrative, so a numeric STAR score is unavailable rather than zero.                    |

**r1: Keep the observed low-data support strength while requesting the missing target baseline.**

Reference: investigate.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                                                                          |
| -------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| GPT-6.1 Sol (high)         | preserve | e1 supports retaining the low-data HTML support route demonstrated useful in three completion tests and requesting the baseline period and corresponding transfer measurement from the named owner to evaluate the stated 20% target, whose achievement is unverified. Evidence: e1. |
| DeepSeek V4.1 Flash (high) | preserve | e1 demonstrates an accessible low-data support route worth preserving, while the absent baseline period means the target comparison requires further evidence rather than inference. Evidence: e1.                                                                                   |

GPT-6.1 Sol (high) verifier diagnostics: recommendations/r1: incorrect action.

DeepSeek V4.1 Flash (high) verifier diagnostics: recommendations/r1: incorrect action.

### star-public-claim-missing-operations

Review dimensions: STAR, impact-business-model, service-necessity. Frozen collector handoff required: no.

Supplied evidence:

```json
[
  {
    "id": "e1",
    "value": {
      "publicClaim": "Our AI advice service is sustainable and benefits every community.",
      "businessModelDocument": null,
      "necessityAssessment": null,
      "alternativeChannelsCompared": null,
      "accessEvidence": {
        "task": "read eligibility criteria",
        "publicHTMLWorksWithoutAccount": true
      },
      "assessmentBoundary": "one anonymous public journey"
    }
  }
]
```

Reference rationale: Missing organizational records preserve unknowns; a tested route is a scoped strength and a slogan is not operational proof.

**q1: The public claim establishes an evidenced impact business model and service necessity assessment.**

Reference: fail.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                                                                   |
| -------------------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | fail     | e1 supplies only an attributed public claim, with no business model document, necessity assessment or alternative-channel comparison, so an evidenced impact model and necessity assessment are unsupported and actual organizational practice remains unknown. Evidence: e1. |
| DeepSeek V4.1 Flash (high) | fail     | e1 supplies a broad public claim but no business-model document, necessity assessment, or alternative-channel comparison, so the claim does not establish either organizational expectation. Evidence: e1.                                                                    |

**q2: The observed public HTML route supports a bounded strength for this one anonymous journey.**

Reference: pass.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                                        |
| -------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | pass     | e1 records that public HTML lets an anonymous visitor read eligibility criteria without an account, supporting a bounded access strength for this journey without establishing access for every community or broader sustainability. Evidence: e1. |
| DeepSeek V4.1 Flash (high) | pass     | e1 records that the public HTML worked without an account for reading eligibility criteria within the declared one-journey boundary, supporting only that bounded access strength. Evidence: e1.                                                   |

**q3: Missing necessity documents establish that the service has no social value.**

Reference: fail.

| Model                      | Judgment | Explanation                                                                                                                                                                                                 |
| -------------------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | fail     | The missing necessity documents in e1 leave social value unassessed rather than proving its absence, while the observed anonymous eligibility route establishes only a narrow access benefit. Evidence: e1. |
| DeepSeek V4.1 Flash (high) | fail     | e1's missing necessity records leave social value unresolved; absence of evidence does not establish that the service has no social value. Evidence: e1.                                                    |

**m1: Verified organization-wide STAR score**

Reference: null score (unavailable).

| Model                      | Judgment                 | Explanation                                                                                                                                                                            |
| -------------------------- | ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | null score (unavailable) | e1 covers one anonymous public journey and supplies no organization-wide evaluation or scoring evidence, so a verified organization-wide STAR score is unavailable rather than zero.   |
| DeepSeek V4.1 Flash (high) | null score (unavailable) | No verified organization-wide STAR score or supporting measurement basis is supplied, and e1's one anonymous journey cannot provide one; unavailable remains unknown rather than zero. |

**r1: Request a necessity assessment and theory of change before judging those organizational practices.**

Reference: investigate.

| Model                      | Judgment    | Explanation                                                                                                                                                                                                                                                                        |
| -------------------------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | investigate | Because e1 lacks necessity and business model records, request a scoped necessity assessment and theory of change documenting user need, alternatives, revenue-impact links and review evidence to assess the organizational claims whose execution remains unknown. Evidence: e1. |
| DeepSeek V4.1 Flash (high) | investigate | Because e1 provides neither a necessity assessment nor a documented theory of change, requesting those records is the appropriate bounded step before judging the organizational practices. Evidence: e1.                                                                          |

### audience-research-changes-low-data-journey

Review dimensions: audience-needs. Frozen collector handoff required: yes.

Supplied evidence:

```json
[
  {
    "id": "e1",
    "value": {
      "research": {
        "participants": 12,
        "targetAudience": "rural service users on prepaid mobile data",
        "finding": "8 participants reported exhausting data before completing downloads"
      },
      "implementedChange": {
        "route": "/eligibility",
        "change": "HTML summary before optional 6 MB PDF",
        "testedWithSameAudience": true,
        "completionsBefore": 4,
        "completionsAfter": 10,
        "testParticipants": 12
      },
      "scope": "eligibility prototype test only"
    }
  }
]
```

Reference rationale: Research linked to a concrete change and relevant test supports a partial audience-needs judgment; 12 people are not universal proof.

**q1: The records show audience constraints informed a tested eligibility design change.**

Reference: pass.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                                                                               |
| -------------------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | pass     | e1 records data exhaustion reported by 8 of 12 rural prepaid-data users, followed by an HTML eligibility summary before an optional 6 MB PDF tested with the same audience; this supports the claim only for the eligibility prototype. Evidence: e1.                                     |
| DeepSeek V4.1 Flash (high) | pass     | e1 records research with 12 rural prepaid-mobile users, including 8 who exhausted data before completing downloads, and a same-audience prototype test of an HTML summary before an optional 6 MB PDF, supporting the claimed informed design change within that prototype. Evidence: e1. |

**q2: The test proves every production user can complete the service.**

Reference: fail.

| Model                      | Judgment | Explanation                                                                                                                                                                                                           |
| -------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | fail     | e1 reports 10 completions among 12 participants in an eligibility prototype test, which does not establish completion of the full service by every production user; production outcomes remain unknown. Evidence: e1. |
| DeepSeek V4.1 Flash (high) | fail     | e1 reports 10 completions among 12 prototype participants and limits its scope to the eligibility prototype test, so it does not establish that every production user can complete the service. Evidence: e1.         |

**m1: Improvement in observed prototype completions**

Reference: 6 participants (calculated).

| Model                      | Judgment                    | Explanation                                                                                                                                                                                              |
| -------------------------- | --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | 6 participants (calculated) | Calculated from e1, observed prototype completions increased by 10 minus 4 = 6 participants among 12 tested; this difference does not establish a production effect or isolate causality.                |
| DeepSeek V4.1 Flash (high) | 6 participants (calculated) | The calculated improvement is 10 observed prototype completions after the change minus 4 before, or 6 participants; this within-test change does not establish causation or production-wide performance. |

**r1: Preserve the tested HTML-first eligibility path and track results in production.**

Reference: preserve.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                                                    |
| -------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | preserve | e1 supports preserving the tested HTML-first eligibility path because observed completions rose from 4 to 10 of 12 participants; tracking production completion would check whether that prototype benefit persists, which is currently unknown. Evidence: e1. |
| DeepSeek V4.1 Flash (high) | preserve | e1 demonstrates improved completion with the HTML-first eligibility path among the tested audience, supporting preservation while production tracking is needed to validate results beyond the 12-participant prototype. Evidence: e1.                         |

### inclusive-testing-attendance-not-coverage

Review dimensions: inclusive-testing, access-barriers. Frozen collector handoff required: no.

Supplied evidence:

```json
[
  {
    "id": "e1",
    "value": {
      "testPlan": {
        "targetUsers": [
          "screen-reader users",
          "older phones on slow networks",
          "desktop users"
        ],
        "requiredTask": "apply for a travel pass"
      },
      "completedTesting": {
        "participants": 5,
        "allOn": "recent desktop browsers with mouse input",
        "screenReaderSessions": 0,
        "olderPhoneSessions": 0
      },
      "publicStatement": "We tested with users."
    }
  }
]
```

Reference rationale: Absence from testing is a documented coverage gap, not proof of inaccessible behavior or total absence of user research.

**q1: The supplied testing record demonstrates participation from the two constrained target groups.**

Reference: fail.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                                        |
| -------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | fail     | e1 records five recent-desktop participants but zero screen-reader or older-phone sessions, so participation from the two constrained target groups is unsupported despite the general public testing statement. Evidence: e1.                     |
| DeepSeek V4.1 Flash (high) | fail     | Evidence e1 shows the test plan named screen-reader users and older-phone users, but all five completed participants used recent desktop browsers with mouse input and the record counts zero sessions for either constrained group. Evidence: e1. |

**q2: The evidence establishes that constrained target users cannot complete the task.**

Reference: fail.

| Model                      | Judgment | Explanation                                                                                                                                                                                                           |
| -------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | fail     | e1 contains no sessions with either constrained target group and no task-completion results for them, so it does not establish that they cannot apply for a travel pass; their ability remains unknown. Evidence: e1. |
| DeepSeek V4.1 Flash (high) | fail     | Evidence e1 contains no completed sessions or task outcomes for either constrained group, so it provides insufficient evidence that those users cannot complete the travel-pass task. Evidence: e1.                   |

**m1: Completed sessions with either specified constrained group**

Reference: 0 sessions (observed).

| Model                      | Judgment              | Explanation                                                                                                                                                                                                                                  |
| -------------------------- | --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | 0 sessions (observed) | e1 explicitly records zero screen-reader sessions and zero older-phone sessions, establishing zero completed sessions with either specified constrained group in this supplied record, without establishing task usability for those groups. |
| DeepSeek V4.1 Flash (high) | 0 sessions (observed) | Evidence e1 explicitly reports zero screen-reader sessions and zero older-phone sessions, yielding zero observed completed sessions with either specified constrained group.                                                                 |

**r1: Run the planned travel-pass task with screen-reader users and older-phone participants before judging those barriers.**

Reference: investigate.

| Model                      | Judgment    | Explanation                                                                                                                                                                                                                                                                                                           |
| -------------------------- | ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | investigate | Because e1 records no sessions with either constrained target group, run the planned travel-pass application task with screen-reader users and older-phone participants under the planned slow-network conditions, recording completion and barriers to resolve their currently unknown task usability. Evidence: e1. |
| DeepSeek V4.1 Flash (high) | investigate | Evidence e1 shows both constrained groups were planned but absent from completed testing, so running the travel-pass task with them is the smallest bounded investigation needed before judging those barriers. Evidence: e1.                                                                                         |

### governance-practice-public-operation-record

Review dimensions: governance-practice, sustainability-goals. Frozen collector handoff required: no.

Supplied evidence:

```json
[
  {
    "id": "e1",
    "value": {
      "policy": {
        "ownerRole": "Service sustainability lead",
        "reviewCadence": "quarterly",
        "target": "reduce median initial transfer by 15% from Q1 2026"
      },
      "publishedReviews": [
        {
          "quarter": "Q2 2026",
          "ownerSigned": true,
          "baselineKB": 1000,
          "currentKB": 900,
          "sameScopeAndMethod": true,
          "decision": "optimize image variants next quarter"
        },
        {
          "quarter": "Q3 2026",
          "ownerSigned": true,
          "baselineKB": 1000,
          "currentKB": 820,
          "sameScopeAndMethod": true,
          "decision": "retain budget; investigate consent-state variance"
        }
      ],
      "internalBoardMinutes": null
    }
  }
]
```

Reference rationale: Public operational records can support bounded governance and target judgments; internal source access is not a universal prerequisite. The exact governance-practice expectation is met for the two reported quarters by signed reviews, comparable monitored results and recorded continuation or next actions.

**q1: The published records demonstrate operation of the named review process for the two reported quarters.**

Reference: pass.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                                                               |
| -------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | pass     | e1 documents owner-signed Q2 and Q3 2026 reviews with matched measurements and resulting decisions, supporting operation of the named quarterly process within these two reported quarters only. Evidence: e1.                                                            |
| DeepSeek V4.1 Flash (high) | pass     | e1 shows owner-signed quarterly reviews for Q2 and Q3 2026 with recorded baseline, current values, and matched scope and method, supporting operation of the named review process for those two reported quarters, though the records remain self-reported. Evidence: e1. |

**q2: The supplied Q3 transfer result meets the stated 15% target for its matched scope.**

Reference: pass.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                                               |
| -------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | pass     | e1 reports Q3 transfer of 820 KB against the matched 1000 KB baseline, a calculated 18% reduction exceeding the 15% target within the supplied scope without independent measurement verification. Evidence: e1.                                          |
| DeepSeek V4.1 Flash (high) | pass     | e1 reports a Q3 baseline of 1000 KB and current transfer of 820 KB on matched scope, a calculated reduction of 18%, which exceeds the stated 15% target; the result is supplied self-report rather than independently verified measurement. Evidence: e1. |

**q3: Missing internal board minutes invalidate the observed public review records.**

Reference: fail.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                |
| -------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | fail     | e1 supplies signed public reviews with results and decisions, so unavailable internal board minutes do not invalidate those records, although internal board activity remains unknown. Evidence: e1.                       |
| DeepSeek V4.1 Flash (high) | fail     | e1 records internalBoardMinutes as null, which leaves an unknown rather than contradicting the owner-signed public review records, so the claim that their absence invalidates those records is unsupported. Evidence: e1. |

**q4: Under contextual-review-v1 governance-practice, these public records satisfy the bounded expectation of accountable review, a monitored result and a resulting action over the two declared quarters.**

Reference: pass.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                                                                                          |
| -------------------------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | pass     | e1 links the named owner and quarterly policy to signed Q2/Q3 results and resulting actions, satisfying the bounded contextual-review-v1 governance-practice expectation without establishing organization-wide practice or full WSG conformance. Evidence: e1.                                      |
| DeepSeek V4.1 Flash (high) | pass     | For the declared Q2-Q3 2026 sample, e1 links the quarterly policy and accountable role to owner-signed reviews with monitored results, stable scope and method, and recorded decisions, meeting the bounded contextual expectation without establishing wider organizational practice. Evidence: e1. |

**m1: Q3 transfer reduction from the stated baseline**

Reference: 18 percent (calculated).

| Model                      | Judgment                  | Explanation                                                                                                                                                                                        |
| -------------------------- | ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | 18.0 percent (calculated) | Calculated from e1 as (1000 − 820) / 1000 × 100 = 18.000000%, using the reported matched Q3 scope and decimal KB values rather than independently observed measurements.                           |
| DeepSeek V4.1 Flash (high) | 18.0 percent (calculated) | Calculated from the observed e1 values: (1000 KB baseline - 820 KB Q3 current) / 1000 KB baseline x 100 = 18.000000 percent; this is a derived value from supplied records, not a new measurement. |

**r1: Preserve the documented quarterly review and its scope and method disclosures.**

Reference: preserve.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                                                                                       |
| -------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | preserve | Preserve the quarterly review and scope/method disclosures because e1 demonstrates accountable monitoring and resulting decisions that support comparable progress assessment, with continued validation limited to future documented reviews. Evidence: e1.                                      |
| DeepSeek V4.1 Flash (high) | preserve | e1 demonstrates owner-signed quarterly reviews with baseline and current results, stable scope and method disclosures, and recorded follow-up decisions, so preserving this documented practice retains useful accountability and traceability, subject to its self-reported scope. Evidence: e1. |

### impact-business-model-outputs-not-outcomes

Review dimensions: impact-business-model. Frozen collector handoff required: no.

Supplied evidence:

```json
[
  {
    "id": "e1",
    "value": {
      "publishedTheoryOfChange": {
        "activity": "offer appointment booking reminders",
        "intendedOutcome": "reduce missed appointments and unnecessary travel",
        "outputs": {
          "remindersSent": 10000
        },
        "outcomeMeasures": null,
        "counterfactualOrBaseline": null
      },
      "revenueModel": "annual service subscription",
      "claim": "We saved 10000 journeys."
    }
  }
]
```

Reference rationale: A stated theory of change is useful scope evidence, while output counts alone do not verify outcomes or causality.

**q1: The document articulates an activity and intended social/environmental outcome.**

Reference: pass.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                         |
| -------------------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | pass     | e1 explicitly links offering appointment booking reminders to the intended reduction of missed appointments and unnecessary travel, supporting articulation of an outcome but not its achievement. Evidence: e1.                    |
| DeepSeek V4.1 Flash (high) | pass     | Evidence e1 articulates the activity of offering appointment booking reminders and the intended outcome of reducing missed appointments and unnecessary travel, although it supplies no outcome measures or baseline. Evidence: e1. |

**q2: The count of reminders establishes 10000 journeys avoided.**

Reference: fail.

| Model                      | Judgment | Explanation                                                                                                                                                                                                            |
| -------------------------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | fail     | e1 reports 10000 reminders sent but supplies neither outcome measures nor a baseline or counterfactual, so it does not establish 10000 journeys avoided. Evidence: e1.                                                 |
| DeepSeek V4.1 Flash (high) | fail     | Evidence e1 reports 10,000 reminders sent but provides no attendance or travel outcome measures, baseline, or counterfactual, so avoided journeys remain unknown and the claim of 10,000 is unsupported. Evidence: e1. |

**m1: Verified avoided journeys**

Reference: null journeys (unavailable).

| Model                      | Judgment                    | Explanation                                                                                                                                                                                       |
| -------------------------- | --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | null journeys (unavailable) | e1 supplies a reminder output count without measured attendance or travel outcomes and a baseline, leaving verified avoided journeys unavailable rather than zero.                                |
| DeepSeek V4.1 Flash (high) | null journeys (unavailable) | Evidence e1 supplies only the observed output of 10,000 reminders sent, with no outcome evidence or baseline from which to verify avoided journeys, so the value is unavailable rather than zero. |

**r1: Measure attendance and travel outcomes against a defined baseline before claiming avoided journeys.**

Reference: investigate.

| Model                      | Judgment    | Explanation                                                                                                                                                                                                                       |
| -------------------------- | ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | investigate | Because e1 lacks outcome measures and a baseline, measuring attendance and travel against a defined baseline is justified to test whether reminders avoid journeys before making that claim. Evidence: e1.                        |
| DeepSeek V4.1 Flash (high) | investigate | Evidence e1 shows that only reminder output is observed, so the proposal is justified as an investigation to collect attendance and travel outcomes against a baseline before retaining the avoided-journeys claim. Evidence: e1. |

### service-necessity-and-access-tradeoff

Review dimensions: service-necessity, access-barriers. Frozen collector handoff required: no.

Supplied evidence:

```json
[
  {
    "id": "e1",
    "value": {
      "ownerAssessment": {
        "task": "renew a permit",
        "alternatives": [
          {
            "channel": "in person",
            "medianTravelKm": 18
          },
          {
            "channel": "telephone",
            "taskCompletionTested": true
          },
          {
            "channel": "public HTML",
            "taskCompletionTested": true
          }
        ],
        "decision": "retain telephone support and HTML; reject mandatory native app",
        "reason": "mandatory app excludes devices still used by target audience"
      },
      "appProposal": {
        "purpose": "same renewal task",
        "uniqueNeededCapability": null,
        "accessibilityTest": null
      }
    }
  }
]
```

Reference rationale: Necessity and access require task and audience reasoning; a smaller digital artifact is not automatically the right service.

**q1: The owner assessment compares alternatives and documents an audience constraint relevant to necessity.**

Reference: pass.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                                                                                                                    |
| -------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| GPT-6.1 Sol (high)         | pass     | e1 records an owner comparison of in-person, telephone and public HTML renewal channels and an audience device constraint against a mandatory app, supporting this bounded documentation claim without independently verifying the assessment. Evidence: e1.                                                                   |
| DeepSeek V4.1 Flash (high) | pass     | e1 supports this by listing in-person, telephone, and public HTML alternatives, testing task completion for the latter two, and recording that a mandatory app would exclude devices still used by the target audience, although the audience constraint is owner-attributed rather than independently verified. Evidence: e1. |

**q2: The supplied evidence establishes that a mandatory native app is needed to complete the renewal task.**

Reference: fail.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                                                                                       |
| -------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | fail     | e1 reports tested telephone and public HTML completion and a decision against a mandatory app, while the proposal supplies neither a unique needed capability nor accessibility testing, so app necessity is unsupported. Evidence: e1.                                                           |
| DeepSeek V4.1 Flash (high) | fail     | e1 does not support necessity because both remote non-app alternatives are task-completion-tested and retained by the owner, while the app proposal identifies no unique needed capability and has no accessibility test, although this does not prove the app has no possible use. Evidence: e1. |

**m1: Tested remote non-app channels**

Reference: 2 channels (observed).

| Model                      | Judgment              | Explanation                                                                                                                                                                                         |
| -------------------------- | --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | 2 channels (observed) | e1 explicitly marks telephone and public HTML task completion as tested, giving two observed remote non-app channels in the supplied synthetic owner record, without independent live verification. |
| DeepSeek V4.1 Flash (high) | 2 channels (observed) | e1 records two remote non-app alternatives marked taskCompletionTested, telephone and public HTML, while the third listed alternative is in person and therefore excluded.                          |

**r1: Replace both tested remote channels with the proposed mandatory native app.**

Reference: not_supported.

| Model                      | Judgment      | Explanation                                                                                                                                                                                                                                                                             |
| -------------------------- | ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | not_supported | e1 reports two tested remote renewal channels and an audience device barrier to a mandatory app, while providing no unique app requirement or accessibility test, so replacing both channels has no demonstrated benefit and risks excluding users. Evidence: e1.                       |
| DeepSeek V4.1 Flash (high) | not_supported | e1 does not justify replacing the two tested remote channels because the proposed mandatory app has no documented unique capability or accessibility test and an owner-identified audience constraint, so displacing the working alternatives lacks demonstrated benefit. Evidence: e1. |

### data-minimization-purpose-and-retention

Review dimensions: data-minimization. Frozen collector handoff required: no.

Supplied evidence:

```json
[
  {
    "id": "e1",
    "value": {
      "form": {
        "task": "email a public checklist",
        "requiredFields": ["email", "date of birth", "household income"],
        "optionalFields": []
      },
      "ownerPurposeRecord": {
        "email": "deliver checklist",
        "date of birth": null,
        "household income": null
      },
      "securityRetentionRecord": {
        "deliveryEmailDeletionDays": 7,
        "otherPersonalDataDeletionDays": null
      },
      "observedTask": "checklist delivery succeeds in test when the two extra fields are removed",
      "legalOrOperationalNeedForExtraFields": null
    }
  }
]
```

Reference rationale: The proposal is bounded to extra fields whose absence was tested and whose purpose is explicitly unestablished; no legal conclusion is made.

**q1: The record establishes a necessary purpose for collecting date of birth and household income for this task.**

Reference: fail.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                    |
| -------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| GPT-6.1 Sol (high)         | fail     | e1 records no purpose or legal or operational need for date of birth or household income, so necessity is unsupported by this record rather than proven absent in all contexts. Evidence: e1.                                  |
| DeepSeek V4.1 Flash (high) | fail     | The purpose and legal-or-operational-need records in e1 cover only checklist delivery by email and leave date of birth and household income undocumented, so the claimed necessary purposes are not established. Evidence: e1. |

**q2: The supplied removal test supports a scoped opportunity to reduce data collection.**

Reference: pass.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                                  |
| -------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | pass     | e1 reports successful checklist delivery with both extra fields removed, supporting reduced collection for this tested task without establishing behavior across other tasks or backend retention. Evidence: e1.                             |
| DeepSeek V4.1 Flash (high) | pass     | The e1 removal test observes checklist delivery succeeding after the two extra required fields are removed, supporting a scoped reduction opportunity for only this tested task rather than untested production or other uses. Evidence: e1. |

**m1: Required fields without a documented purpose in this record**

Reference: 2 fields (calculated).

| Model                      | Judgment              | Explanation                                                                                                                                                                                                                |
| -------------------------- | --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | 2 fields (calculated) | Calculated from e1, two required fields—date of birth and household income—have null purpose records, while email has a delivery purpose; this count concerns documentation in the supplied record.                        |
| DeepSeek V4.1 Flash (high) | 2 fields (calculated) | e1 lists three required fields and documents a purpose only for email, leaving a calculated count of two fields without a documented purpose; this is a record gap, not proof that either field is inherently purposeless. |

**r1: Remove the two purpose-free required fields from this tested checklist task after confirming the supplied purpose record remains current.**

Reference: fix.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                                                                                               |
| -------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | fix      | e1 supports removing both extra required fields after confirming the purpose record remains current, reducing personal data collection for the tested checklist task; recheck delivery after the change because broader task behavior and retention enforcement remain unverified. Evidence: e1.          |
| DeepSeek V4.1 Flash (high) | fix      | The e1 record leaves both fields without a documented purpose while the tested delivery succeeds without them, so removal is supported for this task subject to the proposal's stated confirmation that the purpose record remains current; production and untested uses remain unverified. Evidence: e1. |

### content-lifecycle-policy-and-stale-path

Review dimensions: content-lifecycle. Frozen collector handoff required: yes.

Supplied evidence:

```json
[
  {
    "id": "e1",
    "value": {
      "policy": {
        "reviewIntervalDays": 90,
        "archiveRule": "obsolete guidance must redirect to the current equivalent"
      },
      "sample": {
        "path": "/permit-2024",
        "lastReviewedDaysAgo": 410,
        "text": "Use the retired application form",
        "currentEquivalent": "/permit",
        "redirectsToCurrent": false,
        "currentPageLinksBack": true
      },
      "siteInventoryCompleteness": "one sampled path only"
    }
  }
]
```

Reference rationale: A concrete observed contradiction supports a sampled lifecycle failure; it does not justify a site-wide content verdict.

**q1: The sampled retired guidance follows the supplied review and replacement policy.**

Reference: fail.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                                  |
| -------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | fail     | e1 contradicts compliance for /permit-2024: its last review was 410 days ago against a 90-day interval, it still instructs use of a retired form, and it lacks the required redirect to /permit; other paths were not sampled. Evidence: e1. |
| DeepSeek V4.1 Flash (high) | fail     | Evidence e1 shows the sampled path was last reviewed 410 days ago against a 90-day interval and does not redirect to its current equivalent, contradicting the supplied policy for this sample. Evidence: e1.                                |

**q2: This single stale path establishes that every page is obsolete.**

Reference: fail.

| Model                      | Judgment | Explanation                                                                                                                                                                |
| -------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | fail     | e1 explicitly covers one sampled path only, so its obsolete instruction cannot establish that every page is obsolete; the remaining pages’ state is unknown. Evidence: e1. |
| DeepSeek V4.1 Flash (high) | fail     | Evidence e1 covers only one sampled path and explicitly lacks a complete site inventory, so the stale path cannot establish that every page is obsolete. Evidence: e1.     |

**m1: Days beyond the supplied review interval for this path**

Reference: 320 days (calculated).

| Model                      | Judgment              | Explanation                                                                                                                                                                                      |
| -------------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| GPT-6.1 Sol (high)         | 320 days (calculated) | Calculated from e1 as 410 days since review minus the supplied 90-day review interval, yielding exactly 320 days overdue for this path; no calendar dates or site-wide result are inferred.      |
| DeepSeek V4.1 Flash (high) | 320 days (calculated) | Calculated from evidence e1, 410 days since the last review minus the 90-day interval equals 320 days beyond the interval for this supplied path, and the result does not extend to other pages. |

**r1: Replace the sampled retired form instruction with the current equivalent and repair its inbound link.**

Reference: fix.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                                                                                                          |
| -------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | fix      | e1 supports replacing the retired-form instruction with /permit guidance, adding the required redirect, and repairing the current page’s link back to the stale path so applicants reach current instructions; validate the resulting link and redirect because the corrected journey is not supplied. Evidence: e1. |
| DeepSeek V4.1 Flash (high) | fix      | Evidence e1 shows retired /permit-2024 guidance remains non-redirecting while /permit is the current equivalent and the current page links back to it, so replacing the stale instruction and repairing the link addresses the observed issue for this sample. Evidence: e1.                                         |

### end-of-life-plan-versus-tested-retirement

Review dimensions: service-end-of-life. Frozen collector handoff required: no.

Supplied evidence:

```json
[
  {
    "id": "e1",
    "value": {
      "retirementPlan": {
        "oldHost": "legacy.scope.example",
        "successor": "scope.example",
        "exportAvailable": true,
        "retentionRule": "delete migrated personal data after verification and 30-day appeal window",
        "owner": "service operations"
      },
      "executedChecks": {
        "oldPublicGuideRedirects": true,
        "exportTestPassed": true,
        "migrationVerificationPassed": true,
        "appealWindowElapsed": false,
        "deletionCompleted": false
      },
      "expectedChecks": "verify migration, preserve export, honor appeal window, then execute approved deletion"
    }
  }
]
```

Reference rationale: A timed future obligation is not an observed present failure; partial implementation does not establish full completion.

**q1: The observed redirects and tested export demonstrate two implemented retirement measures.**

Reference: pass.

| Model                      | Judgment | Explanation                                                                                                                                                                                                      |
| -------------------------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | pass     | e1 records working old public guide redirects and a passed export test, supporting these two implemented retirement measures within the supplied checks, without establishing full plan execution. Evidence: e1. |
| DeepSeek V4.1 Flash (high) | pass     | e1 records a successful old-public-guide redirect and a passed export test, which supports exactly two implemented retirement measures without establishing broader plan completion. Evidence: e1.               |

**q2: The lack of deletion before the appeal window closes contradicts this supplied plan.**

Reference: fail.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                     |
| -------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | fail     | e1 requires deletion after migration verification and the 30-day appeal window, so pending deletion while that window remains open follows the supplied sequence, although eventual deletion is unverified. Evidence: e1.       |
| DeepSeek V4.1 Flash (high) | fail     | e1 requires deletion only after the 30-day appeal window and records that the window has not elapsed, so the lack of deletion is plan-consistent rather than contradictory; eventual deletion remains unobserved. Evidence: e1. |

**q3: The supplied checks establish complete execution of the end-of-life plan.**

Reference: fail.

| Model                      | Judgment | Explanation                                                                                                                                                                                                            |
| -------------------------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | fail     | e1 records successful redirects, export and migration verification but an unelapsed appeal window and incomplete deletion, so complete execution is unsupported and later completion remains unverified. Evidence: e1. |
| DeepSeek V4.1 Flash (high) | fail     | e1 shows migration verification and export testing succeeded, but the appeal window has not elapsed and deletion is not complete, so the checks do not establish complete plan execution. Evidence: e1.                |

**m1: Implemented observed retirement measures named in the first question**

Reference: 2 measures (calculated).

| Model                      | Judgment                | Explanation                                                                                                                                                                                                         |
| -------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | 2 measures (calculated) | Calculated from e1 as one observed redirect measure plus one tested export measure, the count is 2 for the measures named in q1 and does not establish completion of other retirement steps.                        |
| DeepSeek V4.1 Flash (high) | 2 measures (calculated) | e1 names two implemented retirement measures assessed in q1, the observed public-guide redirect and the passed export test; this calculated count does not include unobserved measures or completed plan execution. |

**r1: Preserve personal data until the supplied appeal window closes and the approved deletion step becomes due.**

Reference: preserve.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                                                                                               |
| -------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | preserve | e1 supports retaining personal data through the still-open appeal window to preserve the planned appeal opportunity, with approved deletion due afterward and its eventual execution unverified. Evidence: e1.                                                                                            |
| DeepSeek V4.1 Flash (high) | preserve | e1 explicitly requires deletion only after migration verification and a 30-day appeal window and shows that window has not elapsed, so preserving the migrated personal data until the approved deletion becomes due is supported; later deletion timing remains conditional on completion. Evidence: e1. |

### ci-duplicate-trigger-unmeasured-priority

Review dimensions: source-provenance, priority, ci-automation. Frozen collector handoff required: no.

Supplied evidence:

```json
[
  {
    "id": "e1",
    "value": {
      "source": {
        "repository": "https://code.example/org/site",
        "commit": "2222222222222222222222222222222222222222",
        "workflowPath": ".github/workflows/ci.yml",
        "excerptMatchesPinnedSource": true,
        "events": ["push", "pull_request"],
        "job": "run lint and unit tests",
        "sourceComment": "Renovate branches can trigger both event families"
      },
      "operationalEvidence": {
        "workflowRunHistory": null,
        "runsPerMonth": null,
        "medianRuntimeMinutes": null,
        "actualDuplicateRunsConfirmed": false,
        "branchFilteringAndConcurrencyInspected": false
      },
      "visitorFinding": {
        "observation": "optional map bundle loads before interaction on all 3 sampled mobile visits",
        "receivedBytesPerVisit": 1800000,
        "ownerTaskNeedsMapBeforeIntent": false
      },
      "priorityRule": "Investigate unmeasured internal automation candidates at low provisional priority before asserting avoidable runs. Prioritize demonstrated visitor-path regressions over candidates without run frequency or runtime."
    }
  }
]
```

Reference rationale: Source confirms overlapping event configuration, but job frequency, actual duplication and runtime are unmeasured. A bounded check is justified; no quantified saving or high comparative priority follows from the candidate alone.

**q1: The source event configuration establishes a candidate for duplicate CI work, pending branch filtering and operational checks.**

Reference: pass.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                                                                                            |
| -------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| GPT-6.1 Sol (high)         | pass     | The pinned-source-matching configuration in e1 includes push and pull_request triggers, supporting a duplicate-work candidate while branch filters, concurrency and actual duplicate runs remain unverified. Evidence: e1.                                                                             |
| DeepSeek V4.1 Flash (high) | pass     | The workflow is configured for both push and pull_request events, with a source comment noting that Renovate branches can trigger both, which supports a duplicate-work candidate; branch filtering, concurrency, run history, and actual duplication remain uninspected or unconfirmed. Evidence: e1. |

**q2: The candidate establishes a quantified monthly CI energy saving.**

Reference: fail.

| Model                      | Judgment | Explanation                                                                                                                                                                                |
| -------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| GPT-6.1 Sol (high)         | fail     | e1 supplies neither run frequency nor runtime or energy measurements and does not confirm avoidable duplicates, so it cannot establish quantified monthly CI energy savings. Evidence: e1. |
| DeepSeek V4.1 Flash (high) | fail     | No run frequency, runtime, or energy measurement is supplied, and duplicate runs are unconfirmed, so the candidate cannot establish any quantified monthly CI energy saving. Evidence: e1. |

**q3: The evidence justifies ranking this unmeasured CI candidate above the demonstrated visitor-path map transfer finding.**

Reference: fail.

| Model                      | Judgment | Explanation                                                                                                                                                                                                                                                           |
| -------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | fail     | The priority rule in e1 places the unmeasured CI candidate below the optional map transfer observed before interaction on all three sampled mobile visits, with no owner task requiring the map before intent; CI frequency and runtime remain unknown. Evidence: e1. |
| DeepSeek V4.1 Flash (high) | fail     | The supplied priority rule calls for prioritizing the demonstrated visitor-path map transfer finding over unmeasured CI candidates, contradicting the proposed ranking. Evidence: e1.                                                                                 |

**m1: Verified avoidable monthly CI runtime**

Reference: null minutes/month (unavailable).

| Model                      | Judgment                         | Explanation                                                                                                                                                                                 |
| -------------------------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | null minutes/month (unavailable) | e1 provides no run history, monthly frequency or median runtime and confirms no actual duplicate runs, leaving verified avoidable monthly CI runtime unavailable rather than zero.          |
| DeepSeek V4.1 Flash (high) | null minutes/month (unavailable) | Workflow run history, runs per month, and median runtime are all null, and actual duplicate runs are unconfirmed, so verified avoidable monthly CI runtime is unavailable rather than zero. |

**m2: Observed initial map bundle transfer per sampled mobile visit**

Reference: 1800 kB (observed).

| Model                      | Judgment             | Explanation                                                                                                                                                                                                   |
| -------------------------- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | 1800.0 kB (observed) | e1 reports 1800000 received bytes per sampled mobile visit, equivalent to 1800.0000 decimal kB by division by 1000; the observation covers three visits and does not establish site-wide transfer or savings. |
| DeepSeek V4.1 Flash (high) | 1800.0 kB (observed) | The observed 1,800,000 bytes per sampled mobile visit convert exactly to 1,800 decimal kB; this is limited to three sampled visits and does not establish all-visitor behavior.                               |

**r1: At low provisional priority, inspect branch filters, concurrency and run history to establish whether Renovate events duplicate avoidable CI work.**

Reference: investigate.

| Model                      | Judgment    | Explanation                                                                                                                                                                                                                                    |
| -------------------------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPT-6.1 Sol (high)         | investigate | e1 supports inspecting branch filters, concurrency and run history at low provisional priority to determine whether the dual triggers cause avoidable CI work, whose frequency, runtime and potential savings remain unverified. Evidence: e1. |
| DeepSeek V4.1 Flash (high) | investigate | The dual event triggers establish a low-priority candidate, while branch filtering, concurrency, run history, and actual duplicate runs are unmeasured; inspecting them is the bounded next step to resolve the uncertainty. Evidence: e1.     |

## Review and reproduction

Identify the case ID and whether feedback concerns supplied facts, claim wording, numeric basis, reference labels, a proposed operation or model interpretation. The [case book](../initial-implementation/assets/scope-benchmark-cases.json) preserves all inputs, references and rationales. The [results](../initial-implementation/assets/scope-benchmark-results.json) retain complete reports, diagnostics and paired hashes. Regenerate with `uv run --locked --script benchmarks/render_scope.py`, then format the generated Markdown with Prettier.
