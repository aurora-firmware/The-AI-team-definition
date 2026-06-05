---
id: T-062
title: Clarify planning-skill boundaries, EARS pointer, and Gate 2 output format
status: completed
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

### Session 1 — 2026-06-04

Implemented all four acceptance criteria for T-062 in a single TDD cycle.

**What was done:**

- Read the task file and all three source skill bodies before writing a line of code.
- Wrote nine new failing tests in `cli/tests/test_init_scaffolds.py` — three for AC-1 (one per skill), two for AC-2 (spec-breakdown and spec-breakdown-review EARS pointers), two for AC-3 (architect envelope + no-duplicate fields), and two for AC-4 (spec-coverage check present, ordering before dependency/conflict steps).
- Verified all nine tests failed before touching sources.
- Edited `cli/src/ai_team/init/sources/skills/spec-breakdown/body.md`: added an ownership boundary block at the top stating spec-breakdown owns plan coverage, dependencies, and task boundaries; changed the EARS reference from "the `new-task` skill" to "the task template (`cli/src/ai_team/templates/task.md`)".
- Edited `cli/src/ai_team/init/sources/skills/new-task/body.md`: added an ownership boundary block at the top stating new-task owns per-task shape and references spec-breakdown and spec-breakdown-review for their respective scopes.
- Edited `cli/src/ai_team/init/sources/skills/spec-breakdown-review/body.md`: added ownership boundary block at top (references task template for EARS); inserted new Step 2 "Check Spec Coverage" before the dependency check (shifting Steps 2–6 to Steps 3–7); updated the Output Format section to explicitly state the architect envelope wraps the Findings block with no duplicated Result/Summary fields.
- Ran `python3 cli/scripts/sync_init_scaffolds.py` to regenerate all six scaffold files.
- All three task verification greps pass. Full suite: 324 tests pass. Ruff format and lint clean.
- One intermediate issue: a case-sensitivity mismatch (`"no duplicated Result"` vs `"No duplicated Result/Summary fields:"`) was caught on first test run; fixed by adjusting the implementation text to use lowercase at sentence-internal position.

**What was tried and rejected:**

- Initially used "new-task enforces per-task shape" as the test phrase for AC-1 on new-task, but that phrase uses backtick-wrapped `` `new-task` `` in the existing text which would never match. Added an explicit ownership boundary sentence ("new-task owns") to the source instead.

**What remains:**

Nothing — all ACs implemented and verified.

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

Stage 1 — Spec compliance: all four acceptance criteria are satisfied.

- AC-1: Each of spec-breakdown, new-task, and spec-breakdown-review contains an explicit
  "Ownership boundary:" block at the top of its body. spec-breakdown states it owns plan
  coverage/dependencies/task boundaries and references new-task and spec-breakdown-review
  for their scopes. new-task states it owns per-task shape and references spec-breakdown
  for plan-level rules and spec-breakdown-review for Gate 2 readiness. spec-breakdown-review
  states it owns Gate 2 technical readiness. Met.
- AC-2: spec-breakdown EARS reference now points to "the task template
  (`cli/src/ai_team/templates/task.md`)". The negative verification grep confirms no
  "documented in the new-task skill" text remains (grep exits 1). spec-breakdown-review
  similarly references "the task template". Met.
- AC-3: spec-breakdown-review Output Format section explicitly states the architect role
  envelope wraps the Findings block and directs authors not to add a top-level Result:/Summary:
  outside that block. Met.
- AC-4: "Check Spec Coverage" is Step 2 in spec-breakdown-review, inserted before
  "Check Dependency Correctness" (Step 3) and "Check File Conflict Risk" (Step 4). Met.

All three task verification greps pass, including the negative grep (exit code 1, no match).

Stage 2 — Code quality: all checks pass.

- Sources edited first; scaffolds regenerated via sync_init_scaffolds.py; no scaffold was
  hand-edited (source-of-truth-first convention followed).
- 9 new tests added covering AC-1 through AC-4, with both positive assertions and the
  forbidden-phrase negative assertion for AC-2. Tests are independent and focused.
- Full suite: 324 tests pass. Ruff format and lint clean.
- No dead code, hardcoded secrets, or unrelated behavior added.
- Only the three source bodies, their six scaffold counterparts, the test file, and the task
  file were modified — all within the stated scope.
