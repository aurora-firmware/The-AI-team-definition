---
id: T-026
title: Document install in setup-guide and verify end-to-end packaging
status: in-progress
priority: low
assigned-role: developer
created: '2026-05-10'
---

# Document install in setup-guide and verify end-to-end packaging

## Description

Update `guides/setup-guide.md` with installation and usage instructions for the `ai-team` CLI: `pipx install ai-team-cli` (once published) or `pipx install <repo>/cli/dist/*.whl` for local builds; then `ai-team init` in the target repo; then a short overview of daily commands (`status`, `task new`, `task start`, `validate`, `report`).

Verify the package builds and installs cleanly end-to-end. From a clean shell:
1. `cd cli && python scripts/sync_init_scaffolds.py && uv build`
2. `pipx install --force cli/dist/*.whl`
3. `mkdir /tmp/ai-team-smoke && cd /tmp/ai-team-smoke && ai-team init . --tools claude --no-interactive`
4. `ai-team --version && ai-team status`

Document the verification command sequence in the guide so downstream maintainers can repeat it.

## Acceptance Criteria

AC-1: The system shall update `guides/setup-guide.md` to document `pipx install ai-team-cli`, the local-wheel install path, and the basic command set.
AC-2: WHEN `cd cli && python scripts/sync_init_scaffolds.py && uv build` runs THE SYSTEM SHALL produce a wheel under `cli/dist/`.
AC-3: WHEN `pipx install --force cli/dist/*.whl` runs THE SYSTEM SHALL install `ai-team` to the user's pipx environment.
AC-4: WHEN `ai-team init <empty-dir> --tools claude --no-interactive` runs against the freshly installed CLI THE SYSTEM SHALL create the `project/` skeleton, the `.claude/` subset, and `.ai-team.toml` in the target directory.

## Dependencies

- `T-025` — `init` command must work

## Files to Touch

- `guides/setup-guide.md` — install and usage docs

## Verification

```bash
cd cli && python scripts/sync_init_scaffolds.py && uv build \
  && pipx install --force dist/*.whl \
  && d=$(mktemp -d) && ai-team init "$d" --tools claude --no-interactive \
  && test -d "$d/project" && test -f "$d/.ai-team.toml"
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. -->

### Session 1 — 2026-05-10

Implemented T-026 by updating the setup guide with explicit CLI installation paths (`pipx install ai-team-cli` for published package, and local wheel install for maintainers), first-run initialization (`ai-team init . --tools claude --no-interactive`), and a short daily command set (`status`, `task new`, `task start`, `validate`, `report`). I also added a dedicated end-to-end maintainer verification section with the packaging/install/init smoke sequence.

For TDD flow, I first ran red checks using `rg` to confirm the required install/usage content was missing from `guides/setup-guide.md`. After editing, I reran the checks and they passed (green). I then executed runtime smoke verification for AC-2/AC-3/AC-4: wheel build succeeded, pipx installation succeeded, and `ai-team init` produced the expected scaffold (`project/`, `.claude/`, `.ai-team.toml`) in a fresh temp directory.

What was tried and rejected: running the build exactly with `python` failed because this environment has no `python` shim; I used `python3` for execution. Initial attempts to run `uv`/`pipx` inside sandbox failed due read-only cache/state paths; reran with escalation. A full chained rerun also failed once because a prior `ai-team` pipx venv already existed despite `--force`; uninstalling `ai-team` first resolved it.

What remains: no implementation changes remain on this branch; next step is for the loop to append this Work Log entry to the canonical task file on `dev-agent` and proceed to review/integration flow.

## Review

<!-- Reviewer: append verdict here after each review cycle. -->
