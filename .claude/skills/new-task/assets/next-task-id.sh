#!/usr/bin/env bash
# Output the next T-NNN task ID by scanning project/tasks/.
# Run from the project root. Accepts an optional path override as $1.
set -euo pipefail
dir="${1:-project/tasks}"
max=0
if [ -d "$dir" ]; then
  found=$(find "$dir" -name "T-[0-9][0-9][0-9]-*.md" 2>/dev/null \
    | sed 's|.*/T-||' | cut -d'-' -f1 | sort -n | tail -1)
  [ -n "$found" ] && max=$found
fi
printf "T-%03d\n" $(( max + 1 ))
