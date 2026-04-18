---
id: "T-008"
title: "Bug template — add Work Log section"
status: completed
priority: high
assigned-role: implementer
created: 2026-04-18
spec: project/specs/handoff-progress-unification.md
---

# Bug template — add Work Log section

## Description

Per spec `handoff-progress-unification.md` (8.7), add a new `## Work Log` section to `TEMPLATE-bug.md`. The section is additive — the bug template did not previously have a Notes section.

Positioned after `## Fix Verification` and before any future sections. Same template-comment guidance as the task template:

```markdown
## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

```

## Acceptance Criteria

AC-1: The `TEMPLATE-bug.md` file shall contain a `## Work Log` section.
AC-2: The `## Work Log` section shall be positioned after `## Fix Verification`.
AC-3: The `## Work Log` section shall contain an HTML comment identical in guidance content to the task template comment: one entry per session boundary, dated heading `### Session N — YYYY-MM-DD`, free-prose body, read-before-starting, final-entry-is-handoff.
AC-4: No other section of the bug template shall be modified by this task.
AC-5: WHEN `/new-bug` generates a new bug file THE SYSTEM SHALL produce a document with a `## Work Log` section positioned after `## Fix Verification`.

## Dependencies

- None

## Files to Touch

- `.claude/skills/new-bug/assets/TEMPLATE-bug.md` — append Work Log section with guidance comment

## Verification

```bash
grep -n '^## Work Log' .claude/skills/new-bug/assets/TEMPLATE-bug.md
grep -n 'Append one entry per session' .claude/skills/new-bug/assets/TEMPLATE-bug.md
# Work Log appears after Fix Verification
awk '/^## /{print NR": "$0}' .claude/skills/new-bug/assets/TEMPLATE-bug.md
```

## Notes

Reference: spec 8.7, Component 2.

### Handoff Note — 2026-04-18

## What Was Done

- Added `## Work Log` to `.claude/skills/new-bug/assets/TEMPLATE-bug.md`.
- Placed the new section immediately after `## Fix Verification`.
- Reused the same mandatory session-boundary guidance comment from the task template, covering dated `### Session N — YYYY-MM-DD` entries, free-prose body expectations, read-before-starting guidance, and final-entry-as-handoff guidance.
- Verified the requested command-line checks pass and committed the template change in `79151aa`.

## What Remains

- [ ] Reviewer should confirm the additive template change satisfies AC-1 through AC-5.
- [ ] Reviewer should confirm `/new-bug` generation inherits the updated template as expected.

## Current State of Files

| File | State | Notes |
|---|---|---|
| `.claude/skills/new-bug/assets/TEMPLATE-bug.md` | modified | Work Log section added after Fix Verification and committed in `79151aa`. |
| `project/tasks/in-progress/bug-template-work-log-section.md` | modified | Handoff note appended under Notes for this implementation session. |

## Known Issues

- None.

## Context for the Next Agent

- This repository has no executable test suite for this Markdown/process task, so verification used the task's grep and awk inspections as the red/green checks.
- The pre-existing untracked `.codex/skills` path was not touched.

## Review

<!-- Reviewer appends verdict here after each review cycle. -->

### Review Verdict — 2026-04-18

PASS

Stage 1 passed: AC-1 through AC-5 are satisfied. The bug template now contains `## Work Log` immediately after `## Fix Verification`, with guidance content matching the task template, and `/new-bug` copies this template when generating bug files. The only implementation file change is the requested template update; the task-file handoff note is explicitly documented.

Stage 2 passed: visual diff and command-line checks found no process-template quality issues. No executable tests apply for this Markdown/process-only task.
