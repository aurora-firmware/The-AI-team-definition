---
id: T-065
title: Update Claude agent role files to the reviewed state in source
status: completed
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

### Session 1 — 2026-06-04

Read the canonical task file first and confirmed the Work Log was empty. I translated the four acceptance criteria into focused source/scaffold regression tests in `cli/tests/test_t065_claude_agent_role_files.py`: planner retains `change-request`, reviewer points to the `code-review` canonical two-stage checklist without inlining it, architect names the Gate 2 Findings block as wrapped by the role envelope without duplicating Result/Summary fields, and all five Claude role files use the frozen escalation request block. The initial targeted test run failed as expected for reviewer checklist ownership, architect Gate 2 wording, and escalation wording.

I then updated the five Claude role source files, removed the inline reviewer checklist in favor of a short `code-review` pointer, added the architect Gate 2 envelope sentence, and aligned all role escalation blocks to the canonical frozen wording from `escalation-review`. I regenerated scaffolds with `python3 scripts/sync_init_scaffolds.py` after the documented `python` command failed because `python` is not installed in this environment. I rejected editing generated scaffolds directly; all scaffold changes came from the sync script.

Verification passed: the task grep commands found `change-request` in planner and `code-review` in reviewer, the targeted T-065 tests passed, full `uv run pytest` passed with 357 tests, `ruff format --check .` and `ruff check .` passed after formatting the new test file, and `uv build` passed after approved network access for PyPI build dependencies. The implementation was committed on the task branch as `c135719 docs(agents): align claude role files`. Nothing remains for the Developer; ready for Reviewer handoff.

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

Stage 1 acceptance passed. The implementation branch keeps `change-request` in the Claude planner skill surfaces, replaces the Claude reviewer inline checklist with ownership language pointing to the `code-review` skill, adds the reconciled Gate 2 envelope wording to the Claude architect role, and aligns the escalation request block across architect, developer, integrator, planner, and reviewer. The diff is scoped to the expected Claude source role files, regenerated Claude scaffold files, and focused T-065 regression tests.

Stage 2 quality passed. The new tests directly cover all four acceptance criteria against both source and scaffold files, and source/scaffold pairs for all five Claude roles are byte-for-byte aligned. No unrelated behavior, secrets, runtime code paths, or generated-source divergence were found.

Evidence reviewed: `git diff dev-agent...task/T-065-update-claude-agent-role-files`, source/scaffold parity checks for all five Claude roles, `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_t065_claude_agent_role_files.py` (4 passed), `UV_CACHE_DIR=/tmp/uv-cache uv run pytest` (357 passed), `UV_CACHE_DIR=/tmp/uv-cache uv run ruff format --check .` (passed), and `UV_CACHE_DIR=/tmp/uv-cache uv run ruff check .` (passed).
