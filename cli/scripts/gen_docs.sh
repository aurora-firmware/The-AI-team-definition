#!/usr/bin/env bash
# Generate cli/docs/commands.md from the ai_team Typer app.
#
# Run from the repository root:
#   bash cli/scripts/gen_docs.sh
#
# This script is a thin wrapper around `typer ... utils docs`. It prepends a
# header note to the generated output so the file is self-documenting.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUTPUT="${REPO_ROOT}/cli/docs/commands.md"

mkdir -p "$(dirname "${OUTPUT}")"

# Write the header note first.
cat > "${OUTPUT}" <<'HEADER'
<!-- GENERATED FILE — do not edit by hand.
     Regenerate with: bash cli/scripts/gen_docs.sh -->

HEADER

# Append the Typer-generated docs.
cd "${REPO_ROOT}/cli"
uv run typer ai_team.cli utils docs --name "ai-team" >> "${OUTPUT}"
