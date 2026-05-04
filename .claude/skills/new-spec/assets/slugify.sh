#!/usr/bin/env bash
# Convert a title string to a lowercase-hyphenated filename slug.
# Also ensures the specs folder (and its archive subfolder) exist with
# .gitkeep placeholders, since this is the only bash helper run by new-spec.
# Usage: bash slugify.sh "My Feature Title"
set -euo pipefail
specs_dir="${SPECS_DIR:-project/specs}"
for sub in "" archive; do
  target="$specs_dir${sub:+/$sub}"
  mkdir -p "$target"
  [ -e "$target/.gitkeep" ] || touch "$target/.gitkeep"
done
echo "$*" \
  | tr '[:upper:]' '[:lower:]' \
  | tr -cs 'a-z0-9' '-' \
  | sed 's/^-//;s/-$//'
