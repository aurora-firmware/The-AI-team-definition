---
title: "[Specification Title]"
version: "0.1"
status: draft  # draft | review | approved | superseded
created: YYYY-MM-DD
author: "[Author name or agent role]"
---

# [Specification Title]

<!--
This spec describes requirements and measurable criteria in prose.
It is not the implementation. Do not paste full configuration files,
build manifests, or implementation code into the sections below.
Concrete code belongs in the tasks the spec-breakdown skill produces
and in the Developer's output. See the Spec Authoring Guide for the
content contract this template implements.
-->

## Purpose

<!-- Recipe (3–4 sentences):
  1. The problem (what is broken or missing today).
  2. Why it matters now (the trigger or constraint that forced this spec).
  3. The outcome (what is observably true when the work is done).
  4. Optional: the metric that confirms success.
  Do not restate the title. Always name the *why*.
-->

What problem does this solve?
Why is it being built?
What is the expected outcome?

## Exclusions

<!-- For every alternative rejected during brainstorm, and every scope-expanding
  question the human said "no" to, record an explicit exclusion with the reason.
  Almost every spec has at least one. "No exclusions apply" should be rare and
  should follow an explicit human confirmation. -->

What this specification explicitly does NOT cover:

- **Exclusion title.** This specification excludes the work because it belongs in a separate follow-up decision.
- **Another exclusion.** This specification excludes the behavior because it is outside the approved scope.

## Architecture

### Design Principles

<!-- Each principle is a constraint on the design space — a property the design
  must satisfy. Not an implementation choice.
  Good: "Validation must run in under three minutes on the median PR."
  Bad:  "Use GitHub Actions." -->

State the guiding principles for this design.

### System Diagram

<!-- ASCII boxes and arrows. One screen wide. Components labelled. Show data
  flow, not the call graph. Class diagrams of internal classes do not belong
  here. -->

```
[ASCII diagram showing components and their relationships]
```

### Responsibility Separation

<!-- One row per component. Stay at the interface level — no method signatures
  or attribute lists. -->

| Component | Responsibility | Notes |
|---|---|---|
| Component A | What it does | Additional context |
| Component B | What it does | Additional context |

## Components

<!-- One short block per component, three lines max:
  - Purpose: one sentence — what it does.
  - Estimated size: small / medium / large, or rough effort.
  - Interfaces: exposed and consumed, named at the interface level.
  No function lists. No field lists. -->

### Component 1: [Name]

**Purpose:** One-line description.
**Estimated size:** Rough complexity estimate.
**Interfaces:** What it exposes and consumes.

### Component 2: [Name]

**Purpose:** One-line description.
**Estimated size:** Rough complexity estimate.
**Interfaces:** What it exposes and consumes.

## Workflow

<!-- End-to-end flow from trigger to completion. Each step is a sentence or
  short phrase. Mark human gates with ★. Show error paths only when a failure
  mode is interesting. -->

Describe the end-to-end flow from trigger to completion.

```
Step 1
  ↓
Step 2
  ↓
★ Step 3 (human gate if applicable)
  ↓
Step 4
```

## Configuration Requirements

Describe the settings, environment variables, or external configuration the work depends on, **as requirements**:

- **What** setting must exist and **why** (the constraint it satisfies).
- **Where** it lives (env var, config file, CI variable) — described, not pasted.
- **Constraints** on its value (allowed range, format, security class).
- **Default behavior** when the setting is missing or invalid.

Do not paste a real configuration file here. The Developer writes the file against the project's conventions; this section tells them what the file must guarantee.

If — and only if — a literal value is itself the contract (e.g. a fixed external API key name, a wire-protocol field), include it inline and mark it explicitly as **Contract**, not as **Example**.

## Implementation Order

<!-- Coarse phases (typically two to five). Each phase delivers an observable
  outcome. A phase is NOT a task — the spec-breakdown skill produces the actual
  tasks from these phases. -->

| Phase | What | Depends On |
|---|---|---|
| 1 | First deliverable | Nothing |
| 2 | Second deliverable | Phase 1 |
| 3 | Third deliverable | Phase 1 |

## Amendment Log

<!-- Optional. Use when an approved spec is amended after tasks are in flight.
For amendments driven by an accepted ADR, include the ADR ID in the row text.
| Date | What changed | Why | Affected tasks |
|------|-------------|-----|----------------|
| YYYY-MM-DD | Description of change | Reason for amendment | T-XXX, T-YYY |
-->
