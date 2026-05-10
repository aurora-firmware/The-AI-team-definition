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

## Review

<!-- Reviewer: append verdict here after each review cycle. -->
