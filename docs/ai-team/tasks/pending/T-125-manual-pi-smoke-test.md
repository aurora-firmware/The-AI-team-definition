---
id: T-125
title: Manual pi smoke test
status: pending
priority: medium
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Manual pi smoke test

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 4**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P48 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- pi ≥0.87.1 with scratch PI_CODING_AGENT_DIR; V-SYNC; `pi install <repo>/pi`; session in a scratch project, init via the tool; ask the agent to create a task via the new-task skill; confirm T-001 via the ai_team tool and no shell call to ai-team in the session log; record in Work Log; add a "Manual smoke test" section to pi/README.md. Needs pi installed locally. [G2 N10] Manual / human-assisted task: if pi ≥0.87.1 is unavailable the developer returns BLOCKED, never a simulated result. Out of scope: automation.

## Acceptance Criteria

AC-1: T-001 via ai_team with no shell call to ai-team (SC-12).
AC-2: scratch PI_CODING_AGENT_DIR only (Config).
AC-3: Work Log records pi version, steps, evidence (SC-12).
AC-4: README documents the procedure.

## Dependencies

- `T-122` — ai_team tool adapter
- `T-123` — Rendered-skill schema check, binary guard, manifest check

## Files to Touch

- pi/README.md

## Verification

```bash
# manual steps; V-PI; V-PY.
# V-PY: cd cli && uv run pytest && uv run ruff format --check . && uv run ruff check .   # set UV_CACHE_DIR under /tmp if uv cannot write its cache
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
