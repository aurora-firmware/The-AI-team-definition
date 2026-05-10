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

### Session 1 — 2026-05-10

Read the task file and existing Work Log section first (no prior session entries present), then ran the task verification grep as a red check and confirmed existing references to `status-summary.sh` and the bundled `progress-report.md` path. Updated the `status-report` skill procedure to use `ai-team status` for inline summary generation and `ai-team report` for full report generation, and removed template/script references from input requirements and procedural text. Deleted the obsolete files `.claude/skills/status-report/scripts/status-summary.sh` and `.claude/skills/status-report/assets/progress-report.md`. Re-ran the verification grep and got `OK` with no matches under `.claude/`. Considered keeping wording that depended on a bundled template path for Step 6, but rejected it because the task explicitly requires removing bundled-template references after migration. No remaining implementation work identified for this task branch.

## Review

<!-- Reviewer: append verdict here after each review cycle. -->
