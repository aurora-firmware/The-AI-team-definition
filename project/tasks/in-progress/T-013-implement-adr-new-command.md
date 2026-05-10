---
id: "T-013"
title: "Implement ai-team adr new command"
status: pending
priority: medium
assigned-role: developer
created: 2026-05-10
---

# Implement ai-team adr new command

## Description

Create `ai_team.commands.adr` exporting a Typer `app` with `NAME = "adr"` and register a `new` subcommand. `new <title>` accepts optional flags `--status {proposed|accepted|superseded}` (default `proposed`), `--supersedes <ADR-NNN>` (optional reference to a superseded ADR).

It allocates the next ADR ID via `ai_team.core.ids.next_adr_id`, slugifies the title with `python-slugify`, loads the bundled ADR template via `ai_team.core.templates.load_template("adr")`, fills frontmatter (id, title, status, created=today, optional `supersedes`), and writes to `project/decisions/ADR-NNN-<slug>.md`. With `--json`, prints `{"id": "...", "path": "..."}` and no Rich output.

## Acceptance Criteria

AC-1: WHEN `ai-team adr new "<title>"` runs THE SYSTEM SHALL create exactly one file at `project/decisions/ADR-NNN-<slug>.md` with the allocated ID, supplied title, today's date, and supplied flags filled in.
AC-2: The system shall echo the resulting absolute path to stdout.
AC-3: WHERE `--json` is supplied THE SYSTEM SHALL emit `{"id": "...", "path": "..."}` and no Rich output.
AC-4: IF a file with the allocated path already exists THEN THE SYSTEM SHALL exit non-zero without overwriting.

## Dependencies

- `T-004` — uses fs `write_artifact`
- `T-008` — uses ID allocator
- `T-009` — uses template loader

## Files to Touch

- `cli/src/ai_team/commands/adr.py` — Typer app and `new` subcommand
- `cli/tests/test_adr_new.py` — covers default flags, custom flags, JSON output, refuse-overwrite

## Verification

```bash
cd cli && uv run pytest tests/test_adr_new.py -q
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. -->

### Session 1 — 2026-05-10

Implemented `ai-team adr new` at `ai_team.commands.adr` with `NAME = "adr"` and a `new` subcommand that allocates IDs via `next_adr_id`, slugifies titles, loads the bundled ADR template body, writes `project/decisions/ADR-NNN-<slug>.md`, prints absolute path by default, and emits `{"id":"...","path":"..."}` under `--json` with no Rich rendering. Added tests for default creation/output, custom `--status` + `--supersedes` with JSON output, and non-overwrite behavior when the allocated path already exists. Considered reusing richer template-frontmatter parsing (as in `spec`) but rejected it because ADR creation only needs template body and explicit model fields, so the simpler body-extraction path is clearer and consistent with `task`/`bug`. Remaining work: none for this task scope.

## Review

<!-- Reviewer: append verdict here after each review cycle. -->
