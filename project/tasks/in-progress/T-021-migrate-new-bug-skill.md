---
id: "T-021"
title: "Migrate new-bug skill to invoke ai-team CLI"
status: pending
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
