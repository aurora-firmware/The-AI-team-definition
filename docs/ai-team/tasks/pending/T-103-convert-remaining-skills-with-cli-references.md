---
id: T-103
title: Convert remaining skills with CLI references
status: pending
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Convert remaining skills with CLI references

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 2**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P26 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- as T-101 for status-report, dev-loop and bug-loop; orchestrators converted even though not shipped. Out of scope: manifest.

## Acceptance Criteria

AC-1: no ai-team token outside a marker in any skill source.
AC-2: V-GOLD (SC-2).
AC-3: no lowercase ai-team under pi/resources/skills (SC-10).
AC-4: every bare mention of the CLI, including inside non-command fences, uses a noun marker (pi output has no `\bCLI\b` token). Added per Architect escalation ruling 2026-10-01 (T-102).

## Dependencies

- `T-097` — Move raw-body/raw-header test assertions to rendered output
- `T-099` — Pi target in the sync; generate pi/resources/

## Files to Touch

- sources/skills/{status-report,dev-loop,bug-loop}/{body.md,metadata.toml} and generated pi output (grep confirms exactly these three) [G2 N6]

## Verification

```bash
# V-SYNC; V-GOLD; grep -rn ai-team pi/resources/skills (none); V-PY.
# V-SYNC: the sync command documented in CLAUDE.md's Build section (currently: cd cli && python scripts/sync_init_scaffolds.py)
# V-GOLD: git diff --exit-code "$(git merge-base HEAD main)" -- cli/src/ai_team/init/scaffolds/claude cli/src/ai_team/init/scaffolds/codex
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
