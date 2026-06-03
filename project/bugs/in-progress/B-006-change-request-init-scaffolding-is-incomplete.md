---
id: B-006
title: Change-request init scaffolding is incomplete
severity: high
status: in-progress
created: '2026-06-03'
---

# Change-request init scaffolding is incomplete

## Summary

`ai-team init` does not scaffold the change-request surfaces implied by the
0.6.0 change-request workflow. Freshly initialized repositories do not receive a
`change-request` skill, and they also do not receive `project/change-requests/`.
As a result, `ai-team change-request new` fails in a freshly initialized repo
because the destination directory is missing.

## Reproduction Status

Status: confirmed

Confirmed locally on 2026-06-03 against the current repository source after
comparing tags `0.5.0..0.6.0` and running `ai-team init` into `/tmp`.

## Evidence

- Logs / stack traces / failing assertions: `FileNotFoundError: [Errno 2] No such file or directory: '/tmp/ait-init-repro/project/change-requests/CR-001-test-request.md.tmp~'`
- Screenshots or recordings: none
- Failing command or test: `UV_CACHE_DIR=/tmp/uv-cache uv run --project /home/daneel/projects/the-ai-team-definition/cli ai-team change-request new "Test request"` from a freshly initialized repo root
- First diagnostic step if not yet reproduced: compare `cli/src/ai_team/init/sources/skills/`, `cli/src/ai_team/init/scaffolds/*/skills/`, and `cli/scripts/sync_init_scaffolds.py`

## Reproduction Steps

1. Initialize a new repo from the current CLI source:
   ```bash
   cd /home/daneel/projects/the-ai-team-definition/cli
   UV_CACHE_DIR=/tmp/uv-cache uv run ai-team init /tmp/ait-init-repro --tools codex --no-interactive --force
   ```
2. Inspect the generated scaffold:
   ```bash
   find /tmp/ait-init-repro -maxdepth 4 -type f | sort
   ```
3. Observe that no `.codex/skills/change-request/SKILL.md` exists and no `project/change-requests/.gitkeep` exists.
4. From the initialized repo root, attempt to create a change request with the local CLI source:
   ```bash
   cd /tmp/ait-init-repro
   UV_CACHE_DIR=/tmp/uv-cache uv run --project /home/daneel/projects/the-ai-team-definition/cli ai-team change-request new "Test request"
   ```

## Expected Behavior

Fresh `ai-team init` output should include all project artifact directories that
the CLI can create artifacts under, including `project/change-requests/`.

If the framework contract includes a Planner-facing `change-request` skill, init
should also generate `.claude/skills/change-request/SKILL.md` and
`.codex/skills/change-request/SKILL.md`, and Planner agent source definitions
should list that skill.

After init, `ai-team change-request new "<title>"` should create
`project/change-requests/CR-NNN-<slug>.md` without requiring the user to manually
create the directory.

## Actual Behavior

Fresh init output omits `project/change-requests/`. The scaffold generator's
`PROJECT_LEAF_DIRS` does not include `change-requests`, so generated project
scaffolds omit the directory.

Fresh init output also omits a generated `change-request` skill. There is no
`cli/src/ai_team/init/sources/skills/change-request/` source directory, and the
Planner sources do not list `change-request` among primary skills.

When `ai-team change-request new "Test request"` runs in the initialized repo,
the command attempts to write
`project/change-requests/CR-001-test-request.md.tmp~` and crashes with
`FileNotFoundError` because the parent directory does not exist.

## Environment

- OS / platform: local Linux workspace
- Language / runtime version: Python 3.14 via `uv`
- Relevant dependencies: local `ai-team` CLI source
- Branch / commit: `dev-agent`, current working tree on 2026-06-03

## Related

- Task: `T-046`, `T-047`, `T-048`, `T-054`, `T-055`
- Specification: `project/specs/coordinated-process-and-cli-workflow-improvements.md`

## Suspected Area

- `cli/scripts/sync_init_scaffolds.py`
- `cli/src/ai_team/init/sources/skills/`
- `cli/src/ai_team/init/scaffolds/`
- `cli/src/ai_team/init/sources/agents/claude/planner.md`
- `cli/src/ai_team/init/sources/agents/codex/planner.toml`
- `cli/src/ai_team/commands/change_request.py`

## Fix Verification

