---
id: T-044
title: Update spec breakdown docs and test planning
status: pending
priority: high
assigned-role: planner
created: '2026-05-28'
spec: coordinated-process-and-cli-workflow-improvements
---

# Update spec breakdown docs and test planning

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

Update the spec-breakdown skill so task planning explicitly considers
documentation and test updates as implementation work derived from an approved
spec. The skill should not require documentation to be updated before tasks are
created; it should require the Planner to add documentation and test tasks or
acceptance criteria when the spec changes user-facing behavior, commands,
templates, guides, or verification paths.

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

AC-1: WHEN the Planner decomposes an approved spec THE SYSTEM SHALL require the
Planner to consider documentation updates as part of task creation.
AC-2: WHEN the Planner decomposes an approved spec THE SYSTEM SHALL require the
Planner to consider test updates or verification changes as part of task
creation.
AC-3: IF documentation or test updates are not needed THEN THE SYSTEM SHALL
allow the Planner to omit them without creating placeholder tasks.
AC-4: The system shall keep documentation and test planning in spec breakdown,
not as a prerequisite before task creation.

## Dependencies

- None

## Files to Touch

- `cli/src/ai_team/init/sources/skills/spec-breakdown/body.md` — add
  docs/tests planning requirements.
- `cli/src/ai_team/init/scaffolds/claude/skills/spec-breakdown/SKILL.md` —
  regenerated scaffold output for Claude.
- `cli/src/ai_team/init/scaffolds/codex/skills/spec-breakdown/SKILL.md` —
  regenerated scaffold output for Codex.

## Verification

```bash
cd cli
python scripts/sync_init_scaffolds.py
uv run pytest tests/test_init_scaffolds.py
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

### Session 1 — 2026-05-28

Read the canonical task file first, including the existing (empty) Work Log, then implemented this task in two TDD cycles on `task/T-044-update-spec-breakdown-docs-and-test-planning`. In cycle 1, I added a failing test that required spec-breakdown guidance to explicitly treat documentation updates as implementation planning during task creation and to keep that planning inside breakdown rather than as a prerequisite. I then updated `cli/src/ai_team/init/sources/skills/spec-breakdown/body.md`, regenerated scaffolds, and confirmed the test passed before committing (`251f96a`).

In cycle 2, I added a failing test requiring spec-breakdown guidance to explicitly consider test updates/verification changes and to allow omission without placeholder tasks when not needed. I minimally extended the same source body, regenerated scaffolds, verified both new tests passed, and committed (`114e1b9`).

I tried running the verification command exactly as written (`uv run pytest ...`), but this environment cannot spawn `pytest` directly under `uv`; I used the equivalent `uv run python -m pytest ...` and recorded the result. Also, `python` is unavailable here, so scaffold sync was run with `python3`. Final verification is passing (`pytest`, `ruff format --check`, `ruff check`). No remaining implementation work is pending on this branch.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
