---
id: T-080
title: CLAUDE.md pi checks and setup-guide pi install steps
status: in-progress
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# CLAUDE.md pi checks and setup-guide pi install steps

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 0**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P3 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- CLAUDE.md Key Conventions gain pi/, pi/resources/ (generated), fixtures/parity/ (reviewed contract); pi commands from pi/: `npm ci`, `npm run typecheck`, `npm test`, sync first (writes version file); behaviour change starts with reviewed fixture change. Setup guide: one-time sync then `pi install <path-to-pi>`; cross-commit Level 4 mismatch expected; mixed concurrent allocation unsupported; pi init writes empty [init].tools and no .claude/.codex. Out of scope: pi README (T-100), other guides.

## Acceptance Criteria

AC-1: CLAUDE.md documents pi typecheck/test and sync-first (SC-1, SC-13).
AC-2: pi/resources generated, fixtures/parity reviewed contract (ADR-004).
AC-3: local-path install incl. one-time sync (SC-1).
AC-4: mixed concurrency unsupported, cross-commit mismatch expected (SC-7, Config).
AC-5: pi init empty tools, no .claude/.codex.

## Dependencies

- None

## Files to Touch

- CLAUDE.md
- guides/setup-guide.md

## Verification

```bash
# grep for npm run typecheck / pi install / unsupported; V-PY.
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

Read the empty Work Log and the S-005 spec sections on the version file, `init` behaviour, the Level 4 mismatch and the unsupported mixed allocation. Wrote a grep-based red check for the phrases the acceptance criteria require and confirmed it failed (10 missing items). Then edited only `CLAUDE.md` and `guides/setup-guide.md`, committed on `task/T-080-claude-md-pi-checks-setup-guide` as `5606e0f`.

`CLAUDE.md` gained a "Test and Check the pi Package" section and three Key Conventions rows (`pi/`, `pi/resources/` generated, `fixtures/parity/` reviewed contract per ADR-004). The generated-output note now names `pi/resources/` as well as the CLI scaffolds. The setup guide gained an optional "Using the pi coding agent" section with the sync, `pi install <path-to-pi>`, the expected Level 4 mismatch, the unsupported mixed concurrent allocation, and the empty `[init].tools` and no `.claude/`/`.codex/` behaviour of pi `init`.

I deliberately left out a runner location and the `pi/src` layout, since the spec leaves them open. The check passes and the full V-PY verification is green (pytest 461 passed, ruff format and check clean). There was no scaffold or docs regeneration to do. `pi/` and `fixtures/` do not exist yet, so the pi commands are documented only. Review should confirm that "sync first" is worded accurately: `CLAUDE.md` describes the sync as `python scripts/sync_init_scaffolds.py` run from `cli/`, which matches the spec's "existing script gains a pi target". Nothing remains. The pi README (T-100) and other guides are out of scope.

### Session 2 — 2026-09-30

I read the Work Log and the FAIL review verdict from `feat/pi-extension`, then fixed both findings in the "Test and Check the pi Package" section of `CLAUDE.md` and changed nothing else. For the first finding, I removed the claim that typecheck and tests fail without the version file. The text now says only what S-005 states. The sync renders `pi/resources/` and writes the git-ignored version file, the pi package fails to load without it, and so the sync runs first. For the second finding, the working directories are now explicit: run the sync from `cli/` first, then run `npm ci`, `npm run typecheck` and `npm test` from `pi/`. Committed on `task/T-080-claude-md-pi-checks-setup-guide` as `5ebdcc6`.

I kept the session 1 grep check. Every required phrase is still present, so the check needed no changes. I considered mentioning which tool reports the load failure, but rejected it because S-005 leaves that detail open. V-PY is green: pytest 461 passed, and ruff format and check are clean. Nothing remains. I left the setup-guide "duplicate IDs" wording unchanged, as the reviewer marked it non-blocking.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-09-30
FAIL

Stage 1 (acceptance criteria): AC-1 to AC-5 are all addressed in the diff (commit 5606e0f), only `CLAUDE.md` and `guides/setup-guide.md` were touched, and the Level 4 mismatch, unsupported mixed allocation, empty `[init].tools` and no `.claude/`/`.codex/` statements match S-005 (Config section, SC-7). Stage 1 is otherwise satisfied, but one CLAUDE.md statement is not spec-backed and the section is self-contradictory (below), so the work does not meet the "spec-backed, no asserted open details" bar.

Findings:

1. **`CLAUDE.md`, "Test and Check the pi Package", second sentence** ("...the git-ignored version file the pi package needs at load time, so typecheck and tests fail without it.") - S-005 only says that a missing version file makes the pi package fail to load the tool at runtime, with a message telling the user to run the sync. It does not say `npm run typecheck` or `npm test` fail without it, and the spec leaves the runner and toolchain layout open. What should change: restate what the spec says, e.g. that the sync renders `pi/resources/` and writes the git-ignored version file, that the package fails to load without it, and that the sync therefore runs first. Drop the claim that typecheck and tests fail.

2. **`CLAUDE.md`, same section, first sentence** - "From `pi/`, run the scaffold sync first (from `cli/`: `python scripts/sync_init_scaffolds.py`)" is contradictory about the working directory. What should change: make it unambiguous, e.g. "Run the scaffold sync first, from `cli/`: `python scripts/sync_init_scaffolds.py`. Then, from `pi/`, run:" followed by the npm block.

Checked and fine: the pi commands (`npm ci`, `npm run typecheck`, `npm test`) come from the task description and the spec's "TypeScript toolchain for type checking and tests"; no runner location or `pi/src` layout is asserted; no project-specific build commands were added to framework sources beyond this repo's own CLAUDE.md; ADR-004 fixture-first wording is consistent; the setup guide section is spec-backed (local-path install, one-time sync, Level 4 mismatch, unsupported mixed allocation, pi init behaviour). The "can produce duplicate IDs" phrasing in the setup guide is a reasonable reading of the spec's lock rationale (non-blocking).

Next owner: Developer (via the Development Loop).

### Review Verdict — 2026-09-30 (cycle 2)
PASS

Stage 1 (acceptance criteria): reviewed the full branch diff against `feat/pi-extension` (5606e0f + 5ebdcc6); only `CLAUDE.md` and `guides/setup-guide.md` changed.
- AC-1: `CLAUDE.md` documents `npm run typecheck`, `npm test`, `npm ci` and sync-first. Met.
- AC-2: Key Conventions rows mark `pi/resources/` as generated and `fixtures/parity/` as the reviewed contract (ADR-004), with fixture-first wording. Met.
- AC-3: the setup guide gives the one-time sync followed by `pi install <path-to-pi>`. Met.
- AC-4: the setup guide states mixed concurrent allocation is unsupported and the cross-commit Level 4 mismatch is expected. Met.
- AC-5: the setup guide states pi `init` writes an empty `[init].tools` and creates no `.claude/` or `.codex/`. Met.
- Prior finding 1 (unsupported claim that typecheck and tests fail without the version file): resolved. The text now says only that the sync renders `pi/resources/`, writes the git-ignored version file, and that the package fails to load without it.
- Prior finding 2 (contradictory working directory): resolved. The sync is run from `cli/` first, then the npm commands from `pi/`.
- No unspecified behaviour or extra files.

Stage 2 (quality): the wording is accurate and spec-backed, with no asserted open details (runner location, `pi/src` layout). The docs are clear and the Markdown is consistent with the surrounding sections. Nothing is hardcoded into framework sources beyond this repo's own CLAUDE.md. The Developer reported V-PY green (pytest 461 passed, ruff clean); this is a docs-only diff, so I did not re-run it.

Non-blocking: the setup guide phrase "can produce duplicate IDs" is a reasonable reading of the spec's lock rationale.

Next owner: Development Loop.
