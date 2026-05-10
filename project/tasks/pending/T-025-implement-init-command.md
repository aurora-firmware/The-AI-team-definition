---
id: "T-025"
title: "Implement ai-team init command"
status: pending
priority: medium
assigned-role: developer
created: 2026-05-10
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

## Review

<!-- Reviewer: append verdict here after each review cycle. -->
