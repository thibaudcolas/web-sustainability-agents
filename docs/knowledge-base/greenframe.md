# Optional GreenFrame client measurements

GreenFrame is useful for repeated user journeys that include rendering, waiting, consent choices, and scrolling. Its CLI collects browser resource activity and converts it into modeled energy and carbon quantities. Server containers are optional, so public websites can be investigated without deploying or instrumenting their backends. See the [CLI documentation](https://docs.greenframe.io/commands/).

Keep three separate quantities in reports: transferred-data SWDM/Digital Carbon Ratings estimates, co2-runner CPU-package observations, and GreenFrame's modeled scenario energy. Their boundaries overlap and their assumptions differ; adding them would double count. A GreenFrame result is not direct electricity-meter evidence.

## The local example

The supplied `local/bakerydemo-gold-benchmark` checkout, revision `973b3f7e441ceac867a803924da29cbd2bf42d54`, contains homepage, search, filtering, contact, and admin journeys. Its homepage scenario follows a visitor into a bread index and detail page. That is a useful pattern for task-level auditing, rather than measuring only a landing page.

Its configs include application/database containers, and its JavaScript files use the older standalone-function form. Our client adapter omits those containers and generates the `module.exports` form required by [GreenFrame 2.x scenarios](https://docs.greenframe.io/scenario/). It also uses explicit phases: GreenFrame's default scenario scrolls, so it would not represent the requested first-load headline.

## Agent invocation

`audit/greenframe.py` prepares an isolated client-only configuration and checks prerequisites. It requires CLI 2.0.1, based on the [upstream release](https://github.com/marmelab/greenframe-cli/releases/tag/v2.0.1). Preparation does not execute a measurement:

```sh
uv run --locked --script audit/greenframe.py \
  --url https://guide.wagtail.org/en/ \
  --phase initial \
  --output-dir .audit-work/guide-greenframe-initial
```

Use `--run` with a new output directory when the CLI and Docker are available. Later phases require an explicit `--consent-selector` or `--no-banner` declaration:

```sh
uv run --locked --script audit/greenframe.py \
  --url https://guide.wagtail.org/en/ \
  --phase after_scroll --no-banner --samples 3 --run \
  --output-dir .audit-work/guide-greenframe-scroll
```

The Python adapter generates the small JavaScript scenario required by GreenFrame. It sets a 1280 × 800 viewport, uses bounded waits and scrolling, records milestones, disables ad blocking, keeps HTTPS verification, and omits server monitoring. It removes inherited GreenFrame cloud configuration variables. The [configuration reference](https://docs.greenframe.io/configuration/) documents these options and the default three samples.

Each phase is a separate complete scenario. Its total is not the incremental energy attributable to a click or scroll. Use the initial phase as the headline and later phases as investigation evidence. Execute energy work separately from other audits, model campaigns, and tests.

## Reproducibility and current validation

The manifest preserves arguments, scenario/config/wrapper hashes, CLI and Docker preflight output, host context, phase, consent choice, timestamps, return code, and log hash. Successful recognized summaries retain Wh/scenario, gCO2e/scenario, and GreenFrame's reported precision. Unrecognized summaries remain unavailable, rather than zero. The raw log is retained privately.

Preparation and prerequisite detection were executed here: Docker responded, but no GreenFrame executable was installed. No GreenFrame energy measurement has been made or added to the pilot reports. The npm registry also did not provide `greenframe-cli@2.0.1`; use the upstream distribution instructions instead of assuming an npm install works.

Before accepting comparative results, validate the generated scenario with the installed runner, capture its browser version and container image digest, and freeze them with the hardware/load conditions. This adapter pins the CLI interface but does not yet pin or attest the runner image. Repeat measurements, inspect precision, and verify that milestones and page states match the staged browser collector. These are the remaining integration checks, not evidence of energy savings.
