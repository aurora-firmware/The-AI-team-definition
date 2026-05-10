---
id: "T-018"
title: "Implement ai-team report command and bundle progress-report template"
status: pending
priority: medium
assigned-role: developer
created: 2026-05-10
---

# Implement ai-team report command and bundle progress-report template

## Description

Implement `ai_team.commands.report` exporting `app` with `NAME = "report"`. The default command writes a full Gate 5 progress report to `project/docs/reports/progress-report-<YYYY-MM-DD>.md`.

Bundle the existing report template (`.claude/skills/status-report/assets/progress-report.md`) verbatim into `cli/src/ai_team/templates/progress-report.md`. Extend `ai_team.core.templates` with a `load_report_template() -> str` helper or generalise `load_template` to accept the new key.

The command computes the same summary data as `ai-team status` (T-007) and fills the template (counts, in-progress detail, blocked items with action needed, bug listing, next actions, risks/concerns). Creates `project/docs/reports/` if it does not exist. Supports `--out <path>` to override the destination.

## Acceptance Criteria

AC-1: WHEN `ai-team report` runs THE SYSTEM SHALL write a markdown report to `project/docs/reports/progress-report-<YYYY-MM-DD>.md` using the bundled template.
AC-2: WHERE `--out <path>` is supplied THE SYSTEM SHALL write the report to that path instead.
AC-3: The system shall create the destination directory if it does not exist.
AC-4: The system shall fill the template with counts, in-progress task list, blocked task list with reason, bug list, and next-actions section.

## Dependencies

- `T-007` — reuses status-summary computation
- `T-009` — uses template loader (extending it for the report template)

## Files to Touch

- `cli/src/ai_team/templates/progress-report.md` — bundled template
- `cli/src/ai_team/commands/report.py` — Typer app, template fill logic
- `cli/tests/test_report.py` — covers default path, `--out`, directory creation, template fill

## Verification

```bash
cd cli && uv run pytest tests/test_report.py -q
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. -->

## Review

<!-- Reviewer: append verdict here after each review cycle. -->
