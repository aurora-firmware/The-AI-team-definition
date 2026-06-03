---
id: B-007
title: Dev-loop baseline test discovery is too rigid
severity: medium
status: in-progress
created: '2026-06-03'
---

# Dev-loop baseline test discovery is too rigid

## Summary

The `dev-loop` skill's baseline test step is too rigid. It currently starts
with strict instructions to find a test command in a specific root `CLAUDE.md`
format and aborts if that exact command format is missing. The intent of the
baseline step is to confirm the project starts in a green state before
test-driven development begins, but the implementation should be flexible enough
to follow project-specific testing instructions and ask the user when no
instructions or tests are available.

## Reproduction Status

Status: not yet reproduced

Reported from observed dev-loop startup behavior and the current dev-loop skill
description. The first implementation step should confirm the exact wording in
the source and generated scaffold copies.

## Evidence

- Logs / stack traces / failing assertions: none captured
- Screenshots or recordings: none
- Failing command or test: dev-loop startup aborts when it cannot find the expected test command format in root `CLAUDE.md`
- First diagnostic step if not yet reproduced: inspect `cli/src/ai_team/init/sources/skills/dev-loop/body.md` and generated `dev-loop/SKILL.md` scaffold copies for the baseline test command discovery instructions

## Reproduction Steps

1. Start `dev-loop` in a project whose test instructions are valid but not
   expressed in the exact root `CLAUDE.md` format currently required by the
   skill.
2. Observe that dev-loop aborts instead of interpreting the available testing
   guidance or asking the user for the correct test instructions.
3. Start `dev-loop` in a project with no documented test instructions or no test
   suite in place.
4. Observe that dev-loop aborts without asking the user how to proceed.

## Expected Behavior

The baseline step should verify that the project starts in a green state before
test-driven development begins.

The skill should not depend on one exact root `CLAUDE.md` format. It should use
the available project guidance to determine the right testing instructions for
that project, even when the instructions are phrased differently or refer to a
project-local documentation file.

If there are no testing instructions or no tests in place, the skill should ask
the user for the intended test command or for explicit confirmation that no
automated baseline test is available.

## Actual Behavior

The skill description is overly prescriptive about finding a test command in a
specific root `CLAUDE.md` format. If that expected format is absent, dev-loop
aborts rather than using other clear project testing guidance or asking the user.

## Environment

- OS / platform: local workspace
- Language / runtime version: not applicable; process/skill behavior
- Relevant dependencies: generated `dev-loop` skill source and scaffolds
- Branch / commit: `dev-agent`, current working tree on 2026-06-03

## Related

- Task: `T-051`
- Specification: `project/specs/coordinated-process-and-cli-workflow-improvements.md`

## Suspected Area

- `cli/src/ai_team/init/sources/skills/dev-loop/body.md`
- `cli/src/ai_team/init/scaffolds/claude/skills/dev-loop/SKILL.md`
- `cli/src/ai_team/init/scaffolds/codex/skills/dev-loop/SKILL.md`
- `ai-process/processes/workflow-overview.md`
- `ai-process/processes/quality-gates.md`
- `guides/setup-guide.md`

## Fix Verification

```bash
cd cli
python scripts/sync_init_scaffolds.py
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_init_scaffolds.py
UV_CACHE_DIR=/tmp/uv-cache uv run ruff format --check .
UV_CACHE_DIR=/tmp/uv-cache uv run ruff check .

rg -n "ONLY from the root `CLAUDE.md`|exactly one fenced command block|BLOCKED: root CLAUDE.md" \
  src/ai_team/init/sources/skills/dev-loop/body.md \
  src/ai_team/init/scaffolds/claude/skills/dev-loop/SKILL.md \
  src/ai_team/init/scaffolds/codex/skills/dev-loop/SKILL.md
```

