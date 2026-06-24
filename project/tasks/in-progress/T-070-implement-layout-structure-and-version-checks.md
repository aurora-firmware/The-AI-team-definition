---
id: T-070
title: Implement layout structure and version checks
status: pending
priority: high
assigned-role: developer
created: '2026-06-24'
spec: S-003-project-layout-diagnostics-and-cli-development-warning
---

# Implement layout structure and version checks

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

Create the read-only layout-checking core for S-003 and implement validation
levels 1 and 4. Resolve `.ai-team.toml`, the configured project directory,
selected tools, the current package scaffold contract, and the installed CLI
version without relying on the network. Findings must carry validation level,
path, problem, and suggested fix, sort deterministically, and allow checks to
continue when local fallback information is available.

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

AC-1: WHEN a valid `.ai-team.toml` is present THE SYSTEM SHALL resolve its
      project directory, configured tools, framework version, and the running
      CLI distribution version from local data.
AC-2: IF `.ai-team.toml` or a required marker value is missing or invalid THEN
      THE SYSTEM SHALL return an actionable finding and continue checks that
      can safely use repository conventions.
AC-3: WHEN level 1 runs THE SYSTEM SHALL report each missing lifecycle directory
      from the current project scaffold and each missing agent or skill
      directory for configured tools while permitting extra directories.
AC-4: WHEN level 4 runs THE SYSTEM SHALL report a missing, invalid, or non-exact
      framework-version match and include configured and current values when
      available.
AC-5: The system shall return deterministic read-only findings containing level,
      path, problem, and suggested fix without modifying repository contents.

## Dependencies

- `T-069` — completes phase 1's process-wide development warning before phase
  2 layout validation begins, as required by S-003's implementation order.

## Files to Touch

- `cli/src/ai_team/core/layout.py` — define layout resolution, findings, and levels 1 and 4.
- `cli/tests/test_layout.py` — cover marker parsing, scaffold directories, version checks, ordering, and read-only behavior.

## Verification

```bash
cd cli
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_layout.py
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

Implemented the read-only layout contract resolver and validation levels 1 and
4 using TDD. Added coverage for valid and malformed markers, safe conventional
fallbacks, configured tools, package-derived scaffold directories,
extra-directory tolerance, exact framework-version matching, deterministic
ordering, and repository immutability. The initial test run failed as expected
because the layout module did not exist; implementation made all 10 focused
tests pass. I then reduced the production module below the repository's
300-line review threshold without changing behavior. Final targeted
verification, Ruff checks, and the complete 392-test suite pass. No
implementation work remains; lifecycle bookkeeping and review are next.

Obstacles encountered: none.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
