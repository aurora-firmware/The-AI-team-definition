---
title: GitHub Actions CI for CLI tests and Ruff formatting checks
version: '0.1'
status: approved  # draft | review | approved | superseded
created: '2026-05-14'
author: planner
id: S-010
---

# GitHub Actions CI for CLI tests and Ruff formatting checks

## Purpose

The `ai-team` CLI under `cli/` has a pytest suite but nothing runs it automatically,
and the project has no formatter or linter configured at all. Defects and style
drift are only caught when a human or agent remembers to run tests locally.

This specification adds a GitHub Actions continuous-integration workflow that runs
the CLI test suite and enforces formatting/lint checks on every pull request and on
every push to `main`. It also adopts Ruff as the project's formatter and linter,
since none exists today.

Expected outcome: every pull request and every `main` push gets an automated,
check-only signal covering (1) `pytest` correctness and (2) Ruff format + lint
compliance for `cli/`, executed on the project's registered self-hosted runner.

## Exclusions

What this specification explicitly does NOT cover:

- **Markdown linting.** The repository is mostly markdown (skills, agents,
  `ai-process/`, guides), but linting that content is out of scope — it needs its
  own linter selection and rule-set decision.
- **Generated-docs consistency check.** Verifying that `cli/scripts/gen_docs.sh`
  output is current is not part of this workflow; it can be added later as an extra
  job.
- **Auto-format-and-commit-back.** CI is strictly check-only. It never mutates a
  branch — on a violation it fails the job and the developer fixes and re-pushes.
- **CI on `dev-agent` or task/bug branches.** Triggers are limited to
  `pull_request` and `push` to `main`. The `integrate`-skill workflow that merges
  task/bug branches into `dev-agent` is unchanged and gains no CI gate here.
- **Changes to the `integrate` skill or any agent/skill definition.** This is
  additive infrastructure only.

## Architecture

### Design Principles

- **Check-only.** CI observes and reports; it never writes to the repository.
- **Independent signals.** Test failures and lint failures are reported separately
  so one never masks the other.
- **Self-contained runner setup.** The workflow provisions its own `uv` and Python
  toolchain rather than assuming the self-hosted runner has them — the runner is
  shared infrastructure and currently only known to do container image builds.
- **Single source of truth for tooling config.** Ruff configuration lives in
  `cli/pyproject.toml`; the workflow invokes Ruff with no inline rule overrides.
- **Start green.** The existing `cli/` code is brought into Ruff compliance in the
  same change set, so the first CI run on a check-only policy is not red.

### System Diagram

```
                     trigger: pull_request | push to main
                                   │
                                   ▼
                  .github/workflows/ci.yml  (runs-on: self-hosted)
                                   │
              ┌────────────────────┴────────────────────┐
              ▼                                         ▼
        job: lint                                  job: test
   checkout                                   checkout
   astral-sh/setup-uv (uv + Python 3.14)       astral-sh/setup-uv (uv + Python 3.14)
   uv sync (in cli/)                           uv sync (in cli/)
   ruff format --check .                       uv run pytest
   ruff check .
              │                                         │
              ▼                                         ▼
     pass/fail status check               pass/fail status check
              └────────────────────┬────────────────────┘
                                   ▼
                   PR / commit shows two independent checks
```

### Responsibility Separation

| Component | Responsibility | Notes |
|---|---|---|
| `.github/workflows/ci.yml` | Defines triggers and the `lint` + `test` jobs | The only workflow file added |
| `lint` job | Runs `ruff format --check` and `ruff check` over `cli/` | Fails on any formatting or lint violation |
| `test` job | Runs `uv run pytest` for the `ai-team` CLI | Fails on any test failure |
| `cli/pyproject.toml` | Declares Ruff as a dev dependency and holds `[tool.ruff]` config | Single source of truth for lint/format rules |
| One-time formatting pass | Brings existing `cli/` code into Ruff compliance | Committed with the workflow so CI starts green |

## Components

### Component 1: CI workflow file

**Purpose:** A single `.github/workflows/ci.yml` defining two independent
`self-hosted` jobs — `lint` and `test`.
**Estimated size:** Small — one YAML file, ~50–70 lines.
**Interfaces:**
- Consumes: `pull_request` events and `push` events on `main`; the registered
  self-hosted runner; `astral-sh/setup-uv` action; the `cli/` project (`pyproject.toml`,
  `uv.lock`, tests, source).
