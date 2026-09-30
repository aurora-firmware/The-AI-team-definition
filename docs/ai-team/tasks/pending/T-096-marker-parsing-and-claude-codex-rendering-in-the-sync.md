---
id: T-096
title: Marker parsing and claude/codex rendering in the sync
status: pending
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Marker parsing and claude/codex rendering in the sync

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 2**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P19 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- parse three marker kinds against the command map; reject unknown prefixes, unparseable content, flags undefined for the command; claude/codex render verbatim in bodies and [claude]/[codex] headers; wire into sync; test with synthetic bodies. [G2 B1] Update the fake-repo setup in test_init_scaffolds.py (it copies only the sync script, ~lines 171-175) to also copy the marker module and a minimal command map. Out of scope: pi rendering (T-098), skill source edits.

## Acceptance Criteria

AC-1: claude/codex render verbatim (marker contract).
AC-2: unknown kind/unparseable fails naming file and marker (SC-10).
AC-3: header markers rendered per target.
AC-4: unchanged sources pass V-GOLD (SC-2).

## Dependencies

- `T-087` — TS lock entry in skeleton .gitignore; update B-017 tests and usage guide
- `T-094` — Command map plus agreement test against the Typer CLI

## Files to Touch

- cli/scripts/sync_init_scaffolds.py
- new marker module in cli/scripts/
- new cli/tests/test_skill_markers.py
- cli/tests/test_init_scaffolds.py [G2 B1]

## Verification

```bash
# V-SYNC; V-GOLD; V-PY.
# V-SYNC: the sync command documented in CLAUDE.md's Build section (currently: cd cli && python scripts/sync_init_scaffolds.py)
# V-GOLD: git diff --exit-code "$(git merge-base HEAD main)" -- cli/src/ai_team/init/scaffolds/claude cli/src/ai_team/init/scaffolds/codex
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
