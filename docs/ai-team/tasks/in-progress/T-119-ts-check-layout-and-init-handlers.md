---
id: T-119
title: TS check-layout and init handlers
status: pending
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# TS check-layout and init handlers

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 3**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P42 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- check-layout on T-111, porting check_layout.py `_repository_root` (AI_TEAM_ROOT, else walk up for .ai-team.toml or project/, else the start directory; never fails not-found) [G2 B7]; init (path, force, dryRun, createRootGuidance), always non-interactive, writes project skeleton from pi/resources plus .ai-team.toml with empty [init].tools and runtime version, root guidance only when asked, never the declined note, never .claude/.codex. Out of scope: hint rewriting.

## Acceptance Criteria

AC-1: V-PI-F check-layout--, init-- pass (SC-5).
AC-2: init writes empty tools and runtime framework_version (Tool contract).
AC-3: check-layout on init output has zero findings (SC-8).
AC-4: zero type errors (SC-9).

## Dependencies

- `T-093` — Seed fixtures for check-layout and init, incl. init→check-layout chain
- `T-099` — Pi target in the sync; generate pi/resources/
- `T-107` — Port filesystem layer and slug generation
- `T-111` — Port the layout-diagnostics core
- `T-112` — TS parity runner, command registry, handler stubs

## Files to Touch

- pi/src/core/commands/{check-layout,init}.ts

## Verification

```bash
# V-SYNC; V-PI-F per prefix; full V-PI. [G2 B4]
# V-SYNC: the sync command documented in CLAUDE.md's Build section (currently: cd cli && python scripts/sync_init_scaffolds.py)
# V-PI-F: cd pi && npm test -- parity -t "<prefix>"   # a subset of parity cases
# V-PI: cd pi && npm ci && npm run typecheck && npm test   # after V-SYNC
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-10-01
I ran the scaffold sync first and read the Python `check_layout.py` and `init.py` as the reference. `check-layout.ts` ports `_repository_root` and adapts `layout.ts`'s `checkLayout` into the payload shape the fixtures expect. Its `resolvePath` duplicates a private helper in `layout.ts`. I did that to stay inside Files to Touch, instead of exporting the helper. `init.ts` ports `init_repository` with `tools=[]`, no confirm callback and no `.claude`/`.codex` copying. It sorts planned files by path components to match Python's `sorted(Path)` order, and writes the marker with `smol-toml`'s `stringify`, whose output matches the fixtures byte for byte. Reviewers should check that dry-run refusal returns the payload together with the message, and that `exists` takes precedence over `would-write` and `created` unless `force` is set. Both handlers were committed separately. Nothing remains, and I rejected no alternative approaches.

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

Stage 1: AC-1 met (parity `check-layout` 24 and `init` 22 cases pass). AC-2 met: init writes `[init].tools = []` and the runtime `framework_version`, confirmed by the byte-for-byte fixture match. AC-3 met: the init to check-layout chain fixtures report zero findings. AC-4 met: `npm run typecheck` is clean. Only the two files listed in Files to Touch changed, and no unspecified behavior was added.

Stage 2: Both handlers faithfully port the Python reference. `repositoryRoot` never fails, init is non-interactive, and it never writes the declined note or `.claude`/`.codex`. Full V-PI run after the scaffold sync: 26 files, 637 tests pass.

Non-blocking observations:
- `resolvePath` is duplicated from `layout.ts`. This is documented in the work log and was done to stay within scope. Consider exporting the helper later.
- No dedicated unit tests were added. Coverage relies on the parity fixtures, which is acceptable under the task's Verification.
