# Staged measurements and contextual evidence

The active collection workflow is an executable Python script, `audit/run.py`, managed by uv. It measures the site as found, then discovers footprint documentation and runs the PyPI Wappalyzer package in a separate browser. The original JavaScript experiments and frozen benchmark artifacts remain available for historical reproduction.

## Measurement contract

The **initial load is the headline figure**: a fresh browser context, the initial viewport, no scrolling, and no consent interaction. “Above the fold” describes the observation state; it does not mean that offscreen resources already requested by the page are subtracted.

| Checkpoint      | Measurement                                                                                 | Reporting use                                                               |
| --------------- | ------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| `initial`       | Navigation through load plus the configured observation window                              | Headline received bytes and eligible provisional carbon calculation         |
| `after_consent` | Cumulative received bytes after the configured cookie choice and another observation window | Identify traffic present after interaction; record choice and action status |
| `after_scroll`  | Cumulative received bytes after incremental scrolling and a final observation window        | Identify the extra cost of reading the page and deferred resources          |

Each checkpoint also records `additionalBytes` since the preceding checkpoint. These deltas include background activity and late completion of earlier requests; they are not automatically traffic caused by a cookie click or an estimate of avoidable savings. Requests retain the phase in which they started. A later completion does not rewrite the frozen initial measurement.

Accept and reject branches use independent fresh contexts. Compare their complete trajectories and stated choices, not an accept-then-reject sequence whose cookies and caches have already changed. Missing optional controls, failed required actions, and successful clicks have distinct outcomes. A successful click does not prove that consent preferences were enforced. For a site without a configured banner interaction, the middle checkpoint is explicitly marked inapplicable or absent, not treated as a successful consent decision.

The fixed desktop profile is 1,280 × 800 CSS pixels at device scale factor 1, with a three-second observation window. Scrolling uses bounded viewport increments, waits for lazy loading, and records whether the bottom was reached. An infinite feed or delayed content can remain incomplete when the step limit is reached. This protocol does not measure arbitrary eventual activity, all devices, or every user journey.

### Measure resource failures as part of the site

A failed Plausible script is a contextual observation, not a reason to repair the site before auditing it. No resources are blocked or substituted to produce cleaner numbers. HTTP error responses contribute their observed traffic. A fully measured 404 does not by itself make byte accounting incomplete; aborted or unfinished transfers with unknown bytes do.

The ledger distinguishes `resourceErrors`, `unresolvedRequestIds`, and `accountingStatus`. It reports observed bytes even when the accounting is partial. Partial encoded bodies contribute known bytes without being added twice when a final total arrives. Unknown bytes are not asserted to be zero. Initial-load carbon calculations remain withheld for incomplete accounting or a failed main document; the page's as-is traffic observations remain reportable.

The main CDP session does not establish complete child-frame or WebSocket accounting. Sticky coverage flags retain these limitations even if a frame disappears before a checkpoint. Service workers are blocked in this profile. The next measurement validation should compare these totals against another collector, including cross-origin frames, expected aborts, and streaming traffic.

## Interaction configuration

`audit/targets.json` selects URLs and branches. Actions support `click`, `fill`, `press`, `check`, and `select`, with an optional `frameSelector` for embedded controls. Configure selectors and intended choices explicitly; the script does not guess which button means “accept” or “reject.”

```json
{
  "id": "example-home",
  "url": "https://example.com/",
  "branches": [
    {
      "name": "reject",
      "actions": [
        {
          "type": "click",
          "selector": "[data-cookie-opt-out]",
          "optional": true
        }
      ]
    }
  ]
}
```

Additional actions can support bounded task-specific interactions. New flows still need a success condition; filling or clicking a control is not evidence that the user's underlying task succeeded. The default Wagtail configuration does not submit contact or feedback forms or play video.

## Footprint-document discovery

