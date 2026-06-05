---
id: T-063
title: Add committed-PASS gate, lifecycle protection, and safe branch deletion
  to integration
status: completed
priority: medium
assigned-role: unassigned
created: '2026-06-04'
---

# Add committed-PASS gate, lifecycle protection, and safe branch deletion to integration

## Description

Source: `full_skills_review.md` issues I3, I15. Edit the shared source bodies of `integrate`,
`dev-loop`, and `bug-loop`:

- **I3 (integration evidence):** `integrate` must verify the latest committed canonical PASS
  verdict on `dev-agent` before merging, require committed Developer handoffs, and reject
  lifecycle-file edits arriving on implementation branches; the loops must record committed
  handoffs and verdicts on `dev-agent` before integration.
- **I15 (safe deletion):** replace `integrate`'s routine forced-delete (`git branch -D`)
  fallback with stop-and-report (aligns with the guideline in T-060).

## Acceptance Criteria

AC-1: BEFORE merging, `integrate` SHALL verify that the latest committed canonical Review
      Verdict on `dev-agent` is PASS.
AC-2: The existing lifecycle-file guard (integrate stops when an implementation branch edits a
      canonical lifecycle file — already present in source) SHALL be retained and verified.
AC-3: WHEN `git branch -d` is refused, `integrate` SHALL stop and report instead of running
      `git branch -D`.
AC-4: dev-loop and bug-loop SHALL record committed Developer handoffs and Review Verdicts on
      `dev-agent` before invoking integration.

## Dependencies

- `T-059` — Gate 4 committed-PASS precondition defined in quality-gates first
- `T-060` — git-conventions guideline forbids forced deletion first
- `B-010` — also edits `dev-loop/body.md` and `bug-loop/body.md`; land first to avoid conflict

## Files to Touch

- `cli/src/ai_team/init/sources/skills/integrate/body.md` — committed-PASS gate, lifecycle guard, safe delete
- `cli/src/ai_team/init/sources/skills/dev-loop/body.md` — committed-evidence precondition
- `cli/src/ai_team/init/sources/skills/bug-loop/body.md` — committed-evidence precondition

## Verification

```bash
grep -niE "committed.*(pass|verdict)" cli/src/ai_team/init/sources/skills/integrate/body.md
grep -niE "lifecycle" cli/src/ai_team/init/sources/skills/integrate/body.md
! grep -nE "branch -D" cli/src/ai_team/init/sources/skills/integrate/body.md
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-06-04

Implemented all four acceptance criteria for T-063 in a single TDD cycle.

**What was done:**

For AC-1, inserted a new "Step 2b" in `integrate/body.md` that requires the Integrator to read the canonical work item's `## Review` section on `dev-agent`, extract the most recent Review Verdict, and stop with a clear error if the committed verdict is not PASS (or missing). The step is positioned after reading the work item file (Step 2) and before checking out the source branch (Step 3), so the verdict check happens entirely on `dev-agent` before any branch checkout.

For AC-2, verified the existing lifecycle-file guard in Step 3 (line 67 of the original source) was already present and intentionally not touched, as required.

For AC-3, replaced the `git branch -D` forced-delete fallback block in Step 7 with stop-and-report language. The instruction now says "Forced deletion is forbidden — do not escalate to the `-D` flag" and tells the Integrator to report the error and instruct the human to delete the branch manually. The literal string `branch -D` was carefully avoided in the instruction text to satisfy the negative grep verification command.

For AC-4, added an explicit pre-integration precondition paragraph to the "On PASS" handler in both `dev-loop/body.md` and `bug-loop/body.md`. Both paragraphs name the specific committed artifacts that must exist on `dev-agent` (Work Log, Review Verdict, and in bug-loop's case, also the Diagnosis Log) before `integrate` is invoked, and they cross-reference the fact that `integrate` will verify the committed PASS verdict.

Scaffolds were regenerated with `python3 cli/scripts/sync_init_scaffolds.py` after each source edit, as required by CLAUDE.md. Lint was clean after `ruff format` auto-formatted the new test file.

**What was tried and rejected:**

An initial attempt to phrase the AC-3 prohibition as "Do not use `git branch -D`" was rejected because it leaves the literal pattern `branch -D` in the body, which the task's negative grep verification would reject. Rewrote as "do not escalate to the `-D` flag" to express the same constraint without the forbidden string.

**What remains:**

Nothing. All 4 ACs have passing tests, the three task verification commands pass, and the full test suite (334 tests) is green.

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

Both Stage 1 (spec compliance) and Stage 2 (code quality) passed.

**Stage 1 — Acceptance Criteria**

- AC-1: integrate/body.md gains Step 2b at line 46, requiring the integrator to read the `## Review` section on `dev-agent`, extract the latest verdict, and stop if it is not PASS. The task verification grep (`grep -niE "committed.*(pass|verdict)"`) returns five matching lines. Both claude and codex scaffolds carry the same language. Met.
- AC-2: The lifecycle-file guard (Step 3, line 67) was intentionally left untouched. `grep -niE "lifecycle"` returns matches at lines 25, 67, 226, 234, 241, and 251. Met.
- AC-3: `! grep -nE "branch -D"` returns no matches in the source or in either scaffold. The stop-and-report block in Step 7 instructs the integrator that "Forced deletion is forbidden — do not escalate to the `-D` flag" and to ask the human to delete manually. Met.
- AC-4: dev-loop/body.md has the "On PASS" precondition paragraph at line 131–133 requiring committed Work Log and Review Verdict before calling integrate. bug-loop/body.md has an equivalent paragraph at line 123–125 also requiring the committed Diagnosis Log. Met.

**Stage 2 — Code Quality**

- Correctness: Step 2b is positioned between Step 2 (read work item on dev-agent) and Step 3 (check out source branch), which is the correct gate point. The stop condition covers both missing verdict and non-PASS verdict.
- Tests: `cli/tests/test_t063_integration_guards.py` covers all four ACs across source and both scaffolds (claude, codex). Tests cover both positive (content present) and negative (`branch -D` absent) paths. All 334 tests pass (`uv run pytest` from `cli/`).
- Source-of-truth convention: sources edited first, scaffolds regenerated via `sync_init_scaffolds.py`, not hand-edited. Diff confirms only source bodies and their regenerated scaffolds changed, plus the new test file.
- Files modified are exactly the three sources listed in "Files to Touch" plus their two scaffold copies and the test file. No out-of-scope files were modified.
- No dead code, hardcoded secrets, or readability issues observed.
- The task lifecycle file is correctly absent from the implementation branch (Work Log committed only on `dev-agent`).
