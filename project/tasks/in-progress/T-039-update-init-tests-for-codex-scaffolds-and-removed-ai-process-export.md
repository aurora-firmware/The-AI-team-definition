---
id: T-039
title: Update init tests for Codex scaffolds and removed ai-process export
status: pending
priority: medium
assigned-role: developer
created: '2026-05-14'
---

# Update init tests for Codex scaffolds and removed ai-process export

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

Update the CLI test suite for the new init contract from S-001. The tests should prove
that `ai-team init` can scaffold Claude and Codex package assets, that Codex skills are
real files rather than symlinks, and that ai-process export behavior is gone.

This task should not change production init behavior; T-038 owns that. It may adjust
test expectations that currently assume `include_ai_process` is recorded in the marker.

## Acceptance Criteria

AC-1: WHEN `ai-team init --tools codex --no-interactive` runs in tests THE SYSTEM SHALL create `.codex/agents/` and `.codex/skills/` in the target repo.
AC-2: WHEN Codex skills are scaffolded THE SYSTEM SHALL verify they are real files or directories and not symlinks to `.claude`.
AC-3: WHEN `ai-team init --tools all --no-interactive` runs in tests THE SYSTEM SHALL create both `.claude/` and `.codex/` scaffold trees.
AC-4: The system shall assert that `.ai-team.toml` no longer contains `include_ai_process`.
AC-5: IF `--include-ai-process` is passed in tests THEN THE SYSTEM SHALL assert the command fails.

## Dependencies

- `T-042` — generated Codex skill scaffolds must exist before init can copy them in tests
- `T-043` — generated Codex agent scaffolds must exist before init can copy them in tests
- `T-038` — init behavior must remove ai-process export before tests can pass

## Files to Touch

- `cli/tests/test_init.py` — update init behavior coverage
- `cli/tests/test_cli_bootstrap.py` — update package-data reachability checks for Codex scaffold package data

## Verification

```bash
cd cli
uv run pytest tests/test_init.py tests/test_cli_bootstrap.py
uv run ruff check tests/test_init.py tests/test_cli_bootstrap.py
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
