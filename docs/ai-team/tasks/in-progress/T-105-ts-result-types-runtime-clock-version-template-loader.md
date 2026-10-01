---
id: T-105
title: TS result types, runtime clock/version, template loader
status: in-progress
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# TS result types, runtime clock/version, template loader

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 3**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P28 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- result/error types with separate message and hint (mirror T-082); runtime reads the same clock/version override names as T-081 in one place, else the generated version file; missing file raises "run the sync"; template loader reads pi/resources/templates; record variable names in README.

## Acceptance Criteria

AC-1: same override names as Python (Config).
AC-2: missing version file → error telling user to run the sync.
AC-3: loader returns bytes identical to cli/src/ai_team/templates.
AC-4: V-PI passes (SC-9).

## Dependencies

- `T-081` — Injectable "today" and framework version in the Python CLI
- `T-100` — Pi package skeleton

## Files to Touch

- pi/src/core/{result,runtime,templates}.ts
- tests
- pi/README.md

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

### Session 1 — 2026-10-01
Implemented the TS core foundation in `pi/src/core`. `result.ts` has a `Result` shape of status, payload, message and hint, with `success`, `failure` and `resultText`. `resultText` joins message and hint with a space, as the Python `Result.text()` does. It also has an `AiTeamError` that carries the hint separately. `runtime.ts` exports `TODAY_ENV_VAR` and `FRAMEWORK_VERSION_ENV_VAR`, the same names as `ai_team.core.runtime`. `today()` returns a local-date `YYYY-MM-DD` string. It validates the override as a real calendar date, so `2026-02-31` is rejected. `frameworkVersion()` uses the override, else reads and trims `resources/version.txt`. A missing file raises an `AiTeamError` with a "run the sync" hint. `templates.ts` loads the six template kinds from `resources/templates` as raw `Buffer`s, so output is byte-identical to Python's. Unsupported kinds and a missing resources directory raise `AiTeamError`. The env, `now`, version-file path and templates directory are injectable parameters, so tests never touch `process.env`. The README now documents the two override variables.

Tried and rejected: a tagged union for `Result`, because the flat shape matches Python and T-082 and keeps later ports simple. Also returning the date as a `Date` object, because ISO strings are what artifact frontmatter needs. Everything is committed as four cycles on the task branch.

Remaining: nothing for this task. Reviewers may note that `loadTemplate` returns bytes, so later renderer tasks decode them as UTF-8 themselves. I did not use `node:fs` mocking, only a scratch temp directory. The generated `version.txt` and `resources/templates` are read from disk at call time, so the sync must have been run.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
