---
id: T-065
title: Update Claude agent role files to the reviewed state in source
status: pending
priority: medium
assigned-role: unassigned
created: '2026-06-04'
---

# Update Claude agent role files to the reviewed state in source

## Description

Source: `full_skills_review.md` P1 (Claude side) and the role pointers for I9/I11/I12. Bring
the source Claude role files (`cli/src/ai_team/init/sources/agents/claude/*.md`) to the
reviewed state already applied in the `claude_skills/` export: the planner gains `change-request`
in its skills list (I9); the reviewer references the `code-review` canonical checklist instead of
inlining it (I12); the architect wording is consistent with the reconciled Gate 2 output format
(I11); all five roles use the canonical escalation request wording. Four of the five edits are
small pointer/wording changes; the planner and reviewer carry the substantive ones.

## Acceptance Criteria

AC-1: The planner role file SHALL list `change-request` among its skills (already present in
      source `claude/planner.md` — verify retained).
AC-2: The reviewer role file SHALL reference the `code-review` skill's two-stage checklist
      instead of inlining the full checklist.
AC-3: The architect role file SHALL be consistent with the reconciled Gate 2 output format.
AC-4: All five Claude role files SHALL use the canonical escalation request wording.

## Dependencies

- `T-061` — `code-review` must be the canonical checklist before the reviewer points to it
- `T-062` — Gate 2 output format reconciled before the architect role aligns

## Files to Touch

- `cli/src/ai_team/init/sources/agents/claude/planner.md` — add `change-request` skill
- `cli/src/ai_team/init/sources/agents/claude/reviewer.md` — reference `code-review` checklist
- `cli/src/ai_team/init/sources/agents/claude/architect.md` — Gate 2 output format wording
- `cli/src/ai_team/init/sources/agents/claude/developer.md` — escalation wording
- `cli/src/ai_team/init/sources/agents/claude/integrator.md` — escalation wording

## Verification

```bash
grep -n "change-request" cli/src/ai_team/init/sources/agents/claude/planner.md
grep -niE "code-review" cli/src/ai_team/init/sources/agents/claude/reviewer.md
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
