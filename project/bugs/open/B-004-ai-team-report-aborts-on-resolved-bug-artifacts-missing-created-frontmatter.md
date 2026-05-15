---
id: B-004
title: ai-team report aborts on resolved bug artifacts missing 'created' frontmatter
severity: medium
status: open
created: '2026-05-15'
---

# ai-team report aborts on resolved bug artifacts missing 'created' frontmatter

## Summary

`ai-team report` fails before writing any output when a resolved bug artifact does
not have a `created` field in its frontmatter. Because `parse_bug()` treats
`created` as required, a single legacy resolved artifact prevents every report
generation. Gate 5 full reporting is blocked even when the project is otherwise
clean. Originally reported as I-008 in `ai-process-cli-reported-issues.md`.

## Reproduction Status

Status: confirmed

Both the installed CLI and the repo-local CLI fail identically on the current
`dev-agent` state when at least one resolved bug under `project/bugs/resolved/`
lacks `created`. Observed 2026-05-15 during `/status-report`.

## Evidence

- Logs / stack traces / failing assertions:
  ```text
  FrontmatterError: Required frontmatter field 'created' is missing or null in
  project/bugs/resolved/B-001-ai-team-spec-new-cli-does-not-match-new-spec-skill-contract-and-leaves-body-title-placeholder.md
  ```
- Screenshots or recordings: n/a.
- Failing command or test: `uv --directory cli run ai-team report` (or the
  installed `ai-team report`) on a checkout where the named resolved bug exists.
- First diagnostic step if not yet reproduced: confirm the resolved artifact's
  frontmatter has only `id`, `title`, `severity`, and `status` (no `created`),
  then re-run `ai-team report`.

## Reproduction Steps

1. Check out a copy of the repo on `dev-agent`.
2. Confirm `project/bugs/resolved/B-001-...md` (or any resolved bug missing
   `created`) is present.
3. Run `uv --directory cli run ai-team report`.
4. Observe the command aborts with `FrontmatterError: Required frontmatter field
   'created' is missing or null in project/bugs/resolved/B-001-...md` before
   writing any output.

## Expected Behavior

`ai-team report` should be robust across pre-existing lifecycle artifacts. Any of
the following is acceptable:

- Validate all artifacts up front and emit a single actionable error that lists
  every malformed file, rather than aborting on the first one.
- Migrate / backfill legacy bug frontmatter so the required field is populated
  consistently.
- Render resolved bug rows with an unknown/missing `created` value when the field
  is not needed by the report table.

## Actual Behavior

The command halts on the first resolved bug without a `created` field, raising a
`FrontmatterError`, and never produces a report. The status-report skill had to
fall back to writing a manual report file at
`project/docs/reports/progress-report-2026-05-15.md` on 2026-05-15.

## Environment

- OS / platform: Linux (Debian 13).
- Language / runtime version: Python 3.14 (as configured in `cli/pyproject.toml`).
- Relevant dependencies: ai-team CLI as built from this repository; installed CLI
  shows the same failure.
- Branch / commit: observed on `dev-agent` after T-041 integration.

## Related

- Task: not applicable
- Specification: not applicable
- Prior bug: B-001 (the resolved artifact whose frontmatter shape triggers the
  failure).
- Prior issue note: I-008 in `ai-process-cli-reported-issues.md`.
- Affected workflow: Gate 5 (`/status-report`) — blocked from generating a full
  progress report through the CLI.

## Suspected Area

`cli/src/ai_team/commands/report.py` — bug listing path that calls `parse_bug()`
(in the frontmatter/parsing layer) on every artifact under `project/bugs/resolved/`.
`parse_bug()` requires `created`. The hardening should likely live either in
`report.py` (treat `created` as optional for resolved-bug rows) or in the bug
parser / migration helper used at report time.

## Fix Verification

```bash
# 1. Repro on current `dev-agent` (B-001 lacks `created`):
cd /home/daneel/projects/The-AI-team-definition
uv --directory cli run ai-team report
# expected before fix: FrontmatterError on B-001-...md and no report file written.

# 2. After fix:
uv --directory cli run ai-team report
# expected: command exits 0 and writes
#           project/docs/reports/progress-report-<date>.md, with B-001 listed in
#           the resolved-bugs section (created date shown as unknown / migrated /
#           backfilled, per the fix approach).

# 3. Regression test in cli/tests/ covering a resolved bug artifact whose
#    frontmatter has only id, title, severity, status (no `created`), asserting
#    `ai-team report` completes successfully.
uv --directory cli run pytest tests/test_report.py
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
