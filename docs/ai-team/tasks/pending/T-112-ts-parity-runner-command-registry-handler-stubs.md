---
id: T-112
title: TS parity runner, command registry, handler stubs
status: pending
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# TS parity runner, command registry, handler stubs

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 3**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P35 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- vitest runner auto-discovers fixtures/parity cases with the T-088 rules (loads the shared lock-scoping list, applies the isolation rules, normalises only root paths); resolves root, sets overrides, compares tree/status/message; registry maps every tool-contract command to a handler module; stubs throw "not implemented"; later tasks edit only their module; filter by name prefix. [G2 B4] Cases whose command resolves to a stub are reported as skipped/todo, so `npm test` stays green. [G2 B7] Handler interface: `init` takes the start directory (plus `path`); `check-layout` takes the start directory and resolves its own root (port of check_layout.py `_repository_root`); every other handler takes a located ProjectRoot.

Size note (accepted at Gate 2, ruling 7): trivial stubs; removes shared-file conflicts for T-113–T-119.

## Acceptance Criteria

AC-1: new case discovered without registration (ADR-004).
AC-2: registry maps every command to exactly one handler (SC-11 groundwork).
AC-3: mismatch fails with diff (SC-5).
AC-4: V-PI passes; V-PI-F status-- reports the smoke case as pending (stub). [G2 B4]
AC-5: the registry's handler signatures follow the init / check-layout / located-root split. [G2 B7]

## Dependencies

- `T-088` — Parity fixture format and Python fixture runner
- `T-100` — Pi package skeleton
- `T-105` — TS result types, runtime clock/version, template loader
- `T-108` — Port the project root locator

## Files to Touch

- pi/test/parity.test.ts
- pi/src/core/commands/registry.ts
- 13 stub modules under pi/src/core/commands/ (spec, adr, change-request, task, bug, list, show, status, report, validate, archive, check-layout, init); vitest config may be touched

## Verification

```bash
# V-PI; V-PI-F status-- to confirm discovery.
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
