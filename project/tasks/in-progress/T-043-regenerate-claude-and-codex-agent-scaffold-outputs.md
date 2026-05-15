---
id: T-043
title: Regenerate Claude and Codex agent scaffold outputs
status: pending
priority: medium
assigned-role: developer
created: '2026-05-14'
---

# Regenerate Claude and Codex agent scaffold outputs

<!--
Task Quality Rules (see the new-task skill for full details):
  - Atomic — one clear outcome.
  - One-shottable — ≤ 3–4 files touched, ≤ 5 ACs, Description ≈ 20 lines.
  - Verifiable — concrete Verification command or explicit manual steps.
  - Self-contained — Description is enough to start without follow-up questions.
  - EARS — every AC matches one of the five patterns below.
  - Dependency-honest — list every prior task this one reads from or modifies.
-->

## Description

Run the package-owned scaffold generator after T-037 has migrated Claude and Codex agent
source assets. This task owns the generated/copied agent scaffold outputs only. It
should not change canonical agent source files or generator logic.

The generated Codex agent scaffold must be package-owned real files, not a symlink or
reference to the root `.codex/` directory.

## Acceptance Criteria

AC-1: WHEN the scaffold generator runs THE SYSTEM SHALL populate `cli/src/ai_team/init/scaffolds/claude/agents/` from package-owned Claude sources.
AC-2: WHEN the scaffold generator runs THE SYSTEM SHALL populate `cli/src/ai_team/init/scaffolds/codex/agents/` from package-owned Codex sources.
AC-3: The system shall store generated Codex agent scaffold files as real files, not symlinks.
AC-4: WHEN the scaffold generator runs twice THE SYSTEM SHALL leave no additional diff after the second run.
AC-5: The system shall not modify `cli/src/ai_team/init/sources/agents/**` in this task.

## Dependencies

- `T-035` — package-owned scaffold source generator must exist first
- `T-037` — Claude and Codex agent source files must exist before output generation

## Files to Touch

- `cli/src/ai_team/init/scaffolds/claude/agents/**` — generated/copied Claude agent scaffolds
- `cli/src/ai_team/init/scaffolds/codex/agents/**` — generated/copied Codex agent scaffolds

## Verification

```bash
cd cli
python scripts/sync_init_scaffolds.py
test -f src/ai_team/init/scaffolds/claude/agents/planner.md
test -f src/ai_team/init/scaffolds/codex/agents/planner.toml
test ! -L src/ai_team/init/scaffolds/codex/agents/planner.toml
git diff -- src/ai_team/init/scaffolds/claude/agents src/ai_team/init/scaffolds/codex/agents > /tmp/t043-before.diff
python scripts/sync_init_scaffolds.py
git diff -- src/ai_team/init/scaffolds/claude/agents src/ai_team/init/scaffolds/codex/agents > /tmp/t043-after.diff
cmp /tmp/t043-before.diff /tmp/t043-after.diff
uv run pytest tests/test_init_scaffolds.py
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-05-15

The task required populating the Claude and Codex agent scaffold outputs under `cli/src/ai_team/init/scaffolds/claude/agents/` and `cli/src/ai_team/init/scaffolds/codex/agents/` by running the package-owned generator script.

On inspection, the Claude agent scaffolds (`architect.md`, `developer.md`, `integrator.md`, `planner.md`, `reviewer.md`) were already committed — they had been generated in a prior session. The Codex agent scaffolds directory (`codex/agents/`) was missing entirely; only the `codex/skills/` directory existed under scaffolds.

Running `python3 scripts/sync_init_scaffolds.py` created the five Codex agent TOML files as real (non-symlink) files using `shutil.copytree`, which satisfies AC-1 through AC-3 and AC-5 without any generator changes.

For the TDD cycle, I audited the existing tests and found that AC-3 (real files, not symlinks), AC-4 (idempotency), and AC-5 (sources unchanged) had no coverage. I added three new tests to `cli/tests/test_init_scaffolds.py` before verifying that the generator's behaviour already satisfied them — the tests pass because `shutil.copytree` produces real files, the `_replace_tree` helper removes and recreates the destination (idempotent), and the generator only touches `scaffolds/`, never `sources/`. The full task verification commands all confirmed `PASS`. One commit was made on the task branch.

Nothing remains — all five acceptance criteria are satisfied and all 8 tests pass.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-05-15

PASS

Both stages passed.

**Stage 1 — Spec compliance**

- AC-1: The five Claude agent scaffold files (`architect.md`, `developer.md`, `integrator.md`, `planner.md`, `reviewer.md`) are present under `cli/src/ai_team/init/scaffolds/claude/agents/` and their blob hashes match the package-owned sources exactly. Met.
- AC-2: The five Codex agent scaffold files (`architect.toml`, `developer.toml`, `integrator.toml`, `planner.toml`, `reviewer.toml`) were created under `cli/src/ai_team/init/scaffolds/codex/agents/` by running `sync_init_scaffolds.py`. Their blob hashes match the package-owned Codex sources exactly. Met.
- AC-3: No symlinks were found under `cli/src/ai_team/init/scaffolds/codex/agents/`. Git stores all five files as regular blobs (mode `100644`). The new test `test_sync_script_generates_codex_agent_scaffolds_as_real_files_not_symlinks` also confirms this at execution time. Met.
- AC-4: The idempotency test `test_sync_script_is_idempotent_for_agent_scaffolds` captures file contents before and after a second run and asserts equality for both Claude and Codex agent directories. Met.
- AC-5: The T-043 commit (`08f0467`) touches no files under `cli/src/ai_team/init/sources/agents/`. The sources directory contents before and after generation are verified by `test_sync_script_does_not_modify_sources_directory`. Met.

No unspecified functionality was added. The test file modification (`cli/tests/test_init_scaffolds.py`) is explicitly justified in the Work Log as a TDD cycle to cover AC-3, AC-4, and AC-5, which had no prior coverage. Files touched are within the stated scope.

**Stage 2 — Code quality**

- Correctness: Each new test uses `_setup_fake_repo(tmp_path)` for a fully isolated fake repo, runs the generator via subprocess, and makes precise assertions. The idempotency test captures before/after snapshots using `dict[str, str]` content maps — correctly handles both file presence and content equality. No logic errors found.
- Tests: Three new tests cover AC-3 (no symlinks), AC-4 (idempotency), and AC-5 (sources unchanged). All 8 tests in `test_init_scaffolds.py` pass. Tests are independent — each uses `tmp_path` with no shared mutable state.
- Security: No secrets, no external input, no queries. Not applicable.
- Readability: Test names are descriptive and match their docstrings. `collect_file_contents` helper is defined locally within each test that needs it — appropriately scoped. No dead code.
- Performance: Subprocess calls run against a small fake repo; no resource leaks. Not a concern here.
