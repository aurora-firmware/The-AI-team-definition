---
id: "T-014"
title: "Implement task lifecycle commands (start, complete, block, unblock)"
status: completed
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

### Session 1 — 2026-05-10

Implemented T-014 lifecycle commands in `ai_team.commands.task` using TDD cycles.

Completed work:
- Added `task start`, `task complete`, `task block`, and `task unblock`.
- Implemented shared transition logic for task state moves using `update_status` and `move_artifact`.
- Added idempotency handling: when a task is already in the destination state, command exits zero with a clear `already in <state>` message and makes no filesystem changes.
- Added not-found handling with non-zero exit and a message naming searched task folders (`pending`, `in-progress`, `completed`, `blocked`).
- Implemented block reason logging by appending a new Work Log session entry dated today, with monotonically increasing session number, before moving to `blocked/`.

What was tried and rejected:
- Initial not-found test setup invoked commands outside a valid project root and failed with `ProjectRootNotFound`; corrected test fixtures to create project task folders so the command-level not-found behavior is actually exercised.

What remains:
- No known implementation work remains for this task scope; ready for reviewer handoff.

## Review

<!-- Reviewer: append verdict here after each review cycle. -->

### Review Verdict — 2026-05-10

PASS

Stage 1 (Acceptance Criteria): PASS
- AC-1 met: `task start` transitions `pending -> in-progress` and updates frontmatter status via `update_status` then `move_artifact` in `cli/src/ai_team/commands/task.py`.
- AC-2 met: `task block --reason` transitions into `blocked`, sets status `blocked`, and appends a dated Work Log session entry containing the reason (`_append_work_log_entry`).
- AC-3 met: lifecycle commands check destination first and return zero with `already in <state>` without mutation.
- AC-4 met: missing IDs return non-zero with a `not found` message that names searched lifecycle folders.
- File scope check: only expected files changed on implementation branch (`cli/src/ai_team/commands/task.py`, `cli/tests/test_task_lifecycle.py`).

Stage 2 (Code Quality): PASS
- Correctness/readability: shared transition helper keeps command behavior consistent and idempotent.
- Tests: dedicated lifecycle test module covers transitions, idempotency, block reason logging, and not-found behavior.
- Security/performance: no secrets introduced; filesystem operations are bounded and linear over task folders.

Verification evidence:
- `cd cli && uv run pytest tests/test_task_lifecycle.py -q` -> `10 passed`.
- `cd cli && uv run pytest -q` -> `126 passed`.
