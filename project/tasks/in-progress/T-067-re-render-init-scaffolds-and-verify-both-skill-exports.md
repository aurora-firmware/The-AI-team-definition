---
id: T-067
title: Re-render init scaffolds and verify both skill exports
status: pending
priority: medium
assigned-role: unassigned
created: '2026-06-04'
---

# Re-render init scaffolds and verify both skill exports

## Description

Source: `full_skills_review.md` §5 (remediation step 5–6). After all source edits land,
regenerate the init scaffolds and confirm both exports re-converge. Run
`python cli/scripts/sync_init_scaffolds.py`; run the test suite and linters; refresh the
`claude_skills/` and `codex_skills/` working copies from the regenerated scaffolds so they are
consistent with source; run `bash cli/scripts/gen_docs.sh` if command output changed. This is
the final task — it depends on every source-editing task and bug in this batch.

## Acceptance Criteria

AC-1: WHEN all source edits are merged, the init scaffolds SHALL be regenerated via
      `sync_init_scaffolds.py` with no uncommitted scaffold drift remaining.
AC-2: The full test suite (`uv run pytest`) and linters (`ruff format --check`, `ruff check`)
      SHALL pass.
AC-3: The `claude_skills/` and `codex_skills/` exports SHALL match the regenerated scaffolds
      (no divergence from source).

## Dependencies

- `T-058`
- `T-059`
- `T-060`
- `T-061`
- `T-062`
- `T-063`
- `T-064`
- `T-065`
- `T-066`
- `T-068`
- `B-008`
- `B-010`

## Files to Touch

- `cli/src/ai_team/init/scaffolds/` — regenerated (do not hand-edit)
- `claude_skills/` — refreshed from scaffolds
- `codex_skills/` — refreshed from scaffolds

## Verification

```bash
cd cli && UV_CACHE_DIR=/tmp/uv-cache python scripts/sync_init_scaffolds.py
cd cli && UV_CACHE_DIR=/tmp/uv-cache uv run pytest
cd cli && UV_CACHE_DIR=/tmp/uv-cache uv run ruff format --check . && UV_CACHE_DIR=/tmp/uv-cache uv run ruff check .
git -C .. status --short   # expect no unexpected scaffold drift
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-06-05

This was a verification-only task. All predecessor tasks (T-058 through T-066, T-068, B-008, B-010) had already merged into the branch, so the main job was to confirm the scaffold sync, tests, and linters all remained green with no remaining drift.

**AC-1:** Ran `python3 scripts/sync_init_scaffolds.py` from `cli/` — script completed cleanly and `git status --short` showed a completely clean working tree. No scaffold drift existed.

**AC-2:** Ran the full pytest suite (371 tests, all passed in 1.76s). Both ruff format check and ruff lint check passed with zero issues.

**AC-3 (with architecture caveat):** The task's text references root-level `claude_skills/` and `codex_skills/` directories that no longer exist. These were deleted during the T-035/T-036 refactor which moved the framework to package-owned scaffolds. In the current architecture, the two skill exports are `cli/src/ai_team/init/scaffolds/claude/` and `cli/src/ai_team/init/scaffolds/codex/`, both of which contain 18 skills each and converge fully with source after sync. No recreation of the deleted root-level directories was done or warranted.

**gen_docs.sh:** Ran `bash cli/scripts/gen_docs.sh` to check if CLI command help output changed across the batch. It produced no changes to `cli/docs/commands.md`, consistent with the expectation that T-066 (ADR via existing command) and T-068 (skill-body prose) did not alter CLI command output.

No commits were needed — the branch was already clean and the sync produced no drift. This task's deliverable is the verification evidence itself; the branch carries no diff against `dev-agent`.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-06-05

PASS

Both stages passed. This was a verification-only task with no code diff; the Reviewer independently re-ran all checks:

**Stage 1 — Acceptance Criteria:**

- AC-1: `python3 scripts/sync_init_scaffolds.py` ran cleanly from `cli/`. `git status --short` from repo root showed a completely clean working tree. No scaffold drift exists.
- AC-2: `uv run pytest` collected and passed all 371 tests (1.73s). `uv run ruff format --check .` reported 55 files already formatted. `uv run ruff check .` reported all checks passed.
- AC-3: Both `cli/src/ai_team/init/scaffolds/claude/skills/` and `cli/src/ai_team/init/scaffolds/codex/skills/` exist and each contain the same 18 skills that match the source tree under `cli/src/ai_team/init/sources/skills/`. The root-level `claude_skills/` and `codex_skills/` directories referenced in the task text do not exist — they were deleted in the T-035/T-036 package-owned-scaffold refactor. Interpreting AC-3 against the package-owned scaffold trees is a faithful reading: the intent ("both skill format exports converge with source") is satisfied, the Developer documented the architecture caveat clearly in the Work Log, and this is a pre-existing wording artifact in the task rather than a gap introduced by the Developer. No ESCALATE is warranted.
- gen_docs.sh: `bash cli/scripts/gen_docs.sh` produced no changes to `cli/docs/commands.md`; tree remained clean.

**Stage 2 — Code Quality:** Not applicable — this task produced no code changes. The deliverable is verification evidence only.

No issues found. Task is complete.
