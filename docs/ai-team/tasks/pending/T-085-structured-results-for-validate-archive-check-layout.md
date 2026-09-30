---
id: T-085
title: Structured results for validate, archive, check-layout
status: pending
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Structured results for validate, archive, check-layout

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 1**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P8 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- validate returns findings (code, path, message) and selecting flags; archive returns moved/would-move paths; check-layout findings carry suggested fix separately; internal only (S-003 deferral stands). Out of scope: public --json, new finding codes.

## Acceptance Criteria

AC-1: pure handlers.
AC-2: check-layout suggested fix separate from message.
AC-3: archive --dry-run returns candidates, changes nothing.
AC-4: validation failure exit status equals today's.
AC-5: output unchanged, no public flags (SC-6, ADR-004).

## Dependencies

- `T-082` — Structured-result type; apply to spec new, adr new, change-request new

## Files to Touch

- commands/validate.py
- archive.py
- check_layout.py
- new cli/tests/test_structured_results_checks.py [G2 N6]

## Verification

```bash
# V-PY; V-DOCS.
# V-DOCS: bash cli/scripts/gen_docs.sh && git diff --exit-code cli/docs/commands.md
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
