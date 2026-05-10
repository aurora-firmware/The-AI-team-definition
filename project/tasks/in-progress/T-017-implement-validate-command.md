---
id: "T-017"
title: "Implement ai-team validate command"
status: pending
priority: medium
assigned-role: developer
created: 2026-05-10
---

# Implement ai-team validate command

## Description

Implement `ai_team.core.validate` (pure-function findings layer) plus `ai_team.commands.validate` (CLI surface). The command exposes `app` with `NAME = "validate"` and flags `--all|--tasks|--bugs|--specs|--adrs`, `--json`. Default is `--all`.

Checks performed:
1. Every artifact has all required frontmatter fields (delegate to `ai_team.core.models` parsers).
2. IDs match the expected pattern (`T-NNN`, `B-NNN`, `S-NNN`, `ADR-NNN`).
3. Filename matches `<ID>-<slug>.md` for state-foldered artifacts (tasks, bugs, ADRs); `<slug>.md` for specs.
4. The `status` frontmatter field matches the state folder the file lives in (e.g., a task in `pending/` has `status: pending`).
5. Cross-references resolve: a task's `spec:` field, when present, points to an existing spec; a bug's `task:` field, when present, points to an existing task; an ADR's `supersedes:` field, when present, points to an existing ADR.

Each finding has fields `path`, `level` (`error`|`warning`), `code`, `message`. The CLI renders them as a Rich table or, with `--json`, a JSON list. Exits non-zero if any finding has level `error`.

## Acceptance Criteria

AC-1: WHEN `ai-team validate` runs against a project with no issues THE SYSTEM SHALL exit zero and report zero findings.
AC-2: IF an artifact's `status` frontmatter field disagrees with its state folder THEN THE SYSTEM SHALL emit an error finding for that artifact.
AC-3: IF an artifact's cross-reference (task→spec, bug→task, adr→supersedes) does not resolve THEN THE SYSTEM SHALL emit an error finding naming the missing target.
AC-4: WHERE `--json` is supplied THE SYSTEM SHALL emit a JSON list of findings and produce no Rich output.
AC-5: IF any finding has level `error` THEN THE SYSTEM SHALL exit non-zero.

## Dependencies

- `T-002` — uses locator
- `T-003` — uses models
- `T-004` — uses fs read

## Files to Touch

- `cli/src/ai_team/core/validate.py` — pure-function checks returning findings
- `cli/src/ai_team/commands/validate.py` — Typer app and renderers
- `cli/tests/test_validate.py` — covers each check, JSON output, exit code

## Verification

```bash
cd cli && uv run pytest tests/test_validate.py -q
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. -->

### Session 1 — 2026-05-10

Implemented T-017 with a pure validation core and CLI wrapper. I started with a minimal failing AC-1 test (`ai-team validate` on a clean project), implemented the command/module skeleton, and got the first green pass. Then I added failing tests for folder-status mismatch and unresolved cross-references (task→spec, bug→task, ADR supersedes), implemented parser-backed checks plus error findings, and brought those tests green.

After that I expanded coverage for JSON-only output behavior, non-zero exit when any error exists, scope filtering (`--tasks`), and validation of required frontmatter/ID/filename rules. Most of those behaviors were already satisfied by the current implementation, so I kept the code mostly stable and only made a small robustness refactor to accept task spec references with or without `.md` suffix.

Tried/rejected: I considered relaxing spec ID checks because `parse_spec` does not require `id`, but kept spec ID validation as an explicit rule in this task since the requirement includes `S-NNN` ID pattern checks.

Remaining: no known implementation gaps for this task; reviewer can now evaluate against acceptance criteria.

## Review

<!-- Reviewer: append verdict here after each review cycle. -->
