---
id: T-104
title: Record the Phase 2 scaffold golden comparison
status: completed
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Record the Phase 2 scaffold golden comparison

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 2**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P27 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- clean checkout with all Phase 2 merged: V-SYNC, V-GOLD against merge-base with main, no unrendered {{ in generated files; record commands and output. One-time migration gate (SC-2). If it fails, fix the owning source.

## Acceptance Criteria

AC-1: V-GOLD no diff (SC-2).
AC-2: no {{ under scaffolds/ or pi/resources/.
AC-3: Work Log records commands, results and the merge-base commit hash; any unrelated skill edit landing on the base branch before T-104 invalidates the gate and must be reconciled (SC-2). [G2 N7]

## Dependencies

- `T-100` — Pi package skeleton
- `T-101` — Convert new-task, new-spec, new-bug to markers
- `T-102` — Convert new-adr and change-request to markers
- `T-103` — Convert remaining skills with CLI references

## Files to Touch

- none (Work Log only)

## Verification

```bash
# V-SYNC; V-GOLD; grep -rn "{{" scaffolds and pi/resources (none); V-PY.
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

Verification gate only: no repository files were changed and nothing was committed. All commands ran on branch task/T-104-record-the-phase-2-scaffold-golden-comparison. Its HEAD is d47a25d5d46e12594151883cb017be5f233908ce, branched from feat/pi-extension with T-100 to T-103 merged. Merge-base with main: 306ee16b2e7d2bda8afd9e8e39d9d3b75f71f981.

V-SYNC: `cd cli && python scripts/sync_init_scaffolds.py` exited 0 ("Synchronized init scaffolds in .../cli/src/ai_team/init/scaffolds"). `git status --porcelain` afterwards showed no changes to tracked files. The only entries were two untracked files that were already present, docs/ai-team/docs/reports/progress-report-2026-09-30.md and progress-report-2026-10-01.md. The sync therefore reproduces the committed scaffolds and pi/resources exactly.

V-GOLD (AC-1): `git diff --exit-code "$(git merge-base HEAD main)" -- cli/src/ai_team/init/scaffolds/claude cli/src/ai_team/init/scaffolds/codex` printed nothing and exited 0. The Claude and Codex scaffolds are byte-identical to main at the merge-base.

AC-2: `grep -rn '{{' cli/src/ai_team/init/scaffolds/ pi/resources/` produced no matches (grep exit 1). No unrendered markers remain.

AC-3, base-branch edit audit: `git log $(git merge-base HEAD main)..HEAD -- cli/src/ai_team/init/sources/skills cli/src/ai_team/init/sources/agents` lists exactly four commits:
- b23203b feat(skills): convert new-task, new-spec and new-bug CLI references to markers (T-101)
- 7aaa880 feat(skills): convert new-adr and change-request CLI references to markers (T-102)
- 46ed07d feat(skills): render noun and flag markers in non-command fences for pi (T-102 follow-up, per the architect-ruling amendment fa0fee8)
- 12711ec feat(skills): convert status-report, dev-loop and bug-loop to markers (T-103)

Every commit is part of the Phase 2 conversion work. No agents/ source was touched, and no unrelated skill edit landed on the base branch, so the gate is not invalidated.

Other checks:
- `cd cli && UV_CACHE_DIR=/tmp/uvcache uv run pytest`: 1022 passed in 10.89s.
- `uv run ruff format --check .`: 91 files already formatted.
- `uv run ruff check .`: all checks passed.
- `cd pi && npm run typecheck`: `tsc --noEmit` clean.
- `cd pi && npm test`: vitest, 3 files and 12 tests passed.

Nothing remains. The migration gate (SC-2) is satisfied.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-10-01

PASS

Independently re-ran the gate on feat/pi-extension (HEAD 9e67c1d; the only change since the Work Log's base d47a25d is this task file).

Stage 1 (acceptance criteria):
- AC-1: `git diff --exit-code "$(git merge-base HEAD main)" -- cli/src/ai_team/init/scaffolds/claude cli/src/ai_team/init/scaffolds/codex` exited 0 with no output.
- AC-2: `grep -rn '{{' cli/src/ai_team/init/scaffolds/ pi/resources/` produced no matches (exit 1).
- AC-3: merge-base is 306ee16b2e7d2bda8afd9e8e39d9d3b75f71f981, matching the Work Log (main tip is the same commit). The audit of `sources/skills` and `sources/agents` from the merge-base lists exactly b23203b (T-101), 7aaa880 (T-102), 46ed07d (T-102 architect-ruling follow-up) and 12711ec (T-103). All are Phase 2 conversion work, no agents/ change and no unrelated skill edit. The gate is not invalidated.
- V-SYNC: sync exited 0 and left no tracked-file changes (only the two untracked progress reports).
- No implementation diff and no files outside the task file were touched, consistent with "Files to Touch: none".

Stage 2 (quality): no code in scope. The Work Log is specific and its claims reproduced.
- `UV_CACHE_DIR=/tmp/uvcache uv run pytest`: 1022 passed.
- pi: `npm run typecheck` clean, `npm test` 3 files and 12 tests passed.

Non-blocking observation: the Work Log says nothing was committed, while the Work Log commit 9e67c1d itself landed on feat/pi-extension. This is only the lifecycle bookkeeping commit.
