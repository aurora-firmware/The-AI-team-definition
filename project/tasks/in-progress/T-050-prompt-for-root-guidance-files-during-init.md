---
id: T-050
title: Prompt for root guidance files during init
status: pending
priority: high
assigned-role: developer
created: '2026-05-28'
spec: coordinated-process-and-cli-workflow-improvements
---

# Prompt for root guidance files during init

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

Update `ai-team init` so it asks whether to create root `CLAUDE.md` and
`AGENTS.md` guidance files when they do not already exist. The root templates
must be stable repository-owned files that prompt projects to record commands
agents need, especially how to run tests. Existing root files must not be
overwritten unless the init command is already operating in an explicit
overwrite mode.

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

AC-1: WHEN interactive init runs and root `CLAUDE.md` is missing THE SYSTEM
SHALL ask whether to create it from the stable template.
AC-2: WHEN interactive init runs and root `AGENTS.md` is missing THE SYSTEM
SHALL ask whether to create it from the stable template.
AC-3: WHEN non-interactive init runs THE SYSTEM SHALL provide deterministic
behavior for root guidance file creation through documented flags or defaults.
AC-4: IF root guidance creation is declined THEN THE SYSTEM SHALL complete init
and print follow-up guidance about documenting project commands.
AC-5: IF a root guidance file already exists THEN THE SYSTEM SHALL not prompt
to replace it unless explicit overwrite behavior applies.

## Dependencies

- `T-055` — generated project guidance files establish the init guidance-file
  conventions.

## Files to Touch

- `cli/src/ai_team/commands/init.py` — add root guidance prompts and copy logic.
- `cli/src/ai_team/init/sources/root/CLAUDE.md` — add root guidance template.
- `cli/src/ai_team/init/sources/root/AGENTS.md` — add root guidance template.
- `cli/tests/test_init.py` — cover interactive, non-interactive, missing, and
  existing root guidance behavior.

## Verification

```bash
cd cli
uv run pytest tests/test_init.py
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
