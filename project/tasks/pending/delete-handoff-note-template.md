---
id: "T-016"
title: "Delete handoff-note template"
status: pending
priority: low
assigned-role: implementer
created: 2026-04-18
spec: project/specs/handoff-progress-unification.md
---

# Delete handoff-note template

## Description

Per spec `handoff-progress-unification.md` (8.7), delete `ai-process/templates/handoff-note.md`. This is the last step of the Work Log rollout — all references to the handoff-note template must have been removed by prior tasks first.

Before deletion, verify that no remaining file in the repository references `handoff-note.md` by name or path. If residual references are found, the task is blocked until the referencing file is fixed (file a new task if necessary; do not modify the referenced file as part of this task).

If `ai-process/templates/` becomes empty after the deletion, leave the empty directory in place (or remove it if git tracks it as empty) — the decision about what to do with an empty `templates/` folder belongs to T-015.

## Acceptance Criteria

AC-1: The file `ai-process/templates/handoff-note.md` shall not exist after this task completes.
AC-2: IF any remaining file in the repository references `handoff-note.md` by name or path THEN THE SYSTEM SHALL be considered failing this task (the implementer must block on T-010 through T-015 being genuinely complete).
AC-3: No file in the repository shall reference `handoff-note.md` after this task completes.

## Dependencies

- `T-010` — dev-loop prompt no longer references the handoff-note template
- `T-011` — bug-loop prompt no longer references the handoff-note template
- `T-012` — implementer agent, bootstrap-project, integrate skill no longer reference the handoff-note template
- `T-013` — review-checklist and git-conventions no longer reference the handoff note
- `T-014` — workflow-overview and system-overview no longer reference the handoff note
- `T-015` — CLAUDE.md, README, setup-guide no longer reference the handoff-note template

## Files to Touch

- `ai-process/templates/handoff-note.md` — **deleted**

## Verification

```bash
# File is gone
[ ! -f ai-process/templates/handoff-note.md ]
# No residual reference anywhere in the repo
! grep -rln 'handoff-note\.md' --include='*.md' .
```

## Notes

Reference: spec 8.7, Component 5 and Implementation Order Phase 7.
This task is deliberately a late-phase cleanup. Running it before the other 8.7 tasks would break references across the framework.

## Review

<!-- Reviewer appends verdict here after each review cycle. -->
