---
id: B-002
title: code-review skill reviewer mis-scopes git — stages implementation files
  into the verdict commit and reviews working-tree contents instead of the branch diff
severity: high
status: open
---

# code-review skill reviewer mis-scopes git — stages implementation files into the verdict commit and reviews working-tree contents instead of the branch diff

## Summary

The `code-review` skill (and the `reviewer` agent that runs it) has two related
git-scoping defects, both observed during a single `/dev-loop` run.

First, when committing its verdict to the canonical task file on `dev-agent`,
the Reviewer ran a broad `git add` and swept implementation files that had been
checked out for inspection into the lifecycle commit. The verdict commit must
contain only the canonical task file.

Second, the Reviewer evaluated the full current *contents* of changed files
rather than the branch *diff* (`git diff <dest>...<branch>`). It misattributed
pre-existing repository content as additions made by the branch and returned a
factually incorrect `FAIL` verdict.

Both stem from the same root gap: the `code-review` skill does not pin the
Reviewer's git scope — neither what to review (the merge-base diff) nor what to
stage (only the task file).

## Reproduction Status

Status: confirmed

Both behaviours were observed directly during the `/dev-loop` run for the
`ai-team-cli-documentation` spec on `2026-05-14`: the staging defect on T-027,
the review-scope defect on T-031. The review-scope defect was only worked around
after an explicit, manually-scoped re-review instruction was given to the
Reviewer subagent.

## Evidence

- Logs / stack traces / failing assertions:
  - T-027: the Reviewer's `docs(tasks): record T-027 review verdict` commit
    contained `cli/docs/commands.md`, `cli/scripts/gen_docs.sh`, and
    `cli/tests/test_gen_docs.py` in addition to the task file. The orchestrator
    had to rewrite the (non-pushed) commit to contain only the task file before
    integration, because the contaminated state would have made the `integrate`
    "expected changes" check misfire.
  - T-031: the Reviewer's first verdict was `FAIL`, citing "three new README
    subsections (~50 lines)" and "CLAUDE.md modified out of scope." The actual
    `git diff dev-agent...task/T-031-link-docs-and-add-regeneration-rule` was
    4 inserted lines across `README.md` and `guides/setup-guide.md` — all in
    scope. The cited content was pre-existing on `dev-agent` (the merge base).
- Screenshots or recordings: n/a
- Failing command or test: n/a (process defect, not a failing test)
- First diagnostic step if not yet reproduced: n/a (reproduced)

## Reproduction Steps

1. Run `/dev-loop`. When a task reaches the review cycle, spawn the Reviewer per
   the `code-review` skill.
2. Observe (staging defect): if the Reviewer checks out implementation files from
   the task branch to inspect them, its verdict commit on `dev-agent` includes
   those files, not just the canonical task file.
3. Observe (review-scope defect): on a branch whose merge base already contains
   substantial content in the files it touches, the Reviewer evaluates the full
   file contents and attributes pre-existing lines to the branch, producing an
   inaccurate verdict.

## Expected Behavior

- The `code-review` skill must instruct the Reviewer to review strictly against
  the branch diff `git diff <destination>...<branch>` (the merge base), not
  working-tree file contents.
- The `code-review` skill must instruct the Reviewer to stage exactly the
  canonical task or bug lifecycle file when committing its verdict — never a
  broad `git add -A` / `git add .`.

## Actual Behavior

- The Reviewer's verdict commit can include implementation files checked out for
  inspection (T-027).
- The Reviewer can review full file contents instead of the branch diff,
  misattributing pre-existing content and returning a factually wrong verdict
  (T-031).

## Environment

- OS / platform: Linux (6.12.86, Debian 13)
- Language / runtime version: n/a (process/skill defect)
- Relevant dependencies: `.claude/skills/code-review/SKILL.md`,
  `.claude/agents/reviewer.md`, `/dev-loop`, `integrate`
- Branch / commit: `dev-agent` (observed during the `ai-team-cli-documentation`
  dev-loop run)

## Related

- Task: surfaced during T-027 and T-031 of the `ai-team-cli-documentation` spec
- Specification: `project/specs/ai-team-cli-documentation.md`
- See also: `ai-process-cli-reported-issues.md` in the repo root (entries I-001
  and I-002)

## Suspected Area

`.claude/skills/code-review/SKILL.md` — missing explicit git-scope instructions
for both the review target (merge-base diff) and the verdict commit (stage only
the lifecycle file). The `.claude/agents/reviewer.md` agent definition may also
need a `Quality Bar` or `Folder Scope` note reinforcing this.

## Fix Verification

```bash
# 1. The code-review skill pins the review target to the merge-base diff.
grep -nE "git diff .*\.\.\.|merge base|branch diff" .claude/skills/code-review/SKILL.md

# 2. The code-review skill pins verdict-commit staging to the lifecycle file only.
grep -niE "stage only|only the (canonical )?(task|bug)|do not .*git add" .claude/skills/code-review/SKILL.md
```

A subsequent `/dev-loop` review cycle should produce a verdict commit containing
exactly one changed file, and a verdict whose findings trace only to lines
present in `git diff <destination>...<branch>`.

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
