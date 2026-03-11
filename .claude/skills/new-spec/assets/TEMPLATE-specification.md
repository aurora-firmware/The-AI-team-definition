---
title: "[Specification Title]"
version: "0.1"
status: draft  # draft | review | approved | superseded
created: YYYY-MM-DD
author: "[Author name or agent role]"
---

# [Specification Title]

## Purpose

What problem does this solve?
Why is it being built?
What is the expected outcome?

## Architecture

### Design Principles

State the guiding principles for this design.

### System Diagram

```
[ASCII diagram showing components and their relationships]
```

### Responsibility Separation

| Component | Responsibility | Notes |
|---|---|---|
| Component A | What it does | Additional context |
| Component B | What it does | Additional context |

## Components

### Component 1: [Name]

**Purpose:** One-line description.
**Estimated size:** Rough complexity estimate.
**Interfaces:** What it exposes and consumes.

### Component 2: [Name]

**Purpose:** One-line description.
**Estimated size:** Rough complexity estimate.
**Interfaces:** What it exposes and consumes.

## Workflow

Describe the end-to-end flow from trigger to completion.

```
Step 1
  ↓
Step 2
  ↓
Step 3 (human gate if applicable)
  ↓
Step 4
```

## Configuration

```yaml
# Example configuration with inline comments
setting_a: value
setting_b:
  nested_key: value
```

## Implementation Order

| Phase | What | Depends On |
|---|---|---|
| 1 | First deliverable | Nothing |
| 2 | Second deliverable | Phase 1 |
| 3 | Third deliverable | Phase 1 |

## Exclusions

What this specification explicitly does NOT cover:

- Exclusion 1 — reason
- Exclusion 2 — reason

## Future Roadmap

Features or improvements deferred to later versions:

- Future item 1 — rationale for deferral
- Future item 2 — rationale for deferral
