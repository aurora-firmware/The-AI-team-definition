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

### Session 1 — 2026-05-10

Migrated the `new-adr` skill from local template/script generation to CLI-based creation. I first ran the verification grep and confirmed the existing skill still referenced `TEMPLATE-adr.md`; I also checked for the real helper name and confirmed it referenced `next-adr-number.sh`. I updated `SKILL.md` to require `title`, `description`, `status`, and optional `supersedes`, then switched the procedure to building and running `ai-team adr new "<title>" --status "<status>" --json` (with optional `--supersedes`), parsing `id`/`path`, and filling ADR body sections from the supplied description. I then deleted both legacy asset files and removed the now-empty assets directory. I considered broadening edits to other skills that mention old `new-adr` inputs, but rejected that because this task's scoped files are limited to `new-adr` skill migration and asset deletion. Final verification greps are clean, including both helper-name variants. Remaining work: reviewer pass and lifecycle updates on `dev-agent` by the loop.

## Review

<!-- Reviewer: append verdict here after each review cycle. -->
