---
id: T-046
title: Add change request core artifact support
status: pending
priority: high
assigned-role: developer
created: '2026-05-28'
spec: coordinated-process-and-cli-workflow-improvements
---

# Add change request core artifact support

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

Add core parser and ID support for a first-class change-request artifact type.
This task defines the frontmatter model, parser, dumper support, and `CR-NNN`
identifier allocation, but it does not add storage paths, template loading, or
user-facing command behavior yet.

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

AC-1: The system shall support parsing and dumping change-request frontmatter
with a stable `CR-NNN` identifier.
AC-2: The system shall allocate change-request IDs without colliding with
existing change-request filenames in the provided search directories.
AC-3: The system shall preserve frontmatter key order when dumping
change-request artifacts.
AC-4: IF required change-request frontmatter is missing THEN THE SYSTEM SHALL
raise the existing frontmatter error style.

## Dependencies

- None

## Files to Touch

- `cli/src/ai_team/core/models.py` — add change-request model and parser.
- `cli/src/ai_team/core/ids.py` — add change-request ID allocation.
- `cli/tests/test_models.py` — cover change-request parsing and dumping.
- `cli/tests/test_ids.py` — cover `CR-NNN` allocation.

## Verification

```bash
cd cli
uv run pytest tests/test_models.py tests/test_ids.py
uv run ruff format --check .
uv run ruff check .
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
