---
id: T-117
title: TS report handler
status: completed
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# TS report handler

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 3**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P40 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- port commands/report.py (content, default path, out) using T-105 clock. [G2 B3] Import the status payload from status.ts (owned by T-116); do not edit status.ts. [G2 N12] `out` resolves against the handler's start directory, never process.cwd().

## Acceptance Criteria

AC-1: V-PI-F report-- passes, report file byte-identical (SC-5).
AC-2: out writes to that path.
AC-3: zero type errors (SC-9).

## Dependencies

- `T-091` — Seed fixtures for list, show, status, report
- `T-107` — Port filesystem layer and slug generation
- `T-112` — TS parity runner, command registry, handler stubs
- `T-116` — TS list, show, status handlers

## Files to Touch

- pi/src/core/commands/report.ts

## Verification

```bash
# V-PI-F report--; full V-PI. [G2 B4]
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
I ported `commands/report.py` to `pi/src/core/commands/report.ts`, test-first with a new `pi/test/report-handler.test.ts`. The handler reuses `statusPayload` from `status.ts` and `listMarkdownFiles` from `artifact-files.ts`, loads the bundled report template, and applies the same ordered placeholder substitutions as the Python reference. It writes UTF-8 and returns `{path, content}`. The default destination is `docs/reports/progress-report-<today>.md`, with the date from the `runtime.ts` clock. A relative `out` is resolved against `root.repo`, not `process.cwd()` (G2 N12). `RootHandler` receives only the located root, so `root.repo` stands in for the start directory. Reviewers should check this choice. The `report--default`, `report--empty-project` and `report--with-out` parity cases pass byte-identical, and typecheck and the full suite are green. I did not edit `status.ts` or any file outside `report.ts` and the new test file. I tried no alternatives that were rejected.

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

Stage 1 (acceptance):
- AC-1: met. The `report--default`, `report--empty-project` and `report--with-out` parity cases pass byte-identical (3 passed with `-t "report--"`).
- AC-2: met. `out` writes to that path. A relative `out` resolves against `root.repo`, not `process.cwd()` (G2 N12). The test chdirs elsewhere to prove it.
- AC-3: met. `npm run typecheck` reports zero errors.
- Scope: only `report.ts` and a new test file changed. `status.ts` is untouched and `statusPayload` is imported from it (G2 B3). No extra behaviour was added.

Stage 2 (quality):
- The port matches `commands/report.py` placeholder for placeholder, in the same order. `replaceAll` with a replacer function keeps `$` literal.
- The tests cover the default path, the relative and absolute `out` cases, and seeded specs. They are isolated and restore env and cwd.
- Full suite: 562 passed, 64 todo.

Non-blocking observations:
- Python validates `out` through typer. The TS handler adds an input check that rejects an empty or non-string `out`. This is reasonable defensive behaviour.
- Using `root.repo` as the start directory is acceptable given the `RootHandler` signature.
