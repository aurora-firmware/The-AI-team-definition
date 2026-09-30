---
id: T-085
title: Structured results for validate, archive, check-layout
status: completed
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Structured results for validate, archive, check-layout

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 1**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P8 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- validate returns findings (code, path, message) and selecting flags; archive returns moved/would-move paths; check-layout findings carry suggested fix separately; internal only (S-003 deferral stands). Out of scope: public --json, new finding codes.

## Acceptance Criteria

AC-1: pure handlers.
AC-2: check-layout suggested fix separate from message.
AC-3: archive --dry-run returns candidates, changes nothing.
AC-4: validation failure exit status equals today's.
AC-5: output unchanged, no public flags (SC-6, ADR-004).

## Dependencies

- `T-082` — Structured-result type; apply to spec new, adr new, change-request new

## Files to Touch

- commands/validate.py
- archive.py
- check_layout.py
- new cli/tests/test_structured_results_checks.py [G2 N6]

## Verification

```bash
# V-PY; V-DOCS.
# V-DOCS: bash cli/scripts/gen_docs.sh && git diff --exit-code cli/docs/commands.md
# V-PY: cd cli && uv run pytest && uv run ruff format --check . && uv run ruff check .   # set UV_CACHE_DIR under /tmp if uv cannot write its cache
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-09-30

The Work Log was empty, so I started from the acceptance criteria and followed the T-082 to T-084 pattern: a pure handler returning `core.result.Result`, with the Typer wrapper only printing. I wrote `cli/tests/test_structured_results_checks.py` first and confirmed it failed on import.

- **validate**: `validate_artifacts(root, all_scopes, tasks, bugs, specs, adrs, change_requests)` returns the `as_dict()` findings list as the payload. Status is 1 when any finding is error-level, which is the same condition the wrapper used before, so the exit code is unchanged. The `--json` output equals the handler payload, and a test checks this.
- **archive**: `archive_artifacts(root, older_than, dry_run)` returns `{dry_run, moves: [{source, destination}]}`. The real run moves files and `--dry-run` only lists them. The wrapper still prints `WOULD MOVE: src -> dst` for a dry run and the resolved destination path for a real run. An invalid duration is now `Result(status=1, message=...)`, and the wrapper echoes it to stderr and exits 1 as before.
- **check-layout**: `check_repository_layout(repo)` sorts the findings with the existing `_sort_key`. It returns them as `{level, path, message, suggested_fix}`, where `message` is the old `problem`. I kept the module-level `run_layout_checks` name because the existing test monkeypatches it. The rendered text is identical.
- **Tests**: they cover handler payloads, the selecting flags, status for clean and failing projects, dry-run leaving the filesystem untouched, archive and check-layout rejecting `--json`, and CLI output and exit codes matching the handlers.

Decisions: the three commands went in one commit because the shared test file would have left earlier commits failing. "Files to Touch" `archive.py`/`check_layout.py` were taken as `commands/archive.py` and `commands/check_layout.py`.

Rejected: putting a `moved`/`would_move` split into the archive payload. A single `moves` list plus a `dry_run` flag is simpler and keeps one shape for both modes.

Verification: full pytest 530 passed, ruff format/check clean, `gen_docs.sh` leaves `cli/docs/commands.md` unchanged. Nothing remains.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-09-30
PASS

Stage 1 (acceptance): AC-1 met; validate_artifacts, archive_artifacts and check_repository_layout are pure handlers returning Result, and the Typer wrappers only print. AC-2 met; check-layout payload carries `message` and `suggested_fix` as separate fields. AC-3 met; dry-run builds the same move list and skips mkdir/move. AC-4 met; validate exits 1 only on error-level findings, and check-layout exits 1 on any finding, as before. AC-5 met; no new flags, rendered text is unchanged, and the generated docs show no diff. Only the expected files changed.

Stage 2 (quality): tests cover payloads, selecting flags, dry-run with no filesystem change, exit statuses and CLI/handler parity. Verified in a detached worktree: pytest 530 passed, ruff format and check clean, gen_docs.sh produced no diff.

Non-blocking observations: the "Files to Touch" paths were interpreted as commands/archive.py and commands/check_layout.py, which is reasonable. The Work Log says the `--json` output for archive and check-layout is rejected, consistent with the internal-only scope.
