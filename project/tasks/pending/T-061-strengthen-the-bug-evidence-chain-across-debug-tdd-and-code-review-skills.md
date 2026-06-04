---
id: T-061
title: Strengthen the bug evidence chain across debug, tdd, and code-review
  skills
status: pending
priority: medium
assigned-role: unassigned
created: '2026-06-04'
---

# Strengthen the bug evidence chain across debug, tdd, and code-review skills

## Description

Source: `full_skills_review.md` issues I2, I12, I14. Edit the shared source skill bodies:

- **I2 (evidence chain):** make `debug` diagnosis-only and require a fix contract (isolated
  fault + planned fix + planned verification) in the Diagnosis Log before any production code
  change; make `tdd` consume that contract as the implementation target; make `code-review`
  return FAIL when the diagnosis→fix evidence chain is missing rather than inferring intent
  from the diff.
- **I12 (checklist ownership):** make the `code-review` body the canonical home of the
  two-stage review checklist (Stage 1, Stage 2, Bug Fix Addendum). The role files reference it
  (role updates are T-065).
- **I14 (regression evidence):** make `new-bug` require evidence, `source_branch`,
  expected/actual behaviour, and fix-verification for integration-filed regression bugs.

## Acceptance Criteria

AC-1: The `debug` skill SHALL be diagnosis-only and require a fix contract (isolated fault,
      planned fix, planned verification) in the Diagnosis Log before any production code change.
AC-2: The `tdd` skill SHALL consume the diagnosis fix contract as its implementation target for
      bug fixes.
AC-3: IF a bug fix lacks a complete diagnosis→fix evidence chain, THEN `code-review` SHALL
      return FAIL rather than infer intent from the diff.
AC-4: The `code-review` body SHALL contain the canonical two-stage review checklist (Stage 1,
      Stage 2, Bug Fix Addendum).
AC-5: The `new-bug` skill SHALL require evidence, `source_branch`, expected/actual behaviour,
      and fix-verification for integration-filed regression bugs.

## Dependencies

- `T-059` — quality-gates Gate 3 bug addendum must define the evidence chain first

## Files to Touch

- `cli/src/ai_team/init/sources/skills/debug/body.md` — diagnosis-only + fix contract
- `cli/src/ai_team/init/sources/skills/tdd/body.md` — consume the fix contract
- `cli/src/ai_team/init/sources/skills/code-review/body.md` — canonical checklist + evidence-chain gate
- `cli/src/ai_team/init/sources/skills/new-bug/body.md` — regression evidence fields

## Verification

```bash
grep -niE "fix contract|diagnosis only|diagnosis-only" cli/src/ai_team/init/sources/skills/debug/body.md
grep -niE "evidence chain|diagnosis" cli/src/ai_team/init/sources/skills/code-review/body.md
grep -niE "two-stage|stage 1|stage 2|bug fix addendum" cli/src/ai_team/init/sources/skills/code-review/body.md
grep -niE "source.branch|fix.verification|expected" cli/src/ai_team/init/sources/skills/new-bug/body.md
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
