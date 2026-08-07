---
id: "T-001"
title: "Bootstrap cli/ uv project with Typer scaffold and command auto-discovery"
status: completed
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

### Session 1 — 2026-05-10

**What was done**

Implemented T-001 in full from scratch on branch `task/T-001-bootstrap-cli-uv-project`. Both uv 0.10.8 and Python 3.14.3 were available locally, so no environment blockers.

Created `cli/` with the following deliverables:

- `cli/pyproject.toml` — uv/Hatch project declaring `requires-python = ">=3.14"`, all five runtime deps (`typer`, `rich`, `ruamel.yaml`, `tomli-w`, `python-slugify`), `pytest` as a dev dep, the `ai-team = "ai_team.cli:app"` console-script entry, and `force-include` stanzas to ship `.gitkeep` markers in `templates/` and `init/scaffolds/` so those dirs appear in the wheel for later tasks.
- `cli/uv.lock` — committed for reproducible installs.
- `cli/src/ai_team/cli.py` — root Typer app with `--version` / `-V` eager callback reading from `importlib.metadata`, and a top-level call to `discover_and_mount(app)`.
- `cli/src/ai_team/commands/__init__.py` — `discover_and_mount(parent, modules=None)` function. When `modules` is `None` it walks sibling modules via `pkgutil.iter_modules`; when passed an explicit iterable it uses that (used in tests). Modules missing either `NAME` or `app` are silently skipped. Import failures inside a command module are suppressed so a broken module cannot crash the whole CLI.
- `cli/src/ai_team/render.py` — shared `Console` instance and `print_json(obj)` helper that writes JSON + newline to `sys.stdout`.
- `cli/tests/test_cli_bootstrap.py` — 6 tests covering all five acceptance criteria.

**TDD cycle**

Tests were written first and confirmed red before any production code was added. One test had to be revised mid-cycle: the original `test_auto_discovery_skips_module_without_name_attribute` invoked `--help` on an empty Typer app, which Typer 0.25 raises `RuntimeError` for (no commands registered). Fixed by asserting `len(parent_app.registered_groups) == 0` instead, which is the correct behavioral check.

**Approaches considered and rejected**

- `hatch.build.targets.wheel.packages` alone would not include empty dirs. Using `force-include` with `.gitkeep` files was chosen as the simplest portable approach — no Hatch plugin required, and `.gitkeep` files are a well-understood convention.
- Separating `discover_and_mount` into two separate functions (production vs. test variant) was considered but rejected — the optional `modules` parameter is cleaner and keeps the public API surface minimal.

**What remains**

Nothing for T-001 specifically. The scaffold is in place; later tasks T-002 onward simply drop command modules under `ai_team/commands/` and core modules under `ai_team/core/`.

## Review

<!-- Reviewer: append verdict here after each review cycle. -->

### Review Verdict — 2026-05-10

PASS

**Stage 1 — Acceptance Criteria**

- AC-1 (uv sync succeeds): `cd cli && uv sync` completed without error; all 17 packages including `ai-team==0.1.0` installed cleanly under Python 3.14.3. PASS.
- AC-2 (--version prints package version): `uv run ai-team --version` printed `0.1.0`, matching `pyproject.toml`. `test_version_output_matches_package_metadata` confirms this via `importlib.metadata`. PASS.
- AC-3 (console-script entry): `cli/pyproject.toml` declares `ai-team = "ai_team.cli:app"` under `[project.scripts]`; confirmed in the built wheel's `entry_points.txt`. `test_entry_point_resolves_to_cli_app` covers this. PASS.
- AC-4 (auto-discovery without cli.py changes): `commands/__init__.py` implements `discover_and_mount(parent, modules=None)`. When `modules` is `None`, `pkgutil.iter_modules` walks siblings and imports them; each module exporting both `NAME` and `app` is mounted via `parent.add_typer`. `cli.py` calls `discover_and_mount(app)` once at import time; no modification to `cli.py` is needed when new modules are dropped under `commands/`. `test_auto_discovery_registers_subcommand_from_module` and `test_auto_discovery_skips_module_without_name_attribute` cover the expected paths. PASS.
- AC-5 (package data dirs in wheel): `pyproject.toml` uses `force-include` to ship `templates/.gitkeep` and `init/scaffolds/.gitkeep`. Wheel inspection confirmed both paths appear as `ai_team/templates/.gitkeep` and `ai_team/init/scaffolds/.gitkeep`. Runtime check via `importlib.resources.files` confirms both directories are traversable. PASS.

No unspecified functionality was added. The Developer's implementation commit (`5e5272a`) touches only files within `cli/` (the 4 stated files plus supporting scaffolding: `__init__.py` stubs, test file, `.gitignore`, `uv.lock`). The T-002–T-026 pending task files and spec were added in a prior planning commit (`af2a4f5`) and are not the Developer's work — out-of-scope concern does not apply.

**Stage 2 — Code Quality**

- *Correctness*: `discover_and_mount` correctly handles the `modules=None` production path and the explicit-iterable test path. Silent skipping of modules missing `NAME` or `app` is correct. `except Exception: pass` in `_iter_command_modules` suppresses broken module imports safely. `--version` uses `importlib.metadata.version("ai-team")` — reads from installed metadata, not a hardcoded string.
- *Tests*: All 6 tests pass. Success and skip paths are covered for AC-4. Note: `test_package_data_dirs_are_importable_as_packages` asserts only that the `Traversable` objects are not `None` (trivially true); a stronger assertion would call `.is_dir()`. This is a minor observation — the wheel contents were verified separately and the test is non-blocking for this task.
- *Security*: No hardcoded credentials. No external input consumed by this bootstrap scaffold. No database queries.
- *Readability*: Names are descriptive and consistent with the project convention. Functions are focused. Docstrings explain the convention expected of command modules. No dead code or debug artifacts.
- *Performance*: Module discovery runs once at startup. No loops over large data sets.
- *Project-specific leak check*: No project-specific commands, paths, or assumptions were found in `cli/src/`.

**Verification command executed:** `cd cli && uv sync && uv run ai-team --version && uv build` — all steps passed.
