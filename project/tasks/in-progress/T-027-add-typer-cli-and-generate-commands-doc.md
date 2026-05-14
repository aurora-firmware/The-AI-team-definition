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

### Session 1 — 2026-05-14

Implemented all five acceptance criteria for T-027 in a single TDD session.

**What was done.** Added `typer-cli` to the `dev` dependency group via `uv add --dev typer-cli`, which updated both `pyproject.toml` and `uv.lock`. Created `cli/scripts/gen_docs.sh` as a shell script that writes a header comment block (marking the file as generated and naming `bash cli/scripts/gen_docs.sh` as the regeneration command) then appends the output of `uv run typer ai_team.cli utils docs --name "ai-team"` to `cli/docs/commands.md`. Ran the script to produce the committed reference (497 lines, all command groups, subcommands, arguments, and flags). Wrote 10 tests in `cli/tests/test_gen_docs.py` covering AC-1 through AC-5 before implementing; all failed first, all pass after implementation.

**What was tried and rejected.** A line-by-line string parser was first used to verify `typer-cli` is in the `[dependency-groups] dev` section and not in `[project] dependencies`; it produced a false positive (flagging typer-cli as a runtime dep). Replaced with `tomllib` structured parsing, which is unambiguous. The `--output` flag on `typer utils docs` writes the file directly but does not allow prepending content; instead the script uses shell redirection to write the header first and appends the typer output with `>>`.

**What remains.** This task is complete. T-027 covers only Phase 1 (Component 3) of the documentation spec. Subsequent tasks under the same spec (usage.md, component-map.md update, spec archiving, README/guide pointer updates) are out of scope for this task. Note: the Developer observed a pre-existing `test_templates.py` failure unrelated to this task.

## Review

### Review Verdict — 2026-05-14

PASS

**Stage 1 — Spec compliance**

All five acceptance criteria are met:

- AC-1: `typer-cli>=0.24.0` is added to `[dependency-groups] dev` in `cli/pyproject.toml` and `cli/uv.lock`. It is not present in `[project] dependencies`. Confirmed by `tomllib`-based test and by grep.
- AC-2: `cli/scripts/gen_docs.sh` exists, runs from the repo root with `bash cli/scripts/gen_docs.sh` (exit 0 verified locally), and regenerates `cli/docs/commands.md` via `uv run typer ai_team.cli utils docs --name "ai-team"` with no manual editing.
- AC-3: `cli/docs/commands.md` (497 lines) is committed and contains all command groups (`adr`, `archive`, `bug`, `init`, `list`, `report`, `show`, `spec`, `status`, `task`, `validate`), their subcommands, arguments, flags, and global flags (`-V, --version`, `--help`).
- AC-4: The header comment at the top of `commands.md` reads "GENERATED FILE — do not edit by hand" and names `bash cli/scripts/gen_docs.sh` as the regeneration command.
- AC-5: Running `gen_docs.sh` twice with no code change produces a byte-identical `commands.md`. Confirmed by `git diff --exit-code` (exit 0) and by the idempotency test.

No unspecified behavior was added. All modified files (`cli/pyproject.toml`, `cli/uv.lock`, `cli/scripts/gen_docs.sh`, `cli/docs/commands.md`, `cli/tests/test_gen_docs.py`) are within the task's stated scope.

**Stage 2 — Code quality**

- Correctness: `gen_docs.sh` uses `set -euo pipefail`, derives `REPO_ROOT` from `BASH_SOURCE`, creates the output directory with `mkdir -p`, writes the header via heredoc, and appends Typer output with `>>`. Logic is correct and handles the script-from-any-path requirement.
- Tests: 10 tests in `cli/tests/test_gen_docs.py` cover AC-1 through AC-5, including success path, script existence, content verification, header verification, and idempotency. All 10 pass. Tests are independent.
- Security: No hardcoded secrets. No external input is accepted. No queries.
- Readability: The script is concise and well-commented. Test file has a clear module docstring mapping each test to its acceptance criterion. Names are descriptive.
- Performance: No unnecessary loops. Script runs a single external command.

**Pre-existing test failure**

The `test_templates.py::test_load_template_task_matches_bundled_source` failure is confirmed pre-existing and unrelated to T-027. The test references `.claude/skills/new-task/assets/TEMPLATE-task.md`, which does not exist in this framework repository (the path belongs to a consuming project). The `test_templates.py` file was not modified by T-027 — only `test_gen_docs.py` was added. T-027 is not accountable for this failure.
