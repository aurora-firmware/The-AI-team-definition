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

### Session 1 — 2026-05-29

No scaffold drift was found — `sync_init_scaffolds.py` reported no changes after running, confirming that earlier tasks (T-044 through T-055) had already kept sources and scaffolds in sync.

The only meaningful issue was a pre-existing defect in `gen_docs.sh`: the script called `uv run typer` but the `typer` CLI binary is not registered on PATH in this environment. The command exited with code 2 (caught by `set -euo pipefail`), leaving `commands.md` truncated to its 4-line header comment on every prior invocation. This caused 22 cascading test failures (6 in `test_gen_docs.py`, 16 in `test_usage_guide.py`). Fixed by switching the script to `uv run python -m typer`, which resolves correctly through the venv. After the fix, `commands.md` was regenerated to 552 lines covering all command groups including `change-request`, `list change-requests`, and the `--create-root-guidance` init flag.

Two surgical additions were made to `usage.md`: `ai-team list change-requests` was added to the listing section; `ai-team validate --change-requests` was added to the validate section. A new "Root guidance files" subsection was added to the init section explaining the interactive prompt flow, `--create-root-guidance` non-interactive usage, and `--force` behavior.

`guides/customization-guide.md` received a new "Root CLAUDE.md and AGENTS.md" subsection covering what these files are for, the `## Test` section convention and which tooling reads which file (Claude reads `CLAUDE.md`, non-Claude tooling reads `AGENTS.md`), and the workflow for filling in the starter templates after `ai-team init` scaffolds them.

**Scope note for Reviewer.** `cli/scripts/gen_docs.sh` is not in the task's "Files to Touch" list, but the script was the root cause of the command-doc drift (AC-3) and the test failures (AC-4). The Developer judged the fix to be in-scope housekeeping that this task is meant to absorb. The Reviewer should confirm or split the fix into a separate task.

Full suite at end of session: 286 passed, 0 failed. Both ruff checks clean.

Commits on the task branch: `0edfa4b` (gen_docs.sh + commands.md), `be39064` (usage.md + customization-guide.md).

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
