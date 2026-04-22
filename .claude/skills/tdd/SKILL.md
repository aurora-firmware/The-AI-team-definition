---
name: tdd
description: Test-driven implementation cycle for tasks and diagnosed bug fixes. Use after task assignment, or after a bug has a Diagnosis Log, to write a failing test, verify failure, implement the minimal change, verify pass, and refactor.
allowed-tools: Read, Grep, Glob, Write, Edit, Bash
---

# Test-Driven Development (TDD)

## Input Requirements

- **Task or bug file** — with acceptance criteria or fix-verification steps.
- **Project test setup** — test framework, directory structure, how to run tests.
- **Coding standards** — `ai-process/guidelines/coding-standards.md` for framework standards, plus target-project guidance such as the project `CLAUDE.md`, `project/docs/coding_guidelines.md`, README, build configuration, and human-provided instructions.

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

### Step 6: Refactor
Clean up the code without changing behavior.
Run all tests again to confirm nothing broke.

### Step 7: Repeat
Go back to Step 2 for the next acceptance criterion.
Continue until all criteria have tests and passing implementations.

### Step 8: Prepare a Work Log Handoff
After refactor and before handing back to the orchestrator, prepare a dated Work Log entry using the heading `### Session N — YYYY-MM-DD`.
Use a free-prose body that summarizes what was done, what was tried and rejected, and what remains.
The session number increments monotonically across all sessions on the same task or bug.
Return this entry to the active loop. The loop appends and commits it to the canonical task or bug file on `dev-agent`.

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
- The Work Log handoff contains one entry for the current session boundary.

## Common Pitfalls

- **Starting work without reading the Work Log** — always read every existing canonical Work Log entry before the acceptance criteria or any other work.
- **Writing implementation first** — this defeats the purpose of TDD. Always write the test first.
- **Tests that test implementation** — test what the code does (behavior), not how it does it (implementation details). If you refactor internals, tests should still pass.
- **Skipping the "verify it fails" step** — a test that passes before implementation is not testing anything. It gives false confidence.
- **Over-refactoring** — refactor only when the code is messy enough to slow down the next test cycle. Do not refactor preemptively.
- **Giant test functions** — each test should check one thing. If a test has multiple assertions checking different behaviors, split it.
