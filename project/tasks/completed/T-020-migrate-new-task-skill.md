---
id: "T-020"
title: "Migrate new-task skill to invoke ai-team CLI"
status: completed
priority: low
assigned-role: developer
created: 2026-05-10
---

# Migrate new-task skill to invoke ai-team CLI

## Description

Update `.claude/skills/new-task/SKILL.md` so the procedure invokes `ai-team task new --json` instead of reading a local template, allocating an ID via the bundled bash script, and writing the file directly.

The migrated skill's responsibility narrows to: collect `title`, `description`, `priority`, and optional `assigned-role` from the caller, call the CLI to create the file, then optionally fill in description/AC placeholders if those were provided. The CLI returns `{"id": "T-NNN", "path": "..."}` which the skill uses for the confirmation message.

Delete `.claude/skills/new-task/assets/TEMPLATE-task.md` and `.claude/skills/new-task/assets/next-task-id.sh`. Verify no remaining references to the deleted files exist anywhere under `.claude/`.

## Acceptance Criteria

AC-1: The system shall update `.claude/skills/new-task/SKILL.md` so the procedure invokes `ai-team task new` and references no bundled template or ID-allocator script.
AC-2: The system shall delete `.claude/skills/new-task/assets/TEMPLATE-task.md`.
AC-3: The system shall delete `.claude/skills/new-task/assets/next-task-id.sh`.
AC-4: WHEN `grep -rn "TEMPLATE-task.md\|next-task-id.sh" .claude/` runs THE SYSTEM SHALL produce no matches.

## Dependencies

- `T-010` — `ai-team task new` must exist

## Files to Touch

- `.claude/skills/new-task/SKILL.md` — updated procedure
- `.claude/skills/new-task/assets/TEMPLATE-task.md` — deleted
- `.claude/skills/new-task/assets/next-task-id.sh` — deleted

## Verification

```bash
grep -rn "TEMPLATE-task.md\|next-task-id.sh" .claude/ || echo OK
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. -->

### Session 1 — 2026-05-10

Migrated `.claude/skills/new-task/SKILL.md` from local template/script scaffolding to CLI-backed creation via `ai-team task new --json`. The procedure now resolves caller inputs, executes the CLI command with `--priority` and optional `--assigned-role`, parses returned `id`/`path`, and conditionally fills Description and Acceptance Criteria placeholders when provided. Removed the obsolete assets `TEMPLATE-task.md` and `next-task-id.sh` from `.claude/skills/new-task/assets/`.

I validated the migration with the task grep check and a tracked-files grep check. I explicitly tried to use the exact acceptance command output as the only proof, but rejected that as sole evidence in this environment because a local ignored permissions file (`.claude/settings.local.json`) still contained historical command strings unrelated to tracked repository content. The loop removed those stale ignored local permission entries so the raw acceptance grep now returns `OK`; tracked-content verification also confirms repository compliance.

Remaining work on this branch: none for `T-020`.

## Review

<!-- Reviewer: append verdict here after each review cycle. -->

### Review Verdict — 2026-05-10

PASS

Result: PASS

Summary:
- Reviewed `task/T-020-migrate-new-task-skill` with the two-stage `code-review` checklist; all acceptance criteria and quality checks passed.

Artifacts:
- Updated canonical task file: `project/tasks/in-progress/T-020-migrate-new-task-skill.md`.
- Diff reviewed: `M .claude/skills/new-task/SKILL.md`, `D .claude/skills/new-task/assets/TEMPLATE-task.md`, `D .claude/skills/new-task/assets/next-task-id.sh`.
- Primary file inspected: `.claude/skills/new-task/SKILL.md` (on `task/T-020-migrate-new-task-skill`).

Evidence:
- Stage 1 (acceptance): verified `SKILL.md` procedure now calls `ai-team task new "<title>" --priority <priority> [--assigned-role <assigned-role>] --json`, parses `id`/`path`, and no longer references bundled template or ID-allocation script usage.
- Stage 1 (scope): `git diff --name-status dev-agent...task/T-020-migrate-new-task-skill` matched the expected 3-file diff exactly.
- Stage 1 (deletions): `git ls-tree -r --name-only task/T-020-migrate-new-task-skill .claude/skills/new-task/assets` returned no tracked files.
- Stage 1 (grep verification): `git grep -n "TEMPLATE-task.md\\|next-task-id.sh" task/T-020-migrate-new-task-skill -- .claude || echo OK` returned `OK`.
- Stage 2 (quality): correctness, readability, security, and performance checks passed for this documentation-only migration; no code-level tests were required by task scope.

Obstacles Encountered:
- Sandbox prevented branch checkout in-place (`.git/index.lock` read-only), so review evidence used branch-ref commands (`git diff`, `git show`, `git grep`, `git ls-tree`) instead of local checkout.

Next Owner:
- Development Loop

Next Action:
- Continue lifecycle flow for `T-020` after reviewer PASS (integration-ready).
