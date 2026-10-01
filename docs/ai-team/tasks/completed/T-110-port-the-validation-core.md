---
id: T-110
title: Port the validation core
status: completed
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Port the validation core

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 3**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P33 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- port core/validate.py with identical finding codes, messages, relative paths, ordering. Out of scope: validate command (T-118).

## Acceptance Criteria

AC-1: same findings in same order for every T-092 tree (SC-5).
AC-2: malformed frontmatter same code and message.
AC-3: V-PI passes (SC-9).

## Dependencies

- `T-092` — Seed fixtures for validate and archive
- `T-107` — Port filesystem layer and slug generation
- `T-108` — Port the project root locator

## Files to Touch

- pi/src/core/validate.ts
- tests

## Verification

```bash
# V-PI.
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
Ported the validation core to `pi/src/core/validate.ts` as `validateProject(root, scopes)` plus `Finding` and `toRelativePath`, following the Python structure. Cross-reference indexes for spec slugs, task ids and ADR ids are built regardless of the selected scopes, and the specs index includes `specs/archive`. Findings keep Python's order: tasks by state folder, then bugs, specs, ADRs and change requests.

Python behaviour kept: id patterns print the Python source text (e.g. `^T-\d{3}$`) in messages; the matcher uses `\p{Nd}` because Python's `\d` matches all Unicode digits; directory listings sort by code point, not UTF-16 unit; frontmatter errors from the T-089 models become `frontmatter-invalid` findings carrying the parser's message; other errors propagate; the spec id check reads raw frontmatter through the source map so a missing id gives `id-missing`.

`pi/test/validate.test.ts` auto-discovers every `validate--*` case in `fixtures/parity` (15 T-092 fixtures), materialises each before-tree in a temp dir, runs the core, normalises the root to `<ROOT>` and compares to `expected.payload`. Two extra tests cover malformed frontmatter and the empty-scope case. Typecheck clean; 16 files, 336 tests pass.

Not done (belongs to T-118): `--all` / no-flags defaulting; the test helper does the mapping itself. Unhandled edge: a falsy non-string spec id such as YAML `0`/`false`, which Python treats as no id for the filename check while the pi parser stringifies it. No fixture exercises it.

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

Both stages passed on commit e8cb5d7 (only `pi/src/core/validate.ts` and `pi/test/validate.test.ts` touched; no out-of-scope behaviour such as `--all` defaulting).

Stage 1:
- AC-1: met. `validateProject` mirrors `core/validate.py` check-for-check (codes, messages, `id-pattern` printing Python source text, relative paths, per-state folder order, spec index including `specs/archive`). The test auto-discovers all 15 `validate--*` fixtures and compares to `expected.payload`; all pass.
- AC-2: met. Frontmatter errors from the models become `frontmatter-invalid` with the parser message; fixture coverage plus an explicit test.
- AC-3: met. After `sync_init_scaffolds.py`, in a temporary worktree: `npm ci`, `npm run typecheck` clean, `npm test` 16 files / 336 tests pass.

Stage 2: logic, tests (success and failure paths, temp-dir isolation with cleanup), readability and security are acceptable.

Non-blocking observations:
- Known gap (declared in the Work Log): a falsy non-string spec id (YAML `0`/`false`) differs from Python in the filename check. No fixture covers it; consider a follow-up if the parity corpus grows.
- Python `re.match` with `$` also accepts a trailing newline in ids; the JS regex does not. Practically unreachable from single-line frontmatter values.

