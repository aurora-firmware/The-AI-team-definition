---
id: T-095
title: Fixture coverage test for commands and enum values
status: pending
priority: medium
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Fixture coverage test for commands and enum values

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 2**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P18 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- loads the command map and every case; every leaf command has a case; every enum value appears; each case's input fields exist for its command.

## Acceptance Criteria

AC-1: missing command fails naming it (SC-3).
AC-2: missing enum value fails naming it (SC-3).
AC-3: undefined field fails.

## Dependencies

- `T-089` — Seed fixtures for artifact-creation commands
- `T-090` — Seed fixtures for lifecycle transitions
- `T-091` — Seed fixtures for list, show, status, report
- `T-092` — Seed fixtures for validate and archive
- `T-093` — Seed fixtures for check-layout and init, incl. init→check-layout chain
- `T-094` — Command map plus agreement test against the Typer CLI

## Files to Touch

- new cli/tests/test_parity_fixture_coverage.py

## Verification

```bash
# V-PY.
# V-PY: cd cli && uv run pytest && uv run ruff format --check . && uv run ruff check .   # set UV_CACHE_DIR under /tmp if uv cannot write its cache
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
