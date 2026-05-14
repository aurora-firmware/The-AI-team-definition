---
id: "T-027"
title: "Add typer-cli dependency, gen_docs script, and generate commands.md"
status: pending
priority: high
assigned-role: "unassigned"
created: 2026-05-14
---

# Add typer-cli dependency, gen_docs script, and generate commands.md

## Description

Per spec `project/specs/ai-team-cli-documentation.md` (Phase 1, Component 3), the CLI's exhaustive command reference must be generated from the Typer app rather than hand-written, so it cannot drift from the code.

Three deliverables, one outcome (a generated, committed reference exists):
1. Add `typer-cli` as a dev/tooling dependency in `cli/pyproject.toml`. Match the project's existing dependency-group convention (see the `[Open Questions]` note in the spec — confirm dev group vs optional extra from the current `pyproject.toml` layout).
2. Add `cli/scripts/gen_docs.sh`, a thin wrapper that invokes Typer's built-in `utils docs` against the `ai_team.cli` app and writes the output to `cli/docs/commands.md`. It is a sibling to the existing `cli/scripts/sync_init_scaffolds.py`.
3. Run the script to produce `cli/docs/commands.md`, commit it, and give it a header note marking it as generated and naming the regeneration command (`bash cli/scripts/gen_docs.sh`).

The `cli/docs/` directory does not exist yet; this task creates it.

## Acceptance Criteria

AC-1: The system shall declare `typer-cli` as a dev/tooling dependency in `cli/pyproject.toml`, placed in the same dependency group the project already uses for tooling.
AC-2: WHEN `bash cli/scripts/gen_docs.sh` is run from the repo root THE SYSTEM SHALL regenerate `cli/docs/commands.md` from the `ai_team.cli` Typer app with no manual editing.
AC-3: The system shall commit `cli/docs/commands.md` containing every command group, subcommand, argument, and flag, including the global flags.
AC-4: The system shall include a header note in `cli/docs/commands.md` stating the file is generated and must not be hand-edited, and naming the regeneration command.
AC-5: IF `gen_docs.sh` is run twice with no code change THEN THE SYSTEM SHALL produce a byte-identical `cli/docs/commands.md` (idempotent generation).

## Dependencies

- None

## Files to Touch

- `cli/pyproject.toml` — add `typer-cli` dev/tooling dependency
- `cli/scripts/gen_docs.sh` — new wrapper script invoking `typer ... utils docs`
- `cli/docs/commands.md` — new generated, committed command reference

## Verification

```bash
bash cli/scripts/gen_docs.sh
git diff --exit-code cli/docs/commands.md   # idempotent: no diff after regen
grep -q "task" cli/docs/commands.md && grep -q "init" cli/docs/commands.md && grep -q "validate" cli/docs/commands.md
grep -qi "generated" cli/docs/commands.md
grep -q "typer-cli" cli/pyproject.toml
```

## Work Log

## Review
