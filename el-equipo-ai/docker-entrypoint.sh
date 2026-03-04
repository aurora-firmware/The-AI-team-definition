#!/usr/bin/env bash
# Docker entrypoint for El-equipo-AI.
# Sets up OpenCode config and launches a tmux split-pane workspace.

set -e

# ---- OpenCode config (JSON, not TOML) ----
if command -v opencode &>/dev/null; then
    mkdir -p "${HOME}/.config/opencode"
    rm -f "${HOME}/.config/opencode/config.toml"

    # If the user explicitly set OPENCODE_MODEL, use it directly.
    # Otherwise, auto-detect the first available provider from env vars.
    if [ -n "${OPENCODE_MODEL}" ]; then
        _OC_MODEL="${OPENCODE_MODEL}"
    elif [ -n "${ANTHROPIC_API_KEY}" ]; then
        _OC_MODEL="anthropic/claude-sonnet-4-20250514"
    elif [ -n "${OPENAI_API_KEY}" ]; then
        _OC_MODEL="openai/gpt-4o"
    elif [ -n "${NVIDIA_API_KEY}" ]; then
        _OC_MODEL="nvidia/meta/llama-3.3-70b-instruct"
    else
        _OC_MODEL=""
    fi

    # Build the config. For NVIDIA NIM we need a custom provider block
    # because it is not a built-in OpenCode provider.
    _OC_NVIDIA_BLOCK=""
    if [ -n "${NVIDIA_API_KEY}" ]; then
        _OC_NVIDIA_BLOCK=$(cat <<'NVEOF'
,
    "nvidia": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "NVIDIA NIM",
      "options": {
        "baseURL": "https://integrate.api.nvidia.com/v1",
        "apiKey": "{env:NVIDIA_API_KEY}"
      },
      "models": {
        "meta/llama-3.3-70b-instruct": { "name": "Llama 3.3 70B" },
        "deepseek-ai/deepseek-r1": { "name": "DeepSeek R1" }
      }
    }
NVEOF
)
    fi

    if [ -n "${_OC_MODEL}" ]; then
        cat > "${HOME}/.config/opencode/opencode.json" <<OCEOF
{
  "\$schema": "https://opencode.ai/config.json",
  "model": "${_OC_MODEL}",
  "provider": {
    "_placeholder": null${_OC_NVIDIA_BLOCK}
  }
}
OCEOF
        # Remove the placeholder key (keeps JSON valid during generation)
        sed -i '/"_placeholder": null,\?/d' "${HOME}/.config/opencode/opencode.json"
    else
        # No API keys found — generate minimal config; OpenCode will prompt.
        cat > "${HOME}/.config/opencode/opencode.json" <<OCEOF
{
  "\$schema": "https://opencode.ai/config.json"
}
OCEOF
        echo "[el-equipo-ai] WARNING: No API keys detected (ANTHROPIC_API_KEY, OPENAI_API_KEY, NVIDIA_API_KEY)."
        echo "               OpenCode will start but may not be able to connect to a model."
        echo "               Set at least one key in your .env file and restart."
    fi
fi

# ---- Superpowers ----
if [ -d "/superpowers" ]; then
    export SUPERPOWERS_DIR="/superpowers"
fi

# ---- tmux workspace setup ----
# If CMD is the default (starts tmux workspace), set up split panes.
# Otherwise, run whatever command was passed (e.g. docker compose run --rm ... bash).
if [ "$1" = "__tmux_workspace" ]; then
    # Configure tmux status bar with navigation hints
    # tput may fail without a TTY (e.g. docker compose up -d), so fallback to sane defaults.
    _COLS=$(tput cols 2>/dev/null || echo 200)
    _ROWS=$(tput lines 2>/dev/null || echo 50)
    tmux new-session -d -s main -x "${_COLS}" -y "${_ROWS}"

    # Status bar: always-visible navigation help
    tmux set-option -g status on
    tmux set-option -g status-style "bg=colour235,fg=colour248"
    tmux set-option -g status-left "#[fg=colour82,bold] EL-EQUIPO-AI #[fg=colour248]│ "
    tmux set-option -g status-left-length 20
    tmux set-option -g status-right "#[fg=colour214] Ctrl+b ← → #[fg=colour248]switch panes #[fg=colour248]│#[fg=colour214] Ctrl+b d #[fg=colour248]detach "
    tmux set-option -g status-right-length 60

    # Pane border labels
    tmux set-option -g pane-border-status top
    tmux set-option -g pane-border-format " #{?pane_active,#[fg=colour82],#[fg=colour240]}#{pane_title} "

    # Left pane: OpenCode (agent conversation)
    tmux select-pane -T "OpenCode Agent"
    tmux send-keys "opencode" Enter

    # Right pane: zsh shell with aliases and welcome banner
    # shell-profile.sh is auto-sourced via /root/.zshrc (see Dockerfile)
    tmux split-window -h -p 35
    tmux select-pane -T "Shell — type 'help' for commands"

    # Focus the OpenCode pane
    tmux select-pane -t 0

    # Attach to the session (this becomes PID 1)
    exec tmux attach-session -t main
else
    # Non-default CMD: just run it directly
    exec "$@"
fi
