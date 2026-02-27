#!/usr/bin/env bash
# Attach to the El-equipo-AI workspace.
# Run this from the el-equipo-ai/ directory (where docker-compose.yaml lives).
#
# First time:  chmod +x call-the-team.sh
# Then:        ./call-the-team.sh

set -e

# Start the container if it's not running
if ! docker compose ps --status running 2>/dev/null | grep -q el-equipo-ai; then
    echo "Starting El-equipo-AI container..."
    docker compose up -d
    sleep 2
fi

# Attach to the tmux workspace
echo "Attaching to workspace... (Ctrl+b d to detach)"
docker compose exec el-equipo-ai tmux attach
