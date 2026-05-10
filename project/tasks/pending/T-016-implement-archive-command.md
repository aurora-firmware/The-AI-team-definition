---
id: "T-016"
title: "Implement ai-team archive command"
status: pending
priority: low
assigned-role: developer
created: 2026-05-10
---

# Implement ai-team archive command

## Description

Implement `ai_team.commands.archive` exporting Typer `app` with `NAME = "archive"`. The single default command moves completed tasks and resolved bugs older than `--older-than` (default `90d`) into a year-month bucket under `project/archive/`.

The `--older-than` flag accepts a simple duration like `30d`, `12w`, `6m`, `1y` (regex `\d+[dwmy]`); the cutoff is computed against today's date. "Age" is read from the artifact's `created` frontmatter field.

For each artifact older than the cutoff: move `project/tasks/completed/T-NNN-*.md` to `project/archive/<YYYY-MM>/T-NNN-*.md` and `project/bugs/resolved/B-NNN-*.md` to `project/archive/<YYYY-MM>/B-NNN-*.md`, where `<YYYY-MM>` is taken from the artifact's `created` field. Supports `--dry-run` listing what would move without moving.

## Acceptance Criteria

AC-1: WHEN `ai-team archive` runs with the default cutoff THE SYSTEM SHALL move every completed task and resolved bug whose `created` date is more than 90 days before today into `project/archive/<YYYY-MM>/`.
AC-2: WHERE `--dry-run` is supplied THE SYSTEM SHALL list the files that would be moved and produce no filesystem mutation.
AC-3: IF an `--older-than` value does not match `\d+[dwmy]` THEN THE SYSTEM SHALL exit non-zero with a clear error message.
AC-4: The system shall create `project/archive/<YYYY-MM>/` directories on demand.

## Dependencies

- `T-002` — uses locator
- `T-003` — uses models for `created` field
- `T-004` — uses fs `move_artifact`

## Files to Touch

- `cli/src/ai_team/commands/archive.py` — Typer app, duration parser, archiver
- `cli/tests/test_archive.py` — covers cutoff calculation, dry-run, invalid duration, year-month bucketing

## Verification

```bash
cd cli && uv run pytest tests/test_archive.py -q
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. -->

## Review

<!-- Reviewer: append verdict here after each review cycle. -->
