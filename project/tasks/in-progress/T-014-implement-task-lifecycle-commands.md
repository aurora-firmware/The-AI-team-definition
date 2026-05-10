---
id: "T-014"
title: "Implement task lifecycle commands (start, complete, block, unblock)"
status: pending
priority: high
assigned-role: developer
created: 2026-05-10
---

# Implement task lifecycle commands (start, complete, block, unblock)

## Description

Add four lifecycle subcommands to the `ai_team.commands.task` module created in T-010. Each takes a task ID (e.g., `T-042`) and moves the file between state folders while updating the frontmatter `status` field via `ai_team.core.fs.update_status` and `move_artifact`.

State transitions:
- `start <T-NNN>` — `pending/` → `in-progress/`, status=`in-progress`
- `complete <T-NNN>` — `in-progress/` → `completed/`, status=`completed`
- `block <T-NNN> --reason "<text>"` — any state → `blocked/`, status=`blocked`; the `--reason` text is appended to the task's Work Log under a new session entry dated today
- `unblock <T-NNN>` — `blocked/` → `in-progress/`, status=`in-progress`

All operations are idempotent: if the task is already in the destination state, the command prints a clear "already in <state>" message and exits zero without mutating the filesystem. If the task is not found, exits non-zero with a clear message.

## Acceptance Criteria

AC-1: WHEN `ai-team task start T-042` runs against a task in `pending/` THE SYSTEM SHALL move the file to `in-progress/` and rewrite its frontmatter `status` field to `in-progress`.
AC-2: WHEN `ai-team task block T-042 --reason "<text>"` runs THE SYSTEM SHALL move the file to `blocked/`, set status to `blocked`, and append a Work Log entry containing the supplied reason and today's date.
AC-3: WHEN any lifecycle subcommand runs against a task already in the destination state THE SYSTEM SHALL exit zero without mutating the filesystem.
AC-4: IF the supplied task ID does not match an existing task THEN THE SYSTEM SHALL exit non-zero with a "not found" message naming the searched folders.

## Dependencies

- `T-010` — extends the `ai_team.commands.task` module
- `T-004` — uses fs `move_artifact` and `update_status`

## Files to Touch

- `cli/src/ai_team/commands/task.py` — adds four subcommands to the existing Typer app
- `cli/tests/test_task_lifecycle.py` — covers each transition, idempotency, not-found, block reason logging

## Verification

```bash
cd cli && uv run pytest tests/test_task_lifecycle.py -q
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. -->

## Review

<!-- Reviewer: append verdict here after each review cycle. -->
