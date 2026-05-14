---
id: "T-028"
title: "Write cli/docs/usage.md hand-written CLI guide"
status: pending
priority: high
assigned-role: "unassigned"
created: 2026-05-14
---

# Write cli/docs/usage.md hand-written CLI guide

## Description

Per spec `project/specs/ai-team-cli-documentation.md` (Phase 2, Component 1), write `cli/docs/usage.md` — the hand-written narrative documentation for the `ai-team` CLI, serving both end users and maintainers in a single file.

The file must cover:
- **Installation** — `pipx install` (published and local-build paths), the `python scripts/sync_init_scaffolds.py` + `uv build` local flow, and the Python version requirement. Source these from the current `cli/pyproject.toml` and `README.md`.
- **Initialisation** — `ai-team init`, the `--tools` / `--include-ai-process` / `--dry-run` / `--force` flags, what gets scaffolded, and the `.ai-team.toml` marker.
- **Daily workflows** — task-oriented sequences (create-and-ship a task; file-and-resolve a bug; generate a Gate 5 report), not an exhaustive flag list.
- **Expected project folder structure** — the `project/` layout the CLI reads and writes: `specs/` (+ `archive/`), `tasks/{pending,in-progress,completed,blocked}/`, `bugs/{open,in-progress,resolved}/`, `decisions/`, `docs/`, the `.ai-team.toml` marker, and the locator resolution order.
- **Maintainer section** — module map (`ai_team.cli`, `core/`, `commands/`, `templates/`, `init/`, `render`), how to add a new command, how to run tests, how to build and release, and how to regenerate `commands.md`.
- A link to `commands.md` for the exhaustive reference.

Verify CLI behaviour against the actual `cli/src/ai_team/` source and the generated `cli/docs/commands.md`; do not rely on the (now-superseded) development spec.

## Acceptance Criteria

AC-1: The system shall create `cli/docs/usage.md` covering installation, `ai-team init`, daily command workflows, the expected `project/` folder structure, and a maintainer section.
AC-2: The system shall describe the expected `project/` folder structure including `specs/` (+ `archive/`), the `tasks/` and `bugs/` state subfolders, `decisions/`, `docs/`, and the `.ai-team.toml` marker with the locator resolution order.
AC-3: The system shall include a maintainer section with the `ai_team` module map, how to add a command, how to run tests, how to build/release, and how to regenerate `commands.md`.
AC-4: The system shall link from `usage.md` to `commands.md` for the exhaustive command reference.
AC-5: The system shall describe only CLI behaviour that exists in `cli/src/ai_team/`, with no command or flag that is absent from the generated `cli/docs/commands.md`.

## Dependencies

- `T-027` — `cli/docs/commands.md` must exist so `usage.md` can link to it and be cross-checked against it

## Files to Touch

- `cli/docs/usage.md` — new hand-written CLI guide

## Verification

```bash
test -f cli/docs/usage.md
grep -q "commands.md" cli/docs/usage.md
grep -qi "install" cli/docs/usage.md && grep -qi "init" cli/docs/usage.md
grep -qi ".ai-team.toml" cli/docs/usage.md
grep -qiE "maintainer|module map|release" cli/docs/usage.md
```

## Work Log

## Review
