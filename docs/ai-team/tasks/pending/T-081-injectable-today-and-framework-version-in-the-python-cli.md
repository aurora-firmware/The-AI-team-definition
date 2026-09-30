---
id: T-081
title: Injectable "today" and framework version in the Python CLI
status: pending
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Injectable "today" and framework version in the Python CLI

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 1**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P4 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- one core module exposes today and framework version, each reading a test-only env override in one place (task picks names, records them); replace every date.today() and importlib.metadata.version("ai-team"); invalid ISO override fails naming the variable. Out of scope: structured results, locking, --version output, user-visible output.

Size note (accepted at Gate 2, ruling 7): over file guideline, one-line swaps.

## Acceptance Criteria

AC-1: only the new module supplies today/version; no other date.today()/metadata.version("ai-team") in commands/ or core/. cli.py `--version` is explicitly exempt. [G2 N1]
AC-2: clock override used for created dates, work-log dates, report date, archive cut-off.
AC-3: version override written/compared as framework_version.
AC-4: without overrides stdout/stderr/exit codes unchanged (SC-6).
AC-5: invalid ISO fails naming the variable.
AC-6: the new module looks up importlib.metadata.version at call time (no from-import), so the existing monkeypatch in cli/tests/test_layout.py keeps working. [G2 N1]

## Dependencies

- `T-078` — Update the skill guide for the pi target and the marker contract
- `T-079` — Update the component map and system overview
- `T-080` — CLAUDE.md pi checks and setup-guide pi install steps

## Files to Touch

- new cli/src/ai_team/core/<runtime>.py; commands/{spec,task,bug,adr,change_request,archive,report,init}.py; core/layout.py; new test; new maintainer note under cli/docs/ (not usage.md)

## Verification

```bash
# V-PY; grep for date.today()/metadata.version in commands and core (only new module).
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
