---
id: T-122
title: ai_team tool adapter
status: pending
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# ai_team tool adapter

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 4**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P45 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- register ai_team; validate input with T-121; resolve root from session cwd via T-108 only for commands that need a located root (init and check-layout get the session cwd as their start directory) [G2 B7]; dispatch to registry; 1–3 line summary plus structured result as details; domain errors → tool errors with message plus rewritten hint (binary hints like "Run 'ai-team init'" and check-layout suggested fixes become tool instructions); unexpected exceptions → one-line error, no stack; never the dev warning; missing version file → tool fails to load with sync message; tested with a fake pi API, without starting pi.

## Acceptance Criteria

AC-1: summary 1–3 lines plus structured details (Tool contract).
AC-2: root from session cwd, never process cwd (Config).
AC-3: binary hints/suggested fixes rewritten (Tool contract).
AC-4: unexpected exception → one-line error, no stack.
AC-5: missing version file → load failure with sync message.
AC-6: init and check-layout succeed from a directory with no project/. [G2 B7]

## Dependencies

- `T-121` — ai_team tool schema from the command map; handler-mapping test

## Files to Touch

- pi/src/index.ts
- pi/src/adapter/{tool,hints}.ts
- pi/test/adapter.test.ts

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
