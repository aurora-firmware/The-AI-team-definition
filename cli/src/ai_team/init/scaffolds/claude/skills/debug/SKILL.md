---
name: debug
description: Diagnostic debugging procedure for bugs and unexpected failures. Use before fixing any bug, when tests fail unexpectedly, when code misbehaves, or when an integration failure has been bisected to a source branch.
allowed-tools: Read, Grep, Glob, Edit, Bash
---

# Debug

## Input Requirements

- **Failing test or error report** — what is failing, including the error message.
- **Code under investigation** — the files involved.
- **Expected behavior** — what should happen (from the task's acceptance criteria).
- **Actual behavior** — what is happening instead.
- **Available evidence** — reproduction steps, logs, stack traces, environment details, branch context, and prior Work Log or Diagnosis Log entries.

Task and bug files are canonical lifecycle state on `dev-agent`.
Read their existing Work Log and Diagnosis Log entries, but return new diagnosis content as a handoff to the active loop instead of editing lifecycle files directly.

## Procedure

### Step 0: Read Existing Context

Read the bug or task file, including every existing Work Log and Diagnosis Log entry.
Identify:
- Observable symptom.
- Expected behavior.
- Actual behavior.
- Reproduction status.
- Known environment and branch context.
- Fix Verification steps.

Do not change production code during this step.

### Step 1: Reproduce or Confirm the Failure

Run the failing test or trigger the error.
Confirm it fails consistently (not flaky).
Record the exact command, error message, stack trace, logs, failing assertion, or other observable evidence.

If the issue is intermittent, run enough attempts to establish a pattern and record the frequency.
If the issue cannot be reproduced, do not guess at a fix.
Record what was tried, what evidence still exists, and the next diagnostic step; then return `ESCALATE` with the structured four-field block below if no evidence-backed fault hypothesis can be formed. The active loop routes the request to the Architect via the `escalation-review` skill.

```text
Problem: [the observed symptom and why reproduction has failed]
Attempted: [reproduction strategies, instrumentation, logs inspected]
Failed because: [what evidence is missing, what assumptions could not be validated]
Question: [specific decision or guidance needed from the Architect]
```

### Step 2: Gather Context and Logs

Collect the smallest useful evidence set:
- Runtime logs or test output.
- Relevant configuration and environment values.
- Input data or fixture details.
- Recent related changes when branch history is relevant.
- A minimal failing command or manual path.

Avoid adding permanent logging or debug prints.
If temporary instrumentation is needed, remove it before completion and mention it in the Work Log.

### Step 3: Isolate the Fault
Narrow down the failing component:
- Which function or method is producing the wrong result?
- What input triggers the failure?
- Does it fail with the simplest possible input?

Strategies:
- **Binary search**: Comment out or bypass sections to narrow the scope.
- **Minimal reproduction**: Create the smallest test case that still fails.
- **Trace the data flow**: Follow the input from entry point to the point of failure.

### Step 4: Identify the Root Cause
Once isolated, determine WHY it fails:
- Logic error (wrong condition, off-by-one, missing case).
- State error (variable has unexpected value due to earlier operation).
- Environment error (missing dependency, wrong configuration).
- Specification error (the spec itself is contradictory or incomplete).

Record the root cause.
If the evidence supports only a fault hypothesis, label it as a hypothesis and explain why it is the best current explanation.

### Step 5: Prepare the Diagnosis Handoff

Prepare a bug file Diagnosis Log entry before implementing the fix.
Include:
- Reproduction status.
- Evidence captured.
- Isolated fault.
- Root cause or fault hypothesis.
- Planned verification.

Return this entry to the active loop. The loop appends and commits it to the canonical bug file on `dev-agent`.
For task debugging, return the same information as part of the task Work Log handoff.
If the caller requested diagnosis only, stop here and do not change production code.

### Step 6: Fix with Minimal Change

Apply the smallest change that fixes the root cause.
Do not refactor surrounding code, add features, or "improve" unrelated areas.
The fix should be obviously correct and narrowly scoped.
When the defect can be tested automatically, add or update a regression test that fails before the fix and passes after it.

### Step 7: Verify the Fix

Run the originally failing test — it must pass.
Run the full test suite — nothing else should have broken.
If something else broke, the fix was too broad or the root cause was misidentified. Return to Step 2.

## Output Format

- **Fix applied** — the specific code change.
- **Root cause** — brief explanation of what was wrong and why.
- **Verification** — confirmation that the fix resolves the issue and all tests pass.
- **Diagnosis Log handoff** — for bug fixes, a dated entry for the active loop to record before the Work Log handoff.

## Quality Criteria

- The root cause is identified and documented, not just the symptom.
- Reproduction status and evidence are recorded before implementation starts.
- The fix is minimal — only the necessary change, nothing more.
- All tests pass after the fix (both the failing test and the full suite).
- No new debugging artifacts remain in the code (print statements, commented-out code).

## Common Pitfalls

- **Fixing symptoms, not causes** — if a function returns the wrong value, do not add a corrective step downstream. Fix the function.
- **Shotgun debugging** — making multiple changes at once and hoping one of them fixes it. Change one thing at a time and test after each change.
- **Skipping reproduction** — do not patch from a vague symptom unless a reproduction is impossible and the evidence still supports a clear fault hypothesis.
- **Leaving debug code** — remove all print statements, logging additions, and temporary code before completing the fix.
- **Broadening scope** — the urge to "clean up while I'm here" leads to larger diffs, more risk, and harder reviews. Stay focused on the bug.
