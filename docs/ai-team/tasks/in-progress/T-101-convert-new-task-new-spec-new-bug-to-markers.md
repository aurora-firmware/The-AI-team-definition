---
id: T-101
title: Convert new-task, new-spec, new-bug to markers
status: in-progress
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Convert new-task, new-spec, new-bug to markers

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 2**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P24 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- replace every CLI reference in bodies and "via the ai-team CLI" in [claude]/[codex] headers with the right marker kind; noun marker claude/codex text reproduces each site exactly; V-SYNC.

## Acceptance Criteria

AC-1: every reference uses a marker.
AC-2: V-GOLD passes (SC-2).
AC-3: pi SKILL.md has no lowercase ai-team (SC-10).
AC-4: new-task renders task new as call form with title and priority.

## Dependencies

- `T-097` — Move raw-body/raw-header test assertions to rendered output
- `T-099` — Pi target in the sync; generate pi/resources/

## Files to Touch

- sources/skills/{new-task,new-spec,new-bug}/{body.md,metadata.toml}
- their generated pi skills and skill-calls
- new cli/tests/test_render_create_skills.py [G2 N6]

## Verification

```bash
# V-SYNC; V-GOLD; grep ai-team in the three pi skills (none); V-PY.
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