The final `rg` command should either return no matches or only historical
context that no longer controls dev-loop startup behavior. Add or update tests
so the skill source and both generated scaffold copies require flexible project
test discovery and user clarification when test instructions are missing.

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
Reproduction status: Confirmed by inspecting the source-of-truth dev-loop skill and generated scaffold copies before changing production files.
Evidence captured: `cli/src/ai_team/init/sources/skills/dev-loop/body.md` says to discover and run the baseline test command "ONLY from the root `CLAUDE.md` `## Test` section", forbids fallback to project docs, README, or build configs, and reports missing or ambiguous cases with `BLOCKED: root CLAUDE.md ...` messages. The same text is present in `cli/src/ai_team/init/scaffolds/claude/skills/dev-loop/SKILL.md` and `cli/src/ai_team/init/scaffolds/codex/skills/dev-loop/SKILL.md`. Current scaffold tests assert the rigid behavior through phrases such as `ONLY from the root `CLAUDE.md``, exact fenced-code-block conditions, and `BLOCKED: root CLAUDE.md`.
Isolated fault: The dev-loop skill's Step 2 baseline guard is written as a single-file root `CLAUDE.md` parser with no fallback to other clear project guidance and no user clarification path when no automated baseline command is documented.
Root cause or fault hypothesis: Task T-051 encoded deterministic command discovery as an exact root-CLAUDE contract, but the broader workflow intent is to confirm a green baseline using project-specific guidance and to ask the human when no clear command exists.
Planned verification: Update the source dev-loop skill and generated scaffold copies to require flexible project test discovery, user clarification for missing or unavailable automated tests, and preservation of the startup baseline guard. Update scaffold tests so they reject the old rigid phrases and require the new behavior. Regenerate scaffolds with the sync script, then run `tests/test_init_scaffolds.py`, ruff format/check, and an `rg` verification showing the old rigid control phrases are absent.

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-06-03
Implemented the dev-loop baseline discovery fix on `bug/B-007-dev-loop-baseline-test-discovery-is-too-rigid`. Replaced the root-`CLAUDE.md`-only startup guard in the source dev-loop skill with flexible project guidance discovery: root guidance files, referenced project docs, common project documentation/configuration, then the smallest explicitly documented automated baseline command. The new behavior asks the human for the intended command when no automated baseline command is documented or when multiple plausible commands are present, and it can continue only after explicit confirmation that no automated baseline test exists.

Updated generated Claude and Codex scaffold copies with `UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/sync_init_scaffolds.py`. Updated `cli/tests/test_init_scaffolds.py` to require the flexible discovery order, missing/ambiguous clarification messages, explicit no-automated-test confirmation handling, and absence of the old rigid control phrases. Because this changes framework behavior, also updated `ai-process/processes/workflow-overview.md`, `ai-process/processes/quality-gates.md`, and `guides/setup-guide.md` so the owning process/setup docs match the new baseline guard contract.

Verification passed with `UV_CACHE_DIR=/tmp/uv-cache uv run --group dev python -m pytest tests/test_init_scaffolds.py` (24 passed), `UV_CACHE_DIR=/tmp/uv-cache uv run --group dev python -m ruff format --check .`, and `UV_CACHE_DIR=/tmp/uv-cache uv run --group dev python -m ruff check .`. The required `rg -n 'ONLY from the root `CLAUDE.md`|exactly one fenced command block|BLOCKED: root CLAUDE.md' ...` check against the three dev-loop skill files returned no matches; exit code 1 was expected for no matches. No implementation work remains for B-007.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that diagnosis, fix, verification, and code quality passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-06-03
PASS

Diagnosis records the reproduced source/scaffold text, isolated root-only baseline guard, and root cause. The fix addresses the isolated cause by replacing the rigid root-`CLAUDE.md` parser contract with flexible project-guidance discovery, human clarification for missing or ambiguous baseline commands, and explicit no-automated-test confirmation handling. The generated Claude/Codex scaffolds match the source, the owning process/setup docs were updated for the framework contract change, and regression tests assert both the new behavior and absence of the old control phrases. Verification passed with focused scaffold tests, ruff format/check, ruff lint, and the required no-match `rg` check.
