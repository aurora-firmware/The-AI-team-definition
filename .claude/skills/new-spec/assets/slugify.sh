#!/usr/bin/env bash
# Convert a title string to a lowercase-hyphenated filename slug.
# Usage: bash slugify.sh "My Feature Title"
set -euo pipefail
echo "$*" \
  | tr '[:upper:]' '[:lower:]' \
  | tr -cs 'a-z0-9' '-' \
  | sed 's/^-//;s/-$//'
