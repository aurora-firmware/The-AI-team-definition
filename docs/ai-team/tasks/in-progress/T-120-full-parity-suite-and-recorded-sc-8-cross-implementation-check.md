---
id: T-120
title: Full parity suite and recorded SC-8 cross-implementation check
status: pending
priority: critical
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Full parity suite and recorded SC-8 cross-implementation check

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 3**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P43 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- runner fails if any case resolves to a stub; full suite under both runners; [G2 N8] before the cross runs, on a clean tree reinstall the editable package (`uv sync --reinstall-package ai-team`) and record both version strings; [G2 N12] add a permanent guard test: no process.cwd under pi/src/core; from the same checkout record in the Work Log that a pi-init project passes Python check-layout with zero findings, and Python-init projects (no tools; claude,codex) pass TS check-layout with zero findings. Recorded, not a permanent test (TS tests must not shell out to Python, ADR-004 Alternative C).

## Acceptance Criteria

AC-1: every case passes under both runners, none skipped (SC-5).
AC-2: stub-resolved case fails the TS runner (SC-11 groundwork).
AC-3: Work Log records both cross runs with zero findings (SC-8).
AC-4: zero type errors (SC-9).

## Dependencies

- `T-095` — Fixture coverage test for commands and enum values
- `T-113` — TS spec new, adr new, change-request new handlers
- `T-114` — TS task handlers
- `T-115` — TS bug handlers
- `T-116` — TS list, show, status handlers
- `T-117` — TS report handler
- `T-118` — TS validate and archive handlers
- `T-119` — TS check-layout and init handlers

## Files to Touch

- pi/test/parity.test.ts
- pi/test/imports.test.ts (process.cwd guard) [G2 R3]
- possibly pi/src/core/commands/registry.ts (removing stub support)

## Verification

```bash
# V-SYNC; V-PY; V-PI.
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
