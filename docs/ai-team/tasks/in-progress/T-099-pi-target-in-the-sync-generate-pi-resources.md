---
id: T-099
title: Pi target in the sync; generate pi/resources/
status: in-progress
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Pi target in the sync; generate pi/resources/

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 2**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P22 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- write pi/resources/skills/<name>/SKILL.md for every skill (incl. orchestrators); pi/resources/skill-calls/<name>.json (call-form inputs for T-123); artifact templates, project skeleton (incl. .gitignore and leaf dirs), root guidance templates; claude/codex scaffold dir list for check-layout Level 1; copy of command map; git-ignored version file (pi/.gitignore) computed from the source tree via hatch-vcs, not installed metadata; fail if undeterminable. Claude/codex output unchanged. [G2 B1] The fake-repo tests in test_init_scaffolds.py set the version override (or SETUPTOOLS_SCM_PRETEND_VERSION) and one test asserts the "cannot determine version" failure. [G2 N2] The sync still runs under bare `python`: either compute the version without new imports (for example a subprocess to hatch), or switch the documented command to `uv run python scripts/sync_init_scaffolds.py` and update CLAUDE.md's Build section and cli/docs/usage.md's maintainer section accordingly. Out of scope: package.json, TS code, skill conversions.

## Acceptance Criteria

AC-1: V-SYNC produces all listed outputs (Component 2).
AC-2: version file git-ignored and equal to source-tree hatch-vcs version (Config, ADR-004).
AC-3: undeterminable version fails with clear message, asserted by a test (B1).
AC-4: two syncs leave no committed diff; V-GOLD passes (SC-2).
AC-5: the version equals what hatch/setuptools-scm reports with cli/pyproject.toml's raw-options (root "..", tag_regex). [G2 N2]

## Dependencies

- `T-080` — CLAUDE.md pi checks and setup-guide pi install steps
- `T-087` — TS lock entry in skeleton .gitignore; update B-017 tests and usage guide
- `T-097` — Move raw-body/raw-header test assertions to rendered output
- `T-098` — Pi marker rendering and derived pi headers

## Files to Touch

- cli/scripts/sync_init_scaffolds.py
- pi/.gitignore
- pi/resources/** (generated)
- new cli/tests/test_sync_pi_target.py
- cli/tests/test_init_scaffolds.py [G2 B1]
- possibly cli/pyproject.toml
- cli/uv.lock
- CLAUDE.md and cli/docs/usage.md [G2 N2]

## Verification

```bash
# V-SYNC twice; git status --porcelain pi/ cli/src (empty after commit); V-GOLD; V-PY.
# V-SYNC: the sync command documented in CLAUDE.md's Build section (currently: cd cli && python scripts/sync_init_scaffolds.py)
# V-GOLD: git diff --exit-code "$(git merge-base HEAD main)" -- cli/src/ai_team/init/scaffolds/claude cli/src/ai_team/init/scaffolds/codex
# V-PY: cd cli && uv run pytest && uv run ruff format --check . && uv run ruff check .   # set UV_CACHE_DIR under /tmp if uv cannot write its cache
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
