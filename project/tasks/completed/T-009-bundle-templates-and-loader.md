---
id: "T-009"
title: "Bundle artifact markdown templates and implement template loader"
status: completed
priority: medium
assigned-role: developer
created: 2026-05-10
---

# Bundle artifact markdown templates and implement template loader

## Description

Bundle the four artifact templates as package data and implement a loader. Copy the existing skill-bundled templates verbatim into `cli/src/ai_team/templates/` as `task.md`, `bug.md`, `spec.md`, `adr.md`. Sources to copy from:

- `task.md` ← `.claude/skills/new-task/assets/TEMPLATE-task.md`
- `bug.md` ← `.claude/skills/new-bug/assets/TEMPLATE-bug.md`
- `spec.md` ← `.claude/skills/new-spec/assets/TEMPLATE-specification.md`
- `adr.md` ← `.claude/skills/new-adr/assets/TEMPLATE-adr.md`

Implement `ai_team.core.templates` exposing `load_template(kind: Literal["task","bug","spec","adr"]) -> str` using `importlib.resources.files("ai_team.templates")`. The loader must work both when the package is installed and when run from source (via `uv run`).

The package-data configuration in `pyproject.toml` was already laid down by T-001; this task only adds files into the existing data directory.

## Acceptance Criteria

AC-1: WHEN `load_template("task")` runs THE SYSTEM SHALL return the byte-equal contents of `.claude/skills/new-task/assets/TEMPLATE-task.md` at the time of bundling.
AC-2: WHEN `load_template(<kind>)` runs for each of the four artifact kinds THE SYSTEM SHALL return a non-empty string starting with `---`.
AC-3: WHEN the package is built with `uv build` THE SYSTEM SHALL include all four template files in the resulting wheel.
AC-4: IF `load_template` is called with an unknown kind THEN THE SYSTEM SHALL raise `ValueError` naming the supported kinds.

## Dependencies

- `T-001` — needs the package skeleton and package-data config

## Files to Touch

- `cli/src/ai_team/templates/{task,bug,spec,adr}.md` — bundled templates (4 files)
- `cli/src/ai_team/core/templates.py` — `load_template`
- `cli/tests/test_templates.py` — covers all four kinds and the unknown-kind error

## Verification

```bash
cd cli && uv run pytest tests/test_templates.py -q && uv build && unzip -l dist/*.whl | grep templates/
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. -->

### Session 1 — 2026-05-10

Implemented T-009 via two TDD cycles on `task/T-009-bundle-templates-and-loader`.

Cycle 1 targeted AC-1: added a failing test asserting `load_template("task")` is byte-equal to `.claude/skills/new-task/assets/TEMPLATE-task.md`, then implemented `ai_team.core.templates.load_template` minimally and bundled `cli/src/ai_team/templates/task.md` verbatim. Test went red then green and was committed.

Cycle 2 targeted AC-2 and AC-4: expanded tests to cover all four kinds (`task`, `bug`, `spec`, `adr`) returning non-empty strings starting with `---`, plus unknown-kind `ValueError` that names supported kinds. Added verbatim bundled templates (`bug.md`, `spec.md`, `adr.md`) and generalized loader mapping with explicit validation/error text. Tests went red then green and were committed.

I briefly considered adding `cli/src/ai_team/templates/__init__.py`, but rejected it after verifying `importlib.resources.files("ai_team.templates")` already resolves correctly in this package layout.

Ran the verification command from the task. `pytest` passed and `uv build` + wheel inspection confirmed all four template files are included in the built wheel (AC-3). No remaining implementation work for this task.

## Review

<!-- Reviewer: append verdict here after each review cycle. -->

### Review Verdict — 2026-05-10
PASS

Stage 1 passed: all acceptance criteria met and file scope matched expectation (`cli/src/ai_team/core/templates.py`, four bundled template files, and `cli/tests/test_templates.py`). Verified byte-equality for all four bundled templates against their `.claude/skills/new-*/assets/` sources, verified unknown-kind `ValueError` includes supported kinds, and verified wheel includes all four templates.

Stage 2 passed: loader logic is correct and explicit, tests cover success and failure paths, no security concerns observed, readability is good, and no performance issues identified for this scope.
