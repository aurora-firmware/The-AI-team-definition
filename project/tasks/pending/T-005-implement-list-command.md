---
id: "T-005"
title: "Implement ai-team list command"
status: pending
priority: medium
assigned-role: developer
created: 2026-05-10
---

# Implement ai-team list command

## Description

Implement `ai_team.commands.list` exporting Typer `app` with `NAME = "list"`. Subcommands: `tasks`, `bugs`, `specs`, `adrs`. Common flags: `--state <name>` (filter by state folder where applicable), `--json`.

Default human output is a Rich table with columns appropriate to the artifact type:
- tasks: ID, title, state, priority, assigned-role
- bugs: ID, title, state, severity
- specs: ID, title, status, version
- adrs: ID, title, status

JSON output is a list of dicts with the same fields. Use `ai_team.core.locator.find_project_root` to resolve folders and `ai_team.core.models.parse_*` to load each artifact. Skip files matching `.gitkeep` and template files (`TEMPLATE-*.md`).

## Acceptance Criteria

AC-1: WHEN `ai-team list tasks` runs in a project with tasks across multiple state folders THE SYSTEM SHALL print a Rich table containing every non-template task.
AC-2: WHERE `--state <name>` is supplied THE SYSTEM SHALL only list artifacts in that state folder.
AC-3: WHERE `--json` is supplied THE SYSTEM SHALL emit a JSON list of dicts and produce no Rich-styled output.
AC-4: The system shall skip files named `.gitkeep` and files matching `TEMPLATE-*.md`.

## Dependencies

- `T-002` — uses locator
- `T-003` — uses models
- `T-004` — uses fs read

## Files to Touch

- `cli/src/ai_team/commands/list.py` — Typer app with four subcommands
- `cli/tests/test_list.py` — covers table output, JSON output, state filter, skip rules

## Verification

```bash
cd cli && uv run pytest tests/test_list.py -q && uv run ai-team list tasks --json
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. -->

## Review

<!-- Reviewer: append verdict here after each review cycle. -->
