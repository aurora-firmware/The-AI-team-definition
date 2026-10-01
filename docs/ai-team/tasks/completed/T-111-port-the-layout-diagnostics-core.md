---
id: T-111
title: Port the layout-diagnostics core
status: completed
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Port the layout-diagnostics core

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 3**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P34 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- port core/layout.py Levels 1–4; reads scaffold dir list and root-guidance starter sections from pi/resources and version from T-105 runtime; suggested fixes a separate field.

## Acceptance Criteria

AC-1: same findings as Python for every T-093 check-layout tree (SC-5).
AC-2: checks directories from the generated scaffold list when tools list claude/codex (S-003 Level 1).
AC-3: suggested fix separate.
AC-4: V-PI passes (SC-9).

## Dependencies

- `T-093` — Seed fixtures for check-layout and init, incl. init→check-layout chain
- `T-099` — Pi target in the sync; generate pi/resources/
- `T-105` — TS result types, runtime clock/version, template loader
- `T-110` — Port the validation core

## Files to Touch

- pi/src/core/layout.ts
- tests

## Verification

```bash
# V-SYNC; V-PI.
# V-SYNC: the sync command documented in CLAUDE.md's Build section (currently: cd cli && python scripts/sync_init_scaffolds.py)
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
Ported the layout core (Levels 1–4) to `pi/src/core/layout.ts` (`checkLayout`, `resolveLayout`, `checkLevel1`–`checkLevel4`), with fixture-driven tests in `pi/test/layout.test.ts`. Findings are `{level, path, problem, suggestedFix}`, so the suggested fix is a separate field. Level 1 reads the directory list from `pi/resources/scaffold-dirs.json` for the configured tools only; Level 3 reads starter sections from `pi/resources/root/{CLAUDE,AGENTS}.md`; the version comes from the T-105 `frameworkVersion` runtime or `options.currentVersion`. Level 2 reuses `validateProject` (T-110) one scope at a time.

Tests: all 23 T-093 `check-layout--*` fixtures materialised from `before.json` and compared with `expected.payload.findings` (`problem`→`message`, `suggestedFix`→`suggested_fix`); extras cover per-tool scaffold dirs, the separate suggested-fix field, Python-style list formatting for invalid tools, and the version override through `env`. Typecheck clean; 17 files, 365 tests pass.

Python behaviours reproduced by hand: `repr` of TOML values, `$`/`^` matching only `\n`, universal newlines, strict UTF-8 keeping the BOM, Python `splitlines` separators, code-point ordering. A `validateProject` error becomes a "blocked" finding only if it carries a Node errno `code`; anything else is rethrown.

Rejected: exporting `buildProjectRoot` from `locator.ts` (outside Files to Touch; duplicated the `ProjectRoot` literal locally); passing smol-toml error text through (fails the `invalid-marker` fixture; a small translator handles the unterminated table header case).

For the reviewer / later: TOML syntax-error wording matches Python only for the unterminated table header case, others carry smol-toml's reason plus line/column (no fixture; broader parity needs a new fixture and ADR-004 review). Blocked Level 2/3 I/O-error wording differs from Python's `[Errno N]` text (no fixture). T-118 must map results to the command payload (`status` 1 on findings) and resolve the repo root. `scaffold-dirs.json` is loaded on each Level 1 call.

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

Reviewed commit a4e57c3 on `task/T-111-port-the-layout-diagnostics-core` (pi/src/core/layout.ts, pi/test/layout.test.ts) against cli/src/ai_team/core/layout.py and the T-093 check-layout fixtures. V-SYNC and V-PI were run in a temporary worktree: typecheck clean, 17 files / 365 tests pass.

Stage 1 (acceptance criteria):
- AC-1 met. All 23 `check-layout--*` fixtures are materialised and compared to `expected.payload.findings`; they pass. Levels 1-4 match the Python logic line by line (messages, suggested fixes, sort order, placeholder rule, version rules).
- AC-2 met. Level 1 reads `pi/resources/scaffold-dirs.json` for the configured tools only; tests cover claude-only and codex-only.
- AC-3 met. `LayoutFinding.suggestedFix` is a separate field and a test asserts it is not in the problem text.
- AC-4 met. V-PI passes.
- Only the two files in Files to Touch were changed. No unspecified behaviour was added.

Stage 2 (quality): logic, error handling, tests, readability and security are acceptable. No blocking issues.

Non-blocking observations:
1. `pythonRepr` cannot reproduce Python's `repr` for TOML floats and dates, because smol-toml returns `1.0` as the number `1`. I confirmed that an unquoted `framework_version = 1.0` yields "Configured framework version 1 is invalid" where Python yields `1.0`. The work log says TOML `repr` was reproduced, which is not accurate for these values. No fixture covers it. If parity is wanted, add a fixture and take it through ADR-004 review. The parser limitation may need a decision.
2. The TOML syntax-error wording and the blocked Level 2/3 I/O-error wording diverge from Python outside the fixtured cases. The Developer already disclosed this.
3. `starterGuidanceSections` is read outside the try block, whereas Python reads it inside. This is harmless because the resource is generated.

Next owner: active Development Loop.
