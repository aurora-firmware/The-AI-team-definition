# El-equipo-AI — single-container deployment
#
# Includes:
#   - Python 3.11 (El-equipo-AI glue code)
#   - Node.js 20 LTS (Vibe Kanban)
#   - Git (worktree operations)
#   - OpenCode (default host agent — 75+ provider support)
#   - Vibe Kanban (via npm global install)
#   - Superpowers (methodology — integrated via OpenCode hooks)
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
    tmux \
    zsh \
    && rm -rf /var/lib/apt/lists/*

# ---- Node.js 20 (for Vibe Kanban) ----
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# ---- Vibe Kanban (pinned version via npm) ----
# NOTE: replace @latest with a pinned version after first stable release
RUN npm install -g vibe-kanban@latest

# ---- OpenCode (default host agent) ----
# OpenCode is a Go binary supporting 75+ providers (NVIDIA NIM, OpenAI, Anthropic, Ollama, etc.)
# Install via official install script (https://opencode.ai), then move binary to PATH.
# The script puts the binary in ~/.opencode/bin/ or ~/bin/ depending on version.
RUN curl -fsSL https://opencode.ai/install | bash \
    && { cp /root/.opencode/bin/opencode /usr/local/bin/opencode 2>/dev/null \
      || cp /root/bin/opencode /usr/local/bin/opencode 2>/dev/null \
      || find /root -name opencode -type f -executable -exec cp {} /usr/local/bin/opencode \; ; } \
    && chmod +x /usr/local/bin/opencode \
    && opencode version

# ---- El-equipo-AI Python package ----
WORKDIR /app
COPY pyproject.toml requirements.txt ./
COPY el_equipo_ai/ ./el_equipo_ai/
COPY tests/ ./tests/

RUN pip install --no-cache-dir -e ".[dev]"

# ---- Superpowers (methodology) ----
# Superpowers is cloned and integrated with OpenCode via hooks.
# The entrypoint script configures OpenCode hooks to auto-bootstrap Superpowers.
# See: https://github.com/obra/superpowers
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
# Default: launch the tmux split-pane workspace (OpenCode + shell).
# Attach from any device: docker compose exec el-equipo-ai tmux attach
# Detach without stopping: Ctrl+b, then d
# Override: docker compose run --rm el-equipo-ai bash
CMD ["__tmux_workspace"]
