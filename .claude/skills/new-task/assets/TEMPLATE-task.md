---
id: "T-000"
title: "[Task Title]"
status: pending  # pending | in-progress | completed | blocked
priority: medium  # critical | high | medium | low
assigned-role: "[agent role or unassigned]"
created: YYYY-MM-DD
---

# [Task Title]

## Description

What needs to be done and why.
Include enough context that an agent can start working without asking questions.

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

AC-1: ...
AC-2: ...
AC-3: ...

## Dependencies

- `T-XXX` — brief description of what must be completed first
- None (if no dependencies)

## Files to Touch

- `path/to/file-a.ext` — what changes are needed
- `path/to/file-b.ext` — what changes are needed

## Verification

```bash
# Command(s) to verify the task is complete
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

### Review 1 — PASS|FAIL
**Date:** YYYY-MM-DD
**Reviewer notes:**
- [For FAIL: file, location, what is wrong, what should change]
- [For PASS: brief confirmation that both stages passed]
-->
