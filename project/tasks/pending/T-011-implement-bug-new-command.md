---
id: "T-011"
title: "Implement ai-team bug new command"
status: pending
priority: medium
assigned-role: developer
created: 2026-05-10
---

# Implement ai-team bug new command

## Description

Create `ai_team.commands.bug` exporting a Typer `app` with `NAME = "bug"` and register a `new` subcommand. (Lifecycle subcommands are added by T-015; this task only introduces the module and `new`.)

`new <title>` accepts optional flags `--severity {critical|high|medium|low}` (default `medium`), `--task <T-NNN>` (optional cross-reference to the originating task). It allocates the next ID via `ai_team.core.ids.next_bug_id`, slugifies the title with `python-slugify`, loads the bundled bug template via `ai_team.core.templates.load_template("bug")`, fills frontmatter (id, title, status=open, severity, created=today, optional `task`), and writes to `project/bugs/open/B-NNN-<slug>.md`. With `--json`, prints `{"id": "B-NNN", "path": "..."}` and no Rich output.

## Acceptance Criteria

AC-1: WHEN `ai-team bug new "<title>"` runs THE SYSTEM SHALL create exactly one file at `project/bugs/open/B-NNN-<slug>.md` whose frontmatter is filled with the allocated ID, the supplied title, today's date, and the supplied flags.
AC-2: The system shall echo the resulting absolute path to stdout.
AC-3: WHERE `--json` is supplied THE SYSTEM SHALL emit `{"id": "...", "path": "..."}` and no Rich output.
AC-4: IF a file with the allocated path already exists THEN THE SYSTEM SHALL exit non-zero without overwriting.

## Dependencies

- `T-004` — uses fs `write_artifact`
- `T-008` — uses ID allocator
- `T-009` — uses template loader

## Files to Touch

- `cli/src/ai_team/commands/bug.py` — Typer app and `new` subcommand
- `cli/tests/test_bug_new.py` — covers default flags, custom flags, JSON output, refuse-overwrite

## Verification

```bash
cd cli && uv run pytest tests/test_bug_new.py -q
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. -->

## Review

<!-- Reviewer: append verdict here after each review cycle. -->
