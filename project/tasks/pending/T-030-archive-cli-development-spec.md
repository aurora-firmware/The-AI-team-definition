---
id: "T-030"
title: "Archive the ai-team-python-cli development spec"
status: pending
priority: medium
assigned-role: "unassigned"
created: 2026-05-14
---

# Archive the ai-team-python-cli development spec

## Description

Per spec `project/specs/ai-team-cli-documentation.md` (Phase 4, Component 5), the original CLI development spec must be retired now that `cli/docs/` is the source of truth for CLI behaviour. Keeping both would leave two contradictory descriptions of the CLI.

Move `project/specs/ai-team-python-cli.md` to `project/specs/archive/`, set its frontmatter `status:` to `superseded`, and add an Amendment Log entry pointing readers to `cli/docs/` as the current source of truth. Use `git mv` so history is preserved. Do not edit the spec body beyond the frontmatter `status` field and the Amendment Log entry.

## Acceptance Criteria

AC-1: WHEN this task completes THE SYSTEM SHALL have `project/specs/ai-team-python-cli.md` located at `project/specs/archive/ai-team-python-cli.md` and absent from `project/specs/`.
AC-2: The system shall set the archived spec's frontmatter `status` field to `superseded`.
AC-3: The system shall add an Amendment Log entry to the archived spec naming `cli/docs/` as the current source of truth for CLI behaviour.
AC-4: The system shall not modify the archived spec's body content other than the `status` field and the Amendment Log entry.

## Dependencies

- `T-027` — `cli/docs/commands.md` must exist before the development spec is retired
- `T-028` — `cli/docs/usage.md` must exist before the development spec is retired

## Files to Touch

- `project/specs/ai-team-python-cli.md` — moved to `project/specs/archive/` (via `git mv`), `status` set to `superseded`, Amendment Log entry added

## Verification

```bash
test ! -e project/specs/ai-team-python-cli.md
test -f project/specs/archive/ai-team-python-cli.md
grep -q "status: superseded" project/specs/archive/ai-team-python-cli.md
grep -q "cli/docs" project/specs/archive/ai-team-python-cli.md
```

## Work Log

## Review
