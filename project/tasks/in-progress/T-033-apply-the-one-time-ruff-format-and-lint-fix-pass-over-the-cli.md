---
id: T-033
title: Apply the one-time Ruff format and lint-fix pass over the CLI
status: in-progress
priority: medium
assigned-role: developer
created: '2026-05-14'
---

# Apply the one-time Ruff format and lint-fix pass over the CLI

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

With Ruff configured by T-032, bring the existing `cli/` codebase into compliance so the
check-only CI added by T-034 starts green. Per approved spec S-001
(`project/specs/github-actions-ci-for-cli-tests-and-ruff-formatting-checks.md`, Phase 1).

This is a **mechanical** pass — no hand-editing of logic:

- From `cli/`, run `uv run ruff format .` to apply formatting.
- Then run `uv run ruff check --fix .` to apply safe lint autofixes (import sorting, etc.).
- Inspect the resulting diff to confirm it is purely formatting / import-ordering churn
  with no behavioural change.
- If `ruff check` reports violations that `--fix` cannot resolve, fix them minimally by
  hand without changing behaviour.
- Re-run the test suite to confirm the reformat introduced no regressions.

Do not modify `cli/pyproject.toml` — its Ruff config is owned by T-032. This task
intentionally stays one task even though it touches many `.py` files: it is a single bulk
mechanical operation, and splitting it per-file would create artificial fragmentation.

## Acceptance Criteria

AC-1: WHEN `uv run ruff format --check .` is executed in `cli/` THE SYSTEM SHALL exit 0 with no files needing formatting.
AC-2: WHEN `uv run ruff check .` is executed in `cli/` THE SYSTEM SHALL exit 0 with no reported violations.
AC-3: WHEN `uv run pytest` is executed in `cli/` THE SYSTEM SHALL pass all tests, with no regressions introduced by the reformat.
AC-4: The task shall not modify `cli/pyproject.toml`.

## Dependencies

- `T-032` — adds Ruff as a dev dependency and the `[tool.ruff]` config that determines the rules applied here

## Files to Touch

- `cli/src/**/*.py` — mechanical formatting and import-ordering changes only
- `cli/tests/**/*.py` — mechanical formatting and import-ordering changes only

## Verification

```bash
cd cli
uv run ruff format --check .
uv run ruff check .
uv run pytest
# AC-4 is confirmed by the reviewer: the branch diff must show no change to cli/pyproject.toml
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-05-14

Executed the one-time Ruff cleanup pass for `cli/` in two TDD-style red→green→refactor cycles and committed each cycle on `task/T-033-apply-the-one-time-ruff-format-and-lint-fix-pass-over-the-cli`.

Cycle 1 (format): ran `uv run ruff format --check .` (red, 33 files needed formatting), applied `uv run ruff format .`, re-ran `--check` (green), reviewed diff scope (mechanical formatting only), and committed.

Cycle 2 (lint): ran `uv run ruff check .` (red with import-order issues and E501 line-length violations), applied `uv run ruff check --fix .` (auto-fixed import/unused-import issues), then manually fixed remaining non-auto-fixable E501 violations by wrapping long strings/docstrings/comments without behavior changes. Re-ran `uv run ruff check .` (green), then ran full `uv run pytest` (green, 211 passed), and committed.

Tried and rejected: relying on Ruff autofix alone for AC-2, because `E501` violations remained and required minimal manual wraps.

Remaining work: none from developer side; ready for reviewer. `pyproject.toml` was not modified.

### Session 2 — 2026-05-14

Addressed the review failure by syncing `task/T-033-apply-the-one-time-ruff-format-and-lint-fix-pass-over-the-cli` with `dev-agent` via a non-destructive merge (`git merge --no-edit dev-agent`). This preserved the canonical lifecycle content for `project/tasks/in-progress/T-033-apply-the-one-time-ruff-format-and-lint-fix-pass-over-the-cli.md` (including the existing Work Log and Review sections) without reverting or rewriting implementation commits. I verified the branch diff no longer removes lifecycle entries from the canonical task file.

What I tried and rejected: manually editing the task file to re-add missing blocks was rejected in favor of branch sync, because the requirement is to preserve canonical content from `dev-agent` rather than reconstructing by hand. Also rejected rebase/cherry-pick because a direct merge cleanly preserved both histories in one step.

What remains: no developer-side code changes remain for this fix; branch is ready for the loop to append this Session 2 entry on `dev-agent` and proceed.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-05-14
FAIL

- **File and location**: `project/tasks/in-progress/T-033-apply-the-one-time-ruff-format-and-lint-fix-pass-over-the-cli.md`, `### Session 1 — 2026-05-14` block (removed in branch diff vs `dev-agent`).
- **What is wrong**: The implementation branch diff includes deletion of the existing canonical task work-log entry from `dev-agent`. This is an unexpected non-implementation regression in canonical lifecycle content.
- **What should change**: Rebase/merge `dev-agent` into `task/T-033-apply-the-one-time-ruff-format-and-lint-fix-pass-over-the-cli`, preserve the canonical task file content, and resubmit with a diff that only contains the intended mechanical Ruff cleanup changes.
