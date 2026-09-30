---
id: T-099
title: Pi target in the sync; generate pi/resources/
status: completed
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Pi target in the sync; generate pi/resources/

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 2**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P22 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- write pi/resources/skills/<name>/SKILL.md for every skill (incl. orchestrators); pi/resources/skill-calls/<name>.json (call-form inputs for T-123); artifact templates, project skeleton (incl. .gitignore and leaf dirs), root guidance templates; claude/codex scaffold dir list for check-layout Level 1; copy of command map; git-ignored version file (pi/.gitignore) computed from the source tree via hatch-vcs, not installed metadata; fail if undeterminable. Claude/codex output unchanged. [G2 B1] The fake-repo tests in test_init_scaffolds.py set the version override (or SETUPTOOLS_SCM_PRETEND_VERSION) and one test asserts the "cannot determine version" failure. [G2 N2] The sync still runs under bare `python`: either compute the version without new imports (for example a subprocess to hatch), or switch the documented command to `uv run python scripts/sync_init_scaffolds.py` and update CLAUDE.md's Build section and cli/docs/usage.md's maintainer section accordingly. Out of scope: package.json, TS code, skill conversions.

## Acceptance Criteria

AC-1: V-SYNC produces all listed outputs (Component 2).
AC-2: version file git-ignored and equal to source-tree hatch-vcs version (Config, ADR-004).
AC-3: undeterminable version fails with clear message, asserted by a test (B1).
AC-4: two syncs leave no committed diff; V-GOLD passes (SC-2).
AC-5: the version equals what hatch/setuptools-scm reports with cli/pyproject.toml's raw-options (root "..", tag_regex). [G2 N2]

## Dependencies

- `T-080` — CLAUDE.md pi checks and setup-guide pi install steps
- `T-087` — TS lock entry in skeleton .gitignore; update B-017 tests and usage guide
- `T-097` — Move raw-body/raw-header test assertions to rendered output
- `T-098` — Pi marker rendering and derived pi headers

## Files to Touch

