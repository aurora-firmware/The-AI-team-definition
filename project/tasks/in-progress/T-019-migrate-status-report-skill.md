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

### Review Verdict — 2026-05-10

PASS

Result: PASS

Summary:
- Reviewed `task/T-019-migrate-status-report-skill` using the two-stage `code-review` checklist; all acceptance criteria and quality checks passed.

Artifacts:
- Updated canonical task file: `project/tasks/in-progress/T-019-migrate-status-report-skill.md`.
- Diff reviewed: `M .claude/skills/status-report/SKILL.md`, `D .claude/skills/status-report/scripts/status-summary.sh`, `D .claude/skills/status-report/assets/progress-report.md`.
- Primary file inspected: `.claude/skills/status-report/SKILL.md` (on `task/T-019-migrate-status-report-skill`).

Evidence:
- Stage 1 (acceptance): verified `SKILL.md` now uses `ai-team status` (Step 1/5) and `ai-team report` (Step 6), with no references to `status-summary.sh` or `status-report/assets/progress-report.md`.
- Stage 1 (scope): `git diff --name-status dev-agent..task/T-019-migrate-status-report-skill` matched expected 3-file diff exactly.
- Stage 1 (deletions): `git ls-tree -r --name-only task/T-019-migrate-status-report-skill .claude/skills/status-report` returned only `.claude/skills/status-report/SKILL.md`.
- Stage 1 (grep verification): `git grep -nE "status-summary.sh|status-report/assets/progress-report.md" task/T-019-migrate-status-report-skill:.claude` returned no matches.
- Stage 2 (quality): correctness, readability, security, and performance checks passed for this documentation-only migration; no test changes required by task scope.

Obstacles Encountered:
- none

Next Owner:
- Development Loop

Next Action:
- Continue lifecycle flow for `T-019` after reviewer PASS (integration-ready).
