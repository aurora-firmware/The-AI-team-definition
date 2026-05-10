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

### Review Verdict — 2026-05-10

PASS

Both stages passed.

**Stage 1 — Spec compliance**

- AC-1: `move_artifact` uses `os.replace` (not `shutil.move`) at the call site in the public function (line 240 of `fs.py`). Atomic rename confirmed. Covered by `test_move_artifact_renames_file_to_new_location` and `test_move_artifact_dest_contains_original_content`.
- AC-2: Dest-exists guard fires before any filesystem mutation; src is verified unchanged after a failed move. Covered by `test_move_artifact_raises_artifact_exists_when_dest_exists` and `test_move_artifact_leaves_src_unchanged_when_dest_exists`.
- AC-3: `update_status` calls `read_artifact` (which returns a `_source_map`-bearing model), sets `model.status`, then serialises via `dump_frontmatter`. The `ruamel.yaml` round-trip preserves YAML inline comments and key order. Covered by four `test_update_status_*` tests including `test_update_status_preserves_inline_yaml_comments`.
- AC-4: `Path.resolve()` is called on both src and dest before comparison; early return when equal. Covered by `test_move_artifact_no_op_when_src_equals_dest` and the redundant-component variant.
- Only the two files listed in `## Files to Touch` were modified. No unspecified functionality added.

**Design decision — `update_status` kind inference**

Acceptable. The four artifact templates have mutually exclusive discriminating frontmatter fields (`severity` for bugs, `assigned-role` for tasks, `author` for specs, everything else → adr). The Developer's documented edge case (a file with both `severity` and `assigned-role`) cannot arise from any template the framework ships. An explicit `kind=` parameter would add caller burden with no correctness benefit given the current template set. No change required.

**Stage 2 — Code quality**

- Correctness: All four public functions handle their documented error cases. `_extract_body` correctly strips the blank-line separator produced by `dump_frontmatter`. `_write_atomically` cleans up the `.tmp~` file on any exception.
- Tests: 21 tests; all ACs covered across success and failure paths. Tests use `tmp_path` (independent, no shared mutable state).
- Security: No hardcoded secrets; no external input used in queries; no new permissions.
- Readability: Helpers extracted and well-named (`_write_atomically`, `_infer_kind`, `_extract_body`). Docstrings explain the non-obvious blank-line normalisation.
- Performance: No unnecessary loops; temp file cleaned up on exception (no resource leak).

**Test evidence:** `uv run pytest tests/test_fs.py -q` → 21 passed. `uv run pytest -q` → 81 passed (60 pre-existing + 21 new, zero regressions).
