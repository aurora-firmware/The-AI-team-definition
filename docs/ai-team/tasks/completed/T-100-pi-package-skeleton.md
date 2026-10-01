---
id: T-100
title: Pi package skeleton
status: completed
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Pi package skeleton

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 2**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P23 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- pi manifest with extension entry and every generated skill except dev-loop, bug-loop, integrate; minimum Node; pi host peer deps with minimum 0.87.1; typecheck and test scripts per CLAUDE.md; full Phase 3/4 runtime dependency set settled here (round-tripping YAML, TOML parser, slug transliteration, pi's schema library) so later tasks run in parallel; strict tsconfig; vitest config; stub index.ts; README (dev setup, one-time sync, scratch PI_CODING_AGENT_DIR, mixed concurrency unsupported). Out of scope: core logic, tool registration.

Size note (accepted at Gate 2, ruling 7): boilerplate for a new package.

## Acceptance Criteria

AC-1: manifest lists every non-orchestrator skill and no orchestrator (SC-10).
AC-2: min Node and pi peer ≥0.87.1 (Config).
AC-3: V-PI after V-SYNC on clean checkout: zero type errors, tests pass (SC-9).
AC-4: README documents scratch dir, sync prerequisite, mixed concurrency unsupported (SC-7).
AC-5: only entry and adapter import the pi API, enforced by a pi/test guard that fails on any pi import under pi/src/core. [G2 N4]
AC-6: the package scripts are named exactly `typecheck` and `test`, matching CLAUDE.md (ruling 4).

## Dependencies

- `T-080` — CLAUDE.md pi checks and setup-guide pi install steps
- `T-099` — Pi target in the sync; generate pi/resources/

## Files to Touch

- pi/package.json
- pi/package-lock.json
- pi/tsconfig.json
- pi vitest config
- pi/src/index.ts
- pi/README.md
- pi/.gitignore (add node_modules/) [G2 N4]
- pi/test/imports.test.ts [G2 N4]

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
Built the pi package skeleton in three commits. First came the toolchain: `package.json`, strict `tsconfig.json` (NodeNext, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`), `vitest.config.ts`, a stub `src/index.ts` and an extended `.gitignore`. It also has the `test/imports.test.ts` guard, which scans `src/core` for static, dynamic or `require` imports of the pi packages. I confirmed it fails when a violation is planted. Second came the manifest: `pi.skills` lists the 16 non-orchestrator generated skills, and `test/manifest.test.ts` checks the skills list, extension entry, engine, peer range and script names. Third came the README, covering the one-time sync, `npm ci`/typecheck/test, a scratch `PI_CODING_AGENT_DIR`, the import rule and the mixed-concurrency limitation, with `test/readme.test.ts` checking those mentions.

I settled the runtime dependencies: `yaml`, `smol-toml`, `transliteration` and `typebox`. I verified the pi host package name and version with `npm view`. The peer range is `>=0.87.1` and the dev dependency is pinned to exactly 0.87.1. The full V-SYNC then V-PI run from a clean `node_modules`, cli pytest (959 passed) and ruff all pass.

Rejected: using `@mariozechner/pi-coding-agent`, which has no 0.87.1 release. Also rejected: comparing versions with array `>=`, which compares as strings. I added two test files beyond the Files to Touch list so that AC-1, AC-2, AC-4 and AC-6 each have a test. The `pi-agent-dev` skills could not be loaded because the Skill tool was disabled. Nothing remains for this task. Later tasks must decide how `typebox` and `src/core` should be resolved at runtime when pi loads the package from a path.

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

Reviewed the triple-dot diff `feat/pi-extension...task/T-100-pi-package-skeleton` (3 commits) in a temporary worktree. Verified: V-SYNC, then `npm ci`, `npm run typecheck` (zero errors) and `npm test` (12 passed in 3 files), plus cli pytest (959 passed).

Stage 1 (acceptance):
- AC-1 met. `pi.skills` lists exactly the 16 non-orchestrator skills. They match `pi/resources/skills` minus dev-loop, bug-loop and integrate, and `manifest.test.ts` asserts this against the generated directory.
- AC-2 met. `engines.node` is `>=22.19.0` and the peer range is `>=0.87.1`.
- AC-3 met. The V-SYNC then V-PI run passed.
- AC-4 met. The README covers the scratch `PI_CODING_AGENT_DIR`, the sync prerequisite and the mixed-concurrency limitation.
- AC-5 met. `imports.test.ts` covers static, dynamic and require forms, and both `@earendil-works` and `@mariozechner` scopes. It also tolerates a missing `src/core`.
- AC-6 met. Scripts are exactly `typecheck` and `test`.

Extra files: `test/manifest.test.ts` and `test/readme.test.ts` are outside Files to Touch. They are accepted. They are the only automated evidence for AC-1, AC-2, AC-4 and AC-6, they add no runtime behaviour, and the Work Log discloses them.

Dependencies: `yaml`, `smol-toml`, `transliteration` and `typebox` match the Phase 3/4 set the task describes. `typebox` 1.3.27 is the same version pi-coding-agent depends on. The pi host is a peer dependency, as S-005 requires, and is pinned to 0.87.1 as a dev dependency. No ADR-004 conflict, since only the manifest and tooling are touched.

Stage 2 (quality): strict tsconfig is appropriate, there is no dead code, and the tests are independent. There are no security concerns.

Non-blocking observations:
- The peer range has no upper bound. This is acceptable for now.
- The Work Log's open question on runtime resolution of `typebox` and `src/core` under a path install belongs to a later task.
