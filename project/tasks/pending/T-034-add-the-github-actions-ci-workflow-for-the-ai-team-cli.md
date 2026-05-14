---
id: T-034
title: Add the GitHub Actions CI workflow for the ai-team CLI
status: pending
priority: medium
assigned-role: developer
created: '2026-05-14'
---

# Add the GitHub Actions CI workflow for the ai-team CLI

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

Per approved spec S-001
(`project/specs/github-actions-ci-for-cli-tests-and-ruff-formatting-checks.md`, Phase 2),
create the CI workflow. The repo has no `.github/` directory yet — this task creates it.

Create `.github/workflows/ci.yml`:

- Triggers: `pull_request` (any branch) and `push` to `main`.
- Two independent jobs, both `runs-on: self-hosted`:
  - `lint` — runs `uv run ruff format --check .` and `uv run ruff check .` from `cli/`.
  - `test` — runs `uv run pytest` from `cli/`.
- Each job: `actions/checkout` → `astral-sh/setup-uv` (provisions uv + Python 3.14) →
  `uv sync` in `cli/` → the job's command(s).
- Pin `actions/checkout` and `astral-sh/setup-uv` to their current major versions
  (resolves spec S-001's open `[TODO]` on action versions — check the latest major).
- CI is check-only: no auto-fix, no commit-back.

Note: spec S-001 Phase 3 (verifying a real PR run on the registered self-hosted runner,
and confirming the runner has network access for `setup-uv`) is post-merge human/
operational acceptance — it is not part of this task.

## Acceptance Criteria

AC-1: The repository shall contain a `.github/workflows/ci.yml` file that parses as valid YAML.
AC-2: The `ci.yml` workflow shall trigger on `pull_request` events and on `push` events to the `main` branch.
AC-3: The `ci.yml` workflow shall define a `lint` job with `runs-on: self-hosted` that executes `ruff format --check` and `ruff check` against `cli/`.
AC-4: The `ci.yml` workflow shall define a `test` job with `runs-on: self-hosted` that executes `pytest` against `cli/`.
AC-5: WHERE a job provisions its toolchain THE SYSTEM SHALL use `astral-sh/setup-uv` pinned to a major version to install uv and Python 3.14.

## Dependencies

- `T-033` — the existing `cli/` code must be Ruff-compliant first, so the `lint` job is green on the workflow's first run

## Files to Touch

- `.github/workflows/ci.yml` — new CI workflow file (creates the `.github/workflows/` directory)

## Verification

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml')); print('valid YAML')"
grep -q 'runs-on: self-hosted' .github/workflows/ci.yml
grep -qE '^\s{2}lint:' .github/workflows/ci.yml
grep -qE '^\s{2}test:' .github/workflows/ci.yml
grep -q 'astral-sh/setup-uv' .github/workflows/ci.yml
grep -q 'pull_request' .github/workflows/ci.yml
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
