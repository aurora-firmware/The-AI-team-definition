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

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
