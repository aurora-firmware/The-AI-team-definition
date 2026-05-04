#!/usr/bin/env bash
# Output the next B-NNN bug ID by scanning project/bugs/.
# Also ensures the bug status folders exist with .gitkeep placeholders.
# Run from the project root. Accepts an optional path override as $1.
set -euo pipefail
dir="${1:-project/bugs}"
for sub in open in-progress resolved; do
  mkdir -p "$dir/$sub"
  [ -e "$dir/$sub/.gitkeep" ] || touch "$dir/$sub/.gitkeep"
done
max=0
found=$(find "$dir" -name "B-[0-9][0-9][0-9]-*.md" 2>/dev/null \
  | sed 's|.*/B-||' | cut -d'-' -f1 | sort -n | tail -1)
[ -n "$found" ] && max=$found
printf "B-%03d\n" $(( max + 1 ))
