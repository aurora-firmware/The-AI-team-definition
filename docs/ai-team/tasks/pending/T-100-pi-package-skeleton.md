---
id: T-100
title: Pi package skeleton
status: pending
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Pi package skeleton

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 2**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P23 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- pi manifest with extension entry and every generated skill except dev-loop, bug-loop, integrate; minimum Node; pi host peer deps with minimum 0.87.1; typecheck and test scripts per CLAUDE.md; full Phase 3/4 runtime dependency set settled here (round-tripping YAML, TOML parser, slug transliteration, pi's schema library) so later tasks run in parallel; strict tsconfig; vitest config; stub index.ts; README (dev setup, one-time sync, scratch PI_CODING_AGENT_DIR, mixed concurrency unsupported). Out of scope: core logic, tool registration.

Size note (accepted at Gate 2, ruling 7): boilerplate for a new package.

## Acceptance Criteria

AC-1: manifest lists every non-orchestrator skill and no orchestrator (SC-10).
AC-2: min Node and pi peer ≥0.87.1 (Config).
AC-3: V-PI after V-SYNC on clean checkout: zero type errors, tests pass (SC-9).
AC-4: README documents scratch dir, sync prerequisite, mixed concurrency unsupported (SC-7).
AC-5: only entry and adapter import the pi API, enforced by a pi/test guard that fails on any pi import under pi/src/core. [G2 N4]
AC-6: the package scripts are named exactly `typecheck` and `test`, matching CLAUDE.md (ruling 4).

## Dependencies

- `T-080` — CLAUDE.md pi checks and setup-guide pi install steps
- `T-099` — Pi target in the sync; generate pi/resources/

## Files to Touch

- pi/package.json
- pi/package-lock.json
- pi/tsconfig.json
- pi vitest config
- pi/src/index.ts
- pi/README.md
- pi/.gitignore (add node_modules/) [G2 N4]
- pi/test/imports.test.ts [G2 N4]

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
