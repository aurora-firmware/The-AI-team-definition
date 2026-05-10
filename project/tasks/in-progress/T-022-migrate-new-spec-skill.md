---
id: "T-022"
title: "Migrate new-spec skill to invoke ai-team CLI"
status: pending
priority: low
assigned-role: developer
created: 2026-05-10
---

# Migrate new-spec skill to invoke ai-team CLI

## Description

Update `.claude/skills/new-spec/SKILL.md` so the procedure invokes `ai-team spec new --json` instead of reading a local template, slugifying via a bundled bash helper, and writing the file directly.

The migrated skill's responsibility narrows to: collect `title`, `description`, `author`, `status` from the caller, call the CLI to create the file, then fill the body sections from the supplied description. Delete `.claude/skills/new-spec/assets/TEMPLATE-specification.md` and `.claude/skills/new-spec/assets/slugify.sh`.

Verify no remaining references to the deleted files exist anywhere under `.claude/`.

## Acceptance Criteria

AC-1: The system shall update `.claude/skills/new-spec/SKILL.md` so the procedure invokes `ai-team spec new` and references no bundled template or slugify script.
AC-2: The system shall delete `.claude/skills/new-spec/assets/TEMPLATE-specification.md`.
AC-3: The system shall delete `.claude/skills/new-spec/assets/slugify.sh`.
AC-4: WHEN `grep -rn "TEMPLATE-specification.md\|new-spec/assets/slugify.sh" .claude/` runs THE SYSTEM SHALL produce no matches.

## Dependencies

- `T-012` — `ai-team spec new` must exist

## Files to Touch

- `.claude/skills/new-spec/SKILL.md` — updated procedure
- `.claude/skills/new-spec/assets/TEMPLATE-specification.md` — deleted
- `.claude/skills/new-spec/assets/slugify.sh` — deleted

## Verification

```bash
grep -rn "TEMPLATE-specification.md\|new-spec/assets/slugify.sh" .claude/ || echo OK
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. -->

### Session 1 — 2026-05-10

Implemented T-022 by migrating `.claude/skills/new-spec/SKILL.md` from local template/script creation to an `ai-team spec new --json` procedure. I kept the same required input semantics (title/description required, author/status optional, `$ARGUMENTS` fallback for title) and changed execution steps to build the CLI command, parse returned `id`/`path`, and then fill body sections from the supplied description while preserving `[TODO]` guidance for unresolved sections. I removed the obsolete assets `TEMPLATE-specification.md` and `slugify.sh` from `.claude/skills/new-spec/assets/`.

For TDD-style verification, I first ran the task grep command to confirm a failing pre-change state (reference present in `SKILL.md`), then applied the migration, deleted assets, and reran the same grep to reach green (`OK`). I also ran a broader sanity grep for both file names to ensure no lingering references under `.claude/`. Considered keeping default values explicitly in the CLI command, but rejected that in favor of honoring CLI defaults when optional fields are not provided, matching the migration intent to delegate file creation behavior to the CLI.

Remaining work in this session: none on the task branch; ready for reviewer pass and lifecycle update on `dev-agent`.

## Review

<!-- Reviewer: append verdict here after each review cycle. -->

### Review Verdict — 2026-05-10

PASS

Result: PASS

Summary:
- Reviewed `task/T-022-migrate-new-spec-skill` against T-022 acceptance criteria and Stage 2 quality checks; both stages passed.

Artifacts:
- Canonical task updated: `project/tasks/in-progress/T-022-migrate-new-spec-skill.md` (Review section).
- Diff reviewed on implementation branch: `M .claude/skills/new-spec/SKILL.md`, `D .claude/skills/new-spec/assets/TEMPLATE-specification.md`, `D .claude/skills/new-spec/assets/slugify.sh`.
- Primary file inspected: `.claude/skills/new-spec/SKILL.md` on `task/T-022-migrate-new-spec-skill`.

Evidence:
- `git diff --name-status dev-agent...task/T-022-migrate-new-spec-skill`
- `git diff dev-agent...task/T-022-migrate-new-spec-skill -- .claude/skills/new-spec/SKILL.md`
- `git show --name-status --oneline task/T-022-migrate-new-spec-skill -- .claude/skills/new-spec`
- `git grep -n "TEMPLATE-specification.md\\|new-spec/assets/slugify.sh" task/T-022-migrate-new-spec-skill -- .claude || true` (no matches)
- `git cat-file -e task/T-022-migrate-new-spec-skill:.claude/skills/new-spec/assets/TEMPLATE-specification.md` (not present in branch)
- `git cat-file -e task/T-022-migrate-new-spec-skill:.claude/skills/new-spec/assets/slugify.sh` (not present in branch)

Obstacles Encountered:
- none

Next Owner:
- Development Loop

Next Action:
- none
