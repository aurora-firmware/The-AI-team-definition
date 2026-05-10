---
id: "T-026"
title: "Document install in setup-guide and verify end-to-end packaging"
status: pending
priority: low
assigned-role: developer
created: 2026-05-10
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

## Review

<!-- Reviewer: append verdict here after each review cycle. -->
