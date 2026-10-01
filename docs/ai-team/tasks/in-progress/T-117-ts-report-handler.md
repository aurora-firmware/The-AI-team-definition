---
id: T-117
title: TS report handler
status: pending
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# TS report handler

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 3**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P40 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- port commands/report.py (content, default path, out) using T-105 clock. [G2 B3] Import the status payload from status.ts (owned by T-116); do not edit status.ts. [G2 N12] `out` resolves against the handler's start directory, never process.cwd().

## Acceptance Criteria

AC-1: V-PI-F report-- passes, report file byte-identical (SC-5).
AC-2: out writes to that path.
AC-3: zero type errors (SC-9).

## Dependencies

- `T-091` — Seed fixtures for list, show, status, report
- `T-107` — Port filesystem layer and slug generation
- `T-112` — TS parity runner, command registry, handler stubs
- `T-116` — TS list, show, status handlers

## Files to Touch

- pi/src/core/commands/report.ts

## Verification

```bash
# V-PI-F report--; full V-PI. [G2 B4]
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
