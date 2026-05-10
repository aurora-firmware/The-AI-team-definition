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

### Session 1 — 2026-05-10

Implemented the `ai-team list` command group end-to-end in `cli/src/ai_team/commands/list.py` with `tasks`, `bugs`, `specs`, and `adrs` subcommands. Each subcommand supports `--json`, and task/bug subcommands support `--state` folder filtering. Listing logic resolves project folders via `find_project_root`, parses artifacts with `parse_task` / `parse_bug` / `parse_spec` / `parse_adr`, and skips `.gitkeep` and `TEMPLATE-*.md` files. Default output renders Rich tables with the required column sets, and JSON output emits list-of-dict payloads with matching fields.

Used TDD in cycles: first wrote and failed a `list tasks` table/skip test, implemented minimal tasks listing, then expanded tests for state/json behavior and for bugs/specs/adrs field coverage, followed by implementation to green. One expected-order assertion in the bug JSON test was revised to match deterministic folder traversal order (`open`, `in-progress`, `resolved`) instead of lexical order.

Tried and rejected: using `uv run` for the canonical verification command in this environment (blocked by cache/temp write restrictions), then used the project venv binaries as an equivalent local verification path. Also attempted to commit after cycles as required, but git could not create `.git/index.lock` in the Developer subagent sandbox. The active loop created the final implementation commit from the completed task-branch diff after verifying the targeted and full test suites.

What remains: review and integration.

## Review

<!-- Reviewer: append verdict here after each review cycle. -->
