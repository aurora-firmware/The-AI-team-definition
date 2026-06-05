---
id: T-057
title: Update Codex generated agent model defaults
status: completed
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

### Session 1 — 2026-06-04
Implemented T-057 on the task branch with a single TDD cycle. I started by reading the canonical task, confirmed the Codex source/scaffold TOMLs still used `gpt-5.4` for Architect and Planner and `gpt-5.3-codex` for Developer, Reviewer, and Integrator, and added a regression test in `cli/tests/test_init_scaffolds.py` that enforces the required role-to-model mapping, rejects `gpt-5.3-codex`, checks source/scaffold parity, and preserves `model_reasoning_effort = "high"`. The new test failed first on the Architect mapping, which gave the expected red state.

For the green step, I updated the five package-owned Codex source TOMLs to the required defaults and regenerated `cli/src/ai_team/init/scaffolds/codex/agents/*.toml` with `scripts/sync_init_scaffolds.py` rather than editing generated output manually. After that, the new targeted regression passed, and the broader verification set passed as well: scaffold tests, the `ai-team init --tools codex` smoke test, `ruff format --check`, `ruff check`, and an `rg` sweep confirming there are no remaining `gpt-5.3-codex` references in the Codex source or scaffold agent TOMLs.

I initially tried running the targeted pytest command from the repo root and hit environment issues, so I switched to running all `uv` commands from `cli/` and set `UV_CACHE_DIR=/tmp/uv-cache` because the default cache path is not writable in this environment. `ruff format --check` also wanted to reflow the new test, so I accepted the formatter's output and reran verification before committing. Nothing remains on the implementation branch for this task.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-06-04
PASS

Stage 1 passed: AC-1 through AC-5 are satisfied by the Codex source TOMLs, regenerated scaffold TOMLs, and the added regression in `cli/tests/test_init_scaffolds.py`, with `model_reasoning_effort = "high"` preserved throughout.

Stage 2 passed: the change set is scoped to the required agent defaults and scaffold coverage, the regression test enforces the full role-to-model mapping plus the unsupported-model guard, and the task verification commands reproduced successfully on the implementation branch.
