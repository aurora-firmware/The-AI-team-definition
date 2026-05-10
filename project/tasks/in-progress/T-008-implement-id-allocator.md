---
id: "T-008"
title: "Implement artifact ID allocator"
status: pending
priority: medium
assigned-role: developer
created: 2026-05-10
---

# Implement artifact ID allocator

## Description

Implement `ai_team.core.ids` providing `next_task_id(project_root) -> str`, `next_bug_id`, `next_spec_id`, `next_adr_id`. Each function scans every state folder of the relevant artifact type for filenames matching the appropriate prefix pattern, parses the numeric portion, and returns the next zero-padded ID.

Patterns:
- tasks: `T-NNN-*.md` across `pending`, `in-progress`, `completed`, `blocked`
- bugs: `B-NNN-*.md` across `open`, `in-progress`, `resolved`
- specs: `S-NNN-*.md` across `project/specs/` and `project/specs/archive/` (treated as one ID space)
- adrs: `ADR-NNN-*.md` across `project/decisions/`

Replicates the behaviour of `.claude/skills/new-task/assets/next-task-id.sh` (and the equivalent shell helpers for bugs/specs/ADRs) but in Python. Pure functions; no Typer dependency.

## Acceptance Criteria

AC-1: WHEN `next_task_id` runs against a project with no existing tasks THE SYSTEM SHALL return `"T-001"`.
AC-2: WHEN `next_task_id` runs against a project containing `T-007-*.md` and `T-012-*.md` across different state folders THE SYSTEM SHALL return `"T-013"`.
AC-3: The system shall return zero-padded three-digit IDs for all artifact types (`T-NNN`, `B-NNN`, `S-NNN`, `ADR-NNN`).
AC-4: The system shall ignore files that do not match the `<PREFIX>-NNN-*.md` pattern (e.g., `TEMPLATE-task.md`, `.gitkeep`).

## Dependencies

- `T-002` — uses `ProjectRoot` to resolve folder paths

## Files to Touch

- `cli/src/ai_team/core/ids.py` — four allocator functions
- `cli/tests/test_ids.py` — covers empty, gap-filled, ignore-non-matching cases

## Verification

```bash
cd cli && uv run pytest tests/test_ids.py -q
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. -->

## Review

<!-- Reviewer: append verdict here after each review cycle. -->
