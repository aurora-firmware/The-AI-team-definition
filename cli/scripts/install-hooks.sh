#!/usr/bin/env bash
# Install the repository git hooks into the local clone's .git/hooks.
#
# Run from anywhere inside the repo:
#   bash cli/scripts/install-hooks.sh
#
# Symlinks .git/hooks/pre-commit to cli/scripts/pre-commit.sh so the installed
# hook stays in sync with the versioned script.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOKS_DIR="$(git rev-parse --git-path hooks)"
SOURCE="${REPO_ROOT}/cli/scripts/pre-commit.sh"

mkdir -p "${HOOKS_DIR}"
ln -sf "${SOURCE}" "${HOOKS_DIR}/pre-commit"
chmod +x "${SOURCE}"

echo "Installed pre-commit hook -> ${SOURCE}"
