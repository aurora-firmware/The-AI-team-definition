---
id: "T-009"
title: "TDD skill — add Step 0 (read Work Log) and Step 8 (append entry)"
status: pending
priority: high
assigned-role: implementer
created: 2026-04-18
spec: project/specs/handoff-progress-unification.md
---

# TDD skill — add Step 0 (read Work Log) and Step 8 (append entry)

## Description

Per spec `handoff-progress-unification.md` (8.7), add two procedural steps to `tdd/SKILL.md`:

- **Step 0 — Read the Work Log.** Before reading the acceptance criteria, read every existing entry in the Work Log. This is mandatory even on the first session (the log is empty; the step is a cheap no-op then).
- **Step 8 — Append a Work Log entry.** After refactor and before handing back to the orchestrator, append `### Session N — YYYY-MM-DD` with a free-prose body summarising what was done, what was tried and rejected, and what remains. Session number increments monotonically across all sessions on this task or bug.

Also update Quality Criteria to include: "The Work Log contains one entry per session boundary".
Also add a Common Pitfall: "Starting work without reading the Work Log".

Do not modify the existing intermediate TDD steps (red → green → refactor).

## Acceptance Criteria

AC-1: The `tdd/SKILL.md` file shall contain a Step 0 instructing the implementer to read every existing Work Log entry before reading the acceptance criteria.
AC-2: Step 0 shall state that the step is mandatory even on the first session, when the Work Log is empty.
AC-3: The `tdd/SKILL.md` file shall contain a Step 8 instructing the implementer to append a dated entry to the Work Log at session end, with heading `### Session N — YYYY-MM-DD` and a free-prose body.
AC-4: Step 8 shall state that the session number increments monotonically across all sessions on the same task or bug.
AC-5: The Quality Criteria section shall contain a bullet about one Work Log entry per session boundary.
AC-6: The Common Pitfalls section shall contain an entry about starting work without reading the Work Log.
AC-7: The existing red → green → refactor steps shall remain unmodified.
AC-8: WHEN the implementer runs the tdd skill THE SYSTEM SHALL require reading the Work Log before any other work, and appending an entry before handing back control.

## Dependencies

- `T-007` — task template must carry the Work Log section that this skill reads and writes
- `T-008` — bug template must carry the Work Log section too (the tdd skill is invoked for both tasks and bugs)

## Files to Touch

- `.claude/skills/tdd/SKILL.md` — insert Step 0, insert Step 8, update Quality Criteria, update Common Pitfalls

## Verification

```bash
# Step 0 and Step 8 present
grep -nE 'Step 0.*Work Log|Read the Work Log' .claude/skills/tdd/SKILL.md
grep -nE 'Step 8.*Work Log|Append.*Work Log' .claude/skills/tdd/SKILL.md
# Session N dated heading format referenced
grep -n 'Session N' .claude/skills/tdd/SKILL.md
# Quality Criteria bullet
grep -n 'one entry per session' .claude/skills/tdd/SKILL.md
# Common Pitfalls entry
grep -n 'without reading the Work Log' .claude/skills/tdd/SKILL.md
```

## Notes

Reference: spec 8.7, Component 3.

## Review

<!-- Reviewer appends verdict here after each review cycle. -->
