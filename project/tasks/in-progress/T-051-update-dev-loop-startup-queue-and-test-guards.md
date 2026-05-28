---
id: T-051
title: Update dev loop startup queue and test guards
status: pending
priority: high
assigned-role: planner
created: '2026-05-28'
spec: coordinated-process-and-cli-workflow-improvements
---

# Update dev loop startup queue and test guards

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

Update the dev-loop skill so it does not start autonomous task execution unless
the branch baseline is suitable. The loop must use the `ai-team` CLI task-listing
interface for pending queue discovery, discover the documented project test
command from project guidance, run that command before claiming a task, and
escalate to the human when the command is missing, ambiguous, or failing.

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

AC-1: WHEN dev-loop starts without a single-task argument THE SYSTEM SHALL use
the `ai-team` CLI task state filter to discover pending tasks.
AC-2: WHEN dev-loop starts THE SYSTEM SHALL discover the documented baseline
test command before claiming a task.
AC-3: WHEN the documented baseline test command passes THE SYSTEM SHALL allow
the loop to continue to task selection and claiming.
AC-4: IF the documented baseline test command is missing or ambiguous THEN THE
SYSTEM SHALL escalate to the human instead of starting the loop.
AC-5: IF the documented baseline test command fails THEN THE SYSTEM SHALL stop
and report the failing command and output summary.

## Dependencies

- `T-050` — root guidance templates define where project test commands should
  be documented.

## Files to Touch

- `cli/src/ai_team/init/sources/skills/dev-loop/body.md` — update startup,
  queue discovery, and baseline test guard instructions.
- `cli/src/ai_team/init/scaffolds/claude/skills/dev-loop/SKILL.md` —
  regenerated scaffold output for Claude.
- `cli/src/ai_team/init/scaffolds/codex/skills/dev-loop/SKILL.md` —
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

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
