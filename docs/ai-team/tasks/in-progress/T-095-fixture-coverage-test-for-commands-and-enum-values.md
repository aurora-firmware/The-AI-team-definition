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

### Session 1 — 2026-10-01
Added `cli/tests/test_parity_fixture_coverage.py`, the only file touched. The task was a coverage test over fixtures that already existed. It has three pure check functions: `missing_commands`, `missing_enum_values` and `undefined_input_fields`. Each takes the command map and a list of cases, and returns a list of readable problems. Two kinds of test use them. Three run them against the real command map (`cli/src/ai_team/init/sources/command_map.json`) and the real fixtures, and assert the result is empty. Four mutation tests feed in a command map or case list with a deliberate gap and assert the failure names it, which proves the AC-1 to AC-3 failures work. Enum coverage means some case for that command has the enum value as the input for the field. Tool fields come from the non-CLI-only flags plus the positional fields in the map. Coverage was already complete, so the real-fixture tests passed on their first run and I added no fixtures. I chose pure functions over pytest parametrisation so a gap shows as one clear message and the checks can be exercised against mutated data. I did not edit any files outside Files to Touch. A redundant `command_map = _load_command_map()` line remains in the file and is harmless. Nothing else remains. The full Python suite and both ruff checks pass.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
