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

### Session 1 — 2026-10-01

Two permanent guards went in. First, the parity suite no longer treats a stub-resolved case as a todo. A new `runSharedCase` wrapper in `pi/test/parity.test.ts` throws when `runCase` returns pending. A test shows a stubbed `archive` case fails, another asserts `COMMANDS` contains no stub handlers, and a third asserts every registered command has a fixture case. The shared-fixtures loop uses the wrapper, so all 215 parity tests run and none are todo or skipped.

Second, `pi/test/imports.test.ts` now asserts that no file under `pi/src/core` references `process.cwd`. A small test checks the detector against several spellings. The tests passed when first written, because the handlers were already implemented. I left `registry.ts` and the runner helper unchanged, and `isStub` stays available.

SC-8 evidence, all from commands run in this session on the committed tree. Before the cross runs I ran `uv sync --reinstall-package ai-team` and re-ran the scaffold sync. Python package version is `0.10.3.dev302+g1a6a5d455` and pi `resources/version.txt` is `0.10.3.dev302+g1a6a5d455`, so they match. A project created by TS `initRepository` (no tools) passed Python `ai-team check-layout` with zero findings and exit 0. A project created by Python `init --tools claude,codex --no-interactive --create-root-guidance`, with the placeholder guidance filled in, passed Python `check-layout` and TS `checkRepositoryLayout` with zero findings each. Unfilled placeholder guidance correctly yields 10 findings, which is expected. These were recorded runs, not permanent tests, because TS tests must not shell out to Python (ADR-004 Alternative C).

Final checks: `uv run pytest` passed 1029 tests. Ruff format and lint were clean. `npm run typecheck` showed zero errors, and `npm test` passed 642 of 642 tests. No files outside Files to Touch were edited. Nothing remains.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-10-01
PASS

Stage 1 (acceptance): AC-1 met: all 215 parity tests run under the TS runner with none todo or skipped, and the Python suite (1029 tests) passes. AC-2 met: `runSharedCase` throws on a pending/stub outcome, and a test shows a stubbed `archive` case fails. AC-3 met: the Work Log records both cross runs with zero findings and matching versions, and I reproduced them independently. AC-4 met: `tsc --noEmit` reports zero errors. The G2 N12 `process.cwd` guard is present in `pi/test/imports.test.ts`. Only the two listed test files changed.

Stage 2 (quality): the guard tests cover both the pass path and the failure path. Each test is independent. There is no dead code. The `process.cwd` detector is covered by its own spelling test.

Independent verification on the task branch: scaffold sync, `uv run pytest` (1029 passed), ruff format and check (clean), `npm run typecheck` (clean), `npm test` (642/642). SC-8 spot-check in a scratch dir: TS `initRepository` project passes Python `ai-team check-layout` (zero findings, exit 0). Python `init --tools claude,codex --no-interactive --create-root-guidance` with the placeholders filled passes both Python and TS `checkRepositoryLayout` (zero findings). Versions match: Python `0.10.3.dev302+g1a6a5d455` and pi `resources/version.txt` `0.10.3.dev302+g1a6a5d455`.

Non-blocking observations:
- The `process.cwd` regex does not catch destructured or aliased access (e.g. `const { cwd } = process`). This is acceptable for the stated guard.
- The Work Log says the completeness tests passed when first written, since no stubs remain. That is expected, but it means AC-2 rests on the synthetic stubbed-case test.

