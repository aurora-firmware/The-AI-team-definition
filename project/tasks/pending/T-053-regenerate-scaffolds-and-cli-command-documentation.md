---
id: T-053
title: Regenerate scaffolds and CLI command documentation
status: pending
priority: medium
assigned-role: developer
created: '2026-05-28'
spec: coordinated-process-and-cli-workflow-improvements
---

# Regenerate scaffolds and CLI command documentation

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

Run the repository's generated-output steps after the source, CLI, and process
changes are complete. This task catches any scaffold drift left by earlier work
and refreshes CLI command documentation so user-facing docs match the final
command surface.

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

AC-1: WHEN scaffold source files differ from generated scaffold outputs THE
SYSTEM SHALL regenerate the scaffold outputs.
AC-2: WHEN CLI command behavior or options change THE SYSTEM SHALL regenerate
the CLI command reference.
AC-3: The system shall leave no generated scaffold or command-doc drift after
the repository checks run.
AC-4: The system shall pass the repo-level CLI checks required by `AGENTS.md`.

## Dependencies

- `T-044` — spec-breakdown source updates.
- `T-045` — spec-breakdown-review source updates.
- `T-047` — change-request creation command.
- `T-048` — change-request listing and validation.
- `T-049` — project guidance scaffold sources.
- `T-055` — generated project guidance scaffold output.
- `T-050` — init root guidance behavior.
- `T-051` — dev-loop source updates.

## Files to Touch

- `cli/src/ai_team/init/scaffolds/` — generated scaffold output refreshed from
  source files.
- `cli/docs/commands.md` — regenerated CLI command reference.
- `cli/docs/usage.md` — user-facing CLI usage updates for change requests and
  init guidance files.
- `guides/customization-guide.md` — guidance for maintaining root
  `CLAUDE.md` and `AGENTS.md` files.

## Verification

```bash
cd cli
python scripts/sync_init_scaffolds.py
bash scripts/gen_docs.sh
uv run pytest
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
