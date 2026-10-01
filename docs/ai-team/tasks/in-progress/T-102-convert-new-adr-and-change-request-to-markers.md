---
id: T-102
title: Convert new-adr and change-request to markers
status: in-progress
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Convert new-adr and change-request to markers

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 2**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P25 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- as T-101; plus the Phase 2 render assertion for the new-adr --supersedes site (bare `supersedes` inside backticks for pi, unchanged for claude/codex).

## Acceptance Criteria

AC-1: every reference uses a marker.
AC-2: V-GOLD (SC-2).
AC-3: supersedes as bare field, no nested span (Inline context).
AC-4: shortened adr new --json intros render as mention form.
AC-5: no lowercase ai-team in pi output (SC-10).

## Dependencies

- `T-097` — Move raw-body/raw-header test assertions to rendered output
- `T-099` — Pi target in the sync; generate pi/resources/

## Files to Touch

- sources/skills/{new-adr,change-request}/{body.md,metadata.toml}
- generated pi output
- new cli/tests/test_render_adr_cr_skills.py [G2 N6]

## Verification

```bash
# V-SYNC; V-GOLD; grep guard; V-PY.
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

### Session 1 — 2026-10-01
Converted the new-adr and change-request skills to markers, following the T-101 pattern.
- **Tests first.** I wrote `cli/tests/test_render_adr_cr_skills.py` and watched 13 tests fail. It covers the five ACs:
  - no unmarked CLI reference in the bodies;
  - noun-marker headers that render the original description for claude and codex;
  - exact claude/codex text for each converted site;
  - pi renders: the supersedes site as `` `supersedes "<supersedes>"` ``, the adr new and change-request new mention forms, and the call forms;
  - no lowercase `ai-team` in the pi SKILL.md files.
- **Source edits.** In new-adr I used command markers for the intro and the Base command, a flag marker for `--supersedes`, and noun markers for "CLI command" and "CLI response values". In change-request I used command markers for the intro and the Run line, plus noun markers for "produced by the CLI", "return the CLI response values", and "from the CLI response". Both headers use the `{{ai-team-cli|the ai-team CLI|the ai_team tool}}` description marker.
- **Tried and rejected.** I first put a noun marker on the `<CLI command result or reason not run>` line in change-request's Output Format fence. The sync fails on a fence that mixes markers with other lines, so I reverted it. The line stays literal, and the AC-1 test strips fenced blocks before checking.
- **Rest of the session.** I ran the sync and committed the regenerated pi resources (`7aaa880`). The full Python suite, ruff, the pi typecheck and pi tests all pass, and the claude/codex scaffold diff against the merge-base is empty.
- **Remaining.** Nothing for this task. If the unmarked fence line is judged an AC-1 gap, fixing it needs either a sync change that allows non-marker fences to carry noun markers, or an ADR or spec decision. It is outside this task's files.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
