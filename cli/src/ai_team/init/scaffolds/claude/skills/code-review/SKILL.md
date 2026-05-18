---
name: code-review
description: Two-stage code review for completed tasks and bug fixes. Use when a Developer submits work and the Reviewer must check task acceptance or bug diagnosis criteria before reviewing code quality.
allowed-tools: Read, Edit, Grep, Glob, Bash(git diff *), Bash(git status *), Bash(git checkout *), Bash(git add *), Bash(git commit *), Skill(git-conventions)
effort: high
---

# Code Review

## Input Requirements

- **Task or bug file** — the task definition with acceptance criteria, or the bug report with diagnosis and fix-verification steps.
- **Code changes** — the diff or set of modified files.
- **Test results** — confirmation that all tests pass.

The task or bug file is canonical lifecycle state on `dev-agent`.
Review verdicts are written and committed there, not on the implementation branch.
The two-stage checklist applied below is the Reviewer role's quality bar, carried by the invoking Reviewer agent.

## Procedure

### Step 1: Read the Work Item
Switch to `dev-agent` and read the canonical task or bug file completely.
For tasks, understand what was asked, what the acceptance criteria are, and which files should have been modified.
For bugs, understand the symptom, reproduction status, diagnostic evidence, isolated fault, root cause or fault hypothesis, and Fix Verification steps.

### Step 2: Stage 1 — Acceptance Or Bug Criteria
For tasks, check each acceptance criterion against the code:
- Is the criterion met? (yes/no, with evidence)
- Was any unspecified behavior or functionality added?
- Were unexpected files modified?

For bug fixes, check:
- Does the Diagnosis Log include reproduction status and evidence?
- Does the fix address the isolated fault or documented root cause?
- Were the Fix Verification steps followed?
- Was unrelated behavior added?

If any task criterion or bug-fix criterion is not met, skip Stage 2 and set the verdict to **FAIL** with specific feedback.

### Step 3: Stage 2 — Code Quality
Apply the Stage 2 checklist from the Reviewer role's quality bar:
- **Correctness**: Logic handles expected inputs and edge cases.
- **Tests**: Tests exist, cover success and failure paths, are independent.
- **Security**: No hardcoded secrets, input is validated, queries are parameterized.
- **Readability**: Names are descriptive, functions are focused, no dead code.
- **Performance**: No unnecessary loops, blocking calls, or resource leaks.

For bug fixes, also run the Bug Fix Addendum from the Reviewer's quality bar.

### Step 4: Produce Verdict

The Reviewer's self-recovery threshold is **one review cycle** for ESCALATE-worthy issues. For ordinary quality issues, issue FAIL (the active loop allows up to three FAIL cycles per work item before it forces escalation on its own).

- If all checks pass → **PASS**. Record the verdict for the active loop.
- If an ordinary quality check fails (bug in logic, missing test, unclear name, etc.) → **FAIL** with specific, actionable feedback. The Developer fixes and re-submits.
- If the code has a fundamental design issue that no amount of Developer fixes can address within the approved specification → **ESCALATE** immediately. Do not issue FAIL first and wait. ESCALATE-worthy examples: the spec is internally contradictory, the acceptance criteria cannot be met without a spec change, the diagnosis points at a root cause outside the bug's stated scope.

### Step 5: Record the Verdict
Switch to `dev-agent`.
Append to the canonical task or bug file under a `### Review Verdict — [date]` heading.
The first line of the section must be one of: `PASS`, `FAIL`, or `ESCALATE`.
Commit the verdict on `dev-agent` using the `git-conventions` skill (commit type `docs` with scope `tasks` or `bugs`, e.g. `docs(tasks): record T-NNN review verdict`).

**On PASS:** Record the verdict with a brief confirmation that both stages passed. Note any minor observations (non-blocking).

**On FAIL:** Record the verdict and list each failed check with the location, what is wrong, and what should change. The work item stays in `in-progress/`. The Developer fixes the issues and re-submits. The active loop tracks the review cycle count. On a third consecutive FAIL, the active loop escalates to the Architect — the Reviewer does not need to change the verdict type.

## Output Format

PASS, FAIL, and ESCALATE append a `### Review Verdict — [date]` section to the canonical task or bug file on `dev-agent`.
The first line of the section is always one of: `PASS`, `FAIL`, or `ESCALATE`.

### On PASS
Verdict: `PASS`
A brief confirmation that both stages passed, noting any minor observations (non-blocking).
Next owner: active Development Loop or Bug-Fix Loop.

### On FAIL
Verdict: `FAIL`
For each failed check:
- **File and location** — which file, which section or line.
- **What is wrong** — specific description of the issue.
- **What should change** — actionable guidance on how to fix it.

### On ESCALATE
Verdict: `ESCALATE`
Record the verdict under `### Review Verdict — [date]` and include a structured escalation request using the standard four-field block:

```text
Problem: [the fundamental design issue observed in the code]
Attempted: [what review cycles and Developer fixes preceded this verdict]
Failed because: [why ordinary Developer fixes cannot resolve it within the approved specification]
Question: [specific decision or guidance needed from the Architect]
```

Next owner: active loop for Architect consultation.

## Quality Criteria

- Every acceptance criterion was explicitly checked (not assumed).
- For bug fixes, diagnostic evidence and Fix Verification were explicitly checked.
- Feedback is specific and actionable — never vague.
- The reviewer checked the actual code, not just the test results.
- No personal style preferences were enforced — only project standards from the coding guidelines.

## Common Pitfalls

- **Rubber-stamping** — approving because tests pass without reading the code. Tests can have gaps.
- **Bikeshedding** — spending review time on naming preferences or formatting instead of correctness and security.
- **Vague feedback** — "this could be better" is not actionable. "This function handles the success case but does not handle the empty-input case described in acceptance criterion 3" is.
- **Scope creep in review** — reviewing code outside the task's scope. Only review what the task changed.
