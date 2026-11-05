# Optional GreenFrame client measurements

GreenFrame is useful for repeated user journeys that include rendering, waiting, consent choices, and scrolling. Its CLI collects browser resource activity and converts it into modeled energy and carbon quantities. Server containers are optional, so public websites can be investigated without deploying or instrumenting their backends. See the [CLI documentation](https://docs.greenframe.io/commands/).

Keep three separate quantities in reports: transferred-data SWDM/Digital Carbon Ratings estimates, co2-runner CPU-package observations, and GreenFrame's modeled scenario energy. Their boundaries overlap and their assumptions differ; adding them would double count. A GreenFrame result is not direct electricity-meter evidence.

## Bakerydemo example

The [bakerydemo-gold-benchmark source snapshot](https://github.com/thibaudcolas/bakerydemo-gold-benchmark/tree/973b3f7e441ceac867a803924da29cbd2bf42d54) contains homepage, search, filtering, contact, and admin journeys. Its homepage scenario follows a visitor into a bread index and detail page. That is a useful pattern for task-level auditing, rather than measuring only a landing page.

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

The [current example reports](../reports/README.md) include three-page, three-repetition GreenFrame 2.0.1 experiments per site. Their reproduction manifests pin the container digest, Chromium version, scenarios and raw samples. Results are resource-model estimates; they do not measure whole-device electricity or establish savings.

Before comparing results, retain matching browser versions, container images, hardware/load conditions and scenario milestones. Repeat measurements sequentially and inspect precision. An annual client-only projection additionally requires explicit traffic, page weights and electricity assumptions; see [energy and traffic scenarios](energy-and-traffic.md). It must stay separate from SWDM and cannot be presented as metered annual site consumption.
