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

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
