---
id: T-087
title: TS lock entry in skeleton .gitignore; update B-017 tests and usage guide
status: pending
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# TS lock entry in skeleton .gitignore; update B-017 tests and usage guide

<!--
Task Quality Rules (see the new-task skill for full details):
  - Atomic — one clear outcome.
  - One-shottable — ≤ 3–4 files touched, ≤ 5 ACs, Description ≈ 20 lines.
  - Verifiable — concrete Verification command or explicit manual steps.
  - Self-contained — Description is enough to start without follow-up questions.
  - EARS — every AC matches one of the five EARS patterns below.
  - Dependency-honest — list every prior task this one reads from or modifies.
-->

## Description

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 1**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P10 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- choose the TS lock path inside the artifact dir, distinct from .ai-team.lock, entry matching file or directory; add to skeleton .gitignore; V-SYNC; update B-017 tests and usage.md (entry reserved for the pi package lock); regenerate command docs. T-109 consumes the path. Out of scope: TS lock implementation, Python flock (unchanged).

Size note (accepted at Gate 2, ruling 7): over guideline, SC-6 binds them, one-line edits.

## Acceptance Criteria

AC-1: skeleton .gitignore has both entries (SC-6, ADR-003).
AC-2: V-SYNC gives identical scaffolds/project/.gitignore.
AC-3: B-017 tests assert both entries.
AC-4: usage.md documents the TS entry.
AC-5: V-DOCS no unintended diff (SC-6).

## Dependencies

- `T-078` — Update the skill guide for the pi target and the marker contract
- `T-079` — Update the component map and system overview
- `T-080` — CLAUDE.md pi checks and setup-guide pi install steps

## Files to Touch

- cli/src/ai_team/init/sources/project/.gitignore
- scaffolds/project/.gitignore (generated)
- cli/tests/test_init_scaffolds.py
- test_init.py
- test_usage_guide.py
- cli/docs/usage.md

## Verification

```bash
# V-SYNC; V-PY; V-DOCS.
# V-SYNC: the sync command documented in CLAUDE.md's Build section (currently: cd cli && python scripts/sync_init_scaffolds.py)
# V-DOCS: bash cli/scripts/gen_docs.sh && git diff --exit-code cli/docs/commands.md
# V-PY: cd cli && uv run pytest && uv run ruff format --check . && uv run ruff check .   # set UV_CACHE_DIR under /tmp if uv cannot write its cache
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-09-30
I picked the TS lock path `.ai-team-ts.lock`, a bare name in `project/.gitignore`. Because it has no trailing slash it matches a file or a directory, so T-109 can implement either. It is distinct from Python's `.ai-team.lock`, which stays unchanged. I followed TDD. First I updated the B-017 tests in `test_init_scaffolds.py` and `test_init.py` to expect both entries, and added a `test_usage_guide.py` test that the TS entry is documented as reserved for the pi package lock. Three tests failed, as expected. Then I changed the source `.gitignore`, ran the scaffold sync so the generated copy is identical, and rewrote the `usage.md` sentinel section to describe both entries. The section now says the Python CLI never creates the TS entry and tells pre-existing projects to add both entries manually. The full pytest suite (545 tests), ruff format and ruff check pass. Regenerating `cli/docs/commands.md` produced no diff. I committed everything as `ca67f65`. Two small fixes along the way: a ruff reformat of `test_init.py`, and a line-wrap fix in `usage.md` so "pi package" stays on one line for the test. Nothing remains. The reviewer should confirm that the path name `.ai-team-ts.lock` is acceptable for T-109 and the parity fixtures. No fixtures currently reference the `.gitignore` content.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-09-30
PASS

Stage 1: AC-1 met (source and generated `project/.gitignore` contain `.ai-team.lock` and `.ai-team-ts.lock`). AC-2 met (re-running the sync in a clean worktree produced no diff; source and scaffold are byte-identical). AC-3 met (test_init.py, test_init_scaffolds.py assert both entries). AC-4 met (usage.md documents the entry as reserved for the pi package lock, with a new test). AC-5 met (gen_docs.sh produced no diff). The path `.ai-team-ts.lock` satisfies ADR-003 and S-005 "TS lock location": separate from `.ai-team.lock`, inside the project artifact directory, a bare name matching a file or directory, and listed in the skeleton .gitignore. No unintended files touched.

Stage 2: pytest 545 passed, ruff format and ruff check clean. Tests are independent and exact-match.

Non-blocking observations: no parity fixtures or pi sources reference the .gitignore content, so no fixture change is needed here. The spec says the fixtures record the skeleton change, so T-109 or the pi init task should cover it when the TS init is implemented. T-109 should consume `.ai-team-ts.lock`.
