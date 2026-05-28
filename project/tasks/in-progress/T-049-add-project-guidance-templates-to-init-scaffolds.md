---
id: T-049
title: Add project guidance templates to init scaffolds
status: pending
priority: high
assigned-role: developer
created: '2026-05-28'
spec: coordinated-process-and-cli-workflow-improvements
---

# Add project guidance templates to init scaffolds

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

Add stable repository-owned `project/CLAUDE.md` and `project/AGENTS.md`
templates to the init scaffold source. These source files describe the purpose
of the generated project artifact folders; a later task updates the scaffold
generator and generated outputs so `ai-team init` creates them.

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

AC-1: The system shall include a source template for `project/CLAUDE.md`.
AC-2: The system shall include a source template for `project/AGENTS.md`.
AC-3: The system shall describe the purpose of specs, tasks, bugs, decisions,
reports, and project-local docs in both project guidance files.
AC-4: The system shall leave generated scaffold output and init collision
behavior to the dependent scaffold-generation task.

## Dependencies

- None

## Files to Touch

- `cli/src/ai_team/init/sources/project/CLAUDE.md` — add project guidance source.
- `cli/src/ai_team/init/sources/project/AGENTS.md` — add project guidance source.

## Verification

```bash
rg -n "specs|tasks|bugs|decisions|reports|project-local docs" \
  cli/src/ai_team/init/sources/project/CLAUDE.md \
  cli/src/ai_team/init/sources/project/AGENTS.md
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-05-28

Started with mandatory Work Log read (no prior entries), then translated AC-1 through AC-4 into a single focused scaffold-source test that asserts `cli/src/ai_team/init/sources/project/CLAUDE.md` and `.../AGENTS.md` both exist and both explicitly describe specs, tasks, bugs, decisions, reports, and project-local docs. Ran the targeted test to confirm red; it failed because `sources/project/CLAUDE.md` did not exist. Implemented the minimal change by adding both source template files with concise folder-purpose guidance. Re-ran the targeted test (green), then re-ran `tests/test_init_scaffolds.py` (all green), and executed the task verification `rg` command confirming all required terms are present in both files. Considered adding generator/scaffold output updates, but rejected that in this task because AC-4 explicitly defers generated scaffold output and init-collision behavior to the dependent scaffold-generation task. Finalized by committing only task-owned files and leaving unrelated root untracked files untouched. Remaining work is reviewer validation and downstream dependent task to wire these new source templates into scaffold generation.

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

Stage 1 passed: AC-1 and AC-2 are satisfied by added source templates at
`cli/src/ai_team/init/sources/project/CLAUDE.md` and
`cli/src/ai_team/init/sources/project/AGENTS.md`; AC-3 is satisfied by explicit
folder-purpose descriptions for specs, tasks, bugs, decisions, reports, and
project-local docs in both files; AC-4 is satisfied because no scaffold
generator or collision-behavior files were modified in this task.

Stage 2 passed: the added test
`test_project_guidance_sources_exist_and_describe_project_artifact_folders`
directly validates file presence and required terms; independent reviewer
verification also passed with `13 passed` for
`tests/test_init_scaffolds.py` and the task `rg` command.
