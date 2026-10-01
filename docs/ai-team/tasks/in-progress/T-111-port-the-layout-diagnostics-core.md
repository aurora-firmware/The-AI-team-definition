---
id: T-111
title: Port the layout-diagnostics core
status: in-progress
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Port the layout-diagnostics core

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 3**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P34 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- port core/layout.py Levels 1–4; reads scaffold dir list and root-guidance starter sections from pi/resources and version from T-105 runtime; suggested fixes a separate field.

## Acceptance Criteria

AC-1: same findings as Python for every T-093 check-layout tree (SC-5).
AC-2: checks directories from the generated scaffold list when tools list claude/codex (S-003 Level 1).
AC-3: suggested fix separate.
AC-4: V-PI passes (SC-9).

## Dependencies

- `T-093` — Seed fixtures for check-layout and init, incl. init→check-layout chain
- `T-099` — Pi target in the sync; generate pi/resources/
- `T-105` — TS result types, runtime clock/version, template loader
- `T-110` — Port the validation core

## Files to Touch

- pi/src/core/layout.ts
- tests

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
