---
id: T-038
title: Remove ai-process export behavior from init
status: pending
priority: medium
assigned-role: developer
created: '2026-05-14'
---

# Remove ai-process export behavior from init

<!--
Task Quality Rules (see the new-task skill for full details):
  - Atomic — one clear outcome.
  - One-shottable — ≤ 3–4 files touched, ≤ 5 ACs, Description ≈ 20 lines.
  - Verifiable — concrete Verification command or explicit manual steps.
  - Self-contained — Description is enough to start without follow-up questions.
  - EARS — every AC matches one of the five patterns below.
  - Dependency-honest — list every prior task this one reads from or modifies.
-->

## Description

Spec S-001 removes `ai-process/` export from `ai-team init` and requires init to copy
the package-owned Claude and Codex scaffold trees selected by `--tools`. Update the
init command implementation so it scaffolds `.claude/` and `.codex/` from packaged
assets, and never offers, prompts for, copies, or records an `ai-process` snapshot.

This task owns the CLI behavior change only. Test updates are T-039 and documentation
updates are T-040/T-041.

## Acceptance Criteria

AC-1: WHEN `ai-team init --tools claude` runs THE SYSTEM SHALL scaffold `.claude/agents/` and `.claude/skills/` from packaged scaffold data.
AC-2: WHEN `ai-team init --tools codex` or `--tools all` runs THE SYSTEM SHALL scaffold `.codex/agents/` and `.codex/skills/` from packaged scaffold data as real files/directories, not symlinks.
AC-3: The system shall not define an `--include-ai-process` option on `ai-team init`, and IF a user passes `--include-ai-process` THEN THE SYSTEM SHALL reject the unknown option.
AC-4: WHEN `ai-team init` runs interactively THE SYSTEM SHALL NOT ask whether to include an ai-process snapshot.
AC-5: WHEN `ai-team init` runs THE SYSTEM SHALL NOT copy `ai-process/` into the target repository, and WHEN it writes `.ai-team.toml` THE SYSTEM SHALL NOT include an `include_ai_process` field.

## Dependencies

- `T-042` — generated skill scaffolds must exist before init behavior is finalized
- `T-043` — generated agent scaffolds must exist before init behavior is finalized

## Files to Touch

- `cli/src/ai_team/commands/init.py` — scaffold Claude/Codex package assets and remove ai-process option, prompt, copy logic, and marker field
- `cli/src/ai_team/init/scaffolds/ai-process/**` — remove bundled ai-process scaffold output

## Verification

```bash
cd cli
uv run ai-team init "$(mktemp -d)" --tools claude --no-interactive
uv run ai-team init "$(mktemp -d)" --tools codex --no-interactive
uv run ai-team init "$(mktemp -d)" --tools all --no-interactive
uv run ai-team init "$(mktemp -d)" --tools claude --include-ai-process --no-interactive
# final command must fail with an unknown-option style error
uv run pytest tests/test_init.py
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

### Review Verdict — 2026-05-15

PASS

Both stages passed.

**Stage 1 — Acceptance criteria:**

- AC-1: `--tools claude` scaffolds `.claude/agents/` and `.claude/skills/` from packaged data via the `if "claude" in selected_tools:` branch. Verified by `test_init_defaults_to_cwd_and_scaffolds_project_claude_and_marker` and the existing explicit-path test. PASS.
- AC-2: `--tools codex` and `--tools all` scaffold `.codex/agents/` and `.codex/skills/` using `shutil.copy2`, which copies file content (never symlinks). Verified by `test_init_tools_codex_scaffolds_codex_agents_and_skills`, `test_init_tools_codex_scaffolds_real_files_not_symlinks`, and `test_init_tools_all_scaffolds_both_claude_and_codex`. PASS.
- AC-3: `--include-ai-process` is not present in `init_command`'s signature; typer rejects it as an unknown option. Verified by `test_init_include_ai_process_is_unknown_option` (asserts `exit_code != 0`). PASS.
- AC-4: The `typer.confirm("Include ai-process snapshot?", ...)` call is removed; no ai-process prompt can appear in interactive mode. Verified by `test_init_interactive_does_not_prompt_for_ai_process_snapshot`. PASS.
- AC-5: No `ai-process/` copy path remains in the code; the `ai-process/` scaffold tree (9 files) is deleted; `include_ai_process` is absent from `marker_data`. Verified by multiple tests asserting `not (target / "ai-process").exists()` and `"include_ai_process" not in data["init"]`. PASS.

No unspecified behavior was added. `cli/tests/test_init.py` was the only file modified outside the task's stated scope; the Work Log explains the justification (the old test invoked `--include-ai-process` and would have caused a persistent suite failure, so it was replaced).

**Stage 2 — Code quality:**

- Correctness: Logic is correct. The `"codex" in selected_tools` guard replaces the removed `include_ai_process` guard with equivalent structure. No off-by-one or unhandled state issues observed.
- Tests: 10 tests pass locally (`uv run pytest tests/test_init.py`). All five ACs are covered by dedicated tests. Both success and failure paths are tested (unknown option, collision without force, dry-run).
- Security: No credentials or secrets. No external input used beyond CLI arguments processed through typer. No queries.
- Readability: Function signatures are clean; helper functions remain focused; no dead code or debug artifacts remain.
- Performance: No loops over large data sets in hot paths; no blocking or resource leak concerns.
