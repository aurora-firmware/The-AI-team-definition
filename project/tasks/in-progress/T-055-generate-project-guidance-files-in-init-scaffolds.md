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

### Session 1 — 2026-05-28

Implemented T-055 in two TDD cycles on branch `task/T-055-generate-project-guidance-files-in-init-scaffolds`.

**What was done:**

Cycle 1 (AC-1 & AC-2): Added project guidance source fixtures (`CLAUDE.md` and `AGENTS.md`) to the `_setup_fake_repo` helper in `test_init_scaffolds.py`, updated the existing `test_sync_script_replaces_project_with_empty_lifecycle_skeleton` test to expect these two files in the project scaffold output, and added a new `test_sync_script_copies_project_guidance_files_from_source` test asserting exact content match between source and scaffold. Tests failed red as expected. Implementation added a `source` parameter to `_replace_project_skeleton` in `sync_init_scaffolds.py` and a loop at the end of that function that uses `shutil.copy2` to copy `CLAUDE.md` and `AGENTS.md` from `sources/project/` into the generated scaffold directory. Tests went green. Ran the sync script to generate the actual `cli/src/ai_team/init/scaffolds/project/CLAUDE.md` and `AGENTS.md` files.

Cycle 2 (AC-3 & AC-4): Added four tests to `test_init.py`: `test_init_creates_project_guidance_files` (init writes both files), `test_init_dry_run_includes_project_guidance_files` (dry-run output lists them), `test_init_refuses_when_project_guidance_file_exists_without_force` (collision refusal), `test_init_force_overwrites_project_guidance_files` (force permits overwrite). All four passed immediately without any `init.py` changes — the existing `_plan_copies(scaffolds_path / "project", ...)` mechanism already handles any files present in the project scaffold directory, so adding the generated files was sufficient.

Applied `ruff format` correction in a tidy-up commit after the main cycles.

**Tried and rejected:** No alternative approaches were considered; the existing `_plan_copies` mechanism made the init-command side of AC-3 and AC-4 trivially correct once the scaffolds existed.

**What remains:** Nothing. All four ACs have passing tests. The verification command (`sync_init_scaffolds.py` + pytest + ruff) passes clean.

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

Both stages passed.

**Stage 1 — Spec compliance:**
- AC-1 met: `_replace_project_skeleton` now copies `sources/project/CLAUDE.md` into the generated scaffold directory via `shutil.copy2`, with a `FileNotFoundError` guard if the source is absent.
- AC-2 met: Same mechanism copies `sources/project/AGENTS.md`.
- AC-3 met: The existing `_plan_copies(scaffolds_path / "project", ...)` in `commands/init.py` iterates all files in the project scaffold directory, so the two newly generated files are automatically planned as init outputs — no changes to `init.py` were required and none were made.
- AC-4 met: The collision-detection path in `commands/init.py` is unchanged; the new files participate in it through the same mechanism, confirmed by `test_init_refuses_when_project_guidance_file_exists_without_force` and `test_init_force_overwrites_project_guidance_files`.
- Only the five files listed in "Files to Touch" plus the task file itself were modified. No unspecified files were touched.
- The generated scaffold files (`scaffolds/project/CLAUDE.md` and `scaffolds/project/AGENTS.md`) exactly match their sources under `sources/project/`.

**Stage 2 — Code quality:**
- Correctness: `FileNotFoundError` guard in `_replace_project_skeleton` correctly fails fast if a source file is missing. Logic is sound.
- Tests: 28 tests pass. New tests cover both success paths (AC-1/AC-2 content match, AC-3 init output, AC-3 dry-run listing, AC-4 force overwrite) and the failure path (AC-4 collision refusal). Tests are independent.
- Security: No secrets, no external input, no queries. Not applicable.
- Readability: Names are descriptive, the loop over `("CLAUDE.md", "AGENTS.md")` is clear, error messages are precise.
- Performance: No concerns for a build-time script.
- Verification command (`sync_init_scaffolds.py` + `pytest` + `ruff format --check` + `ruff check`) ran clean locally against the task branch.