The discovery stage checks DNS TXT pointers, `/carbon.txt`, `/.well-known/carbon.txt`, and the `CarbonTxt-Location` HTTP header. It parses TOML and follows declared disclosure URLs. Parsing is recorded separately from schema validation; the collector is not the carbon.txt validator. It retains the declared version, document metadata, retrieval outcome, digest, and bounded main/article excerpts. See the [carbon.txt discovery conventions](https://carbontxt.org/faq) and [syntax reference](https://carbontxt.org/syntax).

When no usable carbon.txt is found, the collector looks for sustainability and footprint links in the sampled pages and tries common statement paths. A `statementUrls` list can supply known related documentation. The guide target uses the Wagtail project sustainability statement as such a hint; related ownership does not by itself establish the scope of a statement. The document must actually cover the target site.

Discovery is bounded to six disclosure candidates per site, with one-hop follow-up to supporting footprint material. HTTP requests have byte, inactivity, and total-duration limits. Missing documents, malformed URLs, parsing failures, and timeouts remain explicit. Failure to find a statement within this scope is not proof that none exists, and it is not a WSG failure by itself.

Keep an external statement's site/population, reporting period, functional unit, methodology, hosting claims, and uncertainty separate from our sampled page-load estimate. Finding a disclosure never automatically sets the hosting scenario to green, validates an annual footprint, or establishes organizational compliance. [Carbon.txt purpose and setup](https://carbontxt.org/quickstart).

## Technology-informed reporting

The workflow uses **`wappalyzer==2.0.4` from PyPI**, in full browser mode with a reused scanner and one worker. Package and bundled extension hashes are recorded. The separate extension-enabled browser runs after collection, so its requests and instrumentation do not contaminate the three measured phases. [PyPI package and API documentation](https://pypi.org/project/wappalyzer/).

Detections choose relevant follow-up questions. Wagtail/Django suggests examining renditions, rich-text rendering, templates, cache invalidation, and server work before proposing a frontend-framework rewrite. A Cloudflare detection describes part of delivery, not the electricity mix of origin hosting. A PWA fingerprint does not prove offline support. A Plausible fingerprint does not prove that its script loaded successfully.

Raw confidence and version fields are retained as tool outputs, not calibrated probabilities or verified deployment identities. Missing detection is not evidence of absence. `reviewHints` makes these technology-specific implications available to subsequent reviewers as well as in the human report.

## Executed observations

The [staged evidence](assets/staged-audit.json) records actual measurements, carbon.txt discovery, and Wappalyzer results. The [WIP audit report](wagtail-audit.md) uses initial-load figures as its primary table and separates later interaction traffic. Earlier cold/warm captures and model reviews remain linked as historical evidence; the model arms have not yet been rerun against this revised collection protocol and skill.

## Run and verify

```sh
uv sync --dev
npm ci
just audit-install
uv lock --check --script audit/run.py
just audit-sites
```

Or supply another target manifest and output path:

```sh
uv run --locked --script audit/run.py \
  --targets audit/targets.json \
  --output .audit-work/staged-audit.json \
  --publish docs/initial-implementation/assets/staged-audit.json
```

The executable shebang also supports `./audit/run.py`. Inline PEP 723 metadata declares Python 3.14, compatible uv versions, and pinned dependencies; the adjacent script lockfile resolves transitives. The development environment includes the same packages for tests and type checking. [uv scripts and lockfiles](https://docs.astral.sh/uv/guides/scripts/), [uv version requirement](https://docs.astral.sh/uv/reference/settings/#required-version).

Collection, orchestration, disclosure parsing, technology adaptation, and publication are Python. A narrow subprocess bridge calls the existing pinned CO2.js adapter rather than reimplementing SWDM. Node is also retained for the historical fixture and benchmark tools. New scripting work follows the [Python contribution convention](../contributing/README.md#coding-style-conventions).

Private results are checkpointed after each completed run and discovery step. Publication removes URL userinfo, query strings, and fragments, including URLs in keys and error strings. Raw artifact hashes preserve provenance. `--skip-technology` is available for debugging without technology detection and does not stand in for a successful technology scan.

## Next benchmark cases

Expand the Harbor corpus around the new distinctions before a broad crawl:

| Case family                          | Contrasting examples                                                                              | What the evaluation should catch                                                                |
| ------------------------------------ | ------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Interaction phases                   | No banner; accept/reject; absent selector; failed required click; iframe controls                 | Incorrect headline phase, assumed consent success, and mixed cache/consent states               |
| Deferred content                     | Already eager; native lazy loading; explicit activation; infinite scroll                          | Unsupported savings and failures to retain scope or successful activation prerequisites         |
| As-is failures                       | Fully measured 404; partial aborted request; successful third-party script                        | Conflating site errors with measurement errors, or prioritizing repair over measurement         |
| Footprint disclosures                | Root, well-known, DNS/header pointers, missing or malformed file, stale/different-scope statement | Treating discovery as validation or substituting an incompatible emissions figure               |
| Technology context                   | CMS, static site, client-rendered application, misleading/stale fingerprint                       | Generic fixes that conflict with actual architecture or assume version/operation from detection |
| Numerical and recommendation quality | Correct outcome with wrong viewport, units, denominator, or unnecessary remediation               | Explanations that pass an outcome grader but remain untrustworthy                               |

Use deterministic tests for collection and parsing, then frozen public/source-assisted evidence tasks for interpretation. Run the model-bearing campaign with Sol/low and Neuralwatt DeepSeek/high on identical inputs. Keep owner-reviewed development cases separate from a held-out set. This is the next experiment, not a claim that the expanded benchmark has already run.
