---
id: "T-021"
title: "Migrate new-bug skill to invoke ai-team CLI"
status: completed
priority: low
assigned-role: developer
created: 2026-05-10
---

# Migrate new-bug skill to invoke ai-team CLI

## Description

Update `.claude/skills/new-bug/SKILL.md` so the procedure invokes `ai-team bug new --json` instead of reading a local template and writing the file directly.

The migrated skill's responsibility narrows to: collect `title`, `description`, `severity`, and optional `task` reference from the caller, call the CLI to create the file, then optionally fill description/details placeholders if provided. Delete the bundled template and any helper scripts under `.claude/skills/new-bug/assets/`.

Verify no remaining references to the deleted files exist anywhere under `.claude/`.

## Acceptance Criteria

AC-1: The system shall update `.claude/skills/new-bug/SKILL.md` so the procedure invokes `ai-team bug new` and references no bundled template or helper script.
AC-2: The system shall delete every file under `.claude/skills/new-bug/assets/` that was bundled to support the previous procedure (template and any helper scripts identified at migration time).
AC-3: WHEN `grep -rn "TEMPLATE-bug.md\|next-bug-id.sh" .claude/` runs THE SYSTEM SHALL produce no matches.

## Dependencies

- `T-011` — `ai-team bug new` must exist

## Files to Touch

- `.claude/skills/new-bug/SKILL.md` — updated procedure
- `.claude/skills/new-bug/assets/` — delete the previous bundled template and any helper scripts

## Verification

```bash
grep -rn "TEMPLATE-bug.md\|next-bug-id.sh" .claude/ || echo OK
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. -->

### Session 1 — 2026-05-10

Implemented T-021 by migrating `.claude/skills/new-bug/SKILL.md` away from bundled template/script mechanics to CLI invocation via `ai-team bug new --json`. I first ran the acceptance grep and confirmed pre-change references still existed in the skill text (`TEMPLATE-bug.md`, `next-bug-id.sh`), which served as the red phase for this migration. I then rewrote the skill's required inputs to the new narrowed contract (`title`, `description`, `severity`, optional `task`, optional `details`) and replaced the procedure with CLI-command construction/execution plus optional post-create placeholder section filling. After that I deleted the legacy files under `.claude/skills/new-bug/assets/`. Re-ran verification: grep returned no matches and asset directory file scan returned empty. Rejected approach: keeping compatibility fallbacks to local template/script, because the task explicitly requires full migration and deletion of those supports. Remaining work is only lifecycle/log handling on `dev-agent` and reviewer pass.

## Review

<!-- Reviewer: append verdict here after each review cycle. -->

### Review Verdict — 2026-05-10
PASS

Result: PASS

Summary:
- Reviewed `task/T-021-migrate-new-bug-skill` against all T-021 acceptance criteria using the two-stage code-review checklist; both stages passed.

Artifacts:
- Canonical task file updated: `project/tasks/in-progress/T-021-migrate-new-bug-skill.md`
- Diff reviewed: `dev-agent..task/T-021-migrate-new-bug-skill`
- Primary files inspected: `.claude/skills/new-bug/SKILL.md`, `.claude/skills/new-bug/assets/TEMPLATE-bug.md` (deleted), `.claude/skills/new-bug/assets/next-bug-id.sh` (deleted)

Evidence:
- Stage 1 (acceptance): `git diff --name-status dev-agent..task/T-021-migrate-new-bug-skill` matched expected tracked diff exactly.
- Stage 1 (AC-1): `.claude/skills/new-bug/SKILL.md` on the task branch now invokes `ai-team bug new --json` and removes template/helper-script procedure steps.
- Stage 1 (AC-2): `git ls-tree -r --name-only task/T-021-migrate-new-bug-skill .claude/skills/new-bug/assets` returned no files.
- Stage 1 (AC-3): `git grep -nE "TEMPLATE-bug.md|next-bug-id.sh" task/T-021-migrate-new-bug-skill -- .claude/ || echo OK` returned `OK`.
- Stage 2 (quality): checked correctness/readability/scope; no regressions, security concerns, or unnecessary behavior introduced for this migration.

Obstacles Encountered:
- none

Next Owner:
- Development Loop

Next Action:
- none
