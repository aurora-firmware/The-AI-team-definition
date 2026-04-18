---
id: "T-012"
title: "Agent + bootstrap + integrate — Work Log reference sweep"
status: pending
priority: medium
assigned-role: implementer
created: 2026-04-18
spec: project/specs/handoff-progress-unification.md
---

# Agent + bootstrap + integrate — Work Log reference sweep

## Description

Per spec `handoff-progress-unification.md` (8.7), update four files that currently reference the handoff note or the Notes section as the home of information that now belongs in the Work Log:

1. `.claude/agents/implementer.md` — the "Hands Off To" section (or equivalent) must refer to the final Work Log entry rather than the handoff-note artifact. Remove the reference to `ai-process/templates/handoff-note.md`.
2. `.claude/skills/bootstrap-project/SKILL.md` — remove `handoff-note.md` from any asset list used when scaffolding a new project.
3. `.claude/skills/integrate/SKILL.md` — the reading step that today says "Notes/Handoff sections" becomes "Work Log section". The integrator preserves the log as-is on merge (no new behaviour).
4. `.claude/skills/status-report/SKILL.md` — the step that reads the Notes section to report blocker reasons for blocked tasks must be reworded to read the Work Log section instead. After the Work Log sweep, blocked tasks record blocker descriptions in the Work Log (per T-015's CLAUDE.md Lifecycle update); status-report must read the same section to stay consistent.

## Acceptance Criteria

AC-1: The `.claude/agents/implementer.md` file shall refer to the final Work Log entry as the handoff artifact and shall not reference `ai-process/templates/handoff-note.md`.
AC-2: The `.claude/skills/bootstrap-project/SKILL.md` file's asset list shall not include `handoff-note.md`.
AC-3: The `.claude/skills/integrate/SKILL.md` file's reading step shall refer to the Work Log section of the task or bug file, not to Notes or Handoff sections.
AC-4: The integrator skill shall continue to state that the Work Log is preserved on merge (no stripping, no summarisation).
AC-5: IF any of the four files still references `handoff-note.md` as a filename or `handoff note` as an artifact name THEN THE SYSTEM SHALL be considered failing this task.
AC-6: The `.claude/skills/status-report/SKILL.md` file shall reference the Work Log section, not the Notes section, when describing how to read the blocker reason for a blocked task.

## Dependencies

- `T-007` — task template must carry the Work Log section
- `T-008` — bug template must carry the Work Log section

## Files to Touch

- `.claude/agents/implementer.md` — Hands Off To reword
- `.claude/skills/bootstrap-project/SKILL.md` — asset list trim
- `.claude/skills/integrate/SKILL.md` — reading step reword
- `.claude/skills/status-report/SKILL.md` — blocker-reason reading step reword

## Verification

```bash
for f in .claude/agents/implementer.md .claude/skills/bootstrap-project/SKILL.md .claude/skills/integrate/SKILL.md .claude/skills/status-report/SKILL.md; do
  if grep -nE 'handoff-note\.md|handoff note' "$f"; then
    echo "FAIL: residual reference in $f"; exit 1
  fi
done
grep -n 'Work Log' .claude/agents/implementer.md
grep -n 'Work Log' .claude/skills/integrate/SKILL.md
grep -n 'Work Log' .claude/skills/status-report/SKILL.md
! grep -n 'Notes section' .claude/skills/status-report/SKILL.md
```

## Notes

Reference: spec 8.7, Component 5 (partial).

### Session 1 — 2026-04-18

Updated the implementer handoff wording to use the final Work Log entry as the reviewer handoff artifact and removed the obsolete `ai-process/templates/handoff-note.md` reference. Removed the same obsolete asset from the bootstrap project template-source list. Reworded the integrate skill so it reads the Work Log section of the task file and explicitly preserves that log as-is on merge. Reworded the status-report skill so blocked-task reasons are read from the Work Log section instead of Notes.

Used command-line inspections as the red/green verification because this repository has no executable test suite. The initial greps found the expected stale handoff-note and Notes/Handoff references. After each narrow edit, the targeted greps passed and the slice was committed. The final task verification command also passed. No alternate implementation was needed beyond wording the integrate preservation rule directly; nothing remains except reviewer validation.

## Review

<!-- Reviewer appends verdict here after each review cycle. -->

### Review Verdict — 2026-04-18

PASS

Stage 1 passed: all acceptance criteria are met, including removal of `handoff-note.md` / `handoff note` artifact references from the four target files, Work Log wording in the implementer, integrate, and status-report skills, and explicit Work Log preservation in integrate.

Stage 2 passed: the edits are narrow wording/process updates with no executable behavior, no secrets or permission changes, and no readability issues. Verification was performed by visual diff inspection and the task's grep-based command-line checks.
