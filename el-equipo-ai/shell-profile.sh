#!/usr/bin/env bash
# El-equipo-AI shell profile — sourced by zsh in the right tmux pane.
# Provides short aliases for common commands so users don't need to
# remember long flags or paths.

# ---- Aliases ----

alias status='el-equipo-ai status'
alias integrate='el-equipo-ai integrate'
alias tests='pytest /app/tests/ -v'
alias logs='tail -f /data/el-equipo-ai.log 2>/dev/null || echo "No log file yet."'
alias config='cat /app/el-equipo-ai.yaml'
alias oc-config='cat ${HOME}/.config/opencode/opencode.json 2>/dev/null || echo "No OpenCode config found."'
alias oc-version='opencode version'
alias oc-restart='tmux send-keys -t main:0.0 "opencode" Enter && echo "Restarted OpenCode in left pane."'

# help alias — prints the list of all aliases
alias help='_el_equipo_help'
_el_equipo_help() {
    echo ""
    echo "  El-equipo-AI — available commands"
    echo "  ─────────────────────────────────────────────"
    echo "  status       Provider availability & quota state"
    echo "  integrate    Run the integration test phase"
    echo "  tests        Run the full test suite (pytest)"
    echo "  logs         Tail the JSONL event log"
    echo "  config       Show el-equipo-ai.yaml config"
    echo "  oc-config    Show OpenCode config (opencode.json)"
    echo "  oc-version   OpenCode version"
    echo "  oc-restart   Restart OpenCode in the left pane"
    echo "  help         Show this list"
    echo "  ─────────────────────────────────────────────"
    echo "  Any other command works normally (git, python, etc.)"
    echo ""
}

# ---- Welcome banner (shown once on shell start) ----
echo ""
echo "  ┌─────────────────────────────────────────────┐"
echo "  │         El-equipo-AI — Shell                 │"
echo "  │                                              │"
echo "  │  Type 'help' to see available commands.      │"
echo "  │  Type 'status' to check provider state.      │"
echo "  │                                              │"
echo "  │  This is a regular shell — any command works.│"
echo "  └─────────────────────────────────────────────┘"
echo ""
