---
id: "T-020"
title: "Migrate new-task skill to invoke ai-team CLI"
status: pending
priority: low
assigned-role: developer
created: 2026-05-10
---

# Migrate new-task skill to invoke ai-team CLI

## Description

Update `.claude/skills/new-task/SKILL.md` so the procedure invokes `ai-team task new --json` instead of reading a local template, allocating an ID via the bundled bash script, and writing the file directly.

The migrated skill's responsibility narrows to: collect `title`, `description`, `priority`, and optional `assigned-role` from the caller, call the CLI to create the file, then optionally fill in description/AC placeholders if those were provided. The CLI returns `{"id": "T-NNN", "path": "..."}` which the skill uses for the confirmation message.

Delete `.claude/skills/new-task/assets/TEMPLATE-task.md` and `.claude/skills/new-task/assets/next-task-id.sh`. Verify no remaining references to the deleted files exist anywhere under `.claude/`.

## Acceptance Criteria

AC-1: The system shall update `.claude/skills/new-task/SKILL.md` so the procedure invokes `ai-team task new` and references no bundled template or ID-allocator script.
AC-2: The system shall delete `.claude/skills/new-task/assets/TEMPLATE-task.md`.
AC-3: The system shall delete `.claude/skills/new-task/assets/next-task-id.sh`.
AC-4: WHEN `grep -rn "TEMPLATE-task.md\|next-task-id.sh" .claude/` runs THE SYSTEM SHALL produce no matches.

## Dependencies

- `T-010` — `ai-team task new` must exist

## Files to Touch

- `.claude/skills/new-task/SKILL.md` — updated procedure
- `.claude/skills/new-task/assets/TEMPLATE-task.md` — deleted
- `.claude/skills/new-task/assets/next-task-id.sh` — deleted

## Verification

```bash
grep -rn "TEMPLATE-task.md\|next-task-id.sh" .claude/ || echo OK
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. -->

## Review

<!-- Reviewer: append verdict here after each review cycle. -->
