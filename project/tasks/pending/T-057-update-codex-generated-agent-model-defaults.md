---
id: T-057
title: Update Codex generated agent model defaults
status: pending
priority: high
assigned-role: developer
created: '2026-06-03'
---

# Update Codex generated agent model defaults

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

The package-owned Codex agent sources currently assign `gpt-5.3-codex` to Developer, Reviewer, and Integrator, which is not supported in ChatGPT-backed Codex sessions. Update the generated-agent model defaults so exported Codex agents use account-compatible GPT-5 models:

- Architect: `gpt-5.5`
- Planner: `gpt-5.5`
- Developer: `gpt-5.4`
- Reviewer: `gpt-5.4`
- Integrator: `gpt-5.4`

Keep the existing `model_reasoning_effort = "high"` setting unless a test or Codex schema check proves the field name needs to change. The local `.codex/agents/` files were manually patched for the current workspace; this task updates the CLI source of truth and generated scaffold output used by `ai-team init --tools codex`.

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

AC-1: The system shall set Architect and Planner Codex agent source TOMLs to `model = "gpt-5.5"`.
AC-2: The system shall set Developer, Reviewer, and Integrator Codex agent source TOMLs to `model = "gpt-5.4"`.
AC-3: WHEN the scaffold sync script runs THE SYSTEM SHALL regenerate `cli/src/ai_team/init/scaffolds/codex/agents/*.toml` with model values matching the source TOMLs.
AC-4: The system shall include regression coverage that fails if generated Codex agent sources or scaffolds contain `gpt-5.3-codex` or drift from the required role-to-model mapping.
AC-5: WHILE preserving existing reasoning settings THE SYSTEM SHALL keep `model_reasoning_effort = "high"` in the Codex agent source and scaffold TOMLs unless the implementation documents a required schema change.

## Dependencies

- None

## Files to Touch

- `cli/src/ai_team/init/sources/agents/codex/*.toml` — update role model defaults.
- `cli/src/ai_team/init/scaffolds/codex/agents/*.toml` — regenerate from source via `scripts/sync_init_scaffolds.py`.
- `cli/tests/test_init_scaffolds.py` — add model mapping and unsupported-model regression coverage.

## Verification

```bash
cd cli
UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/sync_init_scaffolds.py
UV_CACHE_DIR=/tmp/uv-cache uv run --group dev python -m pytest tests/test_init_scaffolds.py tests/test_init.py::test_init_tools_codex_scaffolds_codex_agents_and_skills
UV_CACHE_DIR=/tmp/uv-cache uv run --group dev python -m ruff format --check .
UV_CACHE_DIR=/tmp/uv-cache uv run --group dev python -m ruff check .
rg -n 'gpt-5\.3-codex' src/ai_team/init/sources/agents/codex src/ai_team/init/scaffolds/codex/agents
```

The final `rg` command should return no matches; exit code 1 is expected.

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
