---
name: tdd
description: Test-driven development cycle. Use when writing code for a task — write test first, verify it fails, implement, verify it passes, refactor.
allowed-tools: Read, Grep, Glob, Write, Edit, Bash
---

# Test-Driven Development (TDD)

## Input Requirements

- **Task file** — with acceptance criteria and verification command.
- **Project test setup** — test framework, directory structure, how to run tests.
- **Coding standards** — `docs/guidelines/coding-standards.md` for naming and structure.

## Procedure

### Step 1: Read the Acceptance Criteria
For each criterion, identify the testable behavior.
Translate each criterion into one or more test cases with:
- Input (what goes in)
- Expected output (what comes out)
- Edge cases (boundaries, empty inputs, error conditions)

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

## Output Format

- **Test files** — one or more test files covering all acceptance criteria.
- **Implementation files** — production code that passes all tests.
- **Verification** — the task's verification command runs successfully.

## Quality Criteria

- Every acceptance criterion has at least one test.
- Tests cover both success and failure paths.
- Tests are independent (no shared mutable state) and deterministic (same result every run, no flakiness).
- Test names describe the expected behavior, not the implementation (e.g., `test_returns_empty_list_when_no_items` not `test_get_items`).
- The implementation is minimal — no code exists that is not required by a test.
- All tests pass when run together.

## Common Pitfalls

- **Writing implementation first** — this defeats the purpose of TDD. Always write the test first.
- **Tests that test implementation** — test what the code does (behavior), not how it does it (implementation details). If you refactor internals, tests should still pass.
- **Skipping the "verify it fails" step** — a test that passes before implementation is not testing anything. It gives false confidence.
- **Over-refactoring** — refactor only when the code is messy enough to slow down the next test cycle. Do not refactor preemptively.
- **Giant test functions** — each test should check one thing. If a test has multiple assertions checking different behaviors, split it.
