---
title: "[Feature/Component] Test Plan"
status: draft  # draft | review | approved
created: YYYY-MM-DD
---

# [Feature/Component] Test Plan

## Scope

What is being tested and what is explicitly out of scope.

## Test Types

### Unit Tests

- **Target:** Individual functions and methods.
- **Coverage goal:** Percentage or description of coverage expectations.
- **Framework:** Test framework to use.

### Integration Tests

- **Target:** Component interactions and data flow.
- **Coverage goal:** Key integration paths to cover.
- **Environment:** What services or dependencies are needed.

### End-to-End Tests

- **Target:** Full user workflows.
- **Coverage goal:** Critical paths to cover.
- **Environment:** Full system requirements.

## Test Data

Describe test fixtures, mock data, or seed data requirements.

## Environment

- Runtime version:
- Required services:
- Configuration:

## Execution

```bash
# Command to run the full test suite
```

```bash
# Command to run a specific test type
```

## Schedule

| Phase | Test Type | When |
|---|---|---|
| During implementation | Unit tests | With each task |
| After task completion | Integration tests | Before code review |
| After merge | End-to-end tests | Before release |
