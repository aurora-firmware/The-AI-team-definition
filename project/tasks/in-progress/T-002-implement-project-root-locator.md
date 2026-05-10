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

### Review Verdict — 2026-05-10

PASS

**Stage 1 — Spec compliance:** All four acceptance criteria are satisfied.

- AC-1: `find_project_root(cwd, root=None, project_dir="project")` signature is exact. Upward filesystem walk correctly resolves the repo root from any nested cwd. Six tests cover the walking path including deeply nested directories, all path fields (specs, tasks, bugs, decisions, docs), and absolute-path guarantees.
- AC-2: `AI_TEAM_ROOT` is checked (strategy 2) before the walk loop (strategies 3+4), giving it correct precedence over directory walking. Two tests verify env-var override and project_dir resolution.
- AC-3: `.ai-team.toml` is parsed with stdlib `tomllib` (no third-party dependency). The `_toml_project_dir` helper correctly returns `data.get("project", {}).get("dir")` and silently returns `None` on any parse or I/O error. Three tests cover: TOML at cwd, TOML in a parent directory, and TOML without a `[project] dir` key falling through to folder walking.
- AC-4: `ProjectRootNotFound` is raised with a message containing the searched paths and the `ai-team init` hint. Four tests cover: not-found when no project folder exists, message names searched paths, message contains `ai-team init`, and not-found when `AI_TEAM_ROOT` points to a repo without the expected folder.

No unspecified behaviour was added. Only the three files listed under "Files to Touch" were modified.

**Stage 2 — Code quality:**

- Correctness: Resolution order matches spec exactly (explicit arg → env var → TOML walk → folder-name walk). Edge case where TOML is present but the declared folder is missing is handled correctly (continues walking). `cwd.resolve()` guarantees absolute paths throughout.
- Tests: 18 tests, all passing (`cd cli && uv run pytest tests/test_locator.py -q` → 18 passed). Tests use `tmp_path` (independent, no shared mutable state). Both success and failure paths covered.
- Security: No hardcoded credentials. External TOML input errors are caught and silently return `None` (no crash on malformed files). No DB queries.
- Readability: `ProjectRoot` is a frozen dataclass with field-level docstrings. `find_project_root` has a clear docstring with Parameters and Raises sections. `_toml_project_dir` is a focused private helper. No dead code or debug artifacts.
- Performance: Single upward walk handles both TOML and folder-name strategies; no double filesystem scan.

Minor observation (non-blocking): when strategy 1 (`root=` arg) is used, `_toml_project_dir(repo)` is also called to allow the TOML to override the project-dir name. The spec does not explicitly address this combination, but it is internally consistent and does not contradict any criterion.
