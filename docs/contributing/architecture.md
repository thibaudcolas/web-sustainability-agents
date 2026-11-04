# Project architecture

How the workspace is organized, and the tooling that supports it.

## Content layers

Organize information by the reader's task, with one maintained home for each subject:

| Location                       | Owns                                                                 | Does not own                                     |
| ------------------------------ | -------------------------------------------------------------------- | ------------------------------------------------ |
| `docs/using/`                  | Installation, invocation and the current audit workflow              | Experiment logs or speculative install commands  |
| `docs/reference/`              | Implemented checks, browser protocols and report/data contracts      | General research or past campaign conclusions    |
| `docs/reports/`                | Entry point to current and historical per-site reports               | Model benchmark rankings                         |
| `docs/knowledge-base/`         | Reusable methodology, evidence interpretation and tool research      | A chronological account of implementation        |
| `docs/feasibility-study/`      | Research questions, design rationale and proposed architecture       | Current setup instructions                       |
| `docs/initial-implementation/` | Implementation scope, roadmap, detailed backlog and evidence history | The default home for every new page              |
| `docs/evaluation/`             | Benchmark design, model protocol, case inventory and campaign index  | Live-site judgments presented as reference truth |
| `docs/contributing/`           | Development, documentation and skill maintenance                     | End-user audit installation                      |

Section `README.md` files serve both MkDocs and GitHub. Existing reports, campaign pages and immutable bundles retain their published paths under `initial-implementation/`; navigation and indexes give them their appropriate reader-facing home. Do not move or reformat hashed evidence for cosmetic consistency.

Update the canonical guide or reference when behavior changes. Add a campaign page only for a distinct reproducible experiment, and link it from the evaluation or report index. Keep completed experiment observations intact, label them historical, and reduce their search prominence when superseded. The roadmap owns sequence; the backlog owns detailed follow-ups. Avoid another rolling checkpoint page that repeats both.

## Documentation build

The site is built with [MkDocs](https://www.mkdocs.org/) and the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme, configured in `mkdocs.yml`. Beyond rendering Markdown to HTML, the build applies a few transforms contributors should be aware of:

- **Last-modified dates** – each page footer shows the last commit date from git, taken via `mkdocs-git-revision-date-localized-plugin`.
- **Folder metadata** – Material's `meta` plugin applies `.meta.yml` values to pages in that folder and its subfolders. The knowledge base defines a shared tag. Page-specific tags are merged with folder tags.
- **Tag index** – the `tags` plugin collects page and folder tags into `tags.json` and renders the listing marker in the [Tags page](../tags.md). See the [style guide](style-guide.md#tags) for authoring syntax.
- **`llms-full.txt`** – the `mkdocs-llmstxt` plugin concatenates select pages into `llms-full.txt` at the site root, so LLMs and agents can ingest the workspace in one file. The plugin's `sections` key in `mkdocs.yml` mirrors `nav`; keep both in sync when adding or removing sections.
- **Abbreviation tooltips** – `contributing/abbreviations.md` is auto-appended to every page by `pymdownx.snippets`, so any abbreviation registered there is available as a hover tooltip across the site.
- **Strict validation** – `mkdocs build --strict` (`just build-docs`) fails on pages missing from `nav`, broken anchors, unrecognized links, root-relative links, and missing snippets. Use file patterns in the top-level `not_in_nav` setting in `mkdocs.yml` for published pages intentionally omitted from navigation. Snippet sources are excluded from page generation with `exclude_docs`.

The Markdown-facing syntax for these features is documented in the [style guide](style-guide.md); `mkdocs.yml` carries inline comments explaining each option.

## Agent skill publishing

The native MkDocs hook in `scripts/publish_skills.py` copies `.agents/skills/` to `site/.well-known/agent-skills/` and generates the discovery index and AI catalog after each build. Skill metadata provides descriptions and versions; MkDocs configuration provides publisher details. The Pages upload includes hidden files so the catalogs reach the deployed site. See [skill maintenance](skills.md) for publishing and [the audit guide](../using/README.md) for installation.

## Continuous integration

[`.github/workflows/ci.yml`](https://github.com/thibaudcolas/web-sustainability-agents/blob/main/.github/workflows/ci.yml) runs on every push to `main` and on pull requests:

- Python linting and formatting checks (`ruff`), type checking (`mypy`, `ty`).
- Non-Python formatting checks (`prettier`).
- Prose checks (Vale, configured in `.vale.ini` with repository-owned rules).
- Local link checking ([lychee](https://lychee.cli.rs), configured in `lychee.toml`).
- Rendering fixtures and agent skill publishing tests.
- A strict documentation build, then upload and deployment of the built `site/` to GitHub Pages.

Python dependencies are installed from the committed lockfile with `uv sync --locked --dev`. The separate workflow in `.github/workflows/external-links.yml` checks HTTP(S) sources on pull requests, pushes to `main`, a weekly schedule, and manual dispatch. Its failures are reported separately and do not block site deployment.
