#!/usr/bin/env bash
# Docker entrypoint for El-equipo-AI.
# Sets up Superpowers plugin path and configures Claude Code if ANTHROPIC_API_KEY is set.

set -e

# Register Superpowers as a Claude Code plugin if installed
if [ -d "/superpowers" ]; then
    export CLAUDE_CODE_PLUGINS_DIR="/superpowers"
fi

# Hand off to the provided command
exec "$@"
