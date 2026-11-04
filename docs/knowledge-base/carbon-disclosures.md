# Using carbon.txt as audit evidence

Carbon.txt is an evidence index, not a green-hosting badge. An audit should distinguish discovery, parseability, declared scope, document retrieval, and substantiation. The [carbon.txt FAQ](https://carbontxt.org/faq) describes DNS, root, well-known, and HTTP-header discovery, and explains how declarations link to supporting disclosures.

## What the collector does

`audit/run.py` tries DNS pointers, `/carbon.txt`, `/.well-known/carbon.txt`, then an HTTP `CarbonTxt-Location` pointer. It records the discovery route, response and redirect information, file hash, declared version, and parsed declarations. A recognized declaration can be present even when it has no usable disclosure URLs. The legacy `carbonStatus` field describes usable disclosure discovery; the newer `carbonPresence` field separates presence from that result.

The search also follows sustainability links, supplied statement hints, and bounded common-path fallbacks. Up to six documents are retrieved; failed requests and unvisited declarations remain visible. A parent site's statement needs an explicit relationship to the audited origin. Neither failure to retrieve a file nor a limited search proves there is no policy.

This is the website's v0.x discovery profile. The separate [carbon.txt Internet-Draft](https://www.ietf.org/archive/id/draft-cowlishaw-carbontxt-00.html) describes a 1.0.0-RC1 profile with different discovery and redirect rules. We do not claim to implement that draft. Version changes need a new collector profile and regression cases.

## How agents use the contents

The [current syntax](https://carbontxt.org/syntax) includes organization disclosures, certification references, and upstream service relationships. `audit/disclosures.py` turns those fields into a review artifact:

- **Disclosures:** original type, title, URL, domain, validity date, and certification references, with pointers back to the declaration and retrieved document.
- **Scope:** exact-host matches, different declared hosts, and undeclared scope stay distinct. Matching the host establishes a declaration's intended scope, not its accuracy.
- **Periods:** validity is compared to the capture timestamp. A past annual report remains useful historical evidence; its date does not automatically make a current website fail.
- **Providers:** CDN, application hosting, storage, and build relationships remain attributed declarations. Agents can use them to target provider research and corroborate technology observations.
- **Uncertainty:** partial structural diagnostics, unavailable documents, and unresolved certification references become concrete review tasks. Parsing and these diagnostics are not full schema validation.

The claims reviewer then reads the retrieved documents, checks their organization, service boundary, method, period, arithmetic, and supporting evidence, and cites each conclusion. It should look for consistency between a public claim, the website measurements, and any supplied source or internal records. Public declarations alone do not change the SWDM renewable-hosting input.

The reference [Python validator](https://carbon-txt-validator.readthedocs.io/) is a possible future schema-validation adapter. Its result would still need to be kept separate from verification of the declared claims. The current interpreter requires no validator API key.

## Repeatable execution

The coordinating agent invokes the staged collector, then derives the review artifact:

```sh
uv run --locked --script audit/disclosures.py \
  --input .audit-work/site/staged.json \
  --output .audit-work/site/disclosures.json
```

The export includes source and script hashes. Reviewers cite JSON pointers, rather than an untraceable summary. Historical measurements are not rewritten when the interpretation changes.

The [derived pilot artifact](../initial-implementation/assets/carbon-disclosure-review.json) uses the existing staged capture. Guide's carbon.txt presence was not established within that search. Wagtail's version 0.4 file declared four disclosure URLs and four upstream service records: Cloudflare, Heroku, AWS, and GitHub. Its 2023 and 2024 reports are past their declared validity periods; that is a reason to check the period of a new claim, not to discard the reports. The existing site scores have not been recalculated from these new interpretation fields.
