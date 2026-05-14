---
id: "T-030"
title: "Archive the ai-team-python-cli development spec"
status: completed
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

### Session 1 — 2026-05-14

Picked up T-030 with an empty Work Log. The task is purely a file-archival operation: move `project/specs/ai-team-python-cli.md` to `project/specs/archive/` via `git mv`, set `status: superseded` in the frontmatter, and add an Amendment Log entry pointing readers to `cli/docs/` as the current source of truth.

Before starting, confirmed both prerequisite deliverables existed: `cli/docs/commands.md` (T-027) and `cli/docs/usage.md` (T-028) were both present. The `project/specs/archive/` directory already existed, so no directory creation was needed.

Ran the task's four verification commands as a red-phase check — all failed as expected. Then applied the three changes atomically: `git mv` to rename with history preservation, `status: approved` replaced with `status: superseded` in the frontmatter, and the Amendment Log comment block replaced with a live table row citing `cli/docs/commands.md` and `cli/docs/usage.md` and explaining the reason for archival. Re-ran all four verification commands — all passed. Committed as a single cycle on the task branch.

Nothing was tried and rejected; the task was unambiguous. Nothing remains.

## Review

### Review Verdict — 2026-05-14

PASS

**Stage 1 — Spec compliance**

- AC-1: The file `project/specs/ai-team-python-cli.md` is absent from `project/specs/` and present at `project/specs/archive/ai-team-python-cli.md` on the task branch. Confirmed via `git ls-tree`.
- AC-2: The frontmatter `status` field reads `superseded`. Confirmed via `git show` on the archived file.
- AC-3: The Amendment Log contains a table row dated 2026-05-14 citing `cli/docs/commands.md` and `cli/docs/usage.md` as the current source of truth. Confirmed via `git show`.
- AC-4: The commit diff (R098 rename with 5 lines changed across the whole file) shows exactly two changes to the file body: `status: approved` → `status: superseded` in the frontmatter, and the Amendment Log HTML comment block replaced with the live table row. No other body content was modified.

Git rename was performed with `git mv`: the commit records `R098` (98% similarity), confirming history is preserved.

Only the stated file (`project/specs/ai-team-python-cli.md` → `project/specs/archive/ai-team-python-cli.md`) was touched. No other files were modified.

**Stage 2 — Code quality**

Not applicable: this task involves no code. The checklist items for tests, security, and performance do not apply to a markdown archival operation. Readability and correctness checks on the Amendment Log entry pass — the entry is accurate, complete, and scoped exactly to what was done.
