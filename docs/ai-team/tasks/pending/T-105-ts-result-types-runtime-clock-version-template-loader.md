---
id: T-105
title: TS result types, runtime clock/version, template loader
status: pending
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# TS result types, runtime clock/version, template loader

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 3**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P28 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- result/error types with separate message and hint (mirror T-082); runtime reads the same clock/version override names as T-081 in one place, else the generated version file; missing file raises "run the sync"; template loader reads pi/resources/templates; record variable names in README.

## Acceptance Criteria

AC-1: same override names as Python (Config).
AC-2: missing version file → error telling user to run the sync.
AC-3: loader returns bytes identical to cli/src/ai_team/templates.
AC-4: V-PI passes (SC-9).

## Dependencies

- `T-081` — Injectable "today" and framework version in the Python CLI
- `T-100` — Pi package skeleton

## Files to Touch

- pi/src/core/{result,runtime,templates}.ts
- tests
- pi/README.md

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
