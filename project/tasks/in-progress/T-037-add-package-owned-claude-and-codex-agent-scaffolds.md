---
id: T-037
title: Add package-owned Claude and Codex agent scaffolds
status: pending
priority: medium
assigned-role: developer
created: '2026-05-14'
---

# Add package-owned Claude and Codex agent scaffolds

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

Spec S-001 keeps agent generation out of scope but requires the CLI package to own the
Claude and Codex agent scaffold assets it exports. Add package-owned agent source files
for both tools under `cli/src/ai_team/init/sources/agents/`.

This task owns only agent source assets and source-level tests. It must not update the
generated/copied scaffold output trees; T-043 owns refreshing
`scaffolds/claude/agents/**` and `scaffolds/codex/agents/**`.

Do not alter role semantics while moving the product source copy.

## Acceptance Criteria

AC-1: The system shall store Claude agent source files under `cli/src/ai_team/init/sources/agents/claude/`.
AC-2: The system shall store Codex agent source files under `cli/src/ai_team/init/sources/agents/codex/`.
AC-3: WHEN source-level scaffold tests run THE SYSTEM SHALL verify every exported role has both Claude and Codex agent source files.
AC-4: The system shall not modify `cli/src/ai_team/init/scaffolds/claude/agents/` or `cli/src/ai_team/init/scaffolds/codex/agents/` in this task.
AC-5: The system shall preserve the current exported agent role semantics in the package-owned source files.

## Dependencies

- `T-035` — package-owned scaffold source generator must exist first
- `T-036` — source-level scaffold tests in `cli/tests/test_init_scaffolds.py` must be extended in order after the skill-source task to avoid overlapping pending edits

## Files to Touch

- `cli/src/ai_team/init/sources/agents/claude/**` — package-owned Claude agent sources
- `cli/src/ai_team/init/sources/agents/codex/**` — package-owned Codex agent sources
- `cli/tests/test_init_scaffolds.py` — source-level coverage for required agent source files

## Verification

```bash
cd cli
uv run pytest tests/test_init_scaffolds.py
uv run ruff check tests/test_init_scaffolds.py
git diff --name-only -- src/ai_team/init/scaffolds/claude/agents src/ai_team/init/scaffolds/codex/agents
# final git diff command should print nothing for this task
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-05-14
Implemented T-037 by adding package-owned agent source assets under `cli/src/ai_team/init/sources/agents/claude/` and `cli/src/ai_team/init/sources/agents/codex/`, plus source-level coverage in `cli/tests/test_init_scaffolds.py` that enforces role parity across both tools and semantic parity with currently exported agent definitions. I followed TDD: first added the new parity test and verified it failed because the source agent trees did not exist; then added the source files and verified the targeted test passed; finally ran full task verification (`pytest`, `ruff`, and scaffold-agent diff check) successfully.

What I tried and rejected: I avoided modifying generated scaffold output trees (`src/ai_team/init/scaffolds/claude/agents/**` and `.../codex/agents/**`) because AC-4 forbids that in this task, and I also rejected copying Claude sources from `.claude/agents` because exported scaffold semantics are currently defined by `scaffolds/claude/agents` and must be preserved exactly for this migration step.

What remains: record this Work Log entry on canonical `dev-agent` task state and proceed to review.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-05-14
PASS

- Stage 1 (acceptance criteria): PASS. The branch diff `dev-agent...task/T-037-add-package-owned-claude-and-codex-agent-scaffolds` adds Claude sources at `cli/src/ai_team/init/sources/agents/claude/*.md` and Codex sources at `cli/src/ai_team/init/sources/agents/codex/*.toml`, extends `cli/tests/test_init_scaffolds.py` to enforce role coverage and semantic parity, and does not modify `cli/src/ai_team/init/scaffolds/claude/agents/` or `cli/src/ai_team/init/scaffolds/codex/agents/`.
- Stage 2 (code quality): PASS. Source-level parity test is deterministic and checks both role-set parity and file-content parity; verification commands passed (`uv run pytest tests/test_init_scaffolds.py`, `uv run ruff check tests/test_init_scaffolds.py`).
