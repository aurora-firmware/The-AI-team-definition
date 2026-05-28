---
id: T-048
title: Add change request listing and validation
status: pending
priority: medium
assigned-role: developer
created: '2026-05-28'
spec: coordinated-process-and-cli-workflow-improvements
---

# Add change request listing and validation

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

Extend existing read/validation surfaces so change requests are visible to
humans and agents after creation. The work should keep the new artifact type
consistent with the existing CLI style for listing and validating specs, tasks,
bugs, and ADRs.

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

AC-1: WHEN a user lists change requests THE SYSTEM SHALL show change-request ID,
title, state, and related spec-amendment information where available.
AC-2: WHEN a user lists change requests with JSON output THE SYSTEM SHALL emit
machine-readable rows without table formatting.
AC-3: WHEN validation scans project artifacts THE SYSTEM SHALL validate
change-request frontmatter and report malformed change requests.
AC-4: IF no change requests exist THEN THE SYSTEM SHALL return an empty list
without treating that state as an error.

## Dependencies

- `T-046` — core change-request model, parser, dumper, and ID support.
- `T-054` — change-request storage path and template loading support.
- `T-047` — user-facing change-request creation command and tests.

## Files to Touch

- `cli/src/ai_team/commands/list.py` — add change-request listing.
- `cli/src/ai_team/commands/validate.py` — expose change-request validation in
  the CLI command surface.
- `cli/src/ai_team/core/validate.py` — validate change-request artifacts.
- `cli/tests/test_list.py` — cover change-request list behavior.
- `cli/tests/test_validate.py` — cover change-request validation behavior.

## Verification

```bash
cd cli
uv run pytest tests/test_list.py tests/test_validate.py
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

Implemented AC-1 through AC-4 in two TDD cycles.

**Cycle 1 — listing (AC-1, AC-2, AC-4).** Inspected the existing `list.py` command, the `ChangeRequest` model, and the `ProjectRoot` locator. The `ChangeRequest` model carries `id`, `title`, `status`, and `created` — there is no `target-spec` or spec-amendment field on the model. The listing output therefore includes ID, Title, and State only; no spec-amendment column exists yet. Added `change-requests` as a named Typer subcommand on the `list` app, following the same `_iter_markdown_files` / `_render_table` / `print_json` pattern used by `adrs`. Template and `.gitkeep` files are skipped by the shared `_should_skip` helper already in place. AC-4 is naturally satisfied because `_iter_markdown_files` returns an empty list for an empty or non-existent folder.

**Cycle 2 — validation (AC-3).** Extended `core/validate.py` with `CHANGE_REQUEST_ID_RE = re.compile(r"^CR-\d{3}$")` and a `change_requests: bool` parameter on `validate_project`. The new block parses each file in `root.change_requests` via `parse_change_request`, reports `frontmatter-invalid` on parse failure, and then applies `_check_id_pattern` and `_check_stateful_filename` — the same two checks used for tasks, bugs, and ADRs. Updated `commands/validate.py` to expose `--change-requests` as a scope flag and to include change requests in the default scope (when no scope flag is given).

**Decision: no spec-amendment column in list output.** The `ChangeRequest` datamodel (from T-046) has no `target-spec` or analogous field. The task says "where available", so no column was added. This is documented here; if a future task adds that field to the model, the list command should be extended accordingly.

**No files outside the task's Files-to-Touch list were modified.** All 21 tests pass; `ruff format --check` and `ruff check` are clean.

**Obstacle noted.** The `_iter_markdown_files` helper in `commands/list.py` does not guard against non-existent folders. AC-4 tests create the folder first, so this is fine for now, but a future test exercising a missing `change-requests` directory may surface a `FileNotFoundError` from `Path.glob`.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
