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

### Session 1 — 2026-05-15

This session implemented all five acceptance criteria for T-038 in a single TDD-driven commit on `task/T-038-remove-ai-process-export-behavior-from-init`.

**What was done:**

The implementation required three coordinated changes: removing the `--include-ai-process` option and related logic from `init.py`, adding `.codex/` scaffolding logic (codex scaffold data already existed from T-042 as real files, not symlinks), and deleting the bundled `cli/src/ai_team/init/scaffolds/ai-process/` tree (9 files).

The TDD cycle proceeded as follows:

1. Red for AC-3: Replaced the existing `test_init_include_ai_process_copies_snapshot_and_records_marker` test with `test_init_include_ai_process_is_unknown_option`, which asserts a non-zero exit code when `--include-ai-process` is passed. This test correctly failed (exit code 0) while the old option still existed.

2. Implementation: Removed the `include_ai_process` parameter from `init_command`, removed the interactive confirm prompt, replaced the `if include_ai_process:` copy block with `if "codex" in selected_tools:` copying from the `codex` scaffold, removed `include_ai_process` from the marker data dict, and deleted the `ai-process/` scaffold directory.

3. The AC-3 test then passed. Running the full suite revealed one additional failing test: `test_init_defaults_to_cwd_and_scaffolds_project_claude_and_marker` was asserting `data["init"]["include_ai_process"] is False`. This test directly validates AC-5 behavior (the field must not exist), so it was updated to assert `"include_ai_process" not in data["init"]` per the task instruction to update tests "directly necessary to validate the new behavior."

4. Added four new tests covering AC-1 (codex agents/skills scaffolded), AC-2 (codex files are real, not symlinks), the `--tools all` combined case (AC-1+AC-2), and AC-4 (interactive mode does not prompt for ai-process). All passed immediately on first run since the implementation was already complete.

**What was tried and rejected:**

No alternative approaches were considered — the changes were straightforward deletions and a one-for-one replacement of the `include_ai_process` branch with the `codex` scaffolding branch.

**Tests left for T-039:**

No tests were skipped. The original `test_init_include_ai_process_copies_snapshot_and_records_marker` test was replaced rather than left in place, because leaving it would have caused a persistent failure in the suite (it invokes `--include-ai-process` which is now an unknown option). T-039 should review whether any additional coverage is warranted for edge cases around the `--tools codex` path.

**What remains:**

Nothing for T-038. All ACs are verified by passing tests. T-039 (test updates) and T-040/T-041 (documentation) are separate tasks.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
