---
id: "T-015"
title: "Implement bug lifecycle commands (start, resolve)"
status: completed
priority: medium
assigned-role: developer
created: 2026-05-10
---

# Implement bug lifecycle commands (start, resolve)

## Description

Add two lifecycle subcommands to the `ai_team.commands.bug` module created in T-011. Each takes a bug ID (e.g., `B-007`) and moves the file between state folders while updating the frontmatter `status` field via `ai_team.core.fs.update_status` and `move_artifact`.

State transitions:
- `start <B-NNN>` — `open/` → `in-progress/`, status=`in-progress`
- `resolve <B-NNN>` — `in-progress/` → `resolved/`, status=`resolved`

Both operations are idempotent: if the bug is already in the destination state, the command prints a clear "already in <state>" message and exits zero without mutating the filesystem. If the bug is not found, exits non-zero with a clear message.

## Acceptance Criteria

AC-1: WHEN `ai-team bug start B-007` runs against a bug in `open/` THE SYSTEM SHALL move the file to `in-progress/` and rewrite its frontmatter `status` field to `in-progress`.
AC-2: WHEN `ai-team bug resolve B-007` runs against a bug in `in-progress/` THE SYSTEM SHALL move the file to `resolved/` and set status to `resolved`.
AC-3: WHEN either subcommand runs against a bug already in the destination state THE SYSTEM SHALL exit zero without mutating the filesystem.
AC-4: IF the supplied bug ID does not match an existing bug THEN THE SYSTEM SHALL exit non-zero with a "not found" message naming the searched folders.

## Dependencies

- `T-011` — extends the `ai_team.commands.bug` module
- `T-004` — uses fs `move_artifact` and `update_status`

## Files to Touch

- `cli/src/ai_team/commands/bug.py` — adds two subcommands to the existing Typer app
- `cli/tests/test_bug_lifecycle.py` — covers each transition, idempotency, not-found

## Verification

```bash
cd cli && uv run pytest tests/test_bug_lifecycle.py -q
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. -->

### Session 1 — 2026-05-10

Implemented T-015 with strict TDD across four red→green→refactor cycles. First cycle introduced `bug start` and verified open→in-progress movement plus frontmatter status rewrite. Second cycle added `bug resolve` for in-progress→resolved with status rewrite. Third cycle added idempotency checks for both commands and refactored shared transition logic so commands return zero with an "already in <state>" message and no file mutation when already in destination. Fourth cycle added not-found behavior checks and updated error handling to return non-zero with a message that names all searched lifecycle folders (`bugs/open`, `bugs/in-progress`, `bugs/resolved`). I considered keeping separate implementations for `start` and `resolve`, but rejected that due duplicated state-transition logic and higher risk of drift; replaced with a shared helper. Final verification command passed. No remaining implementation work for this task branch.

## Review

<!-- Reviewer: append verdict here after each review cycle. -->

### Review Verdict — 2026-05-10

PASS

Result: PASS

Summary:
- Stage 1 acceptance checks and Stage 2 quality checks passed for the submitted `task/T-015-implement-bug-lifecycle-commands` diff.

Artifacts:
- Canonical task file updated: `project/tasks/in-progress/T-015-implement-bug-lifecycle-commands.md`
- Diff reviewed: `cli/src/ai_team/commands/bug.py`, `cli/tests/test_bug_lifecycle.py`
- Primary files inspected: `cli/src/ai_team/commands/bug.py`, `cli/tests/test_bug_lifecycle.py`

Evidence:
- Checked expected diff against `dev-agent..task/T-015-implement-bug-lifecycle-commands`: only `M cli/src/ai_team/commands/bug.py` and `A cli/tests/test_bug_lifecycle.py`.
- AC-1 verified in code/tests: `bug start` moves `open/ -> in-progress/` and updates frontmatter status to `in-progress`.
- AC-2 verified in code/tests: `bug resolve` moves `in-progress/ -> resolved/` and updates status to `resolved`.
- AC-3 verified in code/tests: destination-state idempotency exits zero, prints `already in <state>`, and preserves file bytes.
- AC-4 verified in code/tests: missing ID exits non-zero with not-found message including searched lifecycle folders.
- Verification command run on implementation branch: `cd cli && uv run pytest tests/test_bug_lifecycle.py -q` -> `6 passed in 0.09s`.
- Stage 2 checks passed: correctness, tests, security, readability, and performance for task scope.

Obstacles Encountered:
- Sandbox blocked branch checkout and uv cache writes (`index.lock` and `~/.cache/uv` read-only); review proceeded after approved escalated command execution.

Next Owner:
- Development Loop

Next Action:
- none
