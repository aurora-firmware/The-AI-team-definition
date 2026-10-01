---
id: T-112
title: TS parity runner, command registry, handler stubs
status: completed
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# TS parity runner, command registry, handler stubs

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 3**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P35 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- vitest runner auto-discovers fixtures/parity cases with the T-088 rules (loads the shared lock-scoping list, applies the isolation rules, normalises only root paths); resolves root, sets overrides, compares tree/status/message; registry maps every tool-contract command to a handler module; stubs throw "not implemented"; later tasks edit only their module; filter by name prefix. [G2 B4] Cases whose command resolves to a stub are reported as skipped/todo, so `npm test` stays green. [G2 B7] Handler interface: `init` takes the start directory (plus `path`); `check-layout` takes the start directory and resolves its own root (port of check_layout.py `_repository_root`); every other handler takes a located ProjectRoot.

Size note (accepted at Gate 2, ruling 7): trivial stubs; removes shared-file conflicts for T-113–T-119.

## Acceptance Criteria

AC-1: new case discovered without registration (ADR-004).
AC-2: registry maps every command to exactly one handler (SC-11 groundwork).
AC-3: mismatch fails with diff (SC-5).
AC-4: V-PI passes; V-PI-F status-- reports the smoke case as pending (stub). [G2 B4]
AC-5: the registry's handler signatures follow the init / check-layout / located-root split. [G2 B7]

## Dependencies

- `T-088` — Parity fixture format and Python fixture runner
- `T-100` — Pi package skeleton
- `T-105` — TS result types, runtime clock/version, template loader
- `T-108` — Port the project root locator

## Files to Touch

- pi/test/parity.test.ts
- pi/src/core/commands/registry.ts
- 13 stub modules under pi/src/core/commands/ (spec, adr, change-request, task, bug, list, show, status, report, validate, archive, check-layout, init); vitest config may be touched

## Verification

```bash
# V-PI; V-PI-F status-- to confirm discovery.
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
Built the registry, 13 stub modules and the parity runner in two TDD cycles.

Cycle 1: `pi/src/core/commands/registry.ts` has a `COMMANDS` table mapping each of the 23 tool-contract commands to `{kind, handler}`; kind is `init`, `check-layout` or `root` (the init / check-layout / located-root split). Each command's handler lives in its own stub module so T-113 to T-119 edit only their own module. `handler.ts` holds the shared types plus `notImplemented` / `isStub`, which avoids a circular import with the registry.

Cycle 2: `pi/test/helpers/parity-runner.ts` implements the T-088 format, mirroring `cli/tests/parity_support.py`: discovers cases by `case.json`; loads `lock-sentinels.json` and excludes only those literal paths from the after-tree; unsets `AI_TEAM_ROOT` unless the case sets it, sets `AI_TEAM_TODAY` / `AI_TEAM_FRAMEWORK_VERSION` / `GIT_CEILING_DIRECTORIES`; materialises the before-tree in a temp dir; normalises only the root path (results and file text); drops hints; compares status/payload/message and the after-tree; emits an LCS line diff on mismatch. `parity.test.ts` covers AC-1 and AC-3 with throwaway fixture roots and fake registries, then generates one test per shared fixture. Cases whose command is still a stub become `it.todo` and are never run (192 todo, matching `ls -d fixtures/parity/*--* | wc -l`). Names start with the case directory name so `-t` filters by prefix.

Result: typecheck clean; 18 files, 385 tests pass, 192 todo. Handlers are synchronous like the core; the runner uses `process.env` and no `chdir`.

Rejected: helpers in `registry.ts` (circular import); detecting stubs by calling and catching (runs the code; a `WeakSet` marker is used instead).

Touched outside the listed files, necessarily: `handler.ts`, `test/helpers/parity-runner.ts` (keeps `parity.test.ts` short), and `test/locator.test.ts` (its `process.cwd` source scan now recurses into `commands/` and filters to `.ts`; the check itself is unchanged).

For later tasks: each implementer replaces its `notImplemented(...)` stub, after which its cases become real comparisons. The runner has not yet been exercised against a real handler on a shared fixture, so the first implementer may find edge cases (tree ordering, normalisation). Tree entries sort by JS code-unit order vs Python code point; paths are almost certainly ASCII, but T-113 to T-119 should confirm.

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

Stage 1 (acceptance): all five ACs met.
- AC-1: `discoverCases` finds any directory holding `case.json`; no registration. A unit test adds a new case dir and sees it discovered.
- AC-2: `COMMANDS` keys equal `resources/command-map.json` (23 commands), each with its own distinct handler module; all 23 commands used by the shared fixtures are registered.
- AC-3: mismatches in payload, status/message and after-tree fail with an LCS diff naming expected and actual (covered by tests).
- AC-4: `npm ci && npm run typecheck && npm test` on the task branch (after the scaffold sync, in a temporary worktree): typecheck clean, 18 files, 385 passed, 192 todo. `npm test -- parity -t "<prefix>"` filters by case-name prefix. Stub-backed cases report as todo and are never run.
- AC-5: `InitHandler` and `CheckLayoutHandler` take the start directory; `RootHandler` takes a located `ProjectRoot`; kinds are asserted per command.
- Files outside the list (`handler.ts`, `test/helpers/parity-runner.ts`, `test/locator.test.ts`) are justified in the work log and acceptable. `handler.ts` avoids a circular import, the helper keeps the test file short, and the locator scan change only recurses into `commands/` with no loosening of the check. No unspecified behaviour was added.

Stage 2 (quality): the runner matches `cli/tests/parity_support.py` and ADR-004 and the fixtures README. It loads the lock-sentinel list, excludes only those literal paths from the after-tree, unsets `AI_TEAM_ROOT` unless the case sets it, sets the today/version/git-ceiling overrides, substitutes `<ROOT>`, drops hints, normalises only the root path, rejects unsafe tree paths and symlinks, and restores the environment and temp dir. Tests cover success and failure paths and use independent sandboxes.

Non-blocking observations:
- `normalise` is applied to every string in after-tree entries (including `path` and `base64`), whereas Python rewrites only `text`. Root paths will not appear in those fields, so there is no practical difference.
- The runner does not `chdir` into the root as Python does. Handlers take explicit directories, so this is fine, but a handler that reads the cwd would diverge. T-113 to T-119 should avoid that.
- Tree sort uses JS code-unit order rather than Python code-point order, as the Developer noted. This only matters for non-BMP paths.
- The runner has not yet run a real handler against a shared fixture. The first implementer should check edge cases.
