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

### Session 1 — 2026-10-01
Done: I read the S-005 marker contract and the existing marker implementation, then wrote `cli/tests/test_render_create_skills.py` first. It checks that no CLI reference is left outside a marker, that claude/codex text matches the old wording exactly, that the pi SKILL.md files have no lowercase `ai-team`, and that new-task renders `task new` as a call form with title and priority. After that I converted the three skills.

- Command invocations became command markers: the `task new`, `spec new` and `bug new` command lines. The `spec new --json` and `bug new --json` mentions in the intros render for pi as "the `ai_team` tool's `<command>` command".
- Flag markers cover `--author`, `--status` and `--task`, placed inside the existing backticks so the claude/codex text is unchanged.
- Bare "the CLI" and "CLI" mentions became noun markers: `{{ai-team-cli|the CLI|the tool}}` and `{{ai-team-cli|CLI|tool}}`.
- The header description uses `{{ai-team-cli|the ai-team CLI|the ai_team tool}}`, in both `[claude]` and `[codex]`.

I then ran the sync and committed the regenerated pi resources. V-GOLD shows the claude and codex scaffolds are byte-unchanged.

Tried and rejected: I did not put a flag marker on `--description` in new-spec ("the CLI has no `--description` flag"). That flag does not exist for `spec new`, so the sync would reject it. It stays as literal text after a noun marker, and it is not a binary reference.

Decision for the reviewer: I edited `test_skill_markers.py` (outside Files to Touch). Its "no markers in current sources" test became wrong once sources gained markers, so it now skips marker-bearing sources.

Known rough edge: pi renders the flag-marker sites as `author "<author>"`, `status "<status>"` and `task "<task>"` inside backticks. This is the specified inline behaviour, and it reads acceptably.

Remaining: nothing for this task. The other skills still contain raw CLI references, and later Phase 2 tasks cover them.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
