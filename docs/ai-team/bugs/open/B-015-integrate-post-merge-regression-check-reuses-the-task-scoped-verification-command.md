---
id: B-015
title: integrate post-merge regression check reuses the task-scoped verification
  command
severity: medium
status: open
created: '2026-08-05'
---

# integrate post-merge regression check reuses the task-scoped verification command

## Summary

The `integrate` skill derives one verification command set from the work item's
`## Verification` / `## Fix Verification` section and uses it for both the
pre-merge run on the source branch and the post-merge regression check on the
destination branch. A task whose contract change affects code outside its own
declared verification scope can therefore merge a regression that the post-merge
check is structurally incapable of seeing, leaving the destination branch red
until the next loop iteration trips over its baseline guard.

## Reproduction Status

Status: confirmed by source inspection, plus a field incident

The reporting project hit this with T-101: its `## Verification` was
`cargo test -p pi-agent-supervisor && cargo test -p bob`, while the change broke
five `admin-rpc` dispatch tests. The project's real CI gate is
`cargo test --workspace`. Integration passed both Step 4 and Step 6 and left
`dev-agent` red; the breakage surfaced later as B-013 in that project.

## Evidence

- Logs / stack traces / failing assertions: n/a (the defect is that no failure is
  produced when one should be)
- Screenshots or recordings: n/a
- Failing command or test: the post-merge check in `integrate` Step 6 passes
  while the project's documented baseline suite fails on the destination branch.
- Source inspection (`cli/src/ai_team/init/sources/skills/integrate/body.md`):
  - Step 2, item 7 (line 40) sets the lookup order with the work item's
    `## Verification` section first, project guidance (`CLAUDE.md`, coding
    guidelines, README, build config) only as a fallback.
  - Step 2, item 8 (line 44) states the discovered set is used "for both pre-merge
    and post-merge verification unless the work item or project guidance
    explicitly defines separate source-branch and destination-branch checks" — so
    the default behaviour is a task-scoped post-merge check.
  - Step 6 (line 108) runs "the discovered destination-branch verification
    command set", which in the default case is the same task-scoped command.
- Related gap: `cli/src/ai_team/init/sources/skills/spec-breakdown/body.md:39`
  asks only for "a shell command that proves the task is done" — nothing directs
  the Planner to widen `## Verification` when a task alters a shared or
  cross-module contract.

## Reproduction Steps

1. Create a task whose `## Verification` section names a narrow, module-scoped
   test command.
2. Implement a change on the task branch that alters a shared or public interface
   consumed by a module outside that scope, breaking its tests.
3. Run `integrate` for the task branch.
4. Observe Step 4 (pre-merge) and Step 6 (post-merge) both pass, the merge lands,
   and the project-wide baseline suite is red on the destination branch.

## Expected Behavior

The post-merge regression check must be able to detect regressions outside the
work item's declared verification scope. Concretely, Step 6 should run the
documented project baseline (for example the workspace/full test suite named in
the project's `CLAUDE.md`) in addition to — or in preference to — the
task-scoped command, at minimum whenever the diff touches a shared or public
interface. The Planner-facing guidance should also require `## Verification` to
include the project baseline when a task changes a cross-module contract.

## Actual Behavior

Step 6 re-runs the same narrow command Step 4 ran. Cross-module regressions are
outside the checked scope, so integration reports success and the destination
branch is left broken.

## Environment

- OS / platform: Linux
- Language / runtime version: `ai-team` CLI 0.10.1 (skill sources are
  language-agnostic)
- Relevant dependencies:
  `cli/src/ai_team/init/sources/skills/integrate/body.md`,
  `cli/src/ai_team/init/sources/skills/spec-breakdown/body.md`
- Branch / commit: `dev-agent`, inspected 2026-08-05

## Related

- Task: n/a
- Specification: n/a
- External evidence: `/home/daneel/projects/the-intern/ai-process-cli-reported-issues.md`,
  entry dated 2026-06-23

## Suspected Area

`cli/src/ai_team/init/sources/skills/integrate/body.md` — Step 2 items 7 and 8,
and Step 6. Secondary: the task-authoring guidance in
`cli/src/ai_team/init/sources/skills/spec-breakdown/body.md` and the
`## Verification` guidance in `cli/src/ai_team/templates/task.md`.

## Fix Verification

Documentary, since the fix is a change to skill procedure rather than CLI code:

- `integrate` Step 6 states that the destination-branch check runs the documented
  project baseline, and defines what to do when no baseline is discoverable.
- The Step 2 lookup order distinguishes the source-branch command from the
  destination-branch command rather than defaulting both to the work item's
  section.
- Task-authoring guidance requires `## Verification` to cover the project
  baseline when the change alters a shared or public interface.
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
