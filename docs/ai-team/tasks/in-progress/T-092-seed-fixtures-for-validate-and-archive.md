---
id: T-092
title: Seed fixtures for validate and archive
status: in-progress
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Seed fixtures for validate and archive

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 1**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P15 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- validate each flag alone, combined, all, none; malformed frontmatter (missing fence, missing required key, invalid ID pattern); archive various olderThan values and dryRun; archive age boundary (one day before, on, one day after the cut-off, fixed clock).

## Acceptance Criteria

AC-1: every flag covered (SC-3).
AC-2: malformed frontmatter (SC-4).
AC-3: age boundary both sides and at cut-off (SC-4).
AC-4: Python runner passes (SC-5).

## Dependencies

- `T-088` — Parity fixture format and Python fixture runner

## Files to Touch

- case dirs validate--
- archive--

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
