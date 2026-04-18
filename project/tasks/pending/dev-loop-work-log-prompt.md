---
id: "T-010"
title: "Dev-loop skill — reword implementer prompt to reference Work Log"
status: pending
priority: medium
assigned-role: implementer
created: 2026-04-18
spec: project/specs/handoff-progress-unification.md
---

# Dev-loop skill — reword implementer prompt to reference Work Log

## Description

Per spec `handoff-progress-unification.md` (8.7), rewrite the implementer-spawning prompt in `dev-loop/SKILL.md` (Step 4) so it instructs the implementer to append a Work Log entry at session end instead of a handoff note.

Replace the current instruction (paraphrased: "append a handoff note ... following the format in ai-process/templates/handoff-note.md") with:

> "Append a Work Log entry at session end. The entry's heading is `### Session N — YYYY-MM-DD`; the body is free prose covering what was done, what was tried and rejected, and what remains. The final entry serves as the handoff to the reviewer."

Remove the reference to `ai-process/templates/handoff-note.md` (this file is deleted by T-016).

Additionally, the Step 5 reviewer prompt in `dev-loop/SKILL.md` currently instructs the reviewer to append the verdict to the task file's **Notes section**. Reword this to reference the task file's **Review section** (the section introduced by TEMPLATE-task.md where reviewer verdicts already belong). The Notes section is not the correct target for a reviewer verdict, and after the Work Log sweep the template's section vocabulary is Description / Acceptance Criteria / Dependencies / Files to Touch / Verification / Work Log / Review.

## Acceptance Criteria

AC-1: The `dev-loop/SKILL.md` file shall instruct the implementer to append a Work Log entry at session end.
AC-2: The implementer prompt in `dev-loop/SKILL.md` shall specify the dated-heading format `### Session N — YYYY-MM-DD`.
AC-3: The implementer prompt shall state that the final Work Log entry serves as the handoff to the reviewer.
AC-4: The `dev-loop/SKILL.md` file shall not contain a reference to `ai-process/templates/handoff-note.md`.
AC-5: The `dev-loop/SKILL.md` file shall not contain the phrase "handoff note" as an artifact name (the word "handoff" may appear in contexts describing the reviewer transition).
AC-6: WHEN the orchestrator spawns the implementer via dev-loop THE SYSTEM SHALL supply a prompt that references the Work Log as the session-end artifact.
AC-7: The Step 5 reviewer prompt in `dev-loop/SKILL.md` shall instruct the reviewer to append the verdict to the task file's Review section, not the Notes section.

## Dependencies

- `T-009` — the Work Log read/append steps in the tdd skill must exist before the dev-loop prompt references them

## Files to Touch

- `.claude/skills/dev-loop/SKILL.md` — implementer prompt reword

## Verification

```bash
# Work Log referenced
grep -n 'Work Log' .claude/skills/dev-loop/SKILL.md
# Handoff-note template path no longer referenced
! grep -n 'ai-process/templates/handoff-note' .claude/skills/dev-loop/SKILL.md
# "handoff note" as artifact name removed
! grep -nE 'handoff note' .claude/skills/dev-loop/SKILL.md
# Step 5 reviewer prompt no longer points at the Notes section
! grep -n "task file's Notes section" .claude/skills/dev-loop/SKILL.md
grep -n "task file's Review section" .claude/skills/dev-loop/SKILL.md
```

## Notes

Reference: spec 8.7, Component 4.

## Review

<!-- Reviewer appends verdict here after each review cycle. -->
