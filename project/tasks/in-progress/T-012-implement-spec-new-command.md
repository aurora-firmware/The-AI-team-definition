---
id: "T-012"
title: "Implement ai-team spec new command"
status: pending
priority: medium
assigned-role: developer
created: 2026-05-10
---

# Implement ai-team spec new command

## Description

Create `ai_team.commands.spec` exporting a Typer `app` with `NAME = "spec"` and register a `new` subcommand. `new <title>` accepts optional flags `--author <name>` (default `planner`), `--status {draft|review|approved|superseded}` (default `draft`).

It allocates the next spec ID via `ai_team.core.ids.next_spec_id`, slugifies the title with `python-slugify`, loads the bundled spec template via `ai_team.core.templates.load_template("spec")`, fills frontmatter (id, title, version=`"0.1"`, status, created=today, author), and writes to `project/specs/<slug>.md` (specs are not state-foldered; the slug is the user-facing identifier). With `--json`, prints `{"id": "...", "path": "..."}` and no Rich output.

## Acceptance Criteria

AC-1: WHEN `ai-team spec new "<title>"` runs THE SYSTEM SHALL create exactly one file at `project/specs/<slug>.md` whose frontmatter is filled with the supplied title, today's date, and the supplied flags.
AC-2: The system shall echo the resulting absolute path to stdout.
AC-3: WHERE `--json` is supplied THE SYSTEM SHALL emit `{"id": "...", "path": "..."}` and no Rich output.
AC-4: IF a file with the allocated path already exists THEN THE SYSTEM SHALL exit non-zero without overwriting.

## Dependencies

- `T-004` — uses fs `write_artifact`
- `T-008` — uses ID allocator
- `T-009` — uses template loader

## Files to Touch

- `cli/src/ai_team/commands/spec.py` — Typer app and `new` subcommand
- `cli/tests/test_spec_new.py` — covers default flags, custom flags, JSON output, refuse-overwrite

## Verification

```bash
cd cli && uv run pytest tests/test_spec_new.py -q
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. -->

### Session 1 — 2026-05-10

Implemented `ai-team spec new` with Typer `NAME = "spec"` and `new` subcommand supporting `--author`, `--status`, and `--json`. The command allocates `S-NNN` via `next_spec_id`, slugifies the title for `project/specs/<slug>.md`, loads the bundled `spec` template, and writes via `write_artifact` with overwrite protection. I first considered constructing `Spec` directly without a source map, but that would drop the generated spec ID from frontmatter; I rejected that and instead parsed the template frontmatter map and injected `id` so the written file contains both templated fields/comments and the allocated ID. Added tests for defaults + absolute path output, JSON payload + custom flags, and refusal to overwrite existing files. Remaining work is reviewer/integration lifecycle only.

## Review

<!-- Reviewer: append verdict here after each review cycle. -->
