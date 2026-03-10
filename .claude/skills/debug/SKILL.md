---
name: debug
description: Systematic debugging procedure. Use when a test fails unexpectedly, code misbehaves, or an integration failure has been bisected to a specific task.
allowed-tools: Read, Grep, Glob, Edit, Bash
---

# Debug

## Input Requirements

- **Failing test or error report** — what is failing, including the error message.
- **Code under investigation** — the files involved.
- **Expected behavior** — what should happen (from the task's acceptance criteria).
- **Actual behavior** — what is happening instead.

## Procedure

### Step 1: Reproduce the Failure
Run the failing test or trigger the error.
Confirm it fails consistently (not flaky).
Record the exact error message and stack trace.

### Step 2: Isolate the Cause
Narrow down the failing component:
- Which function or method is producing the wrong result?
- What input triggers the failure?
- Does it fail with the simplest possible input?

Strategies:
- **Binary search**: Comment out or bypass sections to narrow the scope.
- **Minimal reproduction**: Create the smallest test case that still fails.
- **Trace the data flow**: Follow the input from entry point to the point of failure.

### Step 3: Identify the Root Cause
Once isolated, determine WHY it fails:
- Logic error (wrong condition, off-by-one, missing case).
- State error (variable has unexpected value due to earlier operation).
- Environment error (missing dependency, wrong configuration).
- Specification error (the spec itself is contradictory or incomplete).

### Step 4: Fix with Minimal Change
Apply the smallest change that fixes the root cause.
Do not refactor surrounding code, add features, or "improve" unrelated areas.
The fix should be obviously correct and narrowly scoped.

### Step 5: Verify the Fix
Run the originally failing test — it must pass.
Run the full test suite — nothing else should have broken.
If something else broke, the fix was too broad or the root cause was misidentified. Return to Step 2.

## Output Format

- **Fix applied** — the specific code change.
- **Root cause** — brief explanation of what was wrong and why.
- **Verification** — confirmation that the fix resolves the issue and all tests pass.

## Quality Criteria

- The root cause is identified and documented, not just the symptom.
- The fix is minimal — only the necessary change, nothing more.
- All tests pass after the fix (both the failing test and the full suite).
- No new debugging artifacts remain in the code (print statements, commented-out code).

## Common Pitfalls

- **Fixing symptoms, not causes** — if a function returns the wrong value, do not add a corrective step downstream. Fix the function.
- **Shotgun debugging** — making multiple changes at once and hoping one of them fixes it. Change one thing at a time and test after each change.
- **Leaving debug code** — remove all print statements, logging additions, and temporary code before completing the fix.
- **Broadening scope** — the urge to "clean up while I'm here" leads to larger diffs, more risk, and harder reviews. Stay focused on the bug.
