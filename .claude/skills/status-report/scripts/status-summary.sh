#!/usr/bin/env bash
set -euo pipefail

usage() {
  printf 'Usage: %s <project-path>\n' "${0##*/}" >&2
}

if [[ $# -ne 1 ]]; then
  usage
  exit 2
fi

root="${1%/}"
if [[ ! -d "$root" ]]; then
  printf 'Project path not found: %s\n' "$root" >&2
  exit 1
fi

state_dir="$root/project"
if [[ ! -d "$state_dir" ]]; then
  printf 'Project state directory not found: %s\n' "$state_dir" >&2
  exit 1
fi

today="$(date +%Y-%m-%d)"

count_md() {
  local dir="$1"
  if [[ ! -d "$dir" ]]; then
    printf '0'
    return
  fi
  find "$dir" -maxdepth 1 -type f -name '*.md' \
    ! -name 'TEMPLATE-*' ! -name '.gitkeep' | wc -l | tr -d ' '
}

frontmatter_value() {
  local file="$1"
  local key="$2"
  awk -v key="$key" '
    BEGIN { in_fm = 0 }
    NR == 1 && $0 == "---" { in_fm = 1; next }
    in_fm && $0 == "---" { exit }
    in_fm {
      split($0, parts, ":")
      if (parts[1] == key) {
        sub("^[^:]*:[[:space:]]*", "", $0)
        sub("[[:space:]]+#.*$", "", $0)
        gsub(/^"|"$/, "", $0)
        print $0
        exit
      }
    }
  ' "$file"
}

first_heading_title() {
  local file="$1"
  awk '/^# / { sub(/^# /, "", $0); print; exit }' "$file"
}

title_for() {
  local file="$1"
  local title
  title="$(frontmatter_value "$file" "title")"
  if [[ -z "$title" ]]; then
    title="$(first_heading_title "$file")"
  fi
  if [[ -z "$title" ]]; then
    title="$(basename "$file" .md)"
  fi
  printf '%s' "$title"
}

status_for() {
  local file="$1"
  local status
  status="$(frontmatter_value "$file" "status")"
  if [[ -z "$status" ]]; then
    status="unknown"
  fi
  printf '%s' "$status"
}

id_for() {
  local file="$1"
  local id
  id="$(frontmatter_value "$file" "id")"
  if [[ -z "$id" ]]; then
    id="$(basename "$file" .md | sed -E 's/^([A-Z]-[0-9]+).*/\1/')"
  fi
  printf '%s' "$id"
}

assigned_role_for() {
  local file="$1"
  local role
  role="$(frontmatter_value "$file" "assigned-role")"
  if [[ -z "$role" ]]; then
    role="$(frontmatter_value "$file" "assigned_role")"
  fi
  if [[ -z "$role" ]]; then
    role="unassigned"
  fi
  printf '%s' "$role"
}

severity_for() {
  local file="$1"
  local severity
  severity="$(frontmatter_value "$file" "severity")"
  if [[ -z "$severity" ]]; then
    severity="unknown"
  fi
  printf '%s' "$severity"
}

blocking_reason_for() {
  local file="$1"
  local reason
  reason="$(awk '
    /^## Work Log/ { in_log = 1; next }
    in_log && /^## / { exit }
    in_log && NF { print; exit }
  ' "$file")"
  if [[ -z "$reason" ]]; then
    reason="not recorded"
  fi
  printf '%s' "$reason"
}

latest_integration_result() {
  local result=""

  if [[ -d "$state_dir/tasks/completed" ]]; then
    result="$(grep -RihE 'integration|test|verification' "$state_dir/tasks/completed" 2>/dev/null | tail -n 1 || true)"
  fi

  if [[ -z "$result" && -d "$state_dir/bugs/resolved" ]]; then
    result="$(grep -RihE 'integration|test|verification' "$state_dir/bugs/resolved" 2>/dev/null | tail -n 1 || true)"
  fi

  if [[ -z "$result" && -d "$root/.git" ]]; then
    result="$(git -C "$root" log --all --grep='merge\|integration\|test' -n 1 --pretty=format:'%h %s' 2>/dev/null || true)"
  fi

  if [[ -z "$result" ]]; then
    result="not found"
  fi

  printf '%s' "$result"
}

has_markdown_files() {
  local dir="$1"
  [[ -d "$dir" ]] && find "$dir" -maxdepth 1 -type f -name '*.md' ! -name 'TEMPLATE-*' ! -name '.gitkeep' | grep -q .
}

list_specs() {
  local dir="$state_dir/specs"
  if ! has_markdown_files "$dir"; then
    printf '%s\n' '- none'
    return
  fi
  while IFS= read -r file; do
    printf '%s\n' "- $(title_for "$file") — $(status_for "$file")"
  done < <(find "$dir" -maxdepth 1 -type f -name '*.md' ! -name 'TEMPLATE-*' ! -name '.gitkeep' | sort)
}

list_in_progress_tasks() {
  local dir="$state_dir/tasks/in-progress"
  if ! has_markdown_files "$dir"; then
    printf '%s\n' '- none'
    return
  fi
  while IFS= read -r file; do
    printf '%s\n' "- $(id_for "$file") — $(title_for "$file") ($(assigned_role_for "$file"))"
  done < <(find "$dir" -maxdepth 1 -type f -name '*.md' ! -name 'TEMPLATE-*' ! -name '.gitkeep' | sort)
}

list_blocked_tasks() {
  local dir="$state_dir/tasks/blocked"
  if ! has_markdown_files "$dir"; then
    printf '%s\n' '- none'
    return
  fi
  while IFS= read -r file; do
    printf '%s\n' "- $(id_for "$file") — $(title_for "$file"): $(blocking_reason_for "$file")"
  done < <(find "$dir" -maxdepth 1 -type f -name '*.md' ! -name 'TEMPLATE-*' ! -name '.gitkeep' | sort)
}

list_critical_high_bugs() {
  local dir="$state_dir/bugs/open"
  local found=0
  if [[ -d "$dir" ]]; then
    while IFS= read -r file; do
      local severity
      severity="$(severity_for "$file")"
      case "$severity" in
        critical|high)
          printf '%s\n' "- $(id_for "$file") — $(title_for "$file") ($severity)"
          found=1
          ;;
      esac
    done < <(find "$dir" -maxdepth 1 -type f -name '*.md' ! -name 'TEMPLATE-*' ! -name '.gitkeep' | sort)
  fi
  if [[ "$found" -eq 0 ]]; then
    printf '%s\n' '- none'
  fi
}

specs_count="$(count_md "$state_dir/specs")"
pending_count="$(count_md "$state_dir/tasks/pending")"
in_progress_count="$(count_md "$state_dir/tasks/in-progress")"
completed_count="$(count_md "$state_dir/tasks/completed")"
blocked_count="$(count_md "$state_dir/tasks/blocked")"
open_bugs_count="$(count_md "$state_dir/bugs/open")"
bugs_in_progress_count="$(count_md "$state_dir/bugs/in-progress")"
adrs_count="$(count_md "$state_dir/decisions")"

critical_high_count=0
if [[ -d "$state_dir/bugs/open" ]]; then
  while IFS= read -r file; do
    case "$(severity_for "$file")" in
      critical|high) critical_high_count=$((critical_high_count + 1)) ;;
    esac
  done < <(find "$state_dir/bugs/open" -maxdepth 1 -type f -name '*.md' ! -name 'TEMPLATE-*' ! -name '.gitkeep' | sort)
fi

cat <<REPORT
## Status Report — $today

### Summary
- Active specs: $specs_count
- Pending tasks: $pending_count
- In progress: $in_progress_count
- Completed: $completed_count
- Blocked: $blocked_count
- Open bugs: $open_bugs_count ($critical_high_count critical/high)
- Bugs in progress: $bugs_in_progress_count
- ADRs: $adrs_count
- Latest integration result: $(latest_integration_result)

### Specifications
$(list_specs)

### In Progress
$(list_in_progress_tasks)

### Blocked
$(list_blocked_tasks)

### Critical/High Bugs
$(list_critical_high_bugs)
REPORT

if [[ "$blocked_count" -gt 0 || "$critical_high_count" -gt 0 ]]; then
  cat <<REPORT

### Recommended Actions
- Resolve blocked tasks before Gate 5 sign-off.
- Prioritize critical and high severity open bugs before final merge.
REPORT
fi
