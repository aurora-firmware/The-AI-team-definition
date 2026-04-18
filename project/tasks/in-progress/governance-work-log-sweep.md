---
id: "T-015"
title: "Governance surface — CLAUDE.md + README + setup-guide sweep"
status: pending
priority: medium
assigned-role: implementer
created: 2026-04-18
spec: project/specs/handoff-progress-unification.md
---

# Governance surface — CLAUDE.md + README + setup-guide sweep

## Description

Per spec `handoff-progress-unification.md` (8.7), reword handoff-note references in three governance-surface documents:

1. `CLAUDE.md` — the repository-map row that currently reads "Reusable document formats: handoff notes (used when implementer hands off to reviewer)" must be reworded. Since the handoff-note template is being deleted by T-016, the `ai-process/templates/` row should either be removed (if `templates/` ends up empty after the deletion) or reworded to describe what remains. Verify whether `ai-process/templates/` retains any files after T-016 before choosing wording.
2. `CLAUDE.md` Task Lifecycle table — the rows for `in-progress/ → blocked/` and `blocked/ → in-progress/` currently describe the blocker and the resolution as being "described in Notes section" / "resolution noted in Notes section." After the Work Log sweep, the task-file vocabulary is Description / Acceptance Criteria / Dependencies / Files to Touch / Verification / Work Log / Review. Reword these two rows so the blocker description and the resolution are recorded in the Work Log, not the Notes section.
3. `README.md` — the bullet under the `templates/` section that mentions handoff notes must be reworded or removed based on the same verification.
4. `guides/setup-guide.md` — the copy-list for new projects must omit `handoff-note.md` and any instruction to copy it.

## Acceptance Criteria

AC-1: The `CLAUDE.md` repository-map row for `ai-process/templates/` shall no longer describe handoff notes.
AC-2: IF `ai-process/templates/` will be empty after T-016 THEN `CLAUDE.md` shall either remove the row or reword it to reflect the empty-folder status.
AC-3: The `README.md` file shall no longer describe handoff notes in its templates section.
AC-4: The `guides/setup-guide.md` file shall not instruct the reader to copy `handoff-note.md` or any similar handoff-note artifact.
AC-5: Every file touched shall retain coherent prose after the removal or reword — no dangling bullets, broken sentences, or orphan references.
AC-6: No reference to `handoff-note.md` shall remain in any of these three files.
AC-7: The Task Lifecycle table in `CLAUDE.md` shall reference the Work Log, not the Notes section, when describing where blocker descriptions and blocker resolutions are recorded (rows `in-progress/ → blocked/` and `blocked/ → in-progress/`).

## Dependencies

- `T-007` — task template must carry Work Log to give the governance docs a coherent story
- `T-008` — bug template must carry Work Log for the same reason

## Files to Touch

- `CLAUDE.md` — repository-map row for `ai-process/templates/`
- `README.md` — `templates/` bullet
- `guides/setup-guide.md` — copy-list for new projects

## Verification

```bash
for f in CLAUDE.md README.md guides/setup-guide.md; do
  if grep -nE 'handoff-note\.md|handoff note|handoff notes' "$f"; then
    echo "FAIL: residual reference in $f"; exit 1
  fi
done
# Lifecycle table rows point at the Work Log, not the Notes section
! grep -n 'Notes section' CLAUDE.md
grep -nE 'blocker .*Work Log|Work Log.*blocker|resolution .*Work Log|Work Log.*resolution' CLAUDE.md
```

## Notes

Reference: spec 8.7, Component 5 (partial).

### Session 1 — 2026-04-18

Implemented the governance sweep for the three scoped documents.
I first verified the existing Work Log state, the acceptance criteria, and the current `ai-process/templates/` contents.
`ai-process/templates/` currently contains only `handoff-note.md`, and T-016 is expected to delete that file next, so I removed the `CLAUDE.md` repository-map row instead of rewording it as an active templates surface.
I also removed the handoff-note copy-list item from `guides/setup-guide.md` and reworded the `README.md` templates bullet to describe the directory as reserved for reusable formats not tied to a skill.

For the lifecycle criterion, I changed the `CLAUDE.md` `in-progress/ -> blocked/` and `blocked/ -> in-progress/` rows so blocker descriptions and resolutions are recorded in the Work Log rather than the Notes section.
I used command-line inspections as the red/green checks: the handoff-note grep failed before the first edit and passed after it; the lifecycle grep failed while the rows still referenced Notes and passed after the Work Log wording.
The final verification command from the task passes.

Two implementation commits were created: `12ff6d9` for removing handoff-note references from the governance docs, and `39ed098` for pointing the blocker lifecycle rows to the Work Log.
What remains is reviewer validation and T-016's planned deletion of `ai-process/templates/handoff-note.md`.

## Review

<!-- Reviewer appends verdict here after each review cycle. -->

### Review Verdict — 2026-04-18

PASS

Stage 1 passed: all acceptance criteria were checked against the scoped document changes.
`CLAUDE.md` no longer describes handoff notes in the repository map, the lifecycle blocker rows now point to the Work Log, `README.md` no longer describes handoff notes in the templates section, and `guides/setup-guide.md` no longer instructs copying `handoff-note.md`.
The only extra touched file is this task file for Work Log and review documentation.

Stage 2 passed for this Markdown/process change: visual diff inspection found coherent prose and no dangling bullets or orphan references.
Command-line checks passed: `git diff --check dev...HEAD`, residual handoff-reference grep across the three scoped files, and the lifecycle Work Log grep.