```bash
cd cli
python scripts/sync_init_scaffolds.py
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_init.py tests/test_init_scaffolds.py tests/test_change_request_new.py
UV_CACHE_DIR=/tmp/uv-cache uv run ruff format --check .
UV_CACHE_DIR=/tmp/uv-cache uv run ruff check .

rm -rf /tmp/ait-init-repro
UV_CACHE_DIR=/tmp/uv-cache uv run ai-team init /tmp/ait-init-repro --tools codex --no-interactive
test -d /tmp/ait-init-repro/project/change-requests
test -f /tmp/ait-init-repro/.codex/skills/change-request/SKILL.md
cd /tmp/ait-init-repro
UV_CACHE_DIR=/tmp/uv-cache uv run --project /home/daneel/projects/the-ai-team-definition/cli ai-team change-request new "Test request"
```

## Diagnosis Log

<!-- Mandatory before implementation. Append one entry before changing production code. Format:
### Diagnosis N — YYYY-MM-DD
Reproduction status:
Evidence captured:
Isolated fault:
Root cause or fault hypothesis:
Planned verification:
-->

### Diagnosis 1 — 2026-06-03
Reproduction status: Confirmed locally on `bug/B-006-change-request-init-scaffolding-is-incomplete` before changing production code.
Evidence captured: `UV_CACHE_DIR=/tmp/uv-cache uv run ai-team init /tmp/ait-b006-repro --tools codex --no-interactive --force` completed, but `test -d /tmp/ait-b006-repro/project/change-requests` returned `1` and `test -f /tmp/ait-b006-repro/.codex/skills/change-request/SKILL.md` returned `1`. Running `UV_CACHE_DIR=/tmp/uv-cache uv run --project /home/daneel/projects/the-ai-team-definition/cli ai-team change-request new "Test request"` from `/tmp/ait-b006-repro` failed with `FileNotFoundError: [Errno 2] No such file or directory: '/tmp/ait-b006-repro/project/change-requests/CR-001-test-request.md.tmp~'`. A focused pytest attempt, `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_init.py::test_init_tools_codex_scaffolds_codex_agents_and_skills tests/test_change_request_new.py`, could not run because the current uv environment has no `pytest` executable.
Isolated fault: `cli/scripts/sync_init_scaffolds.py` omits `change-requests` from `PROJECT_LEAF_DIRS`, so generated project scaffolds omit `project/change-requests/.gitkeep`. The package-owned skill source tree also lacks `cli/src/ai_team/init/sources/skills/change-request/`, so regenerated Claude and Codex scaffolds cannot include the change-request skill.
Root cause or fault hypothesis: The 0.6.0 change-request CLI/template/model surfaces were added without updating the init scaffold source-of-truth to export the matching project artifact directory and Planner-facing skill.
Planned verification: Add regression coverage for the generated project skeleton and exported skills, add the missing source-of-truth entries, regenerate scaffolds with `python scripts/sync_init_scaffolds.py`, then run the bug's focused pytest/ruff verification and manually confirm fresh init includes `project/change-requests/`, includes `.codex/skills/change-request/SKILL.md`, and allows `ai-team change-request new "Test request"` to create a file.

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-06-03
Implemented the init-scaffolding fix on `bug/B-006-change-request-init-scaffolding-is-incomplete`. Added regression coverage requiring fresh Codex init output to include `.codex/skills/change-request/SKILL.md` and `project/change-requests/.gitkeep`, requiring the sync script's generated project skeleton to include `change-requests/.gitkeep`, and requiring source/generated change-request skill files for both tools.

Updated the source of truth by adding `change-requests` to `cli/scripts/sync_init_scaffolds.py`, adding `cli/src/ai_team/init/sources/skills/change-request/`, and listing the new skill plus `project/change-requests/` write scope in Planner sources. Regenerated scaffolds with `UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/sync_init_scaffolds.py`, which created the generated Claude/Codex skill files and project `.gitkeep`.

Verification passed with `UV_CACHE_DIR=/tmp/uv-cache uv run --group dev python -m pytest tests/test_init.py::test_init_tools_codex_scaffolds_codex_agents_and_skills tests/test_init_scaffolds.py::test_sync_script_replaces_project_with_empty_lifecycle_skeleton tests/test_init_scaffolds.py::test_init_scaffolds_export_change_request_skill_and_project_directory tests/test_change_request_new.py` (7 passed), `UV_CACHE_DIR=/tmp/uv-cache uv run --group dev python -m ruff format --check .`, and `UV_CACHE_DIR=/tmp/uv-cache uv run --group dev python -m ruff check .`. Manual verification also passed: a fresh `/tmp/ait-b006-fixed` Codex init contained `project/change-requests/` and `.codex/skills/change-request/SKILL.md`, and `ai-team change-request new "Test request"` created `/tmp/ait-b006-fixed/project/change-requests/CR-001-test-request.md`.

One environment issue was worked around: the `pytest` console script shim points at a stale interpreter path, so verification used `python -m pytest`. No implementation work remains for B-006.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that diagnosis, fix, verification, and code quality passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
