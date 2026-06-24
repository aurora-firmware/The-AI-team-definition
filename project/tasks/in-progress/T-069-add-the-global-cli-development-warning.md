---
id: T-069
title: Add the global CLI development warning
status: pending
priority: high
assigned-role: developer
created: '2026-06-24'
spec: S-003-project-layout-diagnostics-and-cli-development-warning
---

# Add the global CLI development warning

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

Implement S-003's process-wide development warning at the root CLI boundary.
Every `ai-team` invocation must emit the contract line exactly once on stderr,
including help, version, success, command failure, and commands whose stdout is
JSON. Keep stdout unchanged so existing machine-readable consumers continue to
parse it. The warning is informational only and must not contact the issue URL.

## Acceptance Criteria

<!-- EARS pattern reference. Every criterion must match one pattern:
  1. Ubiquitous            — The system shall [outcome]
  2. Event-driven          — WHEN [trigger] THE SYSTEM SHALL [outcome]
  3. Unwanted-behaviour    — IF [fault] THEN THE SYSTEM SHALL [outcome]
  4. State-driven          — WHILE [state] THE SYSTEM SHALL [outcome]
  5. Optional              — WHERE [feature included] THE SYSTEM SHALL [outcome]

Examples:
  AC-1: WHEN the user submits valid credentials THE SYSTEM SHALL
        redirect to /dashboard within 200ms.
  AC-2: IF the password is incorrect THEN THE SYSTEM SHALL return 401
        and display "Invalid credentials".
  AC-3: The system shall log every authentication attempt with user id
        and outcome.
-->

AC-1: WHEN any `ai-team` process invocation begins THE SYSTEM SHALL emit exactly
      once on stderr `Warning: ai-team is under development. Please report issues at https://github.com/aurora-firmware/The-AI-team-definition/issues`.
AC-2: WHEN help, version, a successful command, or a command error is produced
      THE SYSTEM SHALL include the same single stderr warning without changing
      the command's exit behavior.
AC-3: WHILE a command emits JSON on stdout THE SYSTEM SHALL keep stdout valid
      JSON and emit the warning only on stderr.
AC-4: The system shall perform no network request when it displays the warning.

## Dependencies

- None.

## Files to Touch

- `cli/src/ai_team/cli.py` — emit the contract warning from the root CLI boundary.
- `cli/tests/test_cli_bootstrap.py` — cover all invocation classes and stdout/stderr separation.

## Verification

```bash
cd cli
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_cli_bootstrap.py
UV_CACHE_DIR=/tmp/uv-cache uv run ruff format --check .
UV_CACHE_DIR=/tmp/uv-cache uv run ruff check .
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-06-24

Implemented the exact process-wide development warning at the root Typer/Click
group boundary, with coverage for help, version, successful commands, parse
errors, JSON stdout separation, exact-once stderr emission, and no network
activity. A callback-only approach was considered and rejected because eager
help/version handling and parse failures bypass callbacks. The initial
full-suite run exposed tests that conflated Click 8.2's combined
`result.output` with stdout. Under the Architect-approved scope adjustment,
mechanically migrated only stdout contract assertions and JSON parsers in the
authorized test files to `result.stdout`; stderr assertions were preserved and
combined `result.output` remains only as diagnostic failure context. The
complete 382-test suite and both Ruff checks now pass. Nothing remains for
implementation or verification.

Obstacles encountered: Click 8.2 combines stderr into `Result.output`, causing
35 legacy stdout assertions to fail once the required warning was added. The
Architect resolved the task-file scope mismatch by authorizing the mechanical
test migration.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
