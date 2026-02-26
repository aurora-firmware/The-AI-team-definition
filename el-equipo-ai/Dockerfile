# El-equipo-AI — single-container deployment
#
# Includes:
#   - Python 3.11 (El-equipo-AI glue + agent CLIs)
#   - Node.js 20 LTS (Vibe Kanban)
#   - Git (worktree operations)
#   - Claude Code CLI (primary host agent)
#   - Vibe Kanban (via npm global install)
#
# The container IS the sandbox. Agents operate freely inside it.
# Mount your project repo at /workspace and API keys as env vars.

# ---- Base image ----
FROM python:3.11-slim AS base

# ---- System deps ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ---- Node.js 20 (for Vibe Kanban) ----
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# ---- Vibe Kanban (pinned version via npm) ----
# NOTE: replace @latest with a pinned version after first stable release
RUN npm install -g vibe-kanban@latest

# ---- Claude Code CLI (primary host agent) ----
RUN npm install -g @anthropic-ai/claude-code@latest

# ---- El-equipo-AI Python package ----
WORKDIR /app
COPY pyproject.toml requirements.txt ./
COPY el_equipo_ai/ ./el_equipo_ai/

RUN pip install --no-cache-dir -e ".[dev]"

# ---- Superpowers plugin ----
# Superpowers is installed as a Claude Code plugin / git-cloned skill pack.
# See: https://github.com/obra/superpowers
# The ENTRYPOINT script sets up the plugin path on first run.
# Alternatively mount a pre-cloned superpowers repo at /superpowers.
RUN git clone --depth 1 https://github.com/obra/superpowers /superpowers \
    || echo "WARNING: Could not clone Superpowers (offline build). Mount manually."

# ---- Workspace ----
# Project repos are mounted here at runtime.
RUN mkdir -p /workspace /data

# ---- Config ----
COPY el-equipo-ai.yaml /app/el-equipo-ai.yaml

# ---- Entrypoint ----
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

WORKDIR /workspace
EXPOSE 3000

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["el-equipo-ai", "--help"]
