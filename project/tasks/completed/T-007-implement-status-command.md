---
id: "T-007"
title: "Implement ai-team status command"
status: completed
priority: medium
assigned-role: developer
created: 2026-05-10
---

# Implement ai-team status command

## Description

Implement `ai_team.commands.status` exporting Typer `app` with `NAME = "status"`. The single default command prints a Rich-rendered Gate 5 inline summary equivalent to today's `.claude/skills/status-report/scripts/status-summary.sh` output.

The summary contains: counts of active specs, tasks per state (pending / in-progress / completed / blocked), bugs per state (open / in-progress / resolved), ADR count; a list of in-progress tasks with assigned role; a list of blocked tasks with the blocking reason extracted from frontmatter or the latest Work Log entry; a list of critical/high-severity open bugs; and the latest integration result if discoverable from recent integration commits, otherwise the literal string "not found".

With `--json`, emit a structured object mirroring the same data and produce no Rich output.

## Acceptance Criteria

AC-1: WHEN `ai-team status` runs in a project with mixed-state artifacts THE SYSTEM SHALL print counts for every state folder of every artifact type.
AC-2: The system shall list every in-progress task with its assigned role and every blocked task with its blocking reason.
AC-3: The system shall list every open bug whose severity is `critical` or `high`.
AC-4: WHERE `--json` is supplied THE SYSTEM SHALL emit a structured JSON object and produce no Rich output.
AC-5: IF no integration evidence is discoverable from recent commits THEN THE SYSTEM SHALL report the latest integration result as `"not found"`.

## Dependencies

- `T-002` — uses locator
- `T-003` — uses models
- `T-004` — uses fs read

## Files to Touch

- `cli/src/ai_team/commands/status.py` — Typer app, summary computation, Rich and JSON renderers
- `cli/tests/test_status.py` — covers counts, blocked-with-reason, severity filter, JSON output

## Verification

```bash
cd cli && uv run pytest tests/test_status.py -q && uv run ai-team status --json
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. -->

### Session 1 — 2026-05-10

Implemented the new `status` command module and wired it through command auto-discovery via the existing conventions (`NAME` + Typer `app`). I started with failing tests for summary rendering and JSON output, then added minimal implementation for counts, in-progress tasks, blocked tasks, critical/high bug filtering, and integration result reporting. I then expanded tests to cover two important behaviors: blocked reason fallback from the latest Work Log session when no frontmatter reason exists, and detection of latest integration-like commit subject from git history. I considered reusing shell-script parsing semantics exactly, but rejected that in favor of a native Python implementation aligned with existing command patterns and testability. Remaining work on this task appears limited to downstream lifecycle updates/review flow on `dev-agent`; implementation and verification for this branch are complete.

### Session 2 — 2026-05-10

Synced `project/tasks/in-progress/T-007-implement-status-command.md` on `task/T-007-implement-status-command` to exactly match `dev-agent` (no manual lifecycle-content edits). Committed the sync as `ff20ad8`, preserving the existing `status` implementation and tests. Verified branch scope with `git diff --name-status dev-agent..HEAD` (now only `cli/src/ai_team/commands/status.py` and `cli/tests/test_status.py` differ) and re-ran `cli/.venv/bin/pytest -q cli/tests/test_status.py` (`4 passed`).

## Review

<!-- Reviewer: append verdict here after each review cycle. -->

### Review Verdict — 2026-05-10

FAIL

Stage 1 failed on file-scope constraints.

- **File and location:** `project/tasks/in-progress/T-007-implement-status-command.md` (Work Log section, around `## Work Log`).
- **What is wrong:** Source branch `task/T-007-implement-status-command` includes a lifecycle-file change (the Session 1 Work Log entry is deleted) even though `## Files to Touch` scopes this task to:
  - `cli/src/ai_team/commands/status.py`
  - `cli/tests/test_status.py`
- **What should change:** Sync/rebase `task/T-007-implement-status-command` onto current `dev-agent` and remove the task-file diff so the branch modifies only the two scoped CLI files.

### Review Verdict — 2026-05-10

FAIL

Stage 1 failed on file-scope constraints.

- **File and location:** `project/tasks/in-progress/T-007-implement-status-command.md` (Work Log section, `### Session 2 — 2026-05-10`).
- **What is wrong:** Source branch `task/T-007-implement-status-command` still modifies the canonical lifecycle file relative to `dev-agent` (it removes Session 2), while `## Files to Touch` limits this task to:
  - `cli/src/ai_team/commands/status.py`
  - `cli/tests/test_status.py`
- **What should change:** Re-sync/rebase `task/T-007-implement-status-command` to current `dev-agent` so `git diff --name-only dev-agent..task/T-007-implement-status-command` lists only the two scoped CLI files before re-submitting for review.

### Review Verdict — 2026-05-10

PASS

Stage 1 passed: scope now matches `## Files to Touch` exactly (`cli/src/ai_team/commands/status.py`, `cli/tests/test_status.py`), with no lifecycle-file diffs on the implementation branch.

Stage 2 passed: implementation and tests satisfy AC-1 through AC-5, including blocked-reason fallback, critical/high bug filtering, JSON-only output for `--json`, and `"not found"` behavior when integration evidence is absent.
