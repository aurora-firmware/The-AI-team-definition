---
id: "T-011"
title: "Bug-loop skill — reword implementer prompt to reference Work Log"
status: pending
priority: medium
assigned-role: implementer
created: 2026-04-18
spec: project/specs/handoff-progress-unification.md
---

# Bug-loop skill — reword implementer prompt to reference Work Log

## Description

Per spec `handoff-progress-unification.md` (8.7), rewrite the implementer-spawning prompt in `bug-loop/SKILL.md` (Step 4) so it instructs the implementer to append a Work Log entry at session end instead of a handoff note.

The reword mirrors T-010's change to `dev-loop/SKILL.md`, adapted to bug context:

> "Append a Work Log entry at session end. The entry's heading is `### Session N — YYYY-MM-DD`; the body is free prose covering what was done, what was tried and rejected, and what remains. The final entry serves as the handoff to the reviewer."

Remove the reference to `ai-process/templates/handoff-note.md` (this file is deleted by T-016).

## Acceptance Criteria

AC-1: The `bug-loop/SKILL.md` file shall instruct the implementer to append a Work Log entry at session end.
AC-2: The implementer prompt in `bug-loop/SKILL.md` shall specify the dated-heading format `### Session N — YYYY-MM-DD`.
AC-3: The implementer prompt shall state that the final Work Log entry serves as the handoff to the reviewer.
AC-4: The `bug-loop/SKILL.md` file shall not contain a reference to `ai-process/templates/handoff-note.md`.
AC-5: The `bug-loop/SKILL.md` file shall not contain the phrase "handoff note" as an artifact name.
AC-6: WHEN the orchestrator spawns the implementer via bug-loop THE SYSTEM SHALL supply a prompt that references the Work Log as the session-end artifact.

## Dependencies

- `T-009` — the Work Log read/append steps in the tdd skill must exist before the bug-loop prompt references them

## Files to Touch

- `.claude/skills/bug-loop/SKILL.md` — implementer prompt reword

## Verification

```bash
grep -n 'Work Log' .claude/skills/bug-loop/SKILL.md
! grep -n 'ai-process/templates/handoff-note' .claude/skills/bug-loop/SKILL.md
! grep -nE 'handoff note' .claude/skills/bug-loop/SKILL.md
```

## Notes

Reference: spec 8.7, Component 4.

### Session 1 — 2026-04-18

Updated `.claude/skills/bug-loop/SKILL.md` Step 4 so the implementer prompt now requires a session-end Work Log entry with the `### Session N — YYYY-MM-DD` heading format, free-prose coverage of what was done, what was tried and rejected, and what remains, and an explicit statement that the final entry serves as the handoff to the reviewer.

Used command-line grep checks as the TDD red/green verification because this repository has no executable test suite. The red check confirmed the old prompt still lacked `Work Log` and still referenced both `ai-process/templates/handoff-note.md` and the `handoff note` artifact phrase. After the scoped prompt replacement, the green checks confirmed `Work Log` is present and both forbidden references are absent. No broader refactor was needed or attempted.

What remains: reviewer verification of the prompt wording against the task acceptance criteria.

## Review

<!-- Reviewer appends verdict here after each review cycle. -->
