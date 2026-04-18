---
title: "Code Review Checklist"
status: approved
created: 2026-03-10
---

# Code Review Checklist

This checklist is used by the reviewer agent during the two-stage code review process.

## Stage 1: Spec Compliance

- [ ] All acceptance criteria from the task are met.
- [ ] No functionality is missing compared to what the task specifies.
- [ ] No unspecified behavior or features were added.
- [ ] Soft flag only; do not fail Stage 1 solely for this: Exclusions section is present and contains at least the human-confirmed answer (either concrete exclusions or an explicit 'no exclusions apply').
- [ ] Files modified match the "Files to Touch" list in the task. Any file created or modified that is not listed there must be explicitly justified in the Work Log — otherwise this is a **Fail**.

## Stage 2: Code Quality

### Correctness
- [ ] Logic is correct for all expected inputs (including edge cases).
- [ ] Error handling covers failure modes described in the spec.
- [ ] No off-by-one errors, null reference issues, or unhandled states.

### Tests
- [ ] Tests exist for the new or modified code.
- [ ] Tests cover both success and failure paths.
- [ ] Tests are independent (no shared mutable state).
- [ ] All tests pass. "Pre-existing failure" is not an exception — if a failure exists in the test suite when this task is reviewed, it must be fixed or explicitly excluded from the test runner before this task can pass. A failure that predates the task is still a failure.

### Security
- [ ] No hardcoded credentials or secrets.
- [ ] External input is validated before use.
- [ ] Database queries use parameterized statements.
- [ ] No new permissions or access beyond what is needed.

### Readability
- [ ] Names are descriptive and follow project conventions.
- [ ] Functions are focused (one responsibility each).
- [ ] Comments explain *why*, not *what* (no redundant comments).
- [ ] No dead code, commented-out blocks, or debugging artifacts.

### Performance
- [ ] No unnecessary loops over large data sets.
- [ ] No blocking operations in hot paths without justification.
- [ ] No obvious memory leaks or resource leaks.

## Review Verdict

**Pass** — all checks are satisfied.
**Fail** — one or more checks are not satisfied. Return to implementer with specific, actionable notes for each failed check.
