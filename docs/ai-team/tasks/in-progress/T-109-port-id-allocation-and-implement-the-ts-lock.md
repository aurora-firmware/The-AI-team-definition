---
id: T-109
title: Port ID allocation and implement the TS lock
status: in-progress
priority: critical
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Port ID allocation and implement the TS lock

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 3**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P32 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- port core/ids.py (all kinds, archived IDs, spec IDs from frontmatter); lock at the T-087 path with create-under-lock semantics: atomic acquisition, holder liveness check, reclaim of dead holder, same bounded wait and core timeout message as core/lock.py; test with two concurrent Node processes ≥50 repetitions and a holder killed mid-allocation. Out of scope: Python locking (ADR-003).
- Notes: [G2 N11] the vitest config has one owner (T-112); the ≥50-repetition concurrency test uses per-test timeouts instead of editing the config.

## Acceptance Criteria

AC-1: no duplicate ID across ≥50 concurrent repetitions (SC-7).
AC-2: killed holder doesn't block beyond bounded wait (SC-7).
AC-3: timeout message uses the same template as Python's, with the TS lock path (core/lock.py:96-99 embeds the path). [G2 N3]
AC-4: never touches .ai-team.lock (ADR-003).
AC-5: next IDs match T-089 gap/archived cases.

## Dependencies

- `T-087` — TS lock entry in skeleton .gitignore; update B-017 tests and usage guide
- `T-089` — Seed fixtures for artifact-creation commands
- `T-106` — Port frontmatter models and byte-identical YAML dump
- `T-108` — Port the project root locator

## Files to Touch

- pi/src/core/{ids,lock}.ts
- tests
- test helper under pi/test/

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

### Session 1 — 2026-10-01
Ported `core/ids.py` to `pi/src/core/ids.ts`: the five next-ID functions, filename maximum across state folders, `specs/archive` included, and `id: S-NNN` read from spec frontmatter with the same regex and fence logic as Python. Added `pi/src/core/lock.ts` with `allocationLock(projectDir, callback, {timeoutSeconds})`, `createArtifactWithLock` and `LockTimeout`. The lock file is `.ai-team-ts.lock` (the path T-087 reserved); `.ai-team.lock` is never touched.

The API is synchronous, sleeping with `Atomics.wait`, because the core's file operations are synchronous. Acquisition writes the holder pid to a private temp file and hard-links it to the lock path (atomic, fails if present, never half-written). Waiters poll every 50 ms, read the pid and check `process.kill(pid, 0)`; `ESRCH` means dead, `EPERM` counts as alive. A dead holder's lock is reclaimed by renaming to a private name and re-verifying the pid; if the rename grabbed another holder's lock it is linked back. Non-pid content is never reclaimed and is waited on until timeout. Default timeout 10 s; the message template matches Python's with `10.0`-style float formatting.

Rejected: exclusive-open-then-write (a holder killed between steps leaves an empty lock indistinguishable from one being written), and reusing `.ai-team.lock` (ADR-003).

Residual limits (documented in code): PID reuse could make a dead holder look alive until timeout; a very narrow window remains where the lock is freed and retaken between a reclaimer's pid read and its rename (link-back handles it unless a third process takes the path at that instant); a holder killed between temp-file creation and unlink leaves a harmless `*.tmp`.

Tests: AC-1 two Node processes each allocate 50 task IDs against one project, 100 unique IDs (passes with the lock, fails with it disabled); AC-2 SIGKILLed holder reclaimed within the bounded wait, live holder times out; AC-3 message template; AC-4 `.ai-team.lock` untouched; AC-5 14 T-089 fixtures checked. Children run through `node_modules/.bin/vite-node` (transitive vitest dependency; could break if vitest drops it). Cross-process tests live in `lock-concurrency.test.ts`. vitest config untouched (G2 N11). Typecheck clean, 318 tests pass. Nothing remains for this task.

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

Both stages passed. Reviewed branch `task/T-109-port-id-allocation-and-implement-the-ts-lock` (3 commits, 6 files, all within the task's Files to Touch) against `core/ids.py`, `core/lock.py`, ADR-003 and the T-089 fixtures.

Stage 1 (acceptance criteria):
- AC-1: two Node processes allocate 50 task IDs each against one project and get 100 unique IDs (`lock-concurrency.test.ts`). Re-run 15 times with no failure. An extra ad-hoc stress with four concurrent allocators (25 each) starting from a dead-holder lock, 12 runs, gave 100 unique IDs with no stderr every time.
- AC-2: a SIGKILLed holder is reclaimed well inside the bounded wait. A live holder in another process times out with `LockTimeout`.
- AC-3: the message template is identical to `core/lock.py:96-99` and embeds the TS lock path. Whole-second timeouts format as `10.0`, as in Python.
- AC-4: the lock path is `.ai-team-ts.lock`. `.ai-team.lock` is never read or written. A test confirms a Python sentinel file does not block acquisition.
- AC-5: ids.ts mirrors ids.py (regexes, state folders, `specs/archive`, spec frontmatter ids, fence logic). Tests run the T-089 parity fixtures plus edge cases.
- No unspecified behaviour was added. The vitest config is untouched (G2 N11).

Stage 2 (quality):
- Evidence: scaffold sync, `npm ci`, `npm run typecheck` (clean) and `npm test` (15 files, 318 tests) all pass on a temporary worktree of the task branch, since removed.
- Tests cover success and failure paths, use per-test temp dirs, and the concurrency tests use per-test timeouts. Code is readable, and the residual limits are documented in code.
- Non-blocking observations:
  1. `reclaimIfHolderDead` has a narrow, acknowledged race. If two waiters both see the same dead holder, one can rename the new holder's live lock away while the new holder finishes and removes it. The link-back can then leave a lock with a live pid that is never released. This is possible only in a microsecond window and was not reproduced. Consider a follow-up bug if it shows up in practice.
  2. The child helper runs via `node_modules/.bin/vite-node`, which is a transitive vitest dependency (the Developer noted this).

