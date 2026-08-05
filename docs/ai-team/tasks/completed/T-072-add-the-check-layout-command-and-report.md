---
id: T-072
title: Add the check-layout command and report
status: completed
priority: high
assigned-role: developer
created: '2026-06-24'
spec: S-003-project-layout-diagnostics-and-cli-development-warning
---

# Add the check-layout command and report

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

Expose the completed S-003 validation core as `ai-team check-layout`. Render one
deterministic human-readable report containing all findings from levels 1
through 4. Each issue must identify level, path, problem, and suggested fix.
Return success for a clean project and a non-zero exit for reported issues.
The command must remain strictly observational, aggregate independent findings,
and turn missing prerequisites into report entries rather than crashes.

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

AC-1: WHEN a user invokes `ai-team check-layout` THE SYSTEM SHALL run all four
      validation levels and render findings ordered by level and path.
AC-2: WHEN findings exist THE SYSTEM SHALL report each finding's level, path,
      problem, and suggested fix and exit unsuccessfully after reporting all
      checks that could run.
AC-3: WHEN no findings exist THE SYSTEM SHALL render an unambiguous clean result
      and exit successfully.
AC-4: IF a prerequisite is missing or malformed THEN THE SYSTEM SHALL include an
      actionable report entry rather than expose an unhandled exception.
AC-5: The system shall leave every repository file and directory unchanged by a
      `check-layout` invocation.

## Dependencies

- `T-071` — completes all four validation levels consumed by the command.

## Files to Touch

- `cli/src/ai_team/commands/check_layout.py` — add the discoverable command and report rendering.
- `cli/tests/test_check_layout.py` — cover report fields, ordering, exit codes, aggregation, errors, and read-only behavior.
- `cli/docs/commands.md` — regenerate the committed command reference after adding the discoverable command.

## Verification

```bash
cd cli
bash scripts/gen_docs.sh
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_check_layout.py tests/test_layout.py
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

Implemented the auto-discovered `ai-team check-layout` command using two TDD
cycles. It renders deterministic findings ordered by level and path, includes
level, path, problem, and suggested fix, returns correct clean/issue exit
codes, resolves nested repository roots, reports malformed prerequisites
without crashing, and remains read-only. After Architect approval expanded
scope, regenerated `cli/docs/commands.md` using the repository generator
without hand-editing and committed only its generated delta. A second
generator run produced no diff, and the exact `## \`ai-team check-layout\``
heading is present. Targeted tests, the full suite, and Ruff all pass. Nothing
remains for development; the task is ready for review.

Obstacles encountered: the documentation scope conflict was resolved by the
Architect. The initial generator run hit the read-only default `uv` cache;
rerunning with `/tmp/uv-cache` succeeded.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-06-24

PASS

Stage 1 passed: all five acceptance criteria are satisfied, and the diff is
limited to the three approved files. The command aggregates and orders all
layout findings, reports every required field, handles clean and malformed
inputs with the required exit behavior, and remains observational.

Stage 2 passed: the implementation is focused and readable, success and
failure paths are covered, 31 targeted tests and the full 413-test suite pass,
and Ruff format and lint checks pass. Regenerating `cli/docs/commands.md` twice
left no diff and produced the identical SHA-256
`de110210d910c759d6ad5facd5bd1b35754e3e22ae5d66eb63c8e2441a5e66ec`,
confirming the committed documentation is generated and idempotent.

Next owner: active Development Loop.

Obstacles Encountered: the initial canonical handoff was delayed by a temporary
environment restriction on Git metadata writes; it did not affect the review.
