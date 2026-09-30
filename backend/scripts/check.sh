#!/usr/bin/env sh
# Backend quality gate: lint, format, types, tests, dependency audit. Must pass before finishing.
set -eu
cd "$(dirname "$0")/.."
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest -q
uv run pip-audit --progress-spinner off --skip-editable
