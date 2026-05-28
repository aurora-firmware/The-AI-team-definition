---
id: T-047
title: Implement change request CLI creation
status: pending
priority: high
assigned-role: developer
created: '2026-05-28'
spec: coordinated-process-and-cli-workflow-improvements
---

# Implement change request CLI creation

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

Implement the user-facing CLI command that creates pending change-request
documents from the core artifact support. The command should follow the existing
artifact creation style: allocate an ID, slugify the title, write from the
bundled template, refuse accidental overwrite, and support JSON output for
agent use.

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

AC-1: WHEN a user runs the change-request creation command with a title THE
SYSTEM SHALL create a `CR-NNN-<slug>.md` artifact in the change-request
directory.
AC-2: WHEN a user passes supported metadata flags THE SYSTEM SHALL write those
values into the change-request frontmatter.
AC-3: WHEN a user passes `--json` THE SYSTEM SHALL emit machine-readable `id`
and `path` fields without table formatting.
AC-4: IF the allocated output path already exists THEN THE SYSTEM SHALL refuse
to overwrite it and exit non-zero.

## Dependencies

- `T-046` — core change-request model, parser, dumper, and ID support.
- `T-054` — change-request storage path and template loading support.

## Files to Touch

- `cli/src/ai_team/commands/change_request.py` — add the Typer command group.
- `cli/tests/test_change_request_new.py` — cover create, JSON output, metadata,
  and overwrite refusal.
- `cli/docs/usage.md` — briefly mention the new artifact command in CLI usage.

## Verification

```bash
cd cli
uv run pytest tests/test_change_request_new.py
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
