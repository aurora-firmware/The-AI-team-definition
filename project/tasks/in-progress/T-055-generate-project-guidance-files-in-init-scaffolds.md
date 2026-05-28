---
id: T-055
title: Generate project guidance files in init scaffolds
status: pending
priority: high
assigned-role: developer
created: '2026-05-28'
spec: coordinated-process-and-cli-workflow-improvements
---

# Generate project guidance files in init scaffolds

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

Update the scaffold generator and generated project scaffold output so every
`ai-team init` run creates `project/CLAUDE.md` and `project/AGENTS.md` from the
source templates. Preserve existing collision handling and ensure tests cover
the generated outputs.

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

AC-1: WHEN scaffold generation runs THE SYSTEM SHALL copy source
`project/CLAUDE.md` into generated project scaffolds.
AC-2: WHEN scaffold generation runs THE SYSTEM SHALL copy source
`project/AGENTS.md` into generated project scaffolds.
AC-3: WHEN `ai-team init` runs THE SYSTEM SHALL plan `project/CLAUDE.md` and
`project/AGENTS.md` as project scaffold outputs.
AC-4: IF either generated project guidance file already exists and `--force` is
not set THEN THE SYSTEM SHALL preserve existing collision refusal behavior.

## Dependencies

- `T-049` — project guidance source templates.

## Files to Touch

- `cli/scripts/sync_init_scaffolds.py` — include project guidance sources in
  generated scaffolds.
- `cli/src/ai_team/init/scaffolds/project/CLAUDE.md` — generated scaffold output.
- `cli/src/ai_team/init/scaffolds/project/AGENTS.md` — generated scaffold output.
- `cli/tests/test_init.py` — cover init output and collision behavior.
- `cli/tests/test_init_scaffolds.py` — cover scaffold generation expectations.

## Verification

```bash
cd cli
python scripts/sync_init_scaffolds.py
uv run pytest tests/test_init.py tests/test_init_scaffolds.py
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
