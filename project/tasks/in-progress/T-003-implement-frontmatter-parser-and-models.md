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

## Review

<!-- Reviewer: append verdict here after each review cycle. -->
