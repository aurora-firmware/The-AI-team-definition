---
id: T-086
title: Structured result for init with internal empty-tools mode
status: pending
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Structured result for init with internal empty-tools mode

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 1**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P9 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- pure handler with path, force, dry_run, create_root_guidance and an explicit (possibly empty) tool list, non-interactive; result lists written/planned files and root-guidance outcome; "declined" note is presentation only; can write .ai-team.toml with tools = [] so pi-semantics fixtures can be seeded from Python; CLI --tools/--no-interactive surface unchanged. Out of scope: skeleton .gitignore (T-087), TS.

## Acceptance Criteria

AC-1: explicit possibly-empty tool list without prompting.
AC-2: empty list writes empty [init].tools and framework_version from T-081.
AC-3: declined note excluded from result.
AC-4: dry_run returns plan, writes nothing.
AC-5: CLI output and prompts unchanged (SC-6); `--no-interactive` without `--tools` still fails (init.py:67) — the empty-tools mode is internal only (ruling 5).

## Dependencies

- `T-082` — Structured-result type; apply to spec new, adr new, change-request new

## Files to Touch

- commands/init.py
- new cli/tests/test_structured_results_init.py [G2 N6]

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
Added `init_repository` in `cli/src/ai_team/commands/init.py`. It is a pure, non-interactive handler that takes a path, an explicit possibly-empty tool list, force, dry_run and create_root_guidance. It returns a `Result` whose payload lists the written or planned files and the per-file root-guidance outcome. Unsupported tools and collisions without force return `status=1` results, and the collision result includes the dry-run plan payload so the wrapper can print `WOULD WRITE` lines before the error, as the old code did.

Interactive root-guidance prompting stays a CLI concern. The handler accepts an optional `confirm_root_guidance` callback that the wrapper supplies only when not `--no-interactive`. The "declined" note text is built only in the wrapper, from `declined` outcomes. `--no-interactive` without `--tools` still fails in `_resolve_tools`, so the empty-tools mode is internal only. `--tools none` already produced an empty list and is covered by a test.

Tests are in `cli/tests/test_structured_results_init.py` (AC-1 to AC-5), and the existing init tests pass unchanged. The full suite (544 passed), ruff format and ruff check are clean. `gen_docs.sh` produced no diff. Everything went in one red-green cycle and one commit because the handler and wrapper refactor are coupled. No alternatives were rejected. Nothing remains. Skeleton `.gitignore` is T-087 and the TypeScript side is out of scope.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
