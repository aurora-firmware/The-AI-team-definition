---
id: T-110
title: Port the validation core
status: in-progress
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Port the validation core

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 3**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P33 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- port core/validate.py with identical finding codes, messages, relative paths, ordering. Out of scope: validate command (T-118).

## Acceptance Criteria

AC-1: same findings in same order for every T-092 tree (SC-5).
AC-2: malformed frontmatter same code and message.
AC-3: V-PI passes (SC-9).

## Dependencies

- `T-092` — Seed fixtures for validate and archive
- `T-107` — Port filesystem layer and slug generation
- `T-108` — Port the project root locator

## Files to Touch

- pi/src/core/validate.ts
- tests

## Verification

```bash
# V-PI.
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
