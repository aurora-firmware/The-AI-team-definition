---
id: "T-016"
title: "Implement ai-team archive command"
status: completed
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

### Session 1 — 2026-05-10

Implemented `ai-team archive` in `cli/src/ai_team/commands/archive.py` with a default command that scans `project/tasks/completed` and `project/bugs/resolved`, parses each artifact's `created` frontmatter date, and moves only artifacts older than the computed cutoff into `project/archive/YYYY-MM/` where the bucket comes from the artifact's created month. Added support for `--older-than` with `\d+[dwmy]` parsing (`d/w/m/y` mapped to days), and `--dry-run` output that reports files as "WOULD MOVE" without mutating the filesystem.

Followed TDD in cycles:
- Wrote a failing baseline archive behavior test first, then implemented minimum command behavior to pass.
- Added a failing dry-run wording/safety test, then changed dry-run output to explicitly state "WOULD MOVE".
- Added cutoff (`12w`) and invalid duration tests to complete acceptance coverage.

Tried and rejected keeping the original dry-run label `DRY-RUN:` because it did not align as clearly with the "would move" acceptance wording. Updated output accordingly.

Remaining work in this task branch: none. Verification command passes and the branch is clean.

## Review

<!-- Reviewer: append verdict here after each review cycle. -->

### Review Verdict — 2026-05-10

PASS

Result: PASS

Summary:
- Reviewed `task/T-016-implement-archive-command` against AC-1 through AC-4 and Stage 2 quality checks; all checks passed.

Artifacts:
- Updated canonical task file: `project/tasks/in-progress/T-016-implement-archive-command.md`.
- Reviewed diff: `dev-agent..task/T-016-implement-archive-command` (expected files only).
- Primary files inspected: `cli/src/ai_team/commands/archive.py`, `cli/tests/test_archive.py`.

Evidence:
- Scope check: `git diff --name-status dev-agent..task/T-016-implement-archive-command` returned only `A cli/src/ai_team/commands/archive.py` and `A cli/tests/test_archive.py`.
- Verification run: `cd cli && uv run pytest tests/test_archive.py -q` returned `4 passed in 0.09s`.
- Stage 1: default 90-day cutoff, `--dry-run`, invalid duration handling, and archive bucket directory creation logic are implemented and covered by tests.
- Stage 2: correctness, test coverage (success/failure paths), security, readability, and performance checks passed.

Obstacles Encountered:
- Initial sandbox run of `uv run pytest` failed due a read-only cache lock path; reran with escalated permissions and completed successfully.

Next Owner:
- Development Loop

Next Action:
- Proceed to integration for `task/T-016-implement-archive-command`.
