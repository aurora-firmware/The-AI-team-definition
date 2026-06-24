---
id: T-071
title: Add artifact and guidance layout checks
status: pending
priority: high
assigned-role: developer
created: '2026-06-24'
spec: S-003-project-layout-diagnostics-and-cli-development-warning
---

# Add artifact and guidance layout checks

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

Extend the S-003 layout core from T-070 with validation levels 2 and 3. Reuse
the CLI's existing artifact naming, frontmatter, and lifecycle-status rules
rather than creating a conflicting validator. Check only managed artifacts;
ignore scaffold placeholders and non-artifact documentation. Select root
guidance from configured tools and require project-specific content under all
five contract headings without executing any documented command.

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

AC-1: WHEN level 2 runs THE SYSTEM SHALL validate every managed spec, task, bug,
      change request, and ADR filename and type-appropriate required
      frontmatter using the CLI's current artifact rules.
AC-2: IF a lifecycle artifact's directory and frontmatter status differ THEN
      THE SYSTEM SHALL report the mismatch with an actionable suggested fix.
AC-3: WHILE level 2 scans managed locations THE SYSTEM SHALL ignore `.gitkeep`,
      scaffold templates, and non-artifact documentation.
AC-4: WHEN level 3 runs THE SYSTEM SHALL require `CLAUDE.md` for configured
      Claude, `AGENTS.md` for configured Codex, or both, with non-placeholder
      content under Build and Install, Test, Run, Lint and Format, and Key
      Conventions.
AC-5: IF an input needed by levels 2 or 3 is missing or malformed THEN THE
      SYSTEM SHALL report the blocked check instead of raising an unhandled
      exception and shall continue independent checks.

## Dependencies

- `T-070` — provides layout resolution, finding contracts, and ordered checks.

## Files to Touch

- `cli/src/ai_team/core/layout.py` — add levels 2 and 3 to the layout core.
- `cli/tests/test_layout.py` — cover managed artifacts, lifecycle mismatches, guidance selection, placeholders, and blocked checks.

## Verification

```bash
cd cli
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_layout.py tests/test_validate.py
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

Implemented layout validation levels 2 and 3 using TDD. Level 2 reuses the
existing artifact validator for managed filenames, required frontmatter, and
lifecycle status consistency while ignoring placeholders and documentation.
Level 3 validates configured root guidance files, required non-placeholder
sections, and malformed or missing inputs without executing documented
commands. Integrated both levels into ordered layout checks. No separate
validator was introduced. Nothing remains beyond review and integration.

Obstacles encountered: none.

### Session 2 — 2026-06-24

Reproduced the invalid UTF-8 crash with a regression test, then extended the
existing level-2 boundary to catch `UnicodeError` alongside `OSError`. The test
confirms a blocked level-2 finding is returned and the independent level-3
guidance check continues. Avoided a broad exception handler so unrelated
failures remain visible. Nothing remains beyond review and integration.

Obstacles encountered: none.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-06-24

FAIL

Stage 1 failed AC-5. The other acceptance criteria and the changed-file scope
were verified, and the task's pytest and Ruff verification commands pass.

- **File and location:** `cli/src/ai_team/core/layout.py`, `check_level_2`, the
  exception handler around `validate_project`.
- **What is wrong:** The handler catches only `OSError`, but the reused artifact
  parsers read managed Markdown as UTF-8 and can raise `UnicodeDecodeError`
  (a `UnicodeError`) for malformed input. That exception escapes
  `check_level_2` and aborts `check_layout`, contrary to AC-5's requirement to
  report a blocked check and continue independent checks.
- **What should change:** Handle invalid text encoding as a blocked artifact
  check without suppressing unrelated checks, and add a regression test with a
  non-UTF-8 managed artifact that verifies a level-2 finding is returned and an
  independent level-3 check still runs.

### Review Verdict — 2026-06-24

PASS

Stage 1 passes: all five acceptance criteria are satisfied, including the
cycle-1 malformed UTF-8 case, which now produces a blocked level-2 finding
while the independent level-3 guidance check continues. The implementation
touches only the two task-authorized files and adds no unrelated behavior.

Stage 2 passes: the exception handling is narrow, readable, and covered by an
independent regression test. The task verification passes with 43 tests, both
Ruff checks pass, and the complete CLI suite passes with 409 tests. No
non-blocking observations.

Next owner: active Development Loop.
