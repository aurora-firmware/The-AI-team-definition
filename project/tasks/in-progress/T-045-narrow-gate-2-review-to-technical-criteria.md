---
id: T-045
title: Narrow Gate 2 review to technical criteria
status: pending
priority: high
assigned-role: architect
created: '2026-05-28'
spec: coordinated-process-and-cli-workflow-improvements
---

# Narrow Gate 2 review to technical criteria

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

Update the Gate 2 preflight skill so review feedback focuses on technical
task-plan readiness: dependencies, file conflicts, architectural consistency,
atomicity, and verification. The review must not become a second product/spec
approval pass unless it finds a contradiction that truly requires changing the
approved spec.

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

AC-1: WHEN the Architect reviews a task plan THE SYSTEM SHALL focus findings on
technical task-plan criteria.
AC-2: IF the Architect finds a product-scope concern that does not block task
technical readiness THEN THE SYSTEM SHALL avoid failing Gate 2 for that concern.
AC-3: IF the task plan contradicts the approved spec or existing ADRs THEN THE
SYSTEM SHALL escalate or fail according to the existing Gate 2 procedure.
AC-4: The system shall preserve the existing Gate 2 output format and verdict
vocabulary.

## Dependencies

- None

## Files to Touch

- `cli/src/ai_team/init/sources/skills/spec-breakdown-review/body.md` —
  tighten technical review scope.
- `cli/src/ai_team/init/scaffolds/claude/skills/spec-breakdown-review/SKILL.md`
  — regenerated scaffold output for Claude.
- `cli/src/ai_team/init/scaffolds/codex/skills/spec-breakdown-review/SKILL.md`
  — regenerated scaffold output for Codex.

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

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
