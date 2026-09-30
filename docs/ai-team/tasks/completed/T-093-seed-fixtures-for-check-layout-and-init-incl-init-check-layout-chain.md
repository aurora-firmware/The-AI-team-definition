---
id: T-093
title: Seed fixtures for check-layout and init, incl. init→check-layout chain
status: completed
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

### Session 1 — 2026-10-01
Seeded the `check-layout` and `init` parity fixtures and added `cli/tests/test_parity_layout_init_fixtures.py` as a coverage guard, following the T-091/T-092 pattern. I wrote the guard first and saw 12 failures. I then recorded the cases from the Python CLI with `parity_support.record_case` and reviewed the outputs. The suite now passes with 866 tests, and ruff is clean.

The `init` cases all run in the empty-tools mode, use no `.claude` or `.codex` content, and cover:
- defaults and explicit-false flags
- root guidance on and off
- dry-run, including dry-run combined with root guidance
- a `path` subdirectory, with and without guidance
- a refused overwrite, plus a dry-run refused overwrite
- forced overwrite, and `force` together with `createRootGuidance` over existing guidance
- existing root guidance being kept

Every successful non-dry-run init has a chained `check-layout--after-init-*` case expecting zero findings. The two `path` cases are chained by stripping the `sub/` prefix from the after-tree, because `check-layout` has no `path` input. The `check-layout` cases cover a clean tree and broken trees at levels 1 to 4. They also cover claude-only, codex-only and both-tool trees that contain only their scaffold directories. Root-not-found sets `AI_TEAM_ROOT=<ROOT>`.

The runner's `check-layout` dispatch ignores `AI_TEAM_ROOT`, so that case behaves as an empty tree. I did not touch `parity_support.py`, since it is outside the task's files.

Nothing was tried and rejected apart from adding a `chain_prefix` field to `case.json`. I dropped it because the README field table does not list it, and derived the prefix from the init input instead.

Remaining for T-120: `check-layout--invalid-marker` records Python `tomllib` wording, and `init--refuses-overwrite` depends on Python's sorted collision order. Both need the TS implementation to match the recorded output, or a reviewed fixture change.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-10-01
PASS

Reviewed commit bdcd060 against feat/pi-extension. The diff touches only `fixtures/parity/check-layout--*`, `fixtures/parity/init--*` and `cli/tests/test_parity_layout_init_fixtures.py`. No implementation code changed. `uv run pytest` gives 866 passed, and `ruff format --check` and `ruff check` are clean.

Stage 1:
- AC-1: every init field (`path`, `force`, `dryRun`, `createRootGuidance`) is covered both ways, along with defaults. `check-layout` has a clean case, per-level broken cases, and claude/codex/both tool scaffolds.
- AC-2: a broken tree (missing dirs, invalid marker, placeholder guidance, version mismatch) and init with and without guidance are covered. Root-not-found sets `AI_TEAM_ROOT=<ROOT>`.
- AC-3: every successful non-dry-run init has a `check-layout--after-init-*` case. Its before tree equals the init after tree (rebased for `path`), and it expects zero findings.
- AC-4: the guard asserts `.ai-team-ts.lock` is in every init after-tree `.gitignore`.
- AC-5: the Python runner passes.

Stage 2: the guard tests are independent and read-only. They cover both success and failure paths. Init fixtures contain no `.claude` or `.codex` content.

Non-blocking observations, which the Developer also recorded for T-120:
- `check-layout--invalid-marker` records Python `tomllib` wording.
- `init--refuses-overwrite` depends on Python's sorted collision order.
- The runner's `check-layout` dispatch ignores `AI_TEAM_ROOT`, so the root-not-found case currently behaves like an empty tree. This is outside this task's files.
