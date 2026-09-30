---
id: T-090
title: Seed fixtures for lifecycle transitions
status: completed
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Seed fixtures for lifecycle transitions

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 1**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P13 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- every valid transition; already-in-destination; not found; every invalid transition from each command's source-state set; task block with reason appends a work-log entry on the fixed clock.

## Acceptance Criteria

AC-1: each lifecycle command has a valid case (SC-3).
AC-2: every invalid source state has a case (SC-4).
AC-3: already-in-destination and not-found.
AC-4: Python runner passes (SC-5).

## Dependencies

- `T-088` — Parity fixture format and Python fixture runner

## Files to Touch

- case dirs task-start--
- task-complete--
- task-block--
- task-unblock--
- bug-start--
- bug-resolve--

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
Read the T-088 fixture README, the runner in `parity_support.py`, the seed helper and how T-089 guarded its creation cases. Wrote `test_parity_lifecycle_fixtures.py` first and confirmed it failed (25 failed) on the empty set. It checks that each lifecycle command keeps a valid case, every invalid source state, an already-in-destination no-op and an empty-project not-found. It also checks that `task block` appends a work-log entry on the fixed clock and numbers it after existing sessions. I then generated before-trees in a scratch script and seeded 35 cases through `seed_parity_fixture.py`, with `today` 2026-01-15 and `version` 1.0.0 (commit 7c95069). I inspected the recorded results and trees. Invalid-source cases come out as not-found errors that list all searched state folders. Already-in-destination is status 0 with `changed:false`. Valid cases move the file and rewrite `status`. Block appends `### Session N — 2026-01-15` / `Blocked: <reason>`.

Pre-existing defect found, not fixed (out of scope): `_append_work_log_entry` in `cli/src/ai_team/commands/task.py`, when a task has no `## Work Log` heading, computes `start = len(lines) - 3`, which lands on the blank line before the new heading, so the entry is inserted above `## Work Log`. I tried a `task block` case for this, rejected it rather than record the defect as contract, and dropped it. The loop should file a bug; once fixed, `task-block--creates-missing-work-log` can be seeded after a reviewed change.

Minor recorded quirk (`task-block--appends-after-existing-session`): the new entry is inserted after the section's trailing blank lines, so it abuts the following `## Review` heading with no blank line. The TS core must match this byte for byte. `task block` accepts every source state, so its only invalid outcomes are not-found and already-in-destination.

Scope deviation: the guard test is outside Files to Touch, added because T-089 did the same. Full pytest (720), ruff format and ruff check pass. Nothing remains for this task.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-09-30
PASS

Stage 1 (acceptance): AC-1 met: task-start, task-complete, task-unblock, bug-start and bug-resolve each have a valid-from-source case; task-block has one per source state (pending, in-progress, completed, blocked-as-already) plus a unicode reason, and its work-log entry on the fixed clock (2026-01-15) is recorded. AC-2 met: every invalid source state per command is a case whose recorded result is the not-found error listing the searched folders. AC-3 met: each command has an already-in-destination case (status 0, changed:false, tree unchanged) and an empty-project not-found case. AC-4 met: run from a detached worktree of the task branch, pytest passes (720), ruff format --check and ruff check are clean. Spot-checked case.json/after.json for task-block--appends-after-existing-session, task-start--invalid-from-completed, task-complete--already-completed and bug-resolve--invalid-from-open; they match actual command behaviour. The diff touches only fixtures/parity/ case dirs plus one test file.

Stage 2 (quality): the guard test is independent, parametrised over every command, covers success and failure paths, and is readable. The Developer saw it fail (25 failed) on the empty set before seeding.

Rulings:
(a) Extra guard test `cli/tests/test_parity_lifecycle_fixtures.py` is outside Files to Touch. Accepted as sound, consistent with the T-089 precedent; it adds no product behaviour.
(b) The omitted missing-Work-Log-heading case: bug claim independently verified. In `_append_work_log_entry` (cli/src/ai_team/commands/task.py:77-78), after `lines.extend(["", heading, ""])` the `start = len(lines) - 3` is the blank line before the heading, so the `## ` scan from `start + 1` hits the new heading immediately and the entry is inserted above `## Work Log`. The defect is real and pre-existing. Omitting the case is compatible with the ACs: none of AC-1 to AC-3 requires it (the description lists "task block with reason appends a work-log entry", which the seeded cases cover), and recording the defect as reviewed contract would make the TS core reproduce a bug. Reject-not-record was the right call.

Non-blocking observations:
- Follow-up: file a bug for `_append_work_log_entry` with no `## Work Log` heading; after the fix, seed `task-block--creates-missing-work-log` through a reviewed fixture change.
- task-block--appends-after-existing-session records the new entry abutting the following `## Review` heading with no blank line. It is the current real behaviour and is documented in the Work Log, so the TS core must match it byte for byte. It is arguably a quirk worth a future cleanup, which would need a reviewed fixture change.

