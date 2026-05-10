---
id: "T-004"
title: "Implement filesystem layer for artifact reads, writes, and atomic moves"
status: pending
priority: high
assigned-role: developer
created: 2026-05-10
---

# Implement filesystem layer for artifact reads, writes, and atomic moves

## Description

Implement `ai_team.core.fs` as the single chokepoint for filesystem mutation across the CLI. Every command that reads or writes an artifact must go through this module so atomicity, idempotency, and error handling stay consistent.

Public functions:
- `read_artifact(path) -> tuple[Model, str]` — delegates parsing to `ai_team.core.models` and returns `(model, body)`.
- `write_artifact(path, model, body)` — writes via `ai_team.core.models.dump_frontmatter`; refuses to overwrite an existing path unless `overwrite=True` is passed.
- `move_artifact(src, dest)` — atomic `os.replace`; refuses if `dest` exists; no-op if `src == dest`.
- `update_status(path, new_status)` — rewrites frontmatter `status` field while preserving all other frontmatter content and the body verbatim.

Errors: `ArtifactNotFound`, `ArtifactExists`. Operations are idempotent where reasonable (already-at-target moves succeed silently with a clear message).

## Acceptance Criteria

AC-1: WHEN `move_artifact(src, dest)` runs and `src != dest` and `dest` does not exist THE SYSTEM SHALL atomically rename the file using `os.replace`.
AC-2: IF `move_artifact` is called with a `dest` that already exists THEN THE SYSTEM SHALL raise `ArtifactExists` and leave the filesystem unchanged.
AC-3: WHEN `update_status(path, new_status)` runs THE SYSTEM SHALL rewrite only the `status` frontmatter field and preserve all other frontmatter and body bytes.
AC-4: WHEN `move_artifact(src, dest)` runs with `src == dest` THE SYSTEM SHALL return without error and without mutating the filesystem.

## Dependencies

- `T-003` — uses `ai_team.core.models` for parse/dump

## Files to Touch

- `cli/src/ai_team/core/fs.py` — read/write/move/update functions and error classes
- `cli/tests/test_fs.py` — covers atomic move, refuse-overwrite, idempotent self-move, status-rewrite preservation

## Verification

```bash
cd cli && uv run pytest tests/test_fs.py -q
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. -->

### Session 1 — 2026-05-10

Implemented `ai_team.core.fs` from scratch as the single filesystem mutation chokepoint for the CLI. The module exposes `read_artifact`, `write_artifact`, `move_artifact`, and `update_status`, plus `ArtifactNotFound` and `ArtifactExists` error classes.

`read_artifact(path, kind)` delegates to the appropriate `parse_*` function from `ai_team.core.models` and extracts the body via `_extract_body`. The body extraction required one non-obvious normalisation: `dump_frontmatter` always writes `---\n\n<body>`, so the file on disk has a blank line between the closing fence and body content. `_extract_body` consumes that leading `\n` so the returned body round-trips cleanly through a dump cycle.

`write_artifact` uses `dump_frontmatter` to serialise the model and writes atomically via a sibling `.tmp~` file followed by `os.replace`.

`move_artifact` calls `Path.resolve()` on both src and dest before comparison, satisfying AC-4 (idempotent self-move) even when the caller passes a path with redundant components. AC-2 (refuse to overwrite) is checked before `os.replace`, so src is never modified on rejection.

`update_status` infers the artifact kind from the raw frontmatter text (heuristic: `severity` → bug, `assigned-role` → task, `author` → spec, otherwise → adr) rather than requiring the caller to pass it. This keeps the function ergonomic for the lifecycle-management commands that only know a file path and a new status string. The round-trip write goes through `dump_frontmatter` with the `_source_map`-bearing model, so YAML inline comments survive (AC-3).

Extracted `_write_atomically` to eliminate the duplicated temp-file pattern between `write_artifact` and `update_status`. Extracted `_infer_kind` to clarify the kind-detection logic.

One design decision to flag for review: `update_status` infers kind from field-name heuristics rather than accepting a `kind=` parameter. Convenient for callers but means a file with both `severity` and `assigned-role` in its frontmatter would be misclassified as a bug. Should not occur given distinct templates.

All four ACs pass; 81 tests green (60 pre-existing + 21 new). Committed on the task branch as `feat(fs): add ai_team.core.fs filesystem layer`.

## Review

<!-- Reviewer: append verdict here after each review cycle. -->
