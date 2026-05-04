#!/usr/bin/env bash
# Output the next ADR sequential number (NNN) by scanning project/decisions/.
# Also ensures the decisions folder exists with a .gitkeep placeholder.
# Run from the project root. Accepts an optional path override as $1.
set -euo pipefail
dir="${1:-project/decisions}"
mkdir -p "$dir"
[ -e "$dir/.gitkeep" ] || touch "$dir/.gitkeep"
max=0
found=$(find "$dir" -maxdepth 1 -name "[0-9][0-9][0-9]-*.md" 2>/dev/null \
  | sed 's|.*/||' | cut -d'-' -f1 | sort -n | tail -1)
[ -n "$found" ] && max=$found
printf "%03d\n" $(( max + 1 ))
