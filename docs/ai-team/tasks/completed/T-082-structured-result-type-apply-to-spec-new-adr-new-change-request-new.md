---
id: T-082
title: Structured-result type; apply to spec new, adr new, change-request new
status: completed
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Structured-result type; apply to spec new, adr new, change-request new

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 1**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P5 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- internal result type with exit status, payload, error message and hint as separate fields; CLI text still joins them as today; each command split into a pure handler (explicit ProjectRoot, typed input → result) and the Typer wrapper; for --json commands payload equals the printed JSON. Out of scope: other modules, new public flags (ADR-004).
- [G2 B5] Also split ProjectRootNotFound in core/locator.py (lines ~133-188) so the exception carries message and hint separately, while str() joins them exactly as today. T-082 is the only task that edits locator.py.

## Acceptance Criteria

AC-1: result type carries status, payload, message, hint separately.
AC-2: --json output equals handler payload.
AC-3: handlers run with explicit root, no Typer, no process cwd.
AC-4: domain errors: message equals today's stderr minus hint.
AC-5: CLI output unchanged (SC-6).
AC-6: ProjectRootNotFound exposes separate message and hint fields, and its str() equals today's text (SC-6, Tool contract). [G2 B5]

## Dependencies

- `T-081` — Injectable "today" and framework version in the Python CLI

## Files to Touch

- new core/result.py (or equivalent)
- commands/spec.py
- adr.py
- change_request.py
- cli/src/ai_team/core/locator.py [G2 B5]
- new cli/tests/test_structured_results_create.py

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

I added `cli/src/ai_team/core/result.py` with a frozen `Result(status, payload, message, hint)` dataclass. Its `text()` joins message and hint with a single space, which is what the CLI prints. I gave each of the three `new` commands a pure handler (`create_spec`, `create_adr`, `create_change_request`) that takes an explicit `ProjectRoot` and typed input and returns a `Result`. No handler touches Typer or the process cwd. Committed on `task/T-082-structured-result-type` as `1e96ab4`.

Each Typer wrapper now calls `find_project_root(Path.cwd())`, calls the handler, then does one of three things: on failure it echoes `result.text()` to stderr and exits with `result.status`; with `--json` it prints `result.payload` through `print_json`; otherwise it echoes the path from the payload. `ProjectRootNotFound` in `core/locator.py` now takes `(message, hint)` and exposes both as attributes. The hint is the shared string "Run 'ai-team init' to bootstrap the project structure.", and `str()` gives the same text as before. All three raise sites were updated.

Decisions and rejected options:
- Domain errors (`ArtifactExists`, `LockTimeout`) become `Result(status=1, message=str(exc))` with no hint, because those messages had no separate hint.
- `ProjectRootNotFound` is still not caught by the wrappers, so it propagates exactly as before.
- I kept the result type free of Typer and left the `print_json` and echo logic in each wrapper rather than adding a shared emit helper; `render.py` is outside the task's file list.
- I did not touch the `AI_TEAM_TODAY` invalid-value `ValueError` from T-081, which is out of scope.

Verification: new tests in `cli/tests/test_structured_results_create.py` failed at import first (red), then full V-PY passed: 490 tests, ruff format and ruff check clean. Tests cover AC-1 to AC-4 and AC-6 directly; AC-5 rests on the unchanged existing CLI tests plus a `str()` equality assertion for the `--root` case. I did not diff stdout and exit codes against the pre-change CLI. No scaffold or command-doc regeneration was needed. Obstacles: `ArtifactExists` tests monkeypatch `next_adr_id` to force a collision; `ProjectRootNotFound.__init__` now takes `(message, hint)`, so pickling the exception would break (no caller pickles it).

For the reviewer: the three wrappers repeat the same few emit lines, accepted to stay inside the listed files. The AC-2 tests monkeypatch the handler to return a known payload and check that the CLI `--json` output equals it. Nothing remains for this task.

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

Both stages passed on commit 1e96ab4 (branch `task/T-082-structured-result-type`, reviewed against `feat/pi-extension`).

Stage 1 (acceptance criteria, S-005 and ADR-001..004):
- AC-1 met: frozen `Result(status, payload, message, hint)` in `core/result.py`, no Typer dependency; `text()` joins message and hint.
- AC-2 met: wrappers print `result.payload` via `print_json`; the `--json` output equals the handler payload.
- AC-3 met: `create_spec`, `create_adr` and `create_change_request` take an explicit `ProjectRoot` and typed input; none uses Typer or `Path.cwd()`.
- AC-4 met: `ArtifactExists` and `LockTimeout` become `Result(status=1, message=str(exc))`, which is today's stderr text (those errors had no hint).
- AC-5 met: see the byte-identity check below.
- AC-6 met: `ProjectRootNotFound(message, hint)` exposes both fields and `str()` joins them with one space. All three raise sites use a shared `_INIT_HINT`.
- Only the listed files changed (plus the new test file). No new public flags (ADR-004).

Stage 2 (quality):
- Code is small, focused and readable. The repeated emit lines in the three wrappers are an accepted tradeoff to stay inside the task's file list.
- Tests cover the result type, the handlers, `--json` equality and the locator split.
- Checks run from `cli/` on the task branch: `uv run pytest` gave 490 passed; `ruff format --check` and `ruff check` were clean.

Byte-identity check (reviewer-run; `feat/pi-extension` versus the task branch, in temp projects created with `ai-team init --no-interactive`, `AI_TEAM_TODAY=2026-01-02`):
- Compared: `spec new`, `adr new` and `change-request new`, covering plain, `--json`, `spec --author/--status`, `adr --status/--supersedes`, and the no-project-root case (cwd walk-up and `AI_TEAM_ROOT`).
- stdout and exit codes are identical for every case. Generated artifact trees and file contents are identical. The only difference is `framework_version` in `.ai-team.toml`, which comes from the git describe of each checkout.
- For the no-root case, the uncaught `ProjectRootNotFound` exception message is identical, including the hint. The only stderr differences are source line numbers and code snippets inside Rich's traceback frames, which is inherent to the code change.
- Forced already-exists (real collision for `adr` and `change-request`) and `ArtifactExists`/`LockTimeout` (monkeypatched for `spec`) were compared in-process with CliRunner: identical exit code 1, empty stdout and identical stderr.
- The plain duplicate-title case does not collide because IDs auto-increment; that is why collisions were forced.

Non-blocking observations:
- `ProjectRootNotFound` is not caught by the wrappers, so it still surfaces as a traceback. This is the same as before, and out of scope.
- The pickling caveat in the Work Log is noted and harmless.

Next owner: Development Loop.

