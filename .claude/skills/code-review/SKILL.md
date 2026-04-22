---
name: code-review
description: Two-stage code review for completed tasks and bug fixes. Use when a Developer submits work and the Reviewer must check task acceptance or bug diagnosis criteria before reviewing code quality.
allowed-tools: Read, Edit, Grep, Glob, Bash(git diff *), Bash(git status *), Bash(git checkout *), Bash(git add *), Bash(git commit *)
effort: high
---

# Code Review

## Input Requirements

- **Task or bug file** — the task definition with acceptance criteria, or the bug report with diagnosis and fix-verification steps.
- **Code changes** — the diff or set of modified files.
- **Test results** — confirmation that all tests pass.
- **Review checklist** — `ai-process/guidelines/review-checklist.md`.

The task or bug file is canonical lifecycle state on `dev-agent`.
Review verdicts are written and committed there, not on the implementation branch.

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
Review the code against the checklist in `ai-process/guidelines/review-checklist.md`:
- **Correctness**: Logic handles expected inputs and edge cases.
- **Tests**: Tests exist, cover success and failure paths, are independent.
- **Security**: No hardcoded secrets, input is validated, queries are parameterized.
- **Readability**: Names are descriptive, functions are focused, no dead code.
- **Performance**: No unnecessary loops, blocking calls, or resource leaks.

For bug fixes, also run the Bug Fix Review Addendum from the checklist.

### Step 4: Produce Verdict
If all checks pass: **PASS**. Record the verdict for the active loop.
If any check fails: **FAIL**. Return to Developer with specific, actionable feedback.
If a fundamental design issue makes the task or bug impossible as specified: **ESCALATE**.

### Step 5: Record the Verdict
Switch to `dev-agent`.
Append to the canonical task or bug file under a `### Review Verdict — [date]` heading.
The first line of the section must be one of: `PASS`, `FAIL`, or `ESCALATE`.
Commit the verdict on `dev-agent` according to `ai-process/guidelines/git-conventions.md`.

**On PASS:** Record the verdict with a brief confirmation that both stages passed. Note any minor observations (non-blocking).

**On FAIL:** Record the verdict and list each failed check with the location, what is wrong, and what should change. The work item stays in `in-progress/`. The Developer fixes the issues and re-submits. Up to two retries per work item (three total review attempts). If the work item fails a third time, escalate to architect.

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
Describe the fundamental design issue and why it cannot be resolved without changing the specification.
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
