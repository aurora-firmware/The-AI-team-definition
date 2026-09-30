---
id: T-080
title: CLAUDE.md pi checks and setup-guide pi install steps
status: in-progress
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# CLAUDE.md pi checks and setup-guide pi install steps

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 0**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P3 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- CLAUDE.md Key Conventions gain pi/, pi/resources/ (generated), fixtures/parity/ (reviewed contract); pi commands from pi/: `npm ci`, `npm run typecheck`, `npm test`, sync first (writes version file); behaviour change starts with reviewed fixture change. Setup guide: one-time sync then `pi install <path-to-pi>`; cross-commit Level 4 mismatch expected; mixed concurrent allocation unsupported; pi init writes empty [init].tools and no .claude/.codex. Out of scope: pi README (T-100), other guides.

## Acceptance Criteria

AC-1: CLAUDE.md documents pi typecheck/test and sync-first (SC-1, SC-13).
AC-2: pi/resources generated, fixtures/parity reviewed contract (ADR-004).
AC-3: local-path install incl. one-time sync (SC-1).
AC-4: mixed concurrency unsupported, cross-commit mismatch expected (SC-7, Config).
AC-5: pi init empty tools, no .claude/.codex.

## Dependencies

- None

## Files to Touch

- CLAUDE.md
- guides/setup-guide.md

## Verification

```bash
# grep for npm run typecheck / pi install / unsupported; V-PY.
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

Read the empty Work Log and the S-005 spec sections on the version file, `init` behaviour, the Level 4 mismatch and the unsupported mixed allocation. Wrote a grep-based red check for the phrases the acceptance criteria require and confirmed it failed (10 missing items). Then edited only `CLAUDE.md` and `guides/setup-guide.md`, committed on `task/T-080-claude-md-pi-checks-setup-guide` as `5606e0f`.

`CLAUDE.md` gained a "Test and Check the pi Package" section and three Key Conventions rows (`pi/`, `pi/resources/` generated, `fixtures/parity/` reviewed contract per ADR-004). The generated-output note now names `pi/resources/` as well as the CLI scaffolds. The setup guide gained an optional "Using the pi coding agent" section with the sync, `pi install <path-to-pi>`, the expected Level 4 mismatch, the unsupported mixed concurrent allocation, and the empty `[init].tools` and no `.claude/`/`.codex/` behaviour of pi `init`.

I deliberately left out a runner location and the `pi/src` layout, since the spec leaves them open. The check passes and the full V-PY verification is green (pytest 461 passed, ruff format and check clean). There was no scaffold or docs regeneration to do. `pi/` and `fixtures/` do not exist yet, so the pi commands are documented only. Review should confirm that "sync first" is worded accurately: `CLAUDE.md` describes the sync as `python scripts/sync_init_scaffolds.py` run from `cli/`, which matches the spec's "existing script gains a pi target". Nothing remains. The pi README (T-100) and other guides are out of scope.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
