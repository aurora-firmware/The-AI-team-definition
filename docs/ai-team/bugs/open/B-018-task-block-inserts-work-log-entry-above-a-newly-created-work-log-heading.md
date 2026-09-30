---
id: B-018
title: task block inserts Work Log entry above a newly created Work Log heading
severity: low
status: open
created: '2026-09-30'
---

# task block inserts Work Log entry above a newly created Work Log heading

## Summary

In `_append_work_log_entry` (`cli/src/ai_team/commands/task.py`, around lines 77-78), when a task file has no `## Work Log` heading, `start = len(lines) - 3` lands on the blank line before the newly appended heading. The `## ` scan then stops immediately, so the `### Session 1` entry is inserted above `## Work Log`. Found during T-090 (lifecycle parity fixtures) and confirmed by the reviewer by reading the code path. Impact: `task block` on such a task produces a malformed file, and the TS port cannot take a parity fixture for this case until it is fixed.

## Reproduction Status

Status: confirmed

Seeded output during T-090 showed `### Session 1` above `## Work Log`; the reviewer confirmed the index error by reading the code.

## Evidence

- Logs / stack traces / failing assertions:
- Screenshots or recordings:
- Failing command or test: `task block` on a task file lacking a `## Work Log` heading (no test yet)
- First diagnostic step if not yet reproduced:

## Reproduction Steps

1. Create a task file with no `## Work Log` heading.
2. Run `ai-team task block <id> --reason X` (or call `block_task` on it).
3. Inspect the file: the `### Session 1` entry is above `## Work Log`.

## Expected Behavior

A `## Work Log` heading is created and the `### Session 1` entry is placed beneath it.

## Actual Behavior

The entry appears above the `## Work Log` heading. No error is raised.

## Environment

- Branch / commit: `feat/pi-extension` at the merge of T-090

## Related

- Task: `T-090`

## Suspected Area

`cli/src/ai_team/commands/task.py`, `_append_work_log_entry`.

## Fix Verification

```bash
# Add a unit test plus the parity fixture task-block--creates-missing-work-log
# (deferred by T-090 until this is fixed), then:
cd cli && uv run pytest
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
