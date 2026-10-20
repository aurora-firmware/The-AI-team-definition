---
title: GitHub Actions CI for CLI tests and Ruff formatting checks
version: '0.2'
status: approved  # draft | review | approved | superseded
created: '2026-05-14'
author: planner
id: S-010
---

# GitHub Actions CI for CLI tests and Ruff formatting checks

## Purpose

The `ai-team` CLI under `cli/` has a pytest suite, a generated command reference and
a Ruff configuration, but none of them is checked unless a human or agent remembers to
run them locally, and releases would otherwise be built by hand.

This specification defines the GitHub Actions continuous-integration workflow
(`.github/workflows/ci.yml`) that runs the CLI test suite, enforces Ruff formatting and
lint checks, and checks that the generated command reference is current on every pull
request and every push to `main`, and that builds and publishes a GitHub Release when
a version tag is pushed. Ruff is the project's formatter and linter.

Expected outcome: every pull request and every `main` push gets independent `lint` and
`test` checks, executed on the project's self-hosted runner; a version tag that passes
both produces a GitHub Release carrying the built packages and the command reference.

## Exclusions

What this specification explicitly does NOT cover:

- **Markdown linting.** The repository is mostly markdown (skills, agents,
  `ai-process/`, guides), but linting that content is out of scope — it needs its
  own linter selection and rule-set decision.
- **Auto-format-and-commit-back.** CI never commits or pushes to any branch. On a
  violation it fails the job and the developer fixes and re-pushes.
- **CI on `dev-agent` or task/bug branches.** Triggers are limited to pull requests,
  pushes to `main`, and version tags. The `integrate`-skill workflow that merges
  task/bug branches into `dev-agent` is unchanged and gains no CI gate here.
- **Changes to the `integrate` skill or any agent/skill definition.** This is
  infrastructure only.
- **Publishing to a package index.** A release attaches its files to the GitHub
  Release only.

## Architecture

### Design Principles

- **No writes to the repository.** CI observes and reports. The only thing it
  publishes is a GitHub Release for a version tag; it never commits or pushes.
- **Independent signals.** Test failures and lint failures are reported as separate
  checks so one never masks the other.
- **Self-contained runner setup.** Each job runs in a container image that provides
  `uv` and Python 3.14, so nothing is assumed about the shared self-hosted runner
  beyond Docker support and network access to pull that image.
- **Single source of truth for tooling config.** Ruff configuration lives in
  `cli/pyproject.toml`; the workflow invokes Ruff with no inline rule overrides.
- **Releases are gated.** The release job runs only for a version tag and only after
  `lint` and `test` pass.

### System Diagram

```
        trigger: pull_request | push to main | push of a version tag
                                   │
                                   ▼
             .github/workflows/ci.yml  (self-hosted docker runner,
                                        uv + Python 3.14 container)
                                   │
              ┌────────────────────┴────────────────────┐
              ▼                                         ▼
        job: lint                                  job: test
   checkout, uv sync (cli/)                   checkout, uv sync (cli/)
   ruff format --check, ruff check            uv run pytest
   regenerate commands.md, fail on diff
              └────────────────────┬────────────────────┘
                                   ▼ (version tags only, both passed)
                             job: release
   full-history checkout, version from tag, uv build,
   regenerate commands.md, publish GitHub Release
```

### Responsibility Separation

| Component | Responsibility | Notes |
|---|---|---|
| `.github/workflows/ci.yml` | Defines the triggers and the `lint`, `test` and `release` jobs | The only workflow file |
| `lint` job | Ruff format check, Ruff lint, and the generated-docs drift check over `cli/` | Fails on any violation or drift |
| `test` job | Runs the CLI test suite | Fails on any test failure |
| `release` job | Builds and publishes a GitHub Release for a version tag | Needs `lint` and `test`; the only job the workflow grants write permission |
| `cli/pyproject.toml` | Declares Ruff as a dev dependency and holds the Ruff configuration | Single source of truth for lint/format rules |

## Components

### Component 1: CI workflow file

**Purpose:** `.github/workflows/ci.yml`, defining the `lint`, `test` and `release`
jobs.
**Estimated size:** Small — one YAML file (delivered).
**Interfaces:**
- **Triggers** (`ci.yml:3-10`): every pull request; pushes to `main`; pushes of tags
  of the form `MAJOR.MINOR.PATCH` or `MAJOR.MINOR.PATCH-<suffix>`.
- **Runner** (`ci.yml:17-18`): each job runs on a self-hosted runner labelled
  `self-hosted` and `docker`, inside the `ghcr.io/astral-sh/uv:python3.14-trixie-slim`
  container. The runner therefore needs network access to pull that image and the
  packages the jobs install; it has it today.
