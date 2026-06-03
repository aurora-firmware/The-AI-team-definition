---
id: B-007
title: Dev-loop baseline test discovery is too rigid
severity: medium
status: open
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

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that diagnosis, fix, verification, and code quality passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
