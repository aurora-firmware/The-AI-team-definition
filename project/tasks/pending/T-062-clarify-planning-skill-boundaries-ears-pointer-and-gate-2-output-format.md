---
id: T-062
title: Clarify planning-skill boundaries, EARS pointer, and Gate 2 output format
status: pending
priority: medium
assigned-role: unassigned
created: '2026-06-04'
---

# Clarify planning-skill boundaries, EARS pointer, and Gate 2 output format

## Description

Source: `full_skills_review.md` issues I4, I10, I11. Edit the shared source bodies of
`spec-breakdown`, `new-task`, and `spec-breakdown-review`:

- **I4 (boundaries):** state each skill's single ownership boundary — spec-breakdown owns
  plan coverage / dependencies / task boundaries, new-task owns per-task shape,
  spec-breakdown-review owns Gate 2 technical readiness — and reference the owning skill for
  shared rules instead of restating them.
- **I10 (EARS):** make EARS references point to the task template
  (`cli/src/ai_team/templates/task.md`), not to "the new-task skill".
- **I11 (Gate 2 output format):** state that the architect role envelope wraps the
  spec-breakdown-review Findings block, with no duplicated Result/Summary fields.

(Brainstorm/new-spec content-boundary pointers are handled in T-064.)

## Acceptance Criteria

AC-1: Each of spec-breakdown, new-task, and spec-breakdown-review SHALL state its single
      ownership boundary and reference the owning skill for shared rules.
AC-2: EARS references in spec-breakdown and spec-breakdown-review SHALL point to the task
      template, not to "the new-task skill".
AC-3: The spec-breakdown-review output section SHALL state that the architect role envelope
      wraps its Findings block, with no duplicated Result/Summary fields.
AC-4: The spec-breakdown-review body SHALL include a spec-coverage check (the plan covers the
      whole spec) performed before the dependency and file-conflict checks (issue I7).

## Dependencies

- `B-008` — also edits `spec-breakdown-review/body.md` (new-adr contract); land first to avoid conflict

## Files to Touch

- `cli/src/ai_team/init/sources/skills/spec-breakdown/body.md` — boundary + EARS pointer
- `cli/src/ai_team/init/sources/skills/new-task/body.md` — per-task ownership boundary
- `cli/src/ai_team/init/sources/skills/spec-breakdown-review/body.md` — Gate 2 readiness + output format

## Verification

```bash
grep -niE "task template|templates/task" cli/src/ai_team/init/sources/skills/spec-breakdown/body.md
! grep -niE "documented in the .?new-task" cli/src/ai_team/init/sources/skills/spec-breakdown/body.md
grep -niE "architect|envelope|wraps" cli/src/ai_team/init/sources/skills/spec-breakdown-review/body.md
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
