---
id: T-084
title: Structured results for list, show, status, report
status: pending
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Structured results for list, show, status, report

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 1**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P7 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- --json JSON is the result where it exists; define report's internal result (written path, content/summary pinned by fixtures). [G2 B6] The latest-integration-result lookup (status.py `_latest_integration_result`, a `git log --all --grep` call reused by report via `_payload`) is part of the structured result; fixtures pin its "not found" branch.

## Acceptance Criteria

AC-1: pure handlers for every list leaf, show, status, report.
AC-2: payload equals --json where it exists.
AC-3: report returns written path with/without --out.
AC-4: show unknown id error with today's message.
AC-5: output unchanged (SC-6).

## Dependencies

- `T-082` — Structured-result type; apply to spec new, adr new, change-request new

## Files to Touch

- commands/list.py
- show.py
- status.py
- report.py
- new cli/tests/test_structured_results_query.py [G2 N6]

## Verification

```bash
# V-PY.
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
Implemented T-084 in four TDD cycles on the task branch, one commit per cycle. `list.py` now has `list_tasks(root, state)`, `list_bugs(root, state)`, `list_specs(root)`, `list_adrs(root)` and `list_change_requests(root)`. Each returns `Result(status=0, payload=rows)`, where the rows are exactly what `--json` prints. The Typer commands resolve the root from the cwd, call the handler, and print JSON or the same Rich table as before. `show.py` has `show_artifact(root, identifier)`. It returns `{path, frontmatter, body}` on success, and on failure a `Result` with status 1 whose message is today's text (not found with searched roots, or the ambiguous-match header plus one `- path` line per match, joined by newlines). The wrapper echoes `result.text()` to stderr and exits 1, so the output is identical. `status.py` has `status_summary(root)`, which wraps the existing `_payload`, including `_latest_integration_result` and its "not found" fallback. A test pins that fallback outside a git repo. `report.py` has `write_report(root, out)`, which writes the file and returns `{path, content}` with the resolved path. The wrapper prints the path as before.

Tests are in `cli/tests/test_structured_results_query.py`. They call the handlers with an explicit root while the cwd is elsewhere, and compare payloads with `--json` CLI output.

Two caveats for the reviewer.
- Because the handler always returns body and frontmatter, `show` in text mode now parses the artifact even for specs. Before, only `--json` parsed a matched spec. A malformed spec would now fail in text mode where it previously just rendered. Normal inputs are unaffected and all existing show tests pass.
- The list handlers put a list in `Result.payload`, which is annotated as `dict | None`. `core/result.py` was out of scope, so the annotation should be widened in a follow-up.

Rejected: wrapping the list rows in a dict, such as `{"rows": ...}`, because AC-2 requires the payload to equal `--json`. Nothing remains for this task.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
