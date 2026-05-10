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

## Review

<!-- Reviewer: append verdict here after each review cycle. -->
