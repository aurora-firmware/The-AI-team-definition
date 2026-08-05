---
id: T-025
title: Implement ai-team init command
status: completed
priority: medium
assigned-role: developer
created: '2026-05-10'
---

# Implement ai-team init command

## Description

Implement `ai_team.commands.init` exporting `app` with `NAME = "init"`. Single default command takes optional `path` argument (default cwd), `--tools <list|all|none>` (e.g., `claude,codex`), `--include-ai-process` boolean, `--force` boolean (overwrite), `--dry-run` boolean.

Behaviour: walks the bundled `init/scaffolds/` (created by T-024) and copies into the target path:
1. Always: `project/` skeleton.
2. If `--tools` includes `claude` (or interactive selection), the relevant subset of `.claude/`.
3. If `--include-ai-process`, the `ai-process/` snapshot.

Refuses to overwrite existing files unless `--force` is set. Writes a `.ai-team.toml` marker recording chosen options (`tools`, `include_ai_process`, `framework_version`). Prints a checklist of next steps after success (run `/brainstorm`, then `/write-plan`, etc.).

When invoked without `--tools` or `--no-interactive`, prompts interactively for tool selection and `include_ai_process`.

## Acceptance Criteria

AC-1: WHEN `ai-team init <path> --tools claude --no-interactive` runs into an empty path THE SYSTEM SHALL create the `project/` skeleton, copy `.claude/` for the `claude` tool, and write `.ai-team.toml`.
AC-2: IF the target path contains files that would be overwritten and `--force` is not set THEN THE SYSTEM SHALL exit non-zero without writing.
AC-3: WHERE `--dry-run` is supplied THE SYSTEM SHALL list every file that would be written and produce no filesystem mutation.
AC-4: WHERE `--include-ai-process` is supplied THE SYSTEM SHALL also copy the bundled `ai-process/` snapshot into the target.
AC-5: The system shall write a `.ai-team.toml` recording `tools`, `include_ai_process`, and `framework_version`.

## Dependencies

- `T-024` — bundled scaffolds must exist

## Files to Touch

- `cli/src/ai_team/commands/init.py` — Typer app, interactive prompts, copy logic, `.ai-team.toml` writer
- `cli/tests/test_init.py` — covers default path, `--tools`, `--include-ai-process`, `--force`, `--dry-run`, marker file

## Verification

```bash
cd cli && uv run pytest tests/test_init.py -q
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. -->

### Session 1 — 2026-05-10

Implemented `ai-team init` end-to-end in `cli/src/ai_team/commands/init.py` and covered the acceptance criteria with `cli/tests/test_init.py`. The command now scaffolds `project/` always, conditionally scaffolds `.claude/` when `claude` is selected, optionally scaffolds `ai-process/` with `--include-ai-process`, writes `.ai-team.toml` with `tools`, `include_ai_process`, and `framework_version`, refuses collisions unless `--force`, and supports `--dry-run` by listing all planned file writes without mutating the filesystem. It also prints a post-init checklist (`/brainstorm`, `/write-plan`, `/dev-loop`).

I first implemented a basic callback flow and then hit a parsing issue where `ai-team init <path> --tools ...` treated `--tools` as a subcommand. I tried switching to a single-command sub-Typer, but `add_typer` still required subcommand invocation. I rejected that and fixed the root cause by keeping a callback app and enabling `context_settings={"allow_interspersed_args": True}`, which preserves the required invocation form.

Remaining work on this branch: none. Task lifecycle updates and review logging remain for the loop on `dev-agent`.

## Review

<!-- Reviewer: append verdict here after each review cycle. -->

### Review Verdict — 2026-05-10

PASS

Stage 1: All acceptance criteria are satisfied in the submitted branch, and the branch diff matches expected scope (`cli/src/ai_team/commands/init.py`, `cli/tests/test_init.py`) with no lifecycle file modifications.

Stage 2: Code quality checks pass for correctness, test coverage, security, readability, and performance for the task scope. Verification command `cd cli && uv run pytest tests/test_init.py -q` was re-run and passed (`6 passed`).
