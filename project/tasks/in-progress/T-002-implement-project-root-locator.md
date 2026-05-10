---
id: "T-002"
title: "Implement project root locator"
status: pending
priority: high
assigned-role: developer
created: 2026-05-10
---

# Implement project root locator

## Description

Implement `ai_team.core.locator` so any CLI command can find the consuming project's root from any cwd.

Resolution order: (1) `--root <path>` flag, (2) `AI_TEAM_ROOT` env var, (3) walk parent directories looking for `.ai-team.toml` and use its `[project] dir` setting, (4) walk parent directories looking for a folder named after `--project-dir` (default `project`).

Return a `ProjectRoot` dataclass exposing absolute paths to: `repo`, `project_dir`, `specs/`, the four task state folders (`tasks/{pending,in-progress,completed,blocked}`), the three bug state folders (`bugs/{open,in-progress,resolved}`), `decisions/`, and `docs/`.

Raise `ProjectRootNotFound` with a message naming the searched paths and suggesting `ai-team init` when nothing is found. Pure module; no Typer dependency.

## Acceptance Criteria

AC-1: WHEN `find_project_root(cwd, root=None, project_dir="project")` runs from any directory under a repo containing a `project/` folder THE SYSTEM SHALL return a `ProjectRoot` whose `repo` field is that repo's root.
AC-2: WHERE `AI_TEAM_ROOT` env var is set to a valid repo THE SYSTEM SHALL prefer it over directory walking.
AC-3: WHEN a `.ai-team.toml` file with `[project] dir = "<name>"` is reachable above cwd THE SYSTEM SHALL honour the configured directory name.
AC-4: IF no project root can be resolved THEN THE SYSTEM SHALL raise `ProjectRootNotFound` whose message names the searched paths and suggests `ai-team init`.

## Dependencies

- `T-001` — needs the `ai_team` package skeleton

## Files to Touch

- `cli/src/ai_team/core/__init__.py` — empty package marker
- `cli/src/ai_team/core/locator.py` — `find_project_root`, `ProjectRoot`, `ProjectRootNotFound`
- `cli/tests/test_locator.py` — covers all four resolution paths and the not-found case

## Verification

```bash
cd cli && uv run pytest tests/test_locator.py -q
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. -->

### Session 1 — 2026-05-10

Implemented `ai_team.core.locator` from scratch in a single TDD session.

The test file was written first, covering 18 cases across all four acceptance criteria: upward filesystem walking (AC-1), `AI_TEAM_ROOT` environment variable taking precedence (AC-2), `.ai-team.toml` `[project] dir` override discovered anywhere in the ancestor chain (AC-3), and `ProjectRootNotFound` with diagnostic message and `ai-team init` hint (AC-4).

All tests failed on the first run (import error — `ai_team.core` did not exist). The empty `core/__init__.py` package marker was created, then `locator.py` was implemented.

Design decisions: `ProjectRoot` is a frozen dataclass with one field per artifact directory — this matches the spec's requirement to expose absolute paths to every named folder without any method calls at use-site. Resolution is handled by a single `find_project_root` function that checks strategies in spec order and raises `ProjectRootNotFound` with a `searched_str` of all directories visited. TOML parsing uses stdlib `tomllib` (Python 3.14 ships it); no new dependency was added. A private `_toml_project_dir` helper keeps the main function readable. Strategy 3 (TOML) and strategy 4 (folder-name walk) share a single upward loop rather than two separate passes — this avoids scanning the filesystem twice and keeps the edge-case logic (TOML present but declared folder missing) in one place.

No design alternatives were rejected; the first implementation passed all 18 tests without revision.

Nothing remains for this task: all four acceptance criteria are covered, the verification command passes, and the three files listed under "Files to Touch" are the only files changed.

## Review

<!-- Reviewer: append verdict here after each review cycle. -->
