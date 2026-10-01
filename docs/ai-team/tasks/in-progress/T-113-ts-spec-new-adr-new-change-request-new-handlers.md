---
id: T-113
title: TS spec new, adr new, change-request new handlers
status: in-progress
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# TS spec new, adr new, change-request new handlers

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 3**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P36 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- Notes: [G2 N9] Python adr new and change-request new take no lock; the TS lock there is allowed by ADR-003 and fixtures are unaffected thanks to the lock-path scoping.

## Acceptance Criteria

AC-1: V-PI-F spec-new--, adr-new--, change-request-new-- pass (SC-5).
AC-2: IDs allocated only under the TS lock (SC-7).
AC-3: zero type errors (SC-9).

## Dependencies

- `T-089` — Seed fixtures for artifact-creation commands
- `T-107` — Port filesystem layer and slug generation
- `T-109` — Port ID allocation and implement the TS lock
- `T-112` — TS parity runner, command registry, handler stubs

## Files to Touch

- pi/src/core/commands/{spec,adr,change-request}.ts
- optional tests

## Verification

```bash
# V-PI-F per prefix; full V-PI. [G2 B4]
# V-PI-F: cd pi && npm test -- parity -t "<prefix>"   # a subset of parity cases
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
Implemented the `spec new`, `adr new` and `change-request new` handlers in `pi/src/core/commands/{spec,adr,change-request}.ts`, ported from `cli/src/ai_team/commands/*.py`. Each validates its input (non-empty title; status from the `command-map.json` choices for spec and adr), then calls `createArtifactWithLock` with the matching allocator (`nextSpecId`, `nextAdrId`, `nextChangeRequestId([root.changeRequests])`). `LockTimeout` and `ArtifactExists` become failure results.

The template body comes from `splitFrontmatter`; the title placeholder is replaced via a function replacer so `$` in a title is not interpreted. The spec handler passes the parsed template frontmatter as `sourceMap`, as Python does; ADR and change request dump fresh frontmatter. The TS lock also wraps ADR and change-request creation, which Python does not lock; ADR-003 allows this and lock-path scoping leaves the fixtures unaffected (G2 N9).

Results: all 32 `spec-new--`, `adr-new--`, `change-request-new--` parity cases run as real comparisons and pass; typecheck clean; 19 files, 429 tests pass, 160 todo (fixtures of still-stubbed commands). Added `pi/test/creation-handlers.test.ts` (missing title, status validation, lock release, cwd independence via chdir, ID allocation past an existing file). `pi/test/parity.test.ts` stub examples switched from `spec new` to `task new`.

TDD note: no separate red step — the parity cases were `it.todo` before the stubs were replaced, and the unit tests were written alongside the handlers.

Earlier review notes: the runner's tree sort is JS code-unit vs Python code-point; moot for these fixtures (ASCII slugs), runner left alone as outside Files to Touch. A possible follow-up is switching it to code-point order. Handlers never read `process.cwd`.

Rejected: a shared input-parsing helper (`handler.ts` is outside the task's files, duplication is small); making the write create missing parent folders (Python does not; my first test failures were test setup).

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
