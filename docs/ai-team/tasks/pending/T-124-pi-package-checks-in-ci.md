---
id: T-124
title: Pi package checks in CI
status: pending
priority: medium
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Pi package checks in CI

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 4**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P47 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- new job: Python and uv, V-SYNC (existing SETUPTOOLS_SCM_PRETEND_VERSION pattern acceptable); fail if `git diff --exit-code -- cli/src/ai_team/init/scaffolds pi/resources`; Node at manifest minimum or higher; npm ci, npm run typecheck, npm test in pi/; existing jobs unchanged. Out of scope: npm publishing.

## Acceptance Criteria

AC-1: PRs run pi typecheck and tests after a fresh sync (SC-13).
AC-2: sync changing a committed generated file fails the job.
AC-3: existing lint/test/release jobs unchanged.

## Dependencies

- `T-122` — ai_team tool adapter
- `T-123` — Rendered-skill schema check, binary guard, manifest check

## Files to Touch

- .github/workflows/ci.yml

## Verification

```bash
# locally V-SYNC, git diff --exit-code on generated trees, V-PI, V-PY; then confirm the PR run and record it in the Work Log.
# V-SYNC: the sync command documented in CLAUDE.md's Build section (currently: cd cli && python scripts/sync_init_scaffolds.py)
# V-PY: cd cli && uv run pytest && uv run ruff format --check . && uv run ruff check .   # set UV_CACHE_DIR under /tmp if uv cannot write its cache
# V-PI: cd pi && npm ci && npm run typecheck && npm test   # after V-SYNC
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
