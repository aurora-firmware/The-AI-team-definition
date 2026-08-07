---
id: T-054
title: Add change request storage and template loading
status: completed
priority: high
assigned-role: developer
created: '2026-05-28'
spec: coordinated-process-and-cli-workflow-improvements
---

# Add change request storage and template loading

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

Add the storage path and bundled template loading support that makes the
change-request core model usable by commands. This task creates the
change-request artifact directory surface on `ProjectRoot`, makes the
`change-request` template loadable by the existing template loader, and adds the
initial Markdown template body.

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

AC-1: The system shall expose a project-root path for change-request artifacts.
AC-2: The system shall include a bundled change-request Markdown template that
describes desired changes and possible spec amendments.
AC-3: WHEN the template loader is asked for the change-request template THE
SYSTEM SHALL return the bundled template content.
AC-4: IF the project root is resolved from an initialized repository THEN THE
SYSTEM SHALL include the change-request directory path in the returned root
object.

## Dependencies

- `T-046` — change-request model, parser, dumper, and ID support.

## Files to Touch

- `cli/src/ai_team/core/locator.py` — add the change-request artifact path.
- `cli/src/ai_team/core/templates.py` — ensure the new template is loadable.
- `cli/src/ai_team/templates/change-request.md` — add the bundled template.
- `cli/tests/test_locator.py` — cover the new project-root path.
- `cli/tests/test_templates.py` — cover template loading.

## Verification

```bash
cd cli
uv run pytest tests/test_locator.py tests/test_templates.py
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

Implemented this task in two TDD cycles. First, I added a failing locator test asserting that `find_project_root()` returns a `ProjectRoot` exposing a `change_requests` path for initialized repositories, then added the new dataclass field and constructor wiring to `project/change-requests`, and reran the full locator suite to green. Second, I added failing template tests for a `change-request` template kind (loader round-trip to bundled source plus content checks for desired changes and possible spec amendments), then implemented loader support and created the new bundled markdown template. I rejected guessing a different directory layout and aligned on `project/change-requests` to stay consistent with existing artifact naming patterns. Final verification passed for the task’s pytest target plus ruff format/check. Remaining work is only lifecycle bookkeeping on `dev-agent` (append this Work Log entry and continue loop flow).

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-05-28
PASS

Stage 1 passed: AC-1 through AC-4 are implemented, the bundled `change-request`
template includes desired changes and spec amendments guidance, and only the
task-declared files were modified.

Stage 2 passed: locator/template logic is correct for the requested scope, tests
cover the new path and template behavior, and verification commands passed
(`pytest`, `ruff format --check`, `ruff check`).
