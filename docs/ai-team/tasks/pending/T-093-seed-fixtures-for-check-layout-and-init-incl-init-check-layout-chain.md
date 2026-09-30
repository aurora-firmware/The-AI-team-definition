---
id: T-093
title: Seed fixtures for check-layout and init, incl. init→check-layout chain
status: pending
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Seed fixtures for check-layout and init, incl. init→check-layout chain

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 1**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P16 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- check-layout clean tree; broken tree (missing dirs, bad .ai-team.toml, placeholder root guidance, version mismatch); root not found (the case sets AI_TEAM_ROOT, because check-layout's resolver walks up past the tmp dir and GIT_CEILING_DIRECTORIES doesn't stop it) [G2 R4]; tools = ["claude","codex"] with only the needed scaffold dirs. init with/without createRootGuidance, force, dryRun, path; all with empty tool list. SC-8 chain: each init after tree reused as a check-layout before tree expecting zero findings. Init fixtures never include .claude/.codex content. Out of scope: cross-implementation run (T-120).

## Acceptance Criteria

AC-1: every tool-contract field covered (SC-3).
AC-2: broken tree and init with/without guidance (SC-4).
AC-3: chained check-layout expects zero findings (SC-8).
AC-4: init after trees contain the T-087 .gitignore entry (SC-6).
AC-5: Python runner passes (SC-5).

## Dependencies

- `T-087` — TS lock entry in skeleton .gitignore; update B-017 tests and usage guide
- `T-088` — Parity fixture format and Python fixture runner

## Files to Touch

- case dirs check-layout--
- init--

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
