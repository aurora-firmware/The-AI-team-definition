#!/usr/bin/env bash
# Output the next ADR sequential number (NNN) by scanning project/decisions/.
# Run from the project root. Accepts an optional path override as $1.
set -euo pipefail
dir="${1:-project/decisions}"
max=0
if [ -d "$dir" ]; then
  found=$(find "$dir" -maxdepth 1 -name "[0-9][0-9][0-9]-*.md" 2>/dev/null \
    | sed 's|.*/||' | cut -d'-' -f1 | sort -n | tail -1)
  [ -n "$found" ] && max=$found
fi
printf "%03d\n" $(( max + 1 ))