- cli/scripts/sync_init_scaffolds.py
- pi/.gitignore
- pi/resources/** (generated)
- new cli/tests/test_sync_pi_target.py
- cli/tests/test_init_scaffolds.py [G2 B1]
- possibly cli/pyproject.toml
- cli/uv.lock
- CLAUDE.md and cli/docs/usage.md [G2 N2]

## Verification

```bash
# V-SYNC twice; git status --porcelain pi/ cli/src (empty after commit); V-GOLD; V-PY.
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
Done: I added the pi target to `cli/scripts/sync_init_scaffolds.py`. It runs in two cycles, both committed on the task branch.

Cycle 1 covers the version. `compute_framework_version` returns `SETUPTOOLS_SCM_PRETEND_VERSION` if it is set. Otherwise it shells out to hatchling through `uv run --no-project --with hatchling --with hatch-vcs`, run from `cli/`. That applies the pyproject raw-options and avoids the frozen editable-install metadata, and it keeps the script stdlib-only, so bare `python` still works. The version is computed first and the sync fails with "cannot determine the framework version" if it can't be found. It is written to `pi/resources/version.txt`, which `pi/.gitignore` ignores.

Cycle 2 writes the rest of `pi/resources/`:
- `skills/<name>/SKILL.md` for every skill, including the orchestrators: the header is derived via `derive_pi_header` and the body is rendered for pi.
- `skill-calls/<name>.json`: an array of the call-form input objects in each rendered skill. The array is empty for skills without calls.
- `templates/`
- `project/` (skeleton with `.gitignore` and `.gitkeep` leaf dirs)
- `root/` (root guidance sources)
- `scaffold-dirs.json`: directory lists for project, claude and codex, for `check-layout` Level 1
- `command-map.json`: a byte copy of the source map

The sync replaces `pi/resources` wholesale each run, so stale files don't survive.

Tried and rejected:
- Switching the documented command to `uv run python ...`, because the subprocess approach keeps the documented command unchanged.
- Modifying `skill_markers.py` to collect calls, because the file is out of scope (I used a regex on rendered output).
- Committing the version anywhere, which the ADR forbids.

Follow-up from the T-098 review: `derive_pi_header` emits the description unquoted, and I did not quote it. It lives in `skill_markers.py`, which is not in this task's files. I checked all 19 generated pi descriptions, and none contains a colon-space or a leading YAML-special character, so nothing is broken today. A later task that touches `skill_markers.py` should quote or escape the value. T-123 could assert that the pi headers parse as YAML.

Remaining: T-100 should extend `pi/.gitignore` with the node entries (mine holds only `resources/version.txt`). T-105 reads `pi/resources/version.txt` and should use that name. T-119 and T-111 read `pi/resources/scaffold-dirs.json`, `pi/resources/root/` and `pi/resources/project/`.

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

Reviewed `feat/pi-extension...task/T-099-pi-target-in-the-sync-generate-pi-resources` (869a04e, ed5dd7b) in a detached worktree of the branch head.

Stage 1 (acceptance criteria):
- AC-1: the sync produces every listed output: `skills/*/SKILL.md` (19, orchestrators included), `skill-calls/*.json`, `templates/`, `project/` (with `.gitignore` and leaf dirs), `root/`, `scaffold-dirs.json` (project, claude, codex), `command-map.json` and `version.txt`.
- AC-2: `pi/.gitignore` ignores `resources/version.txt`. `git status --ignored` shows it as `!!`, and it is not tracked. The value `0.10.3.dev149+ged5dd7bbf` equals the hatch output.
- AC-3: `test_sync_fails_clearly_when_the_version_cannot_be_determined` asserts the failure. The version is computed before any output is written.
- AC-4: two consecutive syncs leave `git status --porcelain pi cli/src` empty apart from the ignored version file. V-GOLD (diff of the claude and codex scaffolds against the merge-base with main) is empty.
- AC-5: a test compares the computed version with `hatchling version` run under `cli/pyproject.toml`. I ran the same command by hand and got an identical value.
- Generated `pi/resources/` is committed and everything except `version.txt` is tracked. This matches the task ("no committed diff") and ADR-004, which forbids only committing the version.

Deviations judged:
- `cli/tests/test_skill_markers.py` (autouse version pin and fake-repo fixtures for templates and root) is acceptable. Its fake repos run the real sync, which now needs a version and the new source inputs. The change is minimal and needed to keep the suite green.
- `CLAUDE.md` and `cli/docs/usage.md` are in Files to Touch under G2 N2. They are needed for the `uv` dependency and the override variable, and the edits are small and accurate.
- Regex extraction of skill-calls from the rendered body is acceptable. `skill_markers.py` is outside the task's files, and the regex matches both renderer forms (`tool with` and `tool call`). Tests cover the extracted calls and the empty case.
- Computing the version with `uv run --no-project --with hatchling --with hatch-vcs ... hatchling version` follows ADR-004. The version comes from the source tree via hatch-vcs, is never committed, and is not read from installed metadata. The script stays stdlib-only, so bare `python` works.

Stage 2 (quality): the code is focused and readable. Failure paths are tested (undeterminable version, unrenderable marker, stale-file removal, idempotence). Tests are independent and use tmp_path. Nothing hardcodes secrets. Checks run: `uv run pytest` (959 passed), `ruff format --check` and `ruff check` both clean.

Non-blocking observations:
- All 19 `skill-calls/*.json` are `[]` today because the source skills hold no markers yet. That is expected before the skill conversions.
- The call regex `\{[^`]*\}` would truncate a call whose JSON value contains a backtick. The sync would then fail loudly on invalid JSON rather than emit bad output. Revisit if a flag value can contain a backtick.
- The Developer's follow-up about quoting pi header descriptions in `skill_markers.py` stands (T-123).

Next owner: Development Loop.

