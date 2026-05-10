---
id: "T-001"
title: "Bootstrap cli/ uv project with Typer scaffold and command auto-discovery"
status: pending
priority: high
assigned-role: developer
created: 2026-05-10
---

# Bootstrap cli/ uv project with Typer scaffold and command auto-discovery

## Description

Create the foundation for the `ai-team` CLI: a uv-managed Python package at `cli/` (Python ≥3.14) that produces a `ai-team` console-script.

Lay down `cli/pyproject.toml` declaring the runtime dependencies all later tasks need (`typer`, `rich`, `ruamel.yaml`, `tomli-w`, `python-slugify`) and dev dependencies (`pytest`). Use src-layout: `cli/src/ai_team/`. Configure Hatch (or uv's default backend) to ship `cli/src/ai_team/templates/` and `cli/src/ai_team/init/scaffolds/` as package data — later tasks (T-009, T-018, T-024) drop files into those dirs without touching `pyproject.toml`.

Implement `ai_team/cli.py` exposing a Typer `app` with a `--version` callback that reads from package metadata. Create `ai_team/commands/__init__.py` that auto-discovers all sibling modules via `pkgutil.iter_modules` and mounts each module's exported `app` Typer instance under its declared `NAME`. Provide `ai_team/render.py` with a shared `Console` and a `print_json(obj)` helper.

This task lays the foundation; later command tasks only drop new modules into `commands/` without modifying `cli.py`.

## Acceptance Criteria

AC-1: WHEN `uv sync` runs in `cli/` THE SYSTEM SHALL install all declared dependencies without error.
AC-2: WHEN `uv run ai-team --version` runs THE SYSTEM SHALL print the package version from `pyproject.toml`.
AC-3: The system shall expose an `ai-team` console-script entry pointing to `ai_team.cli:app`.
AC-4: WHEN a module exporting a Typer `app` and a `NAME` attribute is added under `ai_team.commands` THE SYSTEM SHALL automatically register it as a top-level subcommand without changes to `cli.py`.
AC-5: The system shall include `cli/src/ai_team/templates/` and `cli/src/ai_team/init/scaffolds/` as package data in the built wheel.

## Dependencies

- None

## Files to Touch

- `cli/pyproject.toml` — uv project metadata, deps, console-script entry, package-data config
- `cli/src/ai_team/cli.py` — Typer root app and `--version`
- `cli/src/ai_team/commands/__init__.py` — auto-discovery of subcommand modules
- `cli/src/ai_team/render.py` — shared `Console` and `print_json`

## Verification

```bash
cd cli && uv sync && uv run ai-team --version && uv build
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. -->

## Review

<!-- Reviewer: append verdict here after each review cycle. -->
