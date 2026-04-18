---
id: "T-013"
title: "Guidelines sweep — review-checklist + git-conventions reference update"
status: pending
priority: medium
assigned-role: implementer
created: 2026-04-18
spec: project/specs/handoff-progress-unification.md
---

# Guidelines sweep — review-checklist + git-conventions reference update

## Description

Per spec `handoff-progress-unification.md` (8.7), reword handoff-note references in two guideline files:

1. `ai-process/guidelines/review-checklist.md` — the Stage 1 line that currently reads "any file modified outside the task's Files to Touch list must be justified in the handoff note or it is a Fail" must be reworded to reference the Work Log instead of the handoff note. The rule itself is preserved; only the artifact name changes.
2. `ai-process/guidelines/git-conventions.md` — the commit cadence note saying "once more before handoff" becomes "once more before the final Work Log entry".

Do not modify any unrelated lines in either file.

## Acceptance Criteria

AC-1: The `review-checklist.md` Stage 1 out-of-list file rule shall reference the Work Log as the place where justification must appear, not the handoff note.
AC-2: The out-of-list file rule wording in `review-checklist.md` shall otherwise preserve its previous meaning (files modified outside Files to Touch without justification remain a Fail).
AC-3: The `git-conventions.md` commit cadence note shall reference "the final Work Log entry" in place of "handoff".
AC-4: Neither file shall retain the phrase "handoff note" after the sweep.
AC-5: No line in either file that is unrelated to handoff/Work Log wording shall be modified.
AC-6: The Exclusions soft-flag line introduced by T-003 shall remain present in `review-checklist.md` after this task.

## Dependencies

- `T-003` — earlier edit to `review-checklist.md` must land first to avoid conflicts
- `T-007` — task template Work Log section must exist so the reference is meaningful

## Files to Touch

- `ai-process/guidelines/review-checklist.md` — reword Stage 1 out-of-list file rule
- `ai-process/guidelines/git-conventions.md` — reword commit cadence note

## Verification

```bash
! grep -n 'handoff note' ai-process/guidelines/review-checklist.md
! grep -n 'handoff note' ai-process/guidelines/git-conventions.md
grep -n 'Work Log' ai-process/guidelines/review-checklist.md
grep -n 'Work Log' ai-process/guidelines/git-conventions.md
# Exclusions soft flag (T-003) still present
grep -n "Exclusions section is present" ai-process/guidelines/review-checklist.md
```

## Notes

Reference: spec 8.7, Component 5 (partial).

### Session 1 — 2026-04-18

Updated the review checklist Stage 1 out-of-list file rule to require justification in the Work Log while preserving the Fail outcome for unjustified files outside the Files to Touch list. Updated the git conventions implementer cadence row so the final extra commit is described as happening before the final Work Log entry.

Used command-line grep inspections as the red/green checks because this repository has no executable suite for these Markdown process files. The initial checks confirmed the stale review-checklist handoff-note wording and the stale git-conventions "before handoff" wording before each edit. I rejected broader cleanup or status-field edits because the task explicitly limits the guideline changes to handoff/Work Log wording and only requires this progress entry in the task file.

What remains: reviewer verification of the scoped diffs and acceptance criteria. The T-003 Exclusions soft-flag line remained present during verification.

## Review

<!-- Reviewer appends verdict here after each review cycle. -->

### Review Verdict — 2026-04-18

PASS

Stage 1 passed: all acceptance criteria are met. The review-checklist out-of-list file rule now references the Work Log while preserving the Fail condition, git-conventions now references the final Work Log entry, neither target file retains "handoff note", unrelated guideline lines were not modified, and the T-003 Exclusions soft-flag line remains present.

Stage 2 passed for this Markdown/process change. Visual diff inspection and command-line grep checks found no correctness, scope, or documentation-quality issues.
