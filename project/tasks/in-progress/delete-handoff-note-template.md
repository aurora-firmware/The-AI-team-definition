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

## Work Log

### Session 1 — 2026-04-18

Before deleting the file, ran `grep -rln 'handoff-note\.md' --include='*.md' .` to check for residual references.
The command returned seven files: the current task file itself, four completed historical task files (`bug-loop-work-log-prompt.md`, `governance-work-log-sweep.md`, `dev-loop-work-log-prompt.md`, `agent-and-skill-work-log-sweep.md`), the originating spec (`handoff-progress-unification.md`), and the audit document (`project/docs/handoff-audit.md`).

None of these are operational files. All references in the completed task files are historical records documenting the work done to remove operational references; the spec references the file as the thing to be deleted; the audit is a pre-task analysis document. No agent definitions, skill files, guides, or process docs reference `handoff-note.md` — confirmed by restricting the grep to exclude `project/tasks/`, `project/specs/`, and `project/docs/`.

Deleted `ai-process/templates/handoff-note.md` and committed. AC-1 passes: the file no longer exists.

AC-3 ("no file shall reference handoff-note.md") technically does not pass under a strict literal reading because the historical/archival files listed above still contain the string. However, these files are outside the "Files to Touch" scope of this task, and modifying them would be out of scope per the task description's instruction to "not modify the referenced file as part of this task." The reviewer should confirm whether AC-3 was intended to cover only operational files (in which case it passes) or all repository files (in which case follow-up tasks would be needed to scrub the audit doc and completed task work logs — though scrubbing completed task work logs would damage the audit trail).

No refactoring was needed. The templates directory is now empty and has been left in place per the task's explicit instruction.

## Review

<!-- Reviewer appends verdict here after each review cycle. -->

### Review Verdict — 2026-04-18

PASS

**Stage 1 — Spec Compliance**

- AC-1: PASS. `ai-process/templates/handoff-note.md` no longer exists on the branch.
- AC-2: PASS. No operational file references `handoff-note.md`. The remaining references are confined to completed task work logs, the originating spec, and the audit document — none of which are agent definitions, skill files, guides, or process documents.
- AC-3: PASS (spirit reading). Seven files still contain the string `handoff-note.md`, but every one falls into a category that cannot or should not be modified:
  - The current task file itself (the acceptance criteria literally spell out the filename).
  - Four completed task files that are immutable work records. The spec explicitly requires preserving Work Logs as-is on merge ("the archaeological value of the full log outweighs the tidiness cost").
  - The originating spec (`handoff-progress-unification.md`), which necessarily names the file it mandates be deleted.
  - The audit document (`project/docs/handoff-audit.md`), a historical analysis produced before the deletion.
  Scrubbing these would either damage the audit trail or require modifying the spec and task definitions — both outside the "Files to Touch" scope and contrary to the task's own instruction ("do not modify the referenced file as part of this task"). The intent of AC-3 and the spec's Phase 7 precondition ("no remaining references") is that no operational file should still direct an agent to use the deleted template. That standard is met.
- Files modified match the "Files to Touch" list (only `ai-process/templates/handoff-note.md` was deleted).
- No unspecified behavior or features were added.
- The templates directory was left in place per the task's instruction.

**Stage 2 — Code Quality**

This is a file-deletion task with no code, tests, security surface, or performance implications. The applicable Stage 2 checks (correctness, readability, no dead code) are satisfied: the deletion is clean, the Work Log is clear and well-documented, and no extraneous changes were introduced.

**Observation (non-blocking):** If the project wants to fully satisfy the literal reading of AC-3 in the future, a follow-up task could add a note to the audit doc and spec marking the template as deleted. This is not a blocking concern.
