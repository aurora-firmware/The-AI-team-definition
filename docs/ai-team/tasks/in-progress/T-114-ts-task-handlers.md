---
id: T-114
title: TS task handlers
status: pending
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# TS task handlers

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 3**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P37 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- task new, start, complete, block (work-log append with T-105 clock), unblock.

## Acceptance Criteria

AC-1: V-PI-F task- passes (SC-5).
AC-2: invalid transition errors equal fixtures (SC-4).
AC-3: zero type errors (SC-9).

## Dependencies

- `T-089` — Seed fixtures for artifact-creation commands
- `T-090` — Seed fixtures for lifecycle transitions
- `T-107` — Port filesystem layer and slug generation
- `T-109` — Port ID allocation and implement the TS lock
- `T-112` — TS parity runner, command registry, handler stubs

## Files to Touch

- pi/src/core/commands/task.ts
- optional tests

## Verification

```bash
# V-PI-F task-; full V-PI. [G2 B4]
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
Implemented all five task handlers in `pi/src/core/commands/task.ts` as ports of `cli/src/ai_team/commands/task.py`.

- `task new`: validates the title, priority and role, then allocates the ID and writes the file under the lock. The task template body is used with the title placeholder replaced. The model carries no source map, matching Python.
- Transitions: all four share one `transitionTask`. It checks the destination folder first, which gives the idempotent "already in <state>" result. It then searches the allowed source folders and returns the exact not-found message listing all four folders in order. It then runs the optional before-hook, updates the status, and moves the file. Payload paths use `realpathSync`, matching Python's `.resolve()`.
- `task block`: appends a session entry after the highest existing session number. A local `splitLines` copies Python's `splitlines` semantics so line handling is the same.

The B-018 quirk is deliberately kept to match the fixtures. When a Work Log heading is missing, the entry lands above the new heading. `task-block--unicode-reason` records this, so fixing it needs a Python fix and a fixture change together. I added no fixture for it.

Tried and rejected: a plain `sort()` for file lookup, which uses UTF-16 order. I wrote a code-point comparison to match Python's `sorted`.

Also changed `pi/test/parity.test.ts` so its stub-command examples use `bug new`. This file is outside the listed Files to Touch, so the reviewer should confirm it is acceptable.

Nothing remains for this task. Other commands (`bug`, `list`, `show`, and others) are still stubs and belong to their own tasks.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-10-01
PASS

Stage 1 (acceptance):
- AC-1 met: `npm test -- parity -t "task-"` on `task/T-114-ts-task-handlers` ran 45 passed, 0 failed.
- AC-2 met: the invalid-transition and not-found messages match the Python port (destination check first, idempotent "already in <state>", all four folders listed in order). The parity cases pass.
- AC-3 met: `npm run typecheck` reports zero errors.
- Scope: the diff touches `pi/src/core/commands/task.ts`, a new `pi/test/task-handlers.test.ts` (the "optional tests" entry), and `pi/test/parity.test.ts`. The `parity.test.ts` change is acceptable. Its stub-command examples used `task new`, which is no longer a stub, so it now uses `bug new`.

Stage 2 (quality):
- Logic mirrors `cli/src/ai_team/commands/task.py` line by line: template body and title substitution, code-point sort, `splitlines` semantics, session numbering, and `realpathSync` for `.resolve()`.
- Input validation is present (title, priority, id, reason). Creation runs under the lock, and a test checks the lock is released.
- Tests cover success and failure paths and share no mutable state. Full `npm test` gives 484 passed, 115 todo.

Non-blocking observations:
- The B-018 quirk (a missing Work Log heading puts the entry above the new heading) is kept on purpose for parity and documented in the code. Fixing it needs a Python fix and a fixture change together.
- Handler tests do not directly cover the idempotent "already in" path or the completed-to-blocked path. The parity fixtures cover both.

Next owner: Development Loop.
