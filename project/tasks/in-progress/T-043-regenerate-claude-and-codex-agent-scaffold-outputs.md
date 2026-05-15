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
