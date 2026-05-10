---
id: "T-010"
title: "Implement ai-team task new command"
status: pending
priority: high
assigned-role: developer
created: 2026-05-10
---

# Implement ai-team task new command

## Description

Create `ai_team.commands.task` exporting a Typer `app` with `NAME = "task"` and register a `new` subcommand. (Lifecycle subcommands are added by T-014; this task only introduces the module and `new`.)

`new <title>` accepts optional flags `--priority {critical|high|medium|low}` (default `medium`), `--assigned-role <role>` (default `unassigned`), `--spec <S-NNN>` (optional cross-reference). It allocates the next ID via `ai_team.core.ids.next_task_id`; slugifies the title with `python-slugify`; loads the bundled task template via `ai_team.core.templates.load_template("task")`; fills frontmatter (id, title, status=pending, priority, assigned-role, created=today, optional `spec`); writes the result to `project/tasks/pending/T-NNN-<slug>.md`. With `--json`, prints `{"id": "T-NNN", "path": "..."}` and no Rich output.

## Acceptance Criteria

AC-1: WHEN `ai-team task new "<title>"` runs THE SYSTEM SHALL create exactly one file at `project/tasks/pending/T-NNN-<slug>.md` whose frontmatter is filled with the allocated ID, the supplied title, today's date, and the supplied flags.
AC-2: The system shall echo the resulting absolute path to stdout.
AC-3: WHERE `--json` is supplied THE SYSTEM SHALL emit `{"id": "...", "path": "..."}` and no Rich output.
AC-4: IF a file with the allocated path already exists THEN THE SYSTEM SHALL exit non-zero without overwriting.

## Dependencies

- `T-004` — uses fs `write_artifact`
- `T-008` — uses ID allocator
- `T-009` — uses template loader

## Files to Touch

- `cli/src/ai_team/commands/task.py` — Typer app and `new` subcommand
- `cli/tests/test_task_new.py` — covers default flags, custom flags, JSON output, refuse-overwrite

## Verification

```bash
cd cli && uv run pytest tests/test_task_new.py -q
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. -->

### Session 1 — 2026-05-10

Implemented T-010 by adding a new `ai_team.commands.task` module with a Typer `app` and `task new` subcommand. The command now resolves project root, allocates `T-NNN` via `next_task_id`, slugifies the title, loads the bundled `task` template, preserves its body, fills frontmatter fields (`id`, `title`, `status=pending`, `priority`, `assigned-role`, `created`, optional `spec`), and writes to `project/tasks/pending/T-NNN-<slug>.md`. Non-JSON mode prints the absolute artifact path; `--json` emits only `{"id": "...", "path": "..."}`.

Followed TDD in cycles: first wrote and ran a failing default-path/frontmatter test, implemented minimal command behavior, reran green, and committed. Then expanded tests for custom flags, JSON contract, and overwrite refusal; these passed with the existing implementation, so I kept production code unchanged and committed the test expansion. For overwrite testing, I considered relying on natural ID allocation collisions but rejected that because the allocator increments past existing files; I validated AC-4 by pinning `next_task_id` in the test to force an allocated-path conflict and verifying non-zero exit with unchanged file bytes.

No remaining implementation work for this task's stated acceptance criteria; ready for reviewer handoff.

## Review

<!-- Reviewer: append verdict here after each review cycle. -->
