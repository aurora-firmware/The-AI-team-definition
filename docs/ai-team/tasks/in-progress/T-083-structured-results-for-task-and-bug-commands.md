---
id: T-083
title: Structured results for task and bug commands
status: pending
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Structured results for task and bug commands

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 1**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P6 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- task new/start/complete/block/unblock, bug new/start/resolve; "already in <state>" (exit 0) and not-found become structured results.

## Acceptance Criteria

AC-1: pure handlers for every task/bug leaf command.
AC-2: --json equals payload.
AC-3: already-in-state returns success with today's text.
AC-4: not-found error with today's message.
AC-5: output unchanged (SC-6).

## Dependencies

- `T-082` — Structured-result type; apply to spec new, adr new, change-request new

## Files to Touch

- commands/task.py
- commands/bug.py
- new cli/tests/test_structured_results_lifecycle.py

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
Added pure handlers for all task and bug leaf commands, following the T-082 pattern: `create_task`, `start_task`, `complete_task`, `block_task`, `unblock_task`, `create_bug`, `start_bug` and `resolve_bug`. Each takes a `ProjectRoot` and returns a `Result`. The Typer commands (`new_task`, `new_bug`, and the transition wrappers renamed `*_command`) resolve the root from the cwd, call the handler, and print.

Decisions:
- A successful transition returns the payload `{id, path, changed}`, and the wrapper prints `path` as before.
- "Already in <state>" is `status=0` with `message` set to today's text and `changed=False`. The wrapper prints `message` on stdout when it is set.
- Not-found is `status=1` with today's message, printed on stderr by the wrapper.
- `create_*` catch `ArtifactExists` and `LockTimeout` and return them as `status=1` results, the same way `create_spec` does.
- Transition commands got no `--json`. They had none before, and the task says output is unchanged.

Rejected: a shared transition-printing helper. `_emit_transition` is duplicated in `task.py` and `bug.py`, because the task's Files to Touch rules out a new shared module. Reviewer, please consider this.

Verification: ruff format, ruff check and the full pytest (504 passed) are green. Nothing remains.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
