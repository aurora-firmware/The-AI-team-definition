---
name: tdd
description: Test-driven implementation cycle for tasks and diagnosed bug fixes. Use after task assignment, or after a bug has a Diagnosis Log, to write a failing test, verify failure, implement the minimal change, verify pass, and refactor.
allowed-tools: Read, Grep, Glob, Write, Edit, Bash, Skill(git-conventions)
---

# Test-Driven Development (TDD)

## Input Requirements

- **Task or bug file** — with acceptance criteria or fix-verification steps.
- **Project test setup** — test framework, directory structure, how to run tests.
- **Target-project coding guidance** — the project `CLAUDE.md`, `project/docs/coding_guidelines.md`, README, build configuration, and any human-provided instructions (the framework-level coding standards are carried by the invoking role's definition).

Task and bug files are canonical lifecycle state on `dev-agent`.
Read their existing Work Log and Diagnosis Log entries, but return new log content as a handoff to the active loop instead of editing lifecycle files directly.

## Procedure

### Step 0: Read the Work Log
Before reading the acceptance criteria or starting any other work, read every existing entry in the task or bug Work Log.
This step is mandatory even on the first session, when the Work Log is empty and the read is a cheap no-op.
For bug fixes, also read the Diagnosis Log.
If no Diagnosis Log exists, stop and run the debug procedure before writing tests or implementation.

### Step 1: Read the Acceptance Criteria or Fix Verification
For each task criterion or bug fix-verification step, identify the testable behavior.
Translate each criterion into one or more test cases with:
- Input (what goes in)
- Expected output (what comes out)
- Edge cases (boundaries, empty inputs, error conditions)

For a bug fix, the first test should reproduce the diagnosed defect when practical.

### Step 2: Write the Test
Write a failing test for the first acceptance criterion.
The test must be:
- Descriptive: `test_returns_error_when_input_is_empty`.
- Independent: no shared mutable state with other tests.
- Deterministic: same result every time.

### Step 3: Verify the Test Fails
Run the test. It must fail.
If it passes, either the test is wrong (testing nothing meaningful) or the behavior already exists.
Fix the test or skip to the next criterion.

### Step 4: Write the Minimal Implementation
Write the simplest code that makes the test pass.
Do not add extra logic, error handling, or features beyond what the test requires.

### Step 5: Verify the Test Passes
Run the test. It must pass.
If it fails, fix the implementation (not the test, unless the test was wrong).
If Step 4 → Step 5 fails three consecutive times on the same acceptance criterion, stop and apply the Escalation section below.

### Step 6: Refactor
Clean up the code without changing behavior.
Run all tests again to confirm nothing broke.

### Step 7: Commit the Cycle
Commit the completed red -> green -> refactor cycle on the assigned implementation branch using the `git-conventions` skill.
Keep implementation commits on `task/T-NNN-...` or `bug/B-NNN-...` only, and use a message that follows `<type>(<component>): <description>` without repeating the task or bug ID from the branch name.

### Step 8: Repeat
Go back to Step 2 for the next acceptance criterion.
Continue until all criteria have tests and passing implementations.

### Step 9: Prepare a Work Log Handoff
After refactor and before handing back to the orchestrator, prepare a dated Work Log entry using the heading `### Session N — YYYY-MM-DD`.
Use a free-prose body that summarizes what was done, what was tried and rejected, and what remains.
The session number increments monotonically across all sessions on the same task or bug.
Return this entry to the active loop. The loop appends and commits it to the canonical task or bug file on `dev-agent`.

## Escalation

Return `ESCALATE` under any of these conditions. All cases use the same structured four-field request; the active loop forwards it to the Architect via the `escalation-review` skill. Do not resume the TDD cycle until the Architect responds.

**Retry threshold.** Three consecutive Step 4 → Step 5 failures on the same acceptance criterion.

**Boundary violations (no retry — escalate on first detection):**
- The task can only be completed by modifying a file that is not listed under `Files to Touch` in the task file.
- Implementation reveals a dependency on another task that is not listed under `Dependencies`.
- The acceptance criteria cannot be satisfied without changing the approved specification.
- Requirements in the task are internally contradictory.

```text
Problem: [the criterion that will not pass, or the boundary that was violated]
Attempted: [implementations tried on retry, or why the boundary cannot be honoured as written]
Failed because: [the specific reason — test output, scope mismatch, contradictory requirement]
Question: [specific guidance needed to continue within the approved specification]
```

## Output Format

- **Test files** — one or more test files covering all acceptance criteria.
- **Implementation files** — production code that passes all tests.
- **Verification** — the task's verification command runs successfully.
- **Work Log handoff** — the complete `### Session N — YYYY-MM-DD` entry for the active loop to record.

## Quality Criteria

- Every acceptance criterion has at least one test.
- Tests cover both success and failure paths.
- Tests are independent (no shared mutable state) and deterministic (same result every run, no flakiness).
- Test names describe the expected behavior, not the implementation (e.g., `test_returns_empty_list_when_no_items` not `test_get_items`).
- The implementation is minimal — no code exists that is not required by a test.
- All tests pass when run together.
- Each completed TDD cycle is committed on the assigned implementation branch using the `git-conventions` skill.
- The Work Log handoff contains one entry for the current session boundary.

## Common Pitfalls

- **Starting work without reading the Work Log** — always read every existing canonical Work Log entry before the acceptance criteria or any other work.
- **Writing implementation first** — this defeats the purpose of TDD. Always write the test first.
- **Tests that test implementation** — test what the code does (behavior), not how it does it (implementation details). If you refactor internals, tests should still pass.
- **Skipping the "verify it fails" step** — a test that passes before implementation is not testing anything. It gives false confidence.
- **Committing outside the branch model** — implementation commits belong only on the assigned task or bug branch, never on `dev-agent`.
- **Over-refactoring** — refactor only when the code is messy enough to slow down the next test cycle. Do not refactor preemptively.
- **Giant test functions** — each test should check one thing. If a test has multiple assertions checking different behaviors, split it.
