#!/usr/bin/env bash
# Pre-commit hook: verify the CLI sources are ruff-formatted.
#
# Install into a local clone with:
#   bash cli/scripts/install-hooks.sh
#
# The hook fails the commit when `ruff format --check` reports unformatted
# files. Run `uv run ruff format .` from cli/ to fix, then re-stage.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"

cd "${REPO_ROOT}/cli"

if ! uv run ruff format --check .; then
  echo >&2
  echo "pre-commit: ruff format check failed." >&2
  echo "pre-commit: run 'uv run ruff format .' from cli/ and re-stage." >&2
  exit 1
fi
