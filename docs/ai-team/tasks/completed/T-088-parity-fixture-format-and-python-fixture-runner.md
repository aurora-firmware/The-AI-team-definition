---
id: T-088
title: Parity fixture format and Python fixture runner
status: completed
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Parity fixture format and Python fixture runner

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 1**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P11 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- README defines one directory per case named <command-slug>--<case>, holding command and input (tool-contract field names), clock and version, expected exit status and structured result (errors compared on message only), before and after trees. Trees must survive git (empty dirs, nested .gitignore, names like .ai-team.lock, exact bytes/line endings): recommend a serialized tree manifest per side plus .gitattributes -text. Only absolute root paths normalised. [G2 ruling 1] Lock-sentinel scoping: exactly two literal paths, <project_dir>/.ai-team.lock and the T-087 TS lock path (file or directory subtree), no globs, are excluded from the after-tree comparison only; the list is defined once in a machine-readable file under fixtures/parity/ that both runners load, and the README records the reasoning (tree scoping, not normalisation; SC-5, ADR-003). Before-trees may contain .ai-team.lock. The project .gitignore listing both paths is still compared byte for byte. [G2 ruling 2] Serialized tree format is required (the root .gitignore ignores .claude, .codex, .pi and .ai-team.toml at any depth). [G2 B6] Isolation rules for both runners, recorded in the README: unset AI_TEAM_ROOT unless the case sets it; materialise trees outside any git work tree and set GIT_CEILING_DIRECTORIES to the tmp parent; not-found cases are recorded through explicit root or AI_TEAM_ROOT only, so messages contain only the root path. Runner auto-discovers cases (no index), materialises before tree in tmp, sets overrides, dispatches to T-082–T-086 handlers, compares tree/status/result. Seed helper records a new case from Python and refuses to overwrite (ADR-004). One smoke case: status on an empty project. Out of scope: bulk cases (T-089–T-093), TS runner (T-112).

## Acceptance Criteria

AC-1: README defines fields, tree encoding, normalisation, the two-path lock scoping with its reasoning, and the isolation rules (Component 5, ADR-004, ruling 1). [G2]
AC-2: new case discovered without registration.
AC-3: tree/status/message mismatch fails with diff (SC-5).
AC-4: seed helper refuses existing case.
AC-5: clock and version set only via T-081 overrides.
AC-6: the lock-scoping list lives in one machine-readable file that the Python runner loads (and the TS runner will load). [G2 ruling 1]
AC-7: cases run with AI_TEAM_ROOT unset unless set by the case, outside any git work tree, with GIT_CEILING_DIRECTORIES set. [G2 B6]

## Dependencies

- `T-081` — Injectable "today" and framework version in the Python CLI
- `T-082` — Structured-result type; apply to spec new, adr new, change-request new
- `T-083` — Structured results for task and bug commands
- `T-084` — Structured results for list, show, status, report
- `T-085` — Structured results for validate, archive, check-layout
- `T-086` — Structured result for init with internal empty-tools mode
- `T-087` — TS lock entry in skeleton .gitignore; update B-017 tests and usage guide

## Files to Touch

- fixtures/parity/README.md
- fixtures/parity/.gitattributes
- cli/tests/test_parity_fixtures.py (+ optional support module)
- cli/scripts/seed_parity_fixture.py
- fixtures/parity/status--empty/

## Verification

