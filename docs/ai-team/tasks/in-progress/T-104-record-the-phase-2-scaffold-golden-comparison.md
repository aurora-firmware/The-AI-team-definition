---
id: T-104
title: Record the Phase 2 scaffold golden comparison
status: in-progress
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Record the Phase 2 scaffold golden comparison

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 2**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P27 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- clean checkout with all Phase 2 merged: V-SYNC, V-GOLD against merge-base with main, no unrendered {{ in generated files; record commands and output. One-time migration gate (SC-2). If it fails, fix the owning source.

## Acceptance Criteria

AC-1: V-GOLD no diff (SC-2).
AC-2: no {{ under scaffolds/ or pi/resources/.
AC-3: Work Log records commands, results and the merge-base commit hash; any unrelated skill edit landing on the base branch before T-104 invalidates the gate and must be reconciled (SC-2). [G2 N7]

## Dependencies

- `T-100` — Pi package skeleton
- `T-101` — Convert new-task, new-spec, new-bug to markers
- `T-102` — Convert new-adr and change-request to markers
- `T-103` — Convert remaining skills with CLI references

## Files to Touch

- none (Work Log only)

## Verification

```bash
# V-SYNC; V-GOLD; grep -rn "{{" scaffolds and pi/resources (none); V-PY.
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
