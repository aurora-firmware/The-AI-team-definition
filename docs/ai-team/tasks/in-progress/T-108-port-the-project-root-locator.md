---
id: T-108
title: Port the project root locator
status: in-progress
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Port the project root locator

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 3**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P31 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- explicit root → AI_TEAM_ROOT → .ai-team.toml [project] dir → default project folder, from a caller-provided directory, never process cwd; ProjectRoot paths; not-found keeps core message with hint separate. Out of scope: hint rewriting (T-122).

## Acceptance Criteria

AC-1: same resolution order (Config).
AC-2: start dir is a parameter, never process cwd.
AC-3: not-found message equals Python's.
AC-4: V-PI passes (SC-9).

## Dependencies

- `T-082` — Structured-result type; apply to spec new, adr new, change-request new
- `T-105` — TS result types, runtime clock/version, template loader

## Files to Touch

- pi/src/core/locator.ts
- tests

## Verification

```bash
# V-PI; grep process.cwd in pi/src/core (none).
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
Ported the project root locator to `pi/src/core/locator.ts`, with tests in `pi/test/locator.test.ts`. The resolution order is the same as Python's: explicit root, then `AI_TEAM_ROOT`, then the walk-up for `.ai-team.toml` `[project] dir`, then the default `project` folder.

- **Start directory and env:** The start directory is the first parameter and `process.cwd` is never used. The environment is injectable through `options.env` and defaults to `process.env`, so tests are deterministic.
- **Python behaviours kept:** Paths are symlink-resolved when they exist. An explicit or env root that lacks its project folder fails immediately instead of falling through. A marker file naming a missing folder keeps the walk going. An unparseable marker file is ignored. An empty `AI_TEAM_ROOT` is ignored.
- **Not-found error:** `ProjectRootNotFound` extends `AiTeamError`, so `message` and `hint` stay separate and the messages equal Python's text. Hint rewriting is left to T-122.
- **Deliberate difference:** A `[project] dir` that is not a string is treated as absent. Python would raise a type error on it, which seemed like an accident rather than a contract.
- **Cycle structure:** All tests written in one batch and implemented once, so a single red→green cycle. No refactor beyond the initial layout.
- **Remaining:** Nothing for this task. The parity-fixture harness that exercises the locator end to end belongs to later tasks.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