```bash
# V-PY.
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
I built the parity fixture format and the Python runner, in three red→green cycles. First I wrote the tree-manifest, lock-scoping and discovery code. Then the runner and recorder. Last the seed helper, README and smoke case.

Format decisions:
- A case is a directory `<command-slug>--<case>` holding `case.json` (command, tool-contract `input`, `today`, `version`, optional `env` and `project_dir`, and `expected` with status and payload or message), plus `before.json` and `after.json`. The two tree files are serialised manifests: sorted entries of dir or file, with `text` as UTF-8 and `base64` otherwise, so empty directories, `.ai-team.lock`, nested `.gitignore` and exact line endings survive git.
- Remediation hints are never recorded; errors compare the message only.
- Only the absolute root is normalised, to `<ROOT>`, in results and file text.
- `lock-sentinels.json` lists exactly `<project_dir>/.ai-team.lock` and `<project_dir>/.ai-team-ts.lock`. They are dropped from the after tree, including anything beneath the TS path, with no globs. `project/sub/.ai-team.lock` is still compared.
- The runner unsets `AI_TEAM_ROOT` unless the case sets it, and sets `GIT_CEILING_DIRECTORIES` to the temp parent. It materialises the tree in a fresh temp directory and passes an explicit root unless the case sets `AI_TEAM_ROOT`. It sets clock and version only through `AI_TEAM_TODAY` and `AI_TEAM_FRAMEWORK_VERSION`. It restores the environment and cwd afterwards.
- `record_case` and the seed script refuse to overwrite an existing case and reject names that are not slug`--`case.
- Dispatch covers every command in the tool table, not only `status`, so the bulk-case tasks (T-089 to T-093) need no runner changes. `init` runs with an empty tools list. `ProjectRootNotFound` becomes a status-1 result carrying the message.

Tried and rejected:
- Committing raw directory trees. The root `.gitignore` ignores `.claude`, `.codex`, `.pi` and `.ai-team.toml`, and git drops empty directories.
- Per-case lock lists, and passing the lock file location into `_execute`. A single repo-level file is what the TS runner will load.

Verification: full pytest 567 passed, ruff format/check clean. Commits df400a3, 296d908, 6956fba.

What remains:
- The bulk cases (T-089 to T-093) and the TS runner (T-112).
- The runner's `<ROOT>` and `env` conventions should be mirrored exactly in the TS runner.
- The pi lock path was taken from the T-087 skeleton `.gitignore`: `.ai-team-ts.lock` directly under `project_dir`.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-09-30
PASS

Stage 1 (acceptance criteria), checked against the diff and the S-005 and ADR-004 rules:
- AC-1: `fixtures/parity/README.md` defines the case fields, the manifest tree encoding, root-only normalisation, the two-path lock scoping with its reasoning (tree scoping, not normalisation), and the isolation rules. `.gitattributes` sets `-text`.
- AC-2: `discover_cases` globs the directories for `case.json`, with no index. A test adds a case without registering it.
- AC-3: mismatches in the after tree, the exit status and the error message each produce a unified diff. Tests cover all three.
- AC-4: `record_case` and the seed script refuse to overwrite an existing case. A test covers it.
- AC-5: clock and version are set only through `AI_TEAM_TODAY` and `AI_TEAM_FRAMEWORK_VERSION`. A case without them is rejected.
- AC-6: `lock-sentinels.json` lists exactly the two literal paths, `<project_dir>/.ai-team.lock` and `<project_dir>/.ai-team-ts.lock`. The runner loads it. There are no globs, and `project/sub/.ai-team.lock` is still compared. Exclusion applies only to the after tree.
- AC-7: `AI_TEAM_ROOT` is unset unless the case sets it. The tree is materialised in a fresh temp directory and `GIT_CEILING_DIRECTORIES` is set to its parent. The root is passed explicitly otherwise. The environment and cwd are restored afterwards.
- The status--empty smoke case is present. No files outside the task's scope were touched, and there are no `cli/src` changes.

Stage 2 (quality):
- Logic is correct: manifests are sorted, paths are checked for escape, binary content falls back to base64, and hints are dropped so errors compare on message only.
- Tests cover both success and failure paths and are independent.
- Verification in a detached worktree from `cli/`: `uv run pytest` gave 567 passed. `ruff format --check` and `ruff check` are clean.

Non-blocking observations:
- The task frontmatter still says `status: pending`. The loop should handle it on completion.
- The TS runner (T-112) must mirror the `<ROOT>` and `env` conventions, and the `.ai-team-ts.lock` path taken from the T-087 skeleton.
