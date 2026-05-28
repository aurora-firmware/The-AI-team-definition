---
id: T-047
title: Implement change request CLI creation
status: pending
priority: high
assigned-role: developer
created: '2026-05-28'
spec: coordinated-process-and-cli-workflow-improvements
---

# Implement change request CLI creation

<!--
Task Quality Rules (see the new-task skill for full details):
  - Atomic — one clear outcome.
  - One-shottable — ≤ 3–4 files touched, ≤ 5 ACs, Description ≈ 20 lines.
  - Verifiable — concrete Verification command or explicit manual steps.
  - Self-contained — Description is enough to start without follow-up questions.
  - EARS — every AC matches one of the five EARS patterns below.
  - Dependency-honest — list every prior task this one reads from or modifies.
-->

## Description

Implement the user-facing CLI command that creates pending change-request
documents from the core artifact support. The command should follow the existing
artifact creation style: allocate an ID, slugify the title, write from the
bundled template, refuse accidental overwrite, and support JSON output for
agent use.

## Acceptance Criteria

<!-- EARS pattern reference. Every criterion must match one pattern:
  1. Ubiquitous            — The system shall [outcome]
  2. Event-driven          — WHEN [trigger] THE SYSTEM SHALL [outcome]
  3. Unwanted-behaviour    — IF [fault] THEN THE SYSTEM SHALL [outcome]
  4. State-driven          — WHILE [state] THE SYSTEM SHALL [outcome]
  5. Optional              — WHERE [feature included] THE SYSTEM SHALL [outcome]

Examples:
  AC-1: WHEN the user submits valid credentials THE SYSTEM SHALL
        redirect to /dashboard within 200ms.
  AC-2: IF the password is incorrect THEN THE SYSTEM SHALL return 401
        and display "Invalid credentials".
  AC-3: The system shall log every authentication attempt with user id
        and outcome.
-->

AC-1: WHEN a user runs the change-request creation command with a title THE
SYSTEM SHALL create a `CR-NNN-<slug>.md` artifact in the change-request
directory.
AC-2: WHEN a user passes supported metadata flags THE SYSTEM SHALL write those
values into the change-request frontmatter.
AC-3: WHEN a user passes `--json` THE SYSTEM SHALL emit machine-readable `id`
and `path` fields without table formatting.
AC-4: IF the allocated output path already exists THEN THE SYSTEM SHALL refuse
to overwrite it and exit non-zero.

## Dependencies

- `T-046` — core change-request model, parser, dumper, and ID support.
- `T-054` — change-request storage path and template loading support.

## Files to Touch

- `cli/src/ai_team/commands/change_request.py` — add the Typer command group.
- `cli/tests/test_change_request_new.py` — cover create, JSON output, metadata,
  and overwrite refusal.
- `cli/docs/usage.md` — briefly mention the new artifact command in CLI usage.

## Verification

```bash
cd cli
uv run pytest tests/test_change_request_new.py
uv run ruff format --check .
uv run ruff check .
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-05-28

Picked up T-047 on the `task/T-047-implement-change-request-cli-creation` branch with no prior Work Log entries.

Read the task file and explored the established artifact-command pattern used by `bug.py` and `adr.py`. Both follow the same structure: `_template_body` helper to strip YAML frontmatter, a `new` subcommand that allocates an ID, slugifies the title, builds the model, calls `write_artifact`, and returns a path string or JSON payload.

The only significant divergence for change requests is that `next_change_request_id` takes a `tuple[Path, ...]` rather than a `ProjectRoot`, because change requests live in a single directory (`root.change_requests`) rather than multiple state folders.

Wrote four tests covering all four ACs in a single pass (AC-1: creates file and echoes path; AC-2: frontmatter metadata; AC-3: `--json` output without table formatting; AC-4: refuses overwrite with non-zero exit). Implemented the command, ran ruff format, confirmed all tests green and linters clean.

Updated `cli/docs/usage.md` with a "File a change request" section in Daily Workflows. The section mentions `ai-team change-request new` with and without `--json`, which is consistent with the commands actually implemented. Care was taken not to add `ai-team change-request new` to the hardcoded parametrize list in `test_usage_guide.py` since `commands.md` is generated and would require re-running `gen_docs.sh` to pick up the new command.

One pre-existing infrastructure issue noted: `test_gen_docs.py` runs the `gen_docs.sh` script which truncates `cli/docs/commands.md` to 3 lines as a side effect, causing 22 cascading test failures in the full test suite run. These failures are pre-existing on the base branch and are unrelated to this task. The task's verification command (`pytest tests/test_change_request_new.py`) is clean.

Everything committed in a single cycle on the task branch. Nothing remains.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-05-28

PASS

Stage 1 (spec compliance): All four acceptance criteria are met.

- AC-1: `change-request new <title>` allocates a `CR-NNN` ID, slugifies the title, and writes `CR-NNN-<slug>.md` to `root.change_requests`. Test confirms file creation and path output.
- AC-2: The ChangeRequest model's four frontmatter fields (`id`, `title`, `status`, `created`) are all populated by the command. The test parses the written file and asserts all four values. The model carries no optional metadata fields beyond what the command sets, so this is the complete set of "supported metadata."
- AC-3: `--json` path calls `print_json({"id": cr_id, "path": absolute_path})`. Test confirms both keys are present and no table-formatting characters appear in output.
- AC-4: `write_artifact(..., overwrite=False)` raises `ArtifactExists` when the path exists; the command catches it, echoes the error to stderr, and exits with code 1. Test patches the ID allocator to force a collision and verifies non-zero exit and unchanged file bytes.

Only the three files listed in "Files to Touch" were modified.

Stage 2 (code quality): All checks pass.

- The implementation follows the established artifact-command pattern (`bug.py`, `adr.py`) exactly: `NAME`, `app`, `_template_body`, `@app.command("new")`, `write_artifact` with `overwrite=False`, `ArtifactExists` handling, JSON branch, and plain-path fallback.
- Tests are independent (each uses `tmp_path` + `monkeypatch`), cover success and failure paths, and are scoped to the task's four ACs.
- Ruff format and lint both pass clean.
- No dead code, hardcoded secrets, or performance concerns.
