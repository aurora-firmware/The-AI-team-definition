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

### Session 1 — 2026-05-10

Implemented T-011 using TDD on `task/T-011-implement-bug-new-command`. I started by reading the task file (work log was empty) and existing command patterns (`task new`) plus core helpers (`next_bug_id`, `load_template`, `write_artifact`). I then wrote `cli/tests/test_bug_new.py` to cover: default creation to `project/bugs/open/B-NNN-<slug>.md` with correct frontmatter and absolute-path stdout; custom `--severity` + `--task` with `--json` output and no Rich table output; and non-overwrite behavior when the allocated path already exists. Initial test run failed (as expected) because `bug` command did not exist. I implemented `cli/src/ai_team/commands/bug.py` with Typer `app`, `NAME = "bug"`, and `new` subcommand that allocates IDs, slugifies titles, loads the bundled bug template body, writes through `write_artifact(overwrite=False)`, returns JSON when requested, and exits non-zero on existing destination without overwriting. Re-ran verification and all tests passed. I considered extracting shared template-body parsing from `task.py` to avoid duplication, but rejected that in this session to stay within T-011 scope and touched-file boundaries. Nothing remains for this task branch from implementation side; ready for reviewer and lifecycle update on `dev-agent`.

## Review

<!-- Reviewer: append verdict here after each review cycle. -->
