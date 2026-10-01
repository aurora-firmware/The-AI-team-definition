---
id: T-115
title: TS bug handlers
status: pending
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# TS bug handlers

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 3**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P38 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- bug new, start, resolve.

## Acceptance Criteria

AC-1: V-PI-F bug- passes (SC-5).
AC-2: invalid transition errors equal fixtures (SC-4).
AC-3: zero type errors (SC-9).

## Dependencies

- `T-089` — Seed fixtures for artifact-creation commands
- `T-090` — Seed fixtures for lifecycle transitions
- `T-107` — Port filesystem layer and slug generation
- `T-109` — Port ID allocation and implement the TS lock
- `T-112` — TS parity runner, command registry, handler stubs

## Files to Touch

- pi/src/core/commands/bug.ts
- optional tests

## Verification

```bash
# V-PI-F bug-; full V-PI. [G2 B4]
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
I implemented the three bug handlers in `pi/src/core/commands/bug.ts`. `createBug` validates the title, severity (critical, high, medium or low) and an optional string `task`. It then allocates the ID and writes the file under the lock. The body comes from the bundled bug template with the `# [Bug Title]` heading replaced. `startBug` moves a bug from open to in-progress, and `resolveBug` moves it from in-progress to resolved. If the bug is already in the destination, both return an unchanged result with the message "Bug X already in Y." If the bug is missing from its source folder, they return the not-found message listing all three bug folders. The handlers reuse the shared helpers `updateStatus`, `moveArtifact`, `createArtifactWithLock`, `nextBugId` and `loadTemplate`.

I wrote `pi/test/bug-handlers.test.ts` before the implementation and watched it fail. It covers input validation, creation, both transitions, the ID-prefix collision case (`B-0011` must not match `B-001`) and the already-resolved case. I tried sharing the task transition helpers from `task.ts`. I rejected that because `findTaskFile` is private and the task says to touch only `bug.ts`. The cost is a small duplicated `compareCodePoints` and file-lookup helper, which a later refactor could pull into a shared module. The `parity.test.ts` stub assertions moved from `bug new` to `archive`, which is still a stub. Nothing remains for this task. The reviewer should look at that out-of-scope test edit and at the duplicated helpers.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
