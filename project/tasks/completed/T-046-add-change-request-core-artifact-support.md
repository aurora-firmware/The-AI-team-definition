---
id: T-046
title: Add change request core artifact support
status: completed
priority: high
assigned-role: developer
created: '2026-05-28'
spec: coordinated-process-and-cli-workflow-improvements
---

# Add change request core artifact support

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

Add core parser and ID support for a first-class change-request artifact type.
This task defines the frontmatter model, parser, dumper support, and `CR-NNN`
identifier allocation, but it does not add storage paths, template loading, or
user-facing command behavior yet.

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

AC-1: The system shall support parsing and dumping change-request frontmatter
with a stable `CR-NNN` identifier.
AC-2: The system shall allocate change-request IDs without colliding with
existing change-request filenames in the provided search directories.
AC-3: The system shall preserve frontmatter key order when dumping
change-request artifacts.
AC-4: IF required change-request frontmatter is missing THEN THE SYSTEM SHALL
raise the existing frontmatter error style.

## Dependencies

- None

## Files to Touch

- `cli/src/ai_team/core/models.py` — add change-request model and parser.
- `cli/src/ai_team/core/ids.py` — add change-request ID allocation.
- `cli/tests/test_models.py` — cover change-request parsing and dumping.
- `cli/tests/test_ids.py` — cover `CR-NNN` allocation.

## Verification

```bash
cd cli
uv run pytest tests/test_models.py tests/test_ids.py
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

Implemented T-046 using TDD in two cycles. First cycle added failing tests for change-request frontmatter behavior in `test_models.py` (parse returns a typed model, parse populates required fields, dump/round-trip works, missing required field raises the existing `FrontmatterError` style, and dumped key order is preserved). Then added minimal production support in `core/models.py`: new `ChangeRequest` dataclass, `parse_change_request`, dumper field ordering for change requests, and inclusion in the supported model map/union. Ran targeted and full model tests to green.

Second cycle added failing tests for CR ID allocation in `test_ids.py` (starts at `CR-001`, scans multiple provided directories for max existing `CR-NNN-*.md`, ignores non-matching filenames). Then added minimal `next_change_request_id(search_directories)` plus CR filename pattern in `core/ids.py`. Ran targeted and full ID tests to green.

Tried running the task’s exact `uv run pytest ...` command, but this environment has a pre-existing shebang/path issue for direct console script spawning; used equivalent `uv run python -m pytest ...` as the reliable workaround and documented it. `ruff format --check` initially required formatting in `core/models.py`; applied formatter and re-ran all checks successfully. No task lifecycle files were edited on this branch. Remaining work: reviewer pass and loop-managed Work Log append on `dev-agent`.

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

- Stage 1 (acceptance): All ACs satisfied in the submitted code. Change-request frontmatter parsing/dumping support was added with required fields and error handling style (`FrontmatterError` via `_require`), CR ID allocation scans provided directories for max `CR-NNN` filenames, and change-request frontmatter dump ordering is preserved through the ordered field map.
- Stage 1 (scope): Developer commits touched only the expected implementation/test files for this task.
- Stage 2 (quality): Correctness, test coverage, readability, and performance/security checks are acceptable for scope. Targeted verification passed: `UV_CACHE_DIR=/tmp/uv-cache uv run python -m pytest tests/test_models.py tests/test_ids.py` (53 passed), `UV_CACHE_DIR=/tmp/uv-cache uv run ruff format --check .`, and `UV_CACHE_DIR=/tmp/uv-cache uv run ruff check .`.
