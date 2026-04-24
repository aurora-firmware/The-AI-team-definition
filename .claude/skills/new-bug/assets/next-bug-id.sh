#!/usr/bin/env bash
# Output the next B-NNN bug ID by scanning project/bugs/.
# Run from the project root. Accepts an optional path override as $1.
set -euo pipefail
dir="${1:-project/bugs}"
max=0
if [ -d "$dir" ]; then
  found=$(find "$dir" -name "B-[0-9][0-9][0-9]-*.md" 2>/dev/null \
    | sed 's|.*/B-||' | cut -d'-' -f1 | sort -n | tail -1)
  [ -n "$found" ] && max=$found
fi
printf "B-%03d\n" $(( max + 1 ))
