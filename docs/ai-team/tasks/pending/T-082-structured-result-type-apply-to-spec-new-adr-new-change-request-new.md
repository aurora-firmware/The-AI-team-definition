---
id: T-082
title: Structured-result type; apply to spec new, adr new, change-request new
status: pending
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Structured-result type; apply to spec new, adr new, change-request new

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 1**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P5 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- internal result type with exit status, payload, error message and hint as separate fields; CLI text still joins them as today; each command split into a pure handler (explicit ProjectRoot, typed input → result) and the Typer wrapper; for --json commands payload equals the printed JSON. Out of scope: other modules, new public flags (ADR-004).
- [G2 B5] Also split ProjectRootNotFound in core/locator.py (lines ~133-188) so the exception carries message and hint separately, while str() joins them exactly as today. T-082 is the only task that edits locator.py.

## Acceptance Criteria

AC-1: result type carries status, payload, message, hint separately.
AC-2: --json output equals handler payload.
AC-3: handlers run with explicit root, no Typer, no process cwd.
AC-4: domain errors: message equals today's stderr minus hint.
AC-5: CLI output unchanged (SC-6).
AC-6: ProjectRootNotFound exposes separate message and hint fields, and its str() equals today's text (SC-6, Tool contract). [G2 B5]

## Dependencies

- `T-081` — Injectable "today" and framework version in the Python CLI

## Files to Touch

- new core/result.py (or equivalent)
- commands/spec.py
- adr.py
- change_request.py
- cli/src/ai_team/core/locator.py [G2 B5]
- new cli/tests/test_structured_results_create.py

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

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
