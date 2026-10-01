---
id: T-118
title: TS validate and archive handlers
status: pending
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# TS validate and archive handlers

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 3**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P41 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- validate with combinable flags on T-110; archive with olderThan and dryRun on the T-105 clock.

## Acceptance Criteria

AC-1: V-PI-F validate--, archive-- pass (SC-5).
AC-2: age boundary exactly as fixtures (SC-4).
AC-3: dryRun changes nothing.
AC-4: zero type errors (SC-9).

## Dependencies

- `T-092` — Seed fixtures for validate and archive
- `T-107` — Port filesystem layer and slug generation
- `T-110` — Port the validation core
- `T-112` — TS parity runner, command registry, handler stubs

## Files to Touch

- pi/src/core/commands/{validate,archive}.ts

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
I implemented `validate` and `archive` test-first and committed after each. The handler tests went red against the stubs, then green after the implementations. I ported the Python behaviour directly. For `validate` I delegated to `validateProject` from T-110. All scopes are enabled when `all` is set or when no scope flag is set, and the findings array is the payload. Status is 1 when any finding is an error. For `archive` I used the T-105 `today()` clock. I wrote the cutoff arithmetic in UTC so daylight saving cannot shift a day. The strict `created < cutoff` comparison is done on ISO strings, and the `YYYY-MM` bucket is the first 7 characters of `created`. `listMarkdownFiles` and `moveArtifact` are the shared helpers. All 28 relevant parity fixtures pass, and the full typecheck and test run are clean. I also edited `pi/test/parity.test.ts`, outside Files to Touch, because two of its tests depended on `archive` being the stub. They now use a locally built `notImplemented` stub. The reviewer should check that edit. The reviewer should also check how `archive` handles a bug with no `created` date: it throws an `AiTeamError`, where Python would raise `TypeError`. Nothing remains.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
