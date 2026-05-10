---
id: "T-023"
title: "Migrate new-adr skill to invoke ai-team CLI"
status: pending
priority: low
assigned-role: developer
created: 2026-05-10
---

# Migrate new-adr skill to invoke ai-team CLI

## Description

Update `.claude/skills/new-adr/SKILL.md` so the procedure invokes `ai-team adr new --json` instead of reading a local template and writing the file directly.

The migrated skill's responsibility narrows to: collect `title`, `description`, `status`, and optional `supersedes` reference from the caller, call the CLI to create the file, then fill the body sections from the supplied description. Delete the bundled template and any helper scripts under `.claude/skills/new-adr/assets/`.

Verify no remaining references to the deleted files exist anywhere under `.claude/`.

## Acceptance Criteria

AC-1: The system shall update `.claude/skills/new-adr/SKILL.md` so the procedure invokes `ai-team adr new` and references no bundled template or helper script.
AC-2: The system shall delete every file under `.claude/skills/new-adr/assets/` that was bundled to support the previous procedure (template and any helper scripts identified at migration time).
AC-3: WHEN `grep -rn "TEMPLATE-adr.md\|next-adr-id.sh" .claude/` runs THE SYSTEM SHALL produce no matches.

## Dependencies

- `T-013` — `ai-team adr new` must exist

## Files to Touch

- `.claude/skills/new-adr/SKILL.md` — updated procedure
- `.claude/skills/new-adr/assets/` — delete the previous bundled template and any helper scripts

## Verification

```bash
grep -rn "TEMPLATE-adr.md\|next-adr-id.sh" .claude/ || echo OK
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. -->

## Review

<!-- Reviewer: append verdict here after each review cycle. -->
