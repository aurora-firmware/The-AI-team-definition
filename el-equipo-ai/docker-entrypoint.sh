#!/usr/bin/env bash
# Docker entrypoint for El-equipo-AI.
# Sets up OpenCode config and launches a tmux split-pane workspace.

set -e

# ---- OpenCode config (JSON, not TOML) ----
if command -v opencode &>/dev/null; then
    mkdir -p "${HOME}/.config/opencode"

    # Generate OpenCode config if not already present.
    # Manual edits are preserved across container restarts.
    if [ ! -f "${HOME}/.config/opencode/opencode.json" ]; then
        cat > "${HOME}/.config/opencode/opencode.json" <<'OCEOF'
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-20250514"
}
OCEOF
        # NOTE: Edit the model to match your API keys. Examples:
        #   "anthropic/claude-sonnet-4-20250514"
        #   "openai/gpt-4o"
        #   "nvidia/z-ai/glm5"
        # See: https://opencode.ai/docs/config/
    fi

    # Clean up stale TOML config from previous versions
    rm -f "${HOME}/.config/opencode/config.toml"
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
    tmux new-session -d -s main -x "$(tput cols)" -y "$(tput lines)"

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
    tmux split-window -h -p 35
    tmux select-pane -T "Shell — type 'help' for commands"
    tmux send-keys "source /app/shell-profile.sh" Enter

    # Focus the OpenCode pane
    tmux select-pane -t 0

    # Attach to the session (this becomes PID 1)
    exec tmux attach-session -t main
else
    # Non-default CMD: just run it directly
    exec "$@"
fi
