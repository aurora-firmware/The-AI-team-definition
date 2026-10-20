#!/usr/bin/env bash
# Generate cli/docs/commands.md from the ai_team Typer app.
#
# Run from the repository root:
#   bash cli/scripts/gen_docs.sh
#
# This script is a thin wrapper around `typer ... utils docs`. It prepends a
# header note to the generated output so the file is self-documenting.
#
# Optional: --output <path> writes somewhere other than the tracked file, so
# tests can generate docs without modifying the working tree. A relative path
# is resolved against the caller's working directory.
set -euo pipefail

usage() {
  echo "usage: bash cli/scripts/gen_docs.sh [--output <path>]" >&2
}

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUTPUT="${REPO_ROOT}/cli/docs/commands.md"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --output)
      if [ "$#" -lt 2 ]; then
        echo "error: --output requires a path" >&2
        usage
        exit 2
      fi
      case "$2" in
        /*) OUTPUT="$2" ;;
        *) OUTPUT="$(pwd)/$2" ;;
      esac
      shift 2
      ;;
    *)
      echo "error: unknown argument: $1" >&2
      usage
      exit 2
      ;;
  esac
done

mkdir -p "$(dirname "${OUTPUT}")"

# Write the header note first.
cat > "${OUTPUT}" <<'HEADER'
<!-- GENERATED FILE — do not edit by hand.
     Regenerate with: bash cli/scripts/gen_docs.sh -->

HEADER

# Append the Typer-generated docs.
cd "${REPO_ROOT}/cli"
uv run python -m typer ai_team.cli utils docs --name "ai-team" >> "${OUTPUT}"