- **Each job** installs git in the container and checks out the repository with
  `actions/checkout@v6`; `lint` and `test` then run `uv sync` in `cli/` before their
  own steps, while `release` builds with `uv build` without a separate sync. `lint`
  and `test` use the action's default shallow checkout, so no test may depend on git
  history beyond the checked-out commit; only `release` fetches full history
  (`ci.yml:67-69`). Builds outside a tag use a placeholder package version
  (`ci.yml:12-13`).
- **`lint`** (`ci.yml:16-41`): `uv run ruff format --check .` and `uv run ruff check .`
  in `cli/`, then regenerates `cli/docs/commands.md` with `cli/scripts/gen_docs.sh`
  and fails, naming the fix, when it differs from the committed file (S-008).
- **`test`** (`ci.yml:43-55`): `uv run pytest` in `cli/`.
- **`release`** (`ci.yml:57-96`): runs only for a tag and after `lint` and `test`
  pass, with `contents: write` permission. It maps the tag to a PEP 440 version (a
  `-` suffix becomes a `+` local version), builds the wheel and source distribution
  with `uv build`, regenerates `commands.md`, and publishes a GitHub Release named
  after the tag, with generated release notes and the wheel, source distribution and
  `commands.md` attached. It commits nothing.
- **Exposes:** `lint` and `test` status checks on pull requests and `main` commits.

### Component 2: Ruff tooling

**Purpose:** Ruff is the project's formatter and linter, and `cli/` complies with it.
**Estimated size:** Small (delivered).
**Interfaces** (`cli/pyproject.toml:47-60`):
- `ruff` is in the `dev` dependency group.
- Ruff targets Python 3.14, matching `requires-python`, with a line length of 88.
- The lint rule selection is `E`, `F` and `I` (pycodestyle errors, Pyflakes, import
  sorting), with `E501` (line too long) ignored, so line length is left to the
  formatter.

## Workflow

```
Developer pushes a branch and opens a PR (or a commit lands on main)
  ↓
GitHub dispatches ci.yml to the self-hosted runner
  ↓
lint and test jobs each: container → checkout → uv sync
  ↓
lint: ruff format --check + ruff check + commands.md drift check
test: uv run pytest
  ↓
Each job reports an independent pass/fail status check
  ↓
On failure: developer fixes locally and re-pushes (CI never auto-fixes)
On success: both checks green — human review proceeds as before

★ Human pushes a version tag
  ↓
lint and test run as above; on success release builds and publishes the GitHub Release
```

## Configuration

**Self-hosted runner**
- **What must exist:** a runner registered for the repository with the `self-hosted`
  and `docker` labels.
- **Where it lives:** the repository's GitHub Actions runner settings.
- **Constraints:** must run job containers and reach `ghcr.io` and the package mirrors
  the jobs install from.
- **Missing-value behaviour:** jobs stay queued and no check reports.

**Release permission**
- **What must exist:** `contents: write` for the release job only.
- **Where it lives:** the job's `permissions` in the workflow file.
- **Constraints:** the release job is the only job the workflow grants write permission.
- **Missing-value behaviour:** publishing the Release fails; nothing else is affected.

## Implementation Order

All phases are delivered: Ruff adoption with the one-time formatting pass, the
workflow with `lint` and `test`, and verification on a real pull request. The
generated-docs drift check and the `release` job were added to the workflow later
(see the Amendment Log). Later changes follow the amendment flow.

## Open Questions

None. The three questions left open at approval are answered from the repository
(CR-003):

- **Ruff rule selection:** `E`, `F`, `I`, ignoring `E501` (`cli/pyproject.toml:58-60`).
- **Pinned action versions:** `actions/checkout@v6`; `uv` comes from the
  `ghcr.io/astral-sh/uv:python3.14-trixie-slim` container instead of
  `astral-sh/setup-uv` (`.github/workflows/ci.yml:18,22`).
- **Runner network access:** the runner pulls the container image from `ghcr.io` and
  installs git with `apt-get` in every job (`.github/workflows/ci.yml:18,21`), so it
  has outbound network access.

## Amendment Log

| Date | What changed | Why | Affected tasks |
|------|-------------|-----|----------------|
| 2026-10-20 | Moved out of `specs/archive/` as S-010 (was a duplicate `S-001`). The workflow contract now matches `.github/workflows/ci.yml`: version-tag triggers; jobs in the `uv` Python 3.14 container on the self-hosted docker runner; `actions/checkout@v6`; the `commands.md` drift check in `lint` (the exclusion of that check is removed); the `release` job (`contents: write`, publishes a GitHub Release, commits nothing); shallow checkout for `lint` and `test`. Ruff selection pinned to `E`, `F`, `I` ignoring `E501`. Resolved the three open questions from `cli/pyproject.toml` and `.github/workflows/ci.yml`; the embedded YAML and TOML became prose. Driven by CR-003 §10 and Architecture Consistency Review finding F5. | The spec was still `approved` in the archive and the only written contract for CI, but its exclusions, triggers and runner setup no longer matched the workflow. | None in flight |
