---
id: T-118
title: TS validate and archive handlers
status: completed
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

### Review Verdict — 2026-10-01
PASS

Stage 1 (acceptance criteria):
- AC-1: met. `npm test -- parity -t "archive--"` (13 pass) and `-t "validate--"` (15 pass) are green.
- AC-2: met. The cutoff is computed in UTC calendar days and compared with strict `created < cutoff`. This matches `cli/src/ai_team/commands/archive.py`, and the handler test covers the boundary.
- AC-3: met. A dry run skips `mkdirSync` and `moveArtifact`. The test asserts the archive directory is not created and the source files remain.
- AC-4: met. `npm run typecheck` reports zero errors. The full `npm test` run gave 601 passed, 36 todo.
- Only the two handler files were changed, plus tests. The `pi/test/parity.test.ts` edit is justified: two tests relied on `archive` being a stub. They now use a locally built `notImplemented` stub, and the assertions are unchanged in intent.

Stage 2 (quality): the handlers delegate to the shared helpers (`validateProject`, `listMarkdownFiles`, `moveArtifact`, `today`). Success and failure paths are covered by tests, and the tests use per-test temp directories and restore the env var.

Non-blocking observations:
- A bug or task with no `created` date throws `AiTeamError` with a remediation hint. This is a reasonable replacement for Python's `TypeError`.
- A malformed but present `created` string is compared lexically. Python's `date.fromisoformat` would raise an error instead. This is an edge case outside the fixtures.
- `findings as unknown as Record<string, unknown>` is a type cast needed to carry the list payload. It is acceptable, but a payload type that allows arrays would be cleaner later.