- Exposes: two GitHub status checks (`lint`, `test`) on PRs and `main` commits.
- Each job: `actions/checkout` → `astral-sh/setup-uv` (pinned, configured for Python
  3.14) → `uv sync` within `cli/` → the job's check command(s).

### Component 2: Ruff tooling adoption

**Purpose:** Introduce Ruff as the project's formatter and linter and bring the
existing codebase into compliance.
**Estimated size:** Small-to-medium — a dependency addition plus a `[tool.ruff]`
config block, then a mechanical reformat whose diff size depends on how far current
code drifts from Ruff defaults.
**Interfaces:**
- Adds `ruff` to `[dependency-groups] dev` in `cli/pyproject.toml`.
- Adds a `[tool.ruff]` section: `target-version` aligned with `requires-python`
  (Python 3.14), a line length, and an explicit lint rule selection (start from
  Ruff's default `E`/`F` plus a small, agreed set; exact rules are an
  implementation detail to be pinned during the task, `[TODO]`).
- A one-time `ruff format` + `ruff check --fix` pass over `cli/`, committed
  alongside the workflow so `ruff format --check` / `ruff check` pass on the first
  CI run.

## Workflow

```
Developer pushes a branch and opens a PR (or a commit lands on main)
  ↓
GitHub dispatches ci.yml to the self-hosted runner
  ↓
lint job and test job each: checkout → setup-uv → uv sync
  ↓
lint: ruff format --check + ruff check        test: uv run pytest
  ↓
Each job reports an independent pass/fail status check
  ↓
On failure: developer fixes locally and re-pushes (CI never auto-fixes)
On success: both checks green — human Gate / integrate proceeds as before
```

## Configuration

```yaml
# .github/workflows/ci.yml  (shape — exact pinned action versions resolved in the task)
name: CI

on:
  pull_request:
  push:
    branches: [main]

jobs:
  lint:
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5      # provisions uv; installs Python 3.14
        with:
          python-version: "3.14"
      - name: Install dependencies
        run: uv sync
        working-directory: cli
      - name: Ruff format check
        run: uv run ruff format --check .
        working-directory: cli
      - name: Ruff lint
        run: uv run ruff check .
        working-directory: cli

  test:
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with:
          python-version: "3.14"
      - name: Install dependencies
        run: uv sync
        working-directory: cli
      - name: Run tests
        run: uv run pytest
        working-directory: cli
```

```toml
# cli/pyproject.toml additions (shape)

[dependency-groups]
dev = [
    "pytest>=8",
    "typer-cli>=0.24.0",
    "ruff>=0.6",            # exact floor pinned in the task
]

[tool.ruff]
target-version = "py314"
line-length = 88            # confirm during implementation

[tool.ruff.lint]
select = ["E", "F"]         # [TODO] confirm the full rule selection
```

## Implementation Order

| Phase | What | Depends On |
|---|---|---|
| 1 | Add Ruff to `cli/pyproject.toml` dev deps + `[tool.ruff]` config block; run the one-time `ruff format` + `ruff check --fix` pass over `cli/` and commit the result | Nothing |
| 2 | Add `.github/workflows/ci.yml` with the `lint` and `test` jobs | Phase 1 (so `lint` is green on first run) |
| 3 | Verify on a real pull request that both `lint` and `test` checks appear, run on the self-hosted runner, and pass | Phase 2 |

## Open Questions

- `[TODO]` Exact Ruff lint rule selection beyond the `E`/`F` defaults — pin during
  Phase 1 so the one-time fix pass and CI agree.
- `[TODO]` Pinned versions for `astral-sh/setup-uv` and `actions/checkout` — resolve
  to current major versions during Phase 2.
- `[TODO]` Confirm the self-hosted runner has outbound network access for
  `setup-uv` to fetch `uv` and Python 3.14; if it is air-gapped, Phase 2 needs an
  alternative provisioning step.

## Amendment Log

<!-- Optional. Use when an approved spec is amended after tasks are in flight.
| Date | What changed | Why | Affected tasks |
|------|-------------|-----|----------------|
| YYYY-MM-DD | Description of change | Reason for amendment | T-XXX, T-YYY |
-->
