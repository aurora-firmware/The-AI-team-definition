---
id: B-016
title: Developer role has no enforced boundary against committing lifecycle 
  files on task branches
severity: medium
status: in-progress
created: '2026-08-05'
---

# Developer role has no enforced boundary against committing lifecycle files on task branches

## Summary

The rule that task and bug files are canonical on `dev-agent` and must not be
edited from an implementation branch exists only as prose spread across the
`tdd`, `debug`, `git-conventions`, and `dev-loop` sources. The Developer agent
definition's own Folder Scope table — the one place that states hard boundaries
for the role — does not list `project/tasks/` or `project/bugs/` under "Never
touch". In practice the prose has been ignored: a Developer committed a Work Log
into the canonical task file and added a `completed/` copy on the task branch.
The only thing that catches this is `integrate` Step 3.4, which is detection
after the fact and hard-stops the integration.

## Reproduction Status

Status: confirmed by source inspection, plus a field incident

The reporting project observed it during `dev-loop` processing of T-115: the
Developer returned a Work Log *and* wrote it to disk and `git add`ed the task
file on the task branch (commit `4540185`). The loop had to reset the source
branch to the source-only commit and re-record the Work Log on `dev-agent`
before review and integration could proceed.

## Evidence

- Logs / stack traces / failing assertions: n/a
- Screenshots or recordings: n/a
- Failing command or test: n/a — the failure mode is a violated boundary that
  surfaces as an `integrate` hard stop, not a test failure.
- Source inspection:
  - `cli/src/ai_team/init/sources/agents/claude/developer.md:54` — the "Never
    touch" row lists only `project/specs/`, `project/decisions/`,
    `project/docs/`. `project/tasks/` and `project/bugs/` are absent, and the
    Write/Edit row grants `project/bugs/open/` via `new-bug`.
  - `cli/src/ai_team/init/sources/skills/tdd/body.md:9-10` and
    `.../skills/debug/body.md:14-15` carry only the prose "return new log content
    as a handoff … instead of editing lifecycle files directly".
  - `cli/src/ai_team/init/sources/skills/dev-loop/body.md:100` passes the single
    line "Do not edit the task lifecycle file on the task branch" in the
    Developer prompt.
  - `cli/src/ai_team/init/sources/skills/git-conventions/body.md:68` lists
    "Merging lifecycle-file edits from an implementation branch" under *Common
    Pitfalls*, not under *Hard Rules*.
  - `git log -S` confirms the tdd/debug and dev-loop guard wording is unchanged
    since commit `483ea74` (2026-05-14) — i.e. no hardening was added in response
    to the incident.
  - The detection that did fire, `cli/src/ai_team/init/sources/skills/integrate/body.md:67`
    (Step 3.4), stops integration rather than preventing the commit.

## Reproduction Steps

1. Run `/dev-loop` and let it reach Step 5, spawning the Developer for a task.
2. Let the Developer complete implementation and produce its Work Log handoff.
3. Inspect the task branch: `git diff dev-agent...task/T-NNN-… -- project/tasks/`.
4. Observe that nothing in the Developer's own definition or tooling prevents a
   lifecycle-file edit and `git add` from appearing there; when it does,
   `integrate` Step 3.4 hard-stops.

## Expected Behavior

The Developer must not be able to commit lifecycle files from an implementation
branch, and the boundary should be stated where the role's other hard boundaries
live. Either:

- (a) the Developer agent definition adds `project/tasks/` and `project/bugs/`
  (except `project/bugs/open/` via the `new-bug` skill) to "Never touch" and
  forbids `git add`/commit under those paths, and `git-conventions` promotes the
  rule from *Common Pitfalls* to *Hard Rules*; and/or
- (b) `dev-loop` and `bug-loop` strip lifecycle-path changes from the source
  branch before handing it to review, so the violation cannot reach `integrate`.

## Actual Behavior

The prohibition exists only as prose in skills the Developer may or may not
consult, and is contradicted in spirit by a Folder Scope table that enumerates
three other protected paths but not this one. The violation is caught only at
integration time, after the loop has already spent a review cycle.

## Environment

- OS / platform: Linux
- Language / runtime version: `ai-team` CLI 0.10.1 (agent and skill sources are
  language-agnostic)
- Relevant dependencies:
  `cli/src/ai_team/init/sources/agents/{claude/developer.md,codex/developer.toml}`,
  `.../skills/{tdd,debug,dev-loop,bug-loop,git-conventions}/body.md`
- Branch / commit: `dev-agent`, inspected 2026-08-05

## Related

- Task: n/a
- Specification: n/a
- External evidence: `/home/daneel/projects/the-intern/ai-process-cli-reported-issues.md`,
  entry dated 2026-06-30
- Prior art: B-002 fixed the equivalent boundary for the Reviewer by making
  `code-review` switch to `dev-agent` before recording a verdict.

## Suspected Area

`cli/src/ai_team/init/sources/agents/claude/developer.md` Folder Scope table and
its Codex counterpart; `git-conventions` Hard Rules; the Developer prompt in
`dev-loop`/`bug-loop`.

## Fix Verification

Documentary, since the fix is a change to role and skill definitions:

- The Developer agent definition names `project/tasks/` and `project/bugs/` as
  out of bounds for Write/Edit and for `git add`/commit, with the `new-bug`
  exception stated explicitly.
- `git-conventions` lists lifecycle-file commits from an implementation branch
  under Hard Rules.
- Both Claude and Codex Developer definitions carry the same boundary.
- Regenerate and confirm exports stay in sync:

```bash
cd cli && python scripts/sync_init_scaffolds.py && uv run pytest
git status --porcelain cli/src/ai_team/init/scaffolds   # must be empty after regeneration
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
