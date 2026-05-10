---
id: "T-003"
title: "Implement frontmatter parser and artifact data models"
status: pending
priority: high
assigned-role: developer
created: 2026-05-10
---

# Implement frontmatter parser and artifact data models

## Description

Implement `ai_team.core.models` providing dataclasses for the four artifact types — `Task`, `Bug`, `Spec`, `Adr` — parsed from YAML frontmatter using `ruamel.yaml` in round-trip mode (preserves comments and key order, which we want when rewriting frontmatter via lifecycle commands).

Each model holds the common fields (`id`, `title`, `status`, `created`) plus type-specific fields:
- `Task`: `priority`, `assigned-role`, optional `spec` reference
- `Bug`: `severity`, optional `task` reference
- `Spec`: `version`, `author`
- `Adr`: `status` (proposed | accepted | superseded), optional `supersedes`

Provide `parse_task(path)`, `parse_bug(path)`, `parse_spec(path)`, `parse_adr(path)`, and a generic `dump_frontmatter(model, body) -> str`. Raise `FrontmatterError` naming the missing or invalid field on parse failure. Pure module; no I/O beyond reading the supplied path.

## Acceptance Criteria

AC-1: WHEN `parse_task(path)` runs on a task file with valid frontmatter THE SYSTEM SHALL return a `Task` instance with all common and type-specific fields populated.
AC-2: WHEN `dump_frontmatter(model, body)` runs THE SYSTEM SHALL produce output that round-trips through the matching `parse_*` to an equal model.
AC-3: IF a required frontmatter field is missing or has an invalid value THEN THE SYSTEM SHALL raise `FrontmatterError` whose message names the field and the source path.
AC-4: The system shall preserve YAML comments and key order across parse/dump cycles.

## Dependencies

- `T-001` — needs the `ai_team` package and `ruamel.yaml` declared in `pyproject.toml`

## Files to Touch

- `cli/src/ai_team/core/models.py` — dataclasses, parsers, dumper, `FrontmatterError`
- `cli/tests/test_models.py` — round-trip and error-path tests

## Verification

```bash
cd cli && uv run pytest tests/test_models.py -q
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. -->

### Session 1 — 2026-05-10

Implemented `ai_team.core.models` from scratch using TDD. Read the task file, spec at `project/specs/ai-team-python-cli.md` (Component 5 and Responsibility Separation), and all four artifact templates (TEMPLATE-task.md, TEMPLATE-bug.md, TEMPLATE-specification.md, TEMPLATE-adr.md) to establish the exact frontmatter shapes.

One design decision required reconciliation: the TEMPLATE-adr.md uses `number` as the identifier key while the task description specifies `id`. I used `id` for the `Adr` dataclass because the task description is explicit about it and `id` is the consistent naming convention across all other artifact types. The ADR template uses `number: 0` (an integer placeholder), so real ADR files in this project that follow the task description would use `id: "ADR-001"` as shown in the test fixtures.

For the `Bug` model: the `source_branch` field from the template was intentionally omitted from the dataclass because it is a lifecycle-operational field (used by the bug-fix loop to track which branch a task-regression bug came from), not a semantic data field that commands and validators need to reason about. The task description's type-specific fields list for Bug does not include `source_branch`. This is a trade-off: if future components need to read `source_branch`, the model will need extending.

The `dump_frontmatter` function uses `ruamel.yaml` round-trip mode with a `CommentedMap` to guarantee insertion-order preservation. Optional fields (`spec` for Task, `task` for Bug, `supersedes` for Adr) are omitted from output when `None` to keep dumped files clean. The `assigned-role` YAML key maps to `assigned_role` Python attribute to satisfy Python naming conventions while preserving the hyphenated YAML key form that templates use.

All 35 tests pass covering AC-1 through AC-4: parsing all four artifact types, round-trip fidelity, `FrontmatterError` on missing/invalid fields (field name and path in message), and key-order preservation across parse/dump cycles. The full prior test suite (59 total) also passes with no regressions.

## Review

<!-- Reviewer: append verdict here after each review cycle. -->
