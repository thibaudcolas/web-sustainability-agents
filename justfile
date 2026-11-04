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
