# Digital Carbon Ratings in an audit

Reviewed November 4, 2026. **Integrate Digital Carbon Ratings as a deterministic, versioned reporting layer alongside WSG findings.** A rating describes estimated emissions under a specific calculation profile. It does not replace the broader assessment of user needs, accessibility, governance, and operational practices.

## Relationship to SWDM and WSG

Digital Carbon Ratings maps estimated emissions to an A+–F scale. The published scale uses SWDM version 4 and transfer-size percentiles from the June 1, 2023 HTTP Archive crawl. Its comparison profile uses global electricity carbon intensity with a green-hosting adjustment. This is a historical comparison baseline, not a live percentile of today's web. [Digital Carbon Ratings methodology](https://sustainablewebdesign.org/digital-carbon-ratings/).

SWDM estimates operational and embodied emissions across data centers, networks, and user devices. Transfer is a proxy input; the result is not an instrument reading of energy used by a particular page. The methodology permits customized inputs, but changing those inputs also changes comparability. [SWDM version 4](https://sustainablewebdesign.org/estimating-digital-emissions/).

Keep three distinct outputs in the report:

| Output                | Meaning                                                                               | Appropriate use                                     |
| --------------------- | ------------------------------------------------------------------------------------- | --------------------------------------------------- |
| WSG/STAR findings     | Evidence about particular requirements and practices                                  | Explain improvements, coverage, and unknowns        |
| Digital Carbon Rating | A band derived from estimated page-view emissions under a declared profile            | Communicate a comparable transfer-related indicator |
| Scenario measurements | Bytes, requests, observed behavior, and optionally separately bounded energy readings | Assess changes for a particular successful task     |

An A+ page could still autoplay distracting content, omit accessible alternatives, or make unsupported organizational claims. A larger essential service could have valid reasons for its transfer volume. These are proposed reporting interpretations, not exceptions secretly added to the published rating scale.

## Reuse CO2.js, with explicit versions

CO2.js already implements ratings, including separate thresholds for SWDM versions 3 and 4. At inspected commit `27cbe8328aeaad0824fb07b3640dc45b72228c7b`, its constructor accepts `model: "swd"`, `version: 4`, and `rating: true`; trace methods expose calculation inputs. Reuse the library behind an adapter rather than asking a model to calculate or assign a grade. [CO2.js constructor and trace methods](https://github.com/thegreenwebfoundation/co2.js/blob/27cbe8328aeaad0824fb07b3640dc45b72228c7b/src/co2.js).

The inspected version 4 thresholds are:

| Rating | Upper bound in grams CO2e per page view |
| ------ | --------------------------------------- |
| A+     | 0.040                                   |
| A      | 0.079                                   |
| B      | 0.145                                   |
| C      | 0.209                                   |
| D      | 0.278                                   |
| E      | 0.359                                   |
| F      | Above 0.359                             |

Source: [versioned constants](https://github.com/thegreenwebfoundation/co2.js/blob/27cbe8328aeaad0824fb07b3640dc45b72228c7b/src/constants/index.js). The helper compares unrounded values with inclusive upper bounds. Consequently, `0.3591` falls in F even if a display rounds it to `0.359`; the published table's rounded F threshold should not create a gap in implementation. [Rating helper](https://github.com/thegreenwebfoundation/co2.js/blob/27cbe8328aeaad0824fb07b3640dc45b72228c7b/src/helpers/index.js).

Pin the package release and resolved source revision, SWDM version, rating constants, capture protocol, and hosting evidence. Do not rely on a library's default model: CO2.js changed its default to version 4 in release 0.18.0. A grade change after an upgrade may be a methodology change even when the page is unchanged. [CO2.js changelog](https://github.com/thegreenwebfoundation/co2.js/blob/27cbe8328aeaad0824fb07b3640dc45b72228c7b/CHANGELOG.md).

## Proposed integration contract

The collector records transferred bytes and their definition. A rating adapter accepts that observation and a named calculation profile, validates inputs, calls the pinned estimator, and writes the result with its provenance. The LLM explains the result and its limitations; it does not overwrite the calculation.

Store at least:

- Target URL, page state, capture identifier, successful-load status, measurement window, and cache/consent profile.
- Raw transfer bytes, size definition, failed requests, excluded collector traffic, and capture completeness.
- Hosting lookup response, retrieval time, domain scope, and whether the result was positive, negative, or unavailable.
- Estimation library/revision, SWDM version, grid factors, visit/cache assumptions, and rating-threshold revision.
- Unrounded estimated grams, rendered precision, rating, and any sensitivity range.
- Calculation status and whether the profile is suitable for comparison with the published rating scale.

An unavailable hosting lookup must remain distinguishable from a negative result. If the adapter uses an unverified-hosting default, label the assumption and optionally calculate both bounds. Do not turn an HTTP error, incomplete capture, or zero recorded bytes into an A+ result. Likewise, detecting green hosting for the main domain does not independently verify every third party; document the chosen page-level convention and keep per-origin analysis separate.

Use two named profiles where internal data exists. The **comparison profile** preserves the agreed Digital Carbon Ratings assumptions. A **contextual estimate** can use better local information, such as a documented deployment region or measured return-visit mix. Show the second as a scenario estimate; do not silently substitute it into the comparable rating. Internal knowledge should explain differences between estimates, not provide a convenient route to a better badge.

## Page views, journeys, and site summaries

A multi-step journey is not a single page view. Keep its measured resource use and task outcome separately. Publish page ratings for the sampled states with the sampling manifest. If a site summary is wanted, show the distribution of ratings and sample coverage first.

Do not average letter grades. A traffic-weighted emissions estimate requires suitable traffic evidence and an explicit functional unit; an unweighted sample average is only an average of that sample. Do not claim whole-site coverage from a homepage or a sitemap subset.

Avoid counting caching twice. Applying a modeled return-visit reduction to already measured warm-cache bytes could apply two reductions to the same traffic. Validate which input the estimator expects and keep cold measurements, warm measurements, and modeled visit mixtures distinct. The inspected [version 4 implementation](https://github.com/thegreenwebfoundation/co2.js/blob/27cbe8328aeaad0824fb07b3640dc45b72228c7b/src/sustainable-web-design-v4.js) also distinguishes its reload ratio from the methodology's cache ratio; that translation needs a fixture.

## Validation before publishing ratings

Add deterministic golden cases for every threshold, values just above and below it, byte-unit conversions, hosting assumptions, zero/invalid inputs, incomplete captures, and cold/warm behavior. Verify the estimator against reviewed calculation examples and preserve both old and new outputs when methodology versions change.

Add knowledge/evidence benchmark cases asking an agent to reject common overclaims: “A means WSG compliant,” “F proves the service is unnecessary,” and “a rating improved, therefore measured physical emissions fell.” The correct response should identify the claim's missing evidence.

Before releasing a badge, settle the exact capture profile, hosting convention, and boundary behavior against the methodology and library. This research inspected source code but did not execute CO2.js or establish cross-tool rating parity. The [benchmark plan](../agentic-audits/benchmark.md) makes this a prerequisite to public rating claims.
