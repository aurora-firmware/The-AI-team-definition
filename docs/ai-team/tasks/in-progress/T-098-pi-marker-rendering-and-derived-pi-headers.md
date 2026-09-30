---
id: T-098
title: Pi marker rendering and derived pi headers
status: in-progress
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Pi marker rendering and derived pi headers

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 2**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P21 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- call form (all required positionals, or none required) renders ai_team tool-call instruction with input object, --json dropped; mention form renders "the `ai_team` tool's `<cmd>` command"; flag renders "set `<field>`" or bare field inside backticks; noun renders pi text; markers-only fence becomes prose, mixed fence fails; placeholders checked for field name/presence only; pi header from [claude] name/description with noun markers' pi text (ADR-002). Out of scope: writing pi/resources (T-099).

## Acceptance Criteria

AC-1: call vs mention form correct, no --json (marker contract).
AC-2: mixed fence fails.
AC-3: flag inside backticks renders bare field, no nested span.
AC-4: pi header from [claude] name/description only (ADR-002).
AC-5: undefined placeholder field fails.

## Dependencies

- `T-096` — Marker parsing and claude/codex rendering in the sync

## Files to Touch

- marker module in cli/scripts/
- new cli/tests/test_skill_markers_pi.py

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
