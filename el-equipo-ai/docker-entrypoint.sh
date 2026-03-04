#!/usr/bin/env bash
# Docker entrypoint for El-equipo-AI.
# Sets up OpenCode config and launches a tmux split-pane workspace.

set -e

# ---- OpenCode config (JSON, not TOML) ----
if command -v opencode &>/dev/null; then
    mkdir -p "${HOME}/.config/opencode"

    # Always regenerate config to avoid stale keys from previous versions.
    # To customise, set OPENCODE_MODEL env var or mount a volume at
    # ~/.config/opencode/opencode.json.
    rm -f "${HOME}/.config/opencode/config.toml"
    cat > "${HOME}/.config/opencode/opencode.json" <<OCEOF
{
  "\$schema": "https://opencode.ai/config.json",
  "model": "${OPENCODE_MODEL:-anthropic/claude-sonnet-4-20250514}"
}
OCEOF
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
