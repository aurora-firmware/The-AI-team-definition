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

### Review Verdict — 2026-05-10

PASS

Result: PASS

Summary:
- Reviewed `task/T-012-implement-spec-new-command` against T-012 acceptance criteria and Stage 2 code-quality checks; all required checks passed.

Artifacts:
- Updated canonical task file: `project/tasks/in-progress/T-012-implement-spec-new-command.md`
- Diff reviewed: `dev-agent..task/T-012-implement-spec-new-command` (expected two added files only)
- Primary files inspected: `cli/src/ai_team/commands/spec.py`, `cli/tests/test_spec_new.py`

Evidence:
- Scope check: `git diff --name-status dev-agent..task/T-012-implement-spec-new-command` returned only:
  - `A cli/src/ai_team/commands/spec.py`
  - `A cli/tests/test_spec_new.py`
- Stage 1 acceptance checks:
  - AC-1 satisfied: creates exactly one `project/specs/<slug>.md` with frontmatter fields populated from title/date/flags.
  - AC-2 satisfied: non-JSON path output is absolute path on stdout.
  - AC-3 satisfied: `--json` returns `{"id":"...","path":"..."}` shape with no Rich table output.
  - AC-4 satisfied: existing destination exits non-zero and does not overwrite.
- Verification run (task command): `cd cli && uv run pytest tests/test_spec_new.py -q` on exported snapshot of `task/T-012-implement-spec-new-command` → `3 passed`.
- Stage 2 quality checks passed for correctness, tests, security, readability, and performance within task scope.

Obstacles Encountered:
- Direct branch checkout in sandbox failed due `.git/index.lock` write restriction; worked around by reviewing via `git show`/`git diff` and running verification on a `git archive` snapshot in `/tmp`.
- Initial sandbox test run hit restricted network dependency resolution; reran verification with escalated permissions for `uv run pytest`.

Next Owner:
- Development Loop

Next Action:
- none
