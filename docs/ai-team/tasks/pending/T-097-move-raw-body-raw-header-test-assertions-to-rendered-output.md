---
id: T-097
title: Move raw-body/raw-header test assertions to rendered output
status: pending
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Move raw-body/raw-header test assertions to rendered output

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 2**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P20 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- tests reading body.md or raw [claude]/[codex] headers assert on rendered output via a helper calling the T-096 renderer. Known: test_t063, t064, t066, t068, t074, t076, test_status_report_invocation, test_bug_evidence_chain, test_b016, test_init_scaffolds (confirm by grep). Out of scope: changing what is asserted.

Size note (accepted at Gate 2, ruling 7): over guideline, mechanical.

## Acceptance Criteria

AC-1: no test reads body.md/raw headers for content (SC-2).
AC-2: same expectations on rendered output.
AC-3: V-PY passes.

## Dependencies

- `T-087` — TS lock entry in skeleton .gitignore; update B-017 tests and usage guide
- `T-096` — Marker parsing and claude/codex rendering in the sync

## Files to Touch

- affected cli/tests/test_*.py and a new shared helper

## Verification

```bash
# V-PY; review that no remaining test asserts on real source body.md or header content (fixture writes and source-structure checks in test_init_scaffolds.py, ~lines 41-66 and 359-389, are legitimate). [G2 N5]
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
