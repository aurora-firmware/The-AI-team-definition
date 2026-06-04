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

### Session 1 — 2026-06-04

Implemented T-061 in a single TDD session covering all five acceptance criteria.

Started by reading the task file and the Work Log (empty, first session). Read the current bodies of all four target skill files (debug, tdd, code-review, new-bug) to understand the starting state.

Wrote a single test file (`cli/tests/test_bug_evidence_chain.py`) with 23 tests covering AC-1 through AC-5 before touching any source file. Confirmed 13 tests failed (the ones testing for new content) and 10 already passed (testing for phrases already present in the current bodies).

**Implementation decisions:**

- **debug (AC-1):** Removed Steps 6 and 7 (fix and verify) entirely, replacing them with a clear diagnosis-only declaration at the top of the file. Step 5 was rewritten as a "Diagnosis Handoff (Fix Contract)" section that explicitly names the five fields: reproduction status, evidence captured, isolated fault, planned fix, and planned verification. The body now ends at Step 5 with "Stop here. Do not change production code in this skill."

- **tdd (AC-2):** Extended Step 0 to require verifying the fix contract is complete before proceeding, and updated the Step 1 note on bug fixes to explicitly reference using the fix contract as the implementation target. This was the minimal change; the existing "If no Diagnosis Log exists, stop" language was preserved and extended rather than rewritten.

- **code-review (AC-3 + AC-4):** Added an explicit evidence chain verification gate at the end of Step 1 (before Stage 1), with a direct instruction to return FAIL and not infer intent from the diff when the chain is missing. The Stage 2 checklist and Bug Fix Addendum were inlined as canonical content in the body (previously they deferred to "the Reviewer role's quality bar"), satisfying AC-4. The "two-stage checklist" phrase was added to the intro paragraph.

- **new-bug (AC-5):** Added a "For integration-filed regression bugs" block to the Input Requirements section, listing source_branch, expected, actual, evidence, and fix_verification as required fields. Added a Step 6 to the Procedure to populate those fields after creating the bug file.

Ran `python3 cli/scripts/sync_init_scaffolds.py` to regenerate all eight scaffolds (claude + codex for each skill). All 315 tests pass. All four task verification greps return matches. Ruff format and lint clean.

No files were touched outside the four source bodies, their generated scaffolds, and the new test file. All within the task's `Files to Touch` scope.

Nothing remains for the next session; the task is complete.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-06-04

PASS

**Stage 1 — Spec compliance:** All five acceptance criteria are met.

- AC-1: `debug/body.md` declares itself diagnosis-only in the opening paragraph, adds a Step 5 "Diagnosis Handoff (Fix Contract)" section requiring all five contract fields (reproduction status, evidence captured, isolated fault, planned fix, planned verification), and explicitly instructs the agent to stop before changing production code.
- AC-2: `tdd/body.md` Step 0 now requires verifying the fix contract is complete before proceeding, and Step 1 instructs the agent to use the fix contract as the implementation target for bug fixes.
- AC-3: `code-review/body.md` adds an evidence chain verification gate in Step 1, with an explicit FAIL return and "do not infer intent from the diff" instruction.
- AC-4: `code-review/body.md` contains the canonical Stage 1, Stage 2, and Bug Fix Addendum checklists inline. The intro paragraph references "the two-stage checklist below" as the canonical quality bar.
- AC-5: `new-bug/body.md` adds a regression bug block in Input Requirements (source_branch, expected, actual, evidence, fix_verification) and adds Step 6 to populate those fields.

All four verification greps from the task return matches. No files outside the stated `Files to Touch` scope were modified (13 files total: 4 source bodies, 8 regenerated scaffolds, 1 new test file — all within scope or explicitly generated).

**Stage 2 — Code quality:** All checks pass.

- Correctness: skill bodies are procedural Markdown; logic in the new procedural gates is sound and consistent across debug, tdd, and code-review.
- Tests: `cli/tests/test_bug_evidence_chain.py` — 23 tests covering all five ACs, success paths for each field, and scaffold propagation for both claude and codex tools. Tests are independent and deterministic. All 23 pass.
- Full suite: 315/315 tests pass (`uv run pytest` from `cli/`).
- Lint/format: `ruff format --check` and `ruff check` both clean.
- Source-of-truth convention: sources were edited first; scaffolds were regenerated via `python3 cli/scripts/sync_init_scaffolds.py`, not hand-edited. Scaffold content matches source content.
- Security, readability, performance: not applicable to Markdown skill bodies; test file has no secrets, dead code, or resource leaks.

No non-blocking observations.
