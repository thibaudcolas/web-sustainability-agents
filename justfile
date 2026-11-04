# Task runner: https://github.com/casey/just
# Requires: `uv`, `npm`, and `just`.

# List all the justfile recipes.
help:
    just --list --list-prefix 'just '

# Install dependencies and initialize for development.
init:
    uv venv
    uv sync --dev
    npm ci
    npx playwright install chromium
    uv run vale --version
    prek

# Lint the project.
lint:
    uv run ruff check
    uv run ruff format --check
    if git ls-files '*.py' | grep -q .; then uv run mypy .; fi
    uv run ty check
    npm run lint
    just lint-prose

# Check the small, project-owned prose style (Vale is installed by uv).
lint-prose:
    uv run vale README.md CONTRIBUTING.md AGENTS.md docs .agents/skills

# Format project files.
format *paths=".":
    uv run ruff check --fix {{ paths }}
    uv run ruff format {{ paths }}
    npm run format -- {{ paths }}

# Check local links without network access (requires lychee).
check-links:
    lychee --offline --no-progress --hidden .

# Check external sources separately so availability does not block the docs build.
check-external-links:
    lychee --scheme http --scheme https --no-progress --hidden .

# Build the documentation.
build-docs:
    NO_MKDOCS_2_WARNING=1 uv run mkdocs build --strict

# Test skill publishing and documentation rendering in temporary builds.
test:
    uv run python -m unittest discover -s tests
    node --test tests/*.test.js

# Download the browser used by the deterministic audit tests.
audit-install:
    npx playwright install chromium
    uv run python -m playwright install chromium

# Measure initial, cookie-choice, and scroll states, then discover disclosures and technologies.
audit-sites:
    uv run --locked --script audit/run.py --publish docs/initial-implementation/assets/staged-audit.json

# Export per-site reports and long-form metrics from existing evidence.
audit-reports:
    uv run --locked --script audit/report.py

# Prepare harness-independent evidence review packets for the audit skills.
audit-review-packets:
    uv run --locked --script audit/reviews.py --prepare .audit-work/review-packets

# Recalculate scores and annual scenarios from published evidence and reviews.
audit-assess:
    uv run --locked --script audit/assess.py
    uv run --locked --script audit/annual.py
    npx prettier --write docs/initial-implementation/assets/scored-audits.json docs/initial-implementation/assets/annual-footprints.json
    uv run --locked --script audit/report.py
    npx prettier --write docs/initial-implementation/assets/reports/*.json

# Collect metadata, preference, and recovery evidence; publish per-site registers.
audit-scope:
    uv run --locked --script audit/scope.py --publish docs/initial-implementation/assets/scope-extension.json
    npx prettier --write docs/initial-implementation/assets/scope-extension.json
    uv run --locked --script audit/coverage.py

# Measure CPU-package energy with local/co2-runner; keep other workloads idle.
audit-energy:
    uv run --locked --script audit/energy.py

# Retrieve the latest available public CrUX mirror and publish traffic scenarios.
audit-traffic:
    uv run --locked --script audit/traffic.py

# Build the expanded evidence-review tasks; never run during an active campaign.
benchmark-expanded-build:
    uv run --locked --script benchmarks/build_expanded.py

# Freeze the ten new methodology/skill cases in a new directory.
benchmark-methodology-build:
    uv run --locked --script benchmarks/build_expanded.py --methodology

# Build six development tasks from measured controlled fixtures.
benchmark-build:
    node benchmarks/build.js

# Validate grader behavior without model inference.
benchmark-controls:
    harbor run -p .audit-work/tasks -a oracle -n 2 --jobs-dir "$PWD/.audit-work/jobs"
    harbor run -p .audit-work/tasks -a nop -n 2 --jobs-dir "$PWD/.audit-work/jobs"

# Bounded model campaigns; native authentication is supplied outside the repo.
benchmark-neuralwatt:
    harbor run -c benchmarks/neuralwatt.json -p .audit-work/tasks --jobs-dir "$PWD/.audit-work/jobs"

benchmark-codex:
    CODEX_AUTH_JSON_PATH="${CODEX_AUTH_JSON_PATH:-${CODEX_HOME:-$HOME/.codex}/auth.json}" harbor run -c benchmarks/codex.json -p .audit-work/tasks --jobs-dir "$PWD/.audit-work/jobs"

# Build the documentation and serve it locally.
docs:
    NO_MKDOCS_2_WARNING=1 uv run mkdocs serve --strict

# Freeze broader interpretation and collection-handoff tasks.
benchmark-breadth-build:
    uv run --locked --script benchmarks/build_expanded.py --breadth
