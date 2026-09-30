---
id: T-081
title: Injectable "today" and framework version in the Python CLI
status: in-progress
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

### Session 1 — 2026-09-30

Added `cli/src/ai_team/core/runtime.py` as the only place that supplies today's date and the framework version. The override variables are `AI_TEAM_TODAY` (an ISO date) and `AI_TEAM_FRAMEWORK_VERSION`. All `date.today()` calls in the spec, adr, change_request, task, bug, report and archive commands now go through `today()`. The marker write in `init` and the installed-version lookup in `core/layout.py` go through `framework_version()`. The version lookup uses `importlib.metadata.version` at call time, so the `test_layout.py` monkeypatch still works. An invalid date override raises a `ValueError` that names `AI_TEAM_TODAY`. `cli.py --version` is left as is, per AC-1. New tests in `cli/tests/test_t081_runtime_overrides.py` cover each override and include a source-grep test for AC-1. A maintainer note was added at `cli/docs/maintainer-runtime-overrides.md`. Committed on `task/T-081-injectable-today-and-version` as `a45dc18` (feat) and `c77a602` (docs).

The new tests first failed (17 failed) and then passed. Full V-PY passes (478 tests, ruff format and ruff check clean). Test-setup obstacles: the `new` commands need an initialised project tree, so tests run `init` first; the YAML writer quotes the `created` date, so the assertion accepts optional quotes. The bad-date error is an uncaught `ValueError` rather than a formatted CLI error, because structured results are out of scope for this task (T-082 onward). No scaffold sync or `gen_docs.sh` was needed. Nothing remains.

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

Stage 1 (acceptance criteria), checked against the diff of `a45dc18` and `c77a602`:
- AC-1 met. `cli/src/ai_team/core/runtime.py` is the only module in `commands/` or `core/` that calls `date.today()` or `importlib.metadata.version`. The one other call is `cli.py:40` (`--version`), which is exempt.
- AC-2 met. `today()` is used for created dates in spec, task, bug, adr and change_request, for the task work-log session date, for the report date and for the archive cut-off.
- AC-3 met. `framework_version()` supplies the init marker's `framework_version` and the installed version compared in `core/layout.py`.
- AC-4 met. The changes are one-line swaps with unchanged output. The full suite passes with no overrides set.
- AC-5 met. An invalid `AI_TEAM_TODAY` raises `ValueError` naming the variable. It is uncaught, which fits the task's out-of-scope note on structured results.
- AC-6 met. `importlib.metadata.version` is looked up at call time with no from-import. The `test_layout.py` monkeypatch still works.
- The file count is over the guideline, but that was accepted at Gate 2. No unspecified behaviour was added.

Stage 2 (code quality):
- The module is small and readable. The override names are recorded in the maintainer note, which is kept out of `usage.md`. No dead code. Tests cover each override, the invalid-date failure path, and a source-grep for AC-1.
- I ran V-PY from `cli/` on the task branch: `uv run pytest` gave 478 passed, `ruff format --check` was clean and `ruff check` passed.
- This is consistent with S-005 (injectable clock and version) and ADR-001..004. Generated scaffolds are untouched, which is correct.

Non-blocking observations:
- An empty `AI_TEAM_FRAMEWORK_VERSION` is accepted as the version string. Only matters if a test sets it empty.
- The invalid-date error surfaces as a traceback. T-082 onward should map it to a formatted error.

Next owner: Development Loop.

