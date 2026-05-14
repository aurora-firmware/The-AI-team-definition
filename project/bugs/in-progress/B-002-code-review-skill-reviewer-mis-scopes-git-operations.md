---
id: B-002
title: code-review skill reviewer mis-scopes git — stages implementation files
  into the verdict commit and reviews working-tree contents instead of the branch diff
severity: high
status: in-progress
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

### Diagnosis 1 — 2026-05-14

**Reproduction status:** Confirmed. Both behaviours were directly observed during
the `/dev-loop` run for the `ai-team-cli-documentation` spec on 2026-05-14 and are
documented in the bug file with concrete commit and task evidence (T-027 staging
contamination; T-031 wrong-scope verdict).

**Evidence captured:**

Defect 1 — Review scope (what the Reviewer reviews):
`.claude/skills/code-review/SKILL.md` lines 21–33 (Step 2) and lines 41–50 (Step 3)
describe checking "each acceptance criterion against the code" but nowhere instruct
the Reviewer to obtain the branch diff via `git diff <destination>...<branch>`. The
only diff-related text is the `allowed-tools` frontmatter (line 4: `Bash(git diff *)`),
which permits the tool but does not instruct its use. With no constraint on what
"the code" means, a Reviewer naturally reads full working-tree file contents.
`.claude/agents/reviewer.md` — zero matches for `git diff`, merge base, branch diff,
or working-tree scope anywhere in the file.

Defect 2 — Verdict commit staging (what the Reviewer stages):
`.claude/skills/code-review/SKILL.md` Step 5 (lines 59–67) says "append … and commit"
the verdict but never says "stage only the canonical task/bug lifecycle file" or
"do not run `git add -A` / `git add .`". The `allowed-tools` line permits
`Bash(git add *)` without restriction. `.claude/agents/reviewer.md` Folder Scope
table (lines 44–48) lists implementation code as `Never touch` for *editing* but
does not prohibit *staging* implementation files into a commit — a Reviewer that
only read those files via checkout violates the intent without violating the
`Never touch` rule as written.

**Isolated fault:** Two discrete omissions in `.claude/skills/code-review/SKILL.md`:
(1) Step 2 has no instruction to run `git diff <destination>...<branch>` and limit
review scope to that output; (2) Step 5 has no instruction to stage only the
canonical lifecycle file. A reinforcing note is also absent from
`.claude/agents/reviewer.md`.

**Root cause or fault hypothesis:** The `code-review` skill was written at a higher
level of abstraction than is safe for git operations. It delegates "check the code"
and "commit the verdict" to the Reviewer's judgment without pinning the exact git
commands needed to guarantee correct scope. Because the skill is the procedure layer
that must embed these specifics and it omits them, a model executing the skill
defaults to the most straightforward interpretation: read the working tree in full,
then do a broad `git add`. Both defects are specification gaps in the skill, not
model misbehaviour.

**Planned verification:** After the fix, run the Fix Verification commands from this
bug file — both greps (`git diff ...` / merge-base instruction; `stage only` /
`do not git add` instruction) must return at least one match. A subsequent dev-loop
review cycle should produce a verdict commit containing exactly one changed file and
a verdict whose findings trace only to lines in `git diff <destination>...<branch>`.

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-05-14

Read the Diagnosis Log in the bug file and both target files before making any
changes. The diagnosis identified three gaps precisely: Step 2 in the skill had no
instruction to obtain the merge-base diff before checking criteria; Step 5 had no
instruction to stage only the lifecycle file; and the reviewer agent had no
reinforcing observable criteria for either constraint.

The fix was applied in three minimal edits:

1. In `code-review/SKILL.md` Step 2: inserted a block before the criteria checklist
   instructing the Reviewer to run `git diff <destination>...<branch>` and scope all
   findings strictly to that diff, explicitly forbidding attribution of pre-existing
   lines. Placeholder variable names `<destination>` and `<branch>` were used per the
   framework policy against hardcoding branch names.
2. In `code-review/SKILL.md` Step 5: added one sentence instructing the Reviewer to
   stage only the canonical task or bug lifecycle file for the verdict commit and not
   to use `git add -A` / `git add .`, which can sweep in implementation files checked
   out for inspection.
3. In `reviewer.md`: added two bullets to the `### For Reviews` Quality Bar list (one
   for merge-base diff scoping, one for lifecycle-file-only staging) and a parenthetical
   "(for inspection only — never stage implementation files)" to the Read row of the
   Folder Scope table. Both are observable-criteria language, not procedure steps,
   consistent with the agent-vs-skill separation in CLAUDE.md.

The only course correction was a wording tweak in edit 2 ("Stage exactly … never use"
→ "Stage only … do not use") so it matches the Fix Verification grep pattern. Both
verification greps now return matches (`SKILL.md` lines 28/31/38 and line 73). No
automated test exists for a process/spec defect of this kind; verification was
grep-based plus manual review of each full file to confirm structural correctness.
Nothing remains. Fix committed as `38148d0` on
`bug/B-002-code-review-skill-reviewer-mis-scopes-git-operations`.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that diagnosis, fix, verification, and code quality passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
