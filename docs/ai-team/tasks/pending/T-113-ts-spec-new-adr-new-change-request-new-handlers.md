---
id: T-113
title: TS spec new, adr new, change-request new handlers
status: pending
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

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
