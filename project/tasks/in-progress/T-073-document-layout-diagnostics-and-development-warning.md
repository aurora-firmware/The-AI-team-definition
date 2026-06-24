---
id: T-073
title: Document layout diagnostics and development warning
status: pending
priority: medium
assigned-role: developer
created: '2026-06-24'
spec: S-003-project-layout-diagnostics-and-cli-development-warning
---

# Document layout diagnostics and development warning

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

Document both S-003 user-facing surfaces after implementation. Add the
development warning contract and stderr behavior to the usage guide. Document
`check-layout`, its four validation levels, read-only behavior, report fields,
and exit semantics. Regenerate the exhaustive command reference from the Typer
app and extend documentation tests so generated and hand-written references
cannot drift from the shipped command.

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

AC-1: WHEN users read `cli/docs/usage.md` THE SYSTEM SHALL document the exact
      development warning, its issue URL, its once-per-invocation behavior, and
      stderr separation from normal and JSON output.
AC-2: WHEN users read `cli/docs/usage.md` THE SYSTEM SHALL document
      `ai-team check-layout`, all four validation levels, read-only operation,
      report fields, clean and issue exit behavior, and the no-repair exclusion.
AC-3: WHEN command documentation is regenerated THE SYSTEM SHALL include
      `check-layout` in `cli/docs/commands.md` without hand-editing generated
      command content.
AC-4: The system shall include automated documentation checks that fail if the
      usage guide or generated command reference omits the S-003 contracts.

## Dependencies

- `T-069` — supplies the final warning behavior and contract verification.
- `T-072` — supplies the final command name, report, and exit behavior.

## Files to Touch

- `cli/docs/usage.md` — document the warning and layout-check workflow.
- `cli/docs/commands.md` — regenerate the exhaustive command reference.
- `cli/tests/test_usage_guide.py` — enforce hand-written S-003 documentation.
- `cli/tests/test_gen_docs.py` — enforce generated `check-layout` documentation.

## Verification

```bash
cd cli
bash scripts/gen_docs.sh
python scripts/sync_init_scaffolds.py
UV_CACHE_DIR=/tmp/uv-cache uv run pytest
UV_CACHE_DIR=/tmp/uv-cache uv run ruff format --check .
UV_CACHE_DIR=/tmp/uv-cache uv run ruff check .
UV_CACHE_DIR=/tmp/uv-cache uv build
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-06-24

Completed the T-073 documentation implementation in commit `4c4c748`,
covering the exact development warning contract and issue URL,
once-per-invocation stderr behavior, JSON/output separation, and the complete
`check-layout` workflow. Added automated checks for the hand-written usage
guide and generated command reference. The earlier isolated build attempt was
blocked by unavailable PyPI access while resolving `hatchling` and
`hatch-vcs`. On resumption, documentation generation and scaffold
synchronization completed, all 422 tests passed, both Ruff checks passed, and
the required isolated `UV_CACHE_DIR=/tmp/uv-cache uv build` succeeded after
network permission was granted. A non-isolated build workaround was rejected
because it would not satisfy the documented verification contract. No further
implementation work remains; T-073 is ready for review and integration.

Obstacles encountered: the isolated build first reproduced the prior sandbox
DNS/network denial while resolving build dependencies. Retrying the exact
command with network permission succeeded.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-06-24

PASS

Stage 1 passed: all four acceptance criteria are satisfied. The usage guide
preserves the exact development warning and issue URL, documents its
once-per-invocation stderr behavior and stdout/JSON separation, and covers all
four `check-layout` levels, report fields, deterministic clean/issue exits,
read-only behavior, and the no-repair exclusion. Regenerated command
documentation contains the shipped `check-layout` command without a
hand-edited delta, and automated documentation checks cover both references.
The implementation commit changes only the three expected files that required
a delta; `cli/docs/commands.md` was already current from T-072.

Stage 2 passed: the documentation and tests are focused, readable, and free of
unrelated behavior. On commit `4c4c748`, command documentation generation and
scaffold synchronization succeeded, all 422 tests passed, both Ruff checks
passed, and the exact isolated `UV_CACHE_DIR=/tmp/uv-cache uv build` completed
successfully.

Next owner: active Development Loop.

Obstacles Encountered: none remain. The previously blocked isolated build was
re-run successfully with network permission during this review.
