---
id: T-121
title: ai_team tool schema from the command map; handler-mapping test
status: pending
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# ai_team tool schema from the command map; handler-mapping test

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 4**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P44 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- union discriminated on command from pi/resources command map; one variant per leaf command; camelCase fields, defaults and enums from the map; no json field; init has no tools/noInteractive; SC-11 tests (variant↔handler both ways) and map agreement.

## Acceptance Criteria

AC-1: exactly one variant per leaf command (Tool contract).
AC-2: variant without handler or handler without variant fails (SC-11).
AC-3: no json, no init tools/noInteractive.
AC-4: V-PI passes (SC-9).

## Dependencies

- `T-099` — Pi target in the sync; generate pi/resources/
- `T-120` — Full parity suite and recorded SC-8 cross-implementation check

## Files to Touch

- pi/src/adapter/schema.ts
- pi/test/schema.test.ts

## Verification

```bash
# V-SYNC; V-PI.
# V-SYNC: the sync command documented in CLAUDE.md's Build section (currently: cd cli && python scripts/sync_init_scaffolds.py)
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
