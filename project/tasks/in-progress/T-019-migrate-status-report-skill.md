---
id: "T-019"
title: "Migrate status-report skill to invoke ai-team CLI"
status: pending
priority: low
assigned-role: developer
created: 2026-05-10
---

# Migrate status-report skill to invoke ai-team CLI

## Description

Update `.claude/skills/status-report/SKILL.md` so the procedure invokes `ai-team status` (Step 1: inline summary) and `ai-team report` (Step 6: full report file) instead of running the bundled bash script and reading the bundled template.

Specifically: replace the call to `bash .claude/skills/status-report/scripts/status-summary.sh <project-path>` with `ai-team status` (inline summary) and `ai-team report` (full file). Remove any references to the bundled template path. Then delete the obsolete asset files.

Verify no remaining references to the deleted files exist anywhere under `.claude/` after the migration.

## Acceptance Criteria

AC-1: The system shall update `.claude/skills/status-report/SKILL.md` so its procedure references `ai-team status` and `ai-team report` and no longer references `status-summary.sh` or the bundled `progress-report.md` template.
AC-2: The system shall delete `.claude/skills/status-report/scripts/status-summary.sh`.
AC-3: The system shall delete `.claude/skills/status-report/assets/progress-report.md`.
AC-4: WHEN `grep -r "status-summary.sh\|status-report/assets/progress-report.md" .claude/` runs THE SYSTEM SHALL produce no matches.

## Dependencies

- `T-007` — `ai-team status` must exist
- `T-018` — `ai-team report` must exist (and the template is now bundled)

## Files to Touch

- `.claude/skills/status-report/SKILL.md` — updated procedure
- `.claude/skills/status-report/scripts/status-summary.sh` — deleted
- `.claude/skills/status-report/assets/progress-report.md` — deleted

## Verification

```bash
grep -rn "status-summary.sh\|status-report/assets/progress-report.md" .claude/ || echo OK
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. -->

## Review

<!-- Reviewer: append verdict here after each review cycle. -->
