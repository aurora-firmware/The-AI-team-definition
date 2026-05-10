---
id: "T-007"
title: "Implement ai-team status command"
status: pending
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

## Review

<!-- Reviewer: append verdict here after each review cycle. -->
