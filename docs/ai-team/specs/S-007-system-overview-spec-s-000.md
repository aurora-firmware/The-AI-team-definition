---
title: System Overview Spec (S-000)
version: '0.1'
status: draft  # draft | review | approved | superseded
created: '2026-10-19'
author: planner
id: S-007
---

# System Overview Spec (S-000)

<!--
This spec describes requirements and measurable criteria in prose.
It is not the implementation. Do not paste full configuration files,
build manifests, or implementation code into the sections below.
-->

## Purpose

A project started from scratch with the AI team has no document above its specs. Every spec has to re-invent why the project exists and how it is split into components, so specs overlap, leave gaps, or fix interfaces before the component boundaries are settled, and each new session has no single place to learn what the project is for.
This spec adds one canonical, high-level spec per project, **S-000**, written before any other spec. It states the purpose, users, pain points, use cases and solution in plain language, and breaks the solution into components with explicit boundaries and responsibilities. It never defines technology or interfaces.
When it is done, a new project starts with S-000; every later spec covers one S-000 component or a slice of it; agents read S-000 at the start of a session; and the Architect checks each new or changed spec against it.

## Exclusions

- **A separate artifact type or folder for the overview.** S-000 is a spec, so it reuses spec numbering, status, Gate 1 approval, the Amendment Log and the architecture consistency review.
- **A `component` field in spec frontmatter, or a component-to-spec mapping.** The ID `0` is the only marker that a spec is the project overview. A spec names the S-000 component it covers in its Purpose, in prose.
- **Progress tracking inside S-000.** S-000 does not record which components are specified, in progress or done. Pending and completed work is read from specs and tasks.
- **Technology choices and interface contracts in S-000.** They belong in later specs and ADRs.
- **Retrofitting existing projects.** Projects that already have specs are not required to create S-000, and existing specs are not migrated.
- **Changing the rules for how feature specs are decomposed or reviewed**, except where this spec says so below.

## Architecture

### Design Principles

- S-000 must stay abstract enough that it rarely changes: it describes what the project is for and how it is divided, not how any part works.
- S-000 must be readable by a non-technical stakeholder; it uses plain language and names no technology.
- Every rule that treats S-000 differently from other specs must be keyed on the ID `S-000` alone.
- S-000 must never produce tasks, and the tooling must make that mistake impossible to complete.
- Each rule has one owner: the S-000 content contract lives in the spec authoring guide, procedures live in skills, and enforcement lives in the CLI.

### Responsibility Separation

| Component | Responsibility | Notes |
|---|---|---|
| S-000 spec template | Fixed section structure for the overview | Separate from the feature spec template |
| `new-system-overview` skill | Procedure for writing S-000 with the human, from a project description | Calls the CLI to create the file; Planner-owned |
| Spec authoring guide | Content contract for S-000 and the S-000 versus spec boundary | Single owner of "what goes where" |
| Feature spec template and `new-spec` skill | Cover one component's contract; refer to S-000 for system-wide context | System-wide Architecture parts move out |
| Architecture consistency review | Checks a new or changed spec against S-000 | Standing duty; no new gate |
| CLI | Creates S-000 on request, protects its ID, refuses task creation from it | `spec new`, `task new`, `validate` |
| Session-start rules | Agents read S-000 first when it exists | Project instruction scaffolds |

## S-000 content contract

S-000 contains these sections, in this order, written in plain language:

1. **Purpose** — why the project exists and the outcome it must deliver.
2. **Users** — who uses it and in what situations.
3. **Pain points** — what is broken or missing for those users today.
4. **Use cases** — what users must be able to do, each tied to a pain point.
5. **Solution overview** — how the project addresses the pain points, in prose.
6. **Components** — each with a name, the responsibility it owns, its boundary (what it is not responsible for), and which other components it works with.
7. **Project exclusions** — what the project as a whole will not do.

S-000 does not contain technology choices, interface definitions, configuration, implementation order or per-component status.

**Specs versus S-000.** S-000 owns the decomposition: which components exist and what each is for. A spec owns the contract of one component or feature: its interfaces, requirements, success criteria and exclusions. A spec's Purpose names the S-000 component it covers.

## Workflow

```
Human describes the project
  ↓
Planner writes S-000 with the human (new-system-overview)
  ↓
Architect reviews S-000 for internal consistency
  ↓
★ Human approves S-000 (Gate 1)
  ↓
Planner brainstorms and writes one spec per component or slice
  ↓
Architect checks each spec against S-000 (consistency review)
  ↓
★ Human approves each spec (Gate 1) → breakdown → tasks
```

A spec that needs something S-000 does not cover is a signal either to amend S-000 through the normal amendment flow, or to cut the spec back to scope. The Architect names which in its finding.

## Requirements

1. **Creation.** The CLI creates S-000 on explicit request, from its own template, in the specs folder with ID `S-000` and the usual frontmatter. It refuses when an S-000 already exists, including in the spec archive. Normal spec creation is unchanged and still starts at S-001.
2. **No tasks.** Spec breakdown refuses S-000 and says why. The CLI refuses to create a task whose source spec is S-000, and `validate` reports any task that names S-000 as its source spec.
3. **Session start.** When S-000 exists and is approved, every role reads it at the start of a session before reading other specs. The project instruction scaffolds say so.
4. **Planner.** For a project with no specs, the Planner proposes writing S-000 first. For a project that already has specs, S-000 stays optional and the Planner does not require it.
5. **Architecture review.** When S-000 exists, the architecture consistency review confirms that a new or changed spec stays within S-000's purpose and respects each component's boundary and responsibility, and reports a violation as drift per the existing finding rules.
6. **Feature spec template.** The system-wide parts of the Architecture section move out of the feature spec template; the spec keeps principles specific to its own scope and refers to S-000 for the rest. Existing approved specs stay valid unchanged.
7. **Quality gate.** Gate 1 criteria apply to S-000 with its own pass criteria: plain language, no technology or interfaces, every use case tied to a pain point, every component with a boundary and responsibility, and no unresolved `[TODO]`.

## Implementation Order

| Phase | What | Depends On |
|---|---|---|
| 1 | Authoring guide: S-000 content contract and S-000 versus spec boundary | Nothing |
| 2 | S-000 template, `ai-team spec new` creation path, ID and duplicate protection | Phase 1 |
| 3 | `new-system-overview` skill; breakdown refusal; CLI refusal and `validate` check for tasks from S-000 | Phase 2 |
| 4 | Feature spec template and `new-spec` skill changes; Planner and session-start rules; Gate 1 criteria; architecture consistency review check | Phases 1–3 |
| 5 | Regenerate scaffolds and CLI docs; update the component map | Phase 4 |

## Amendment Log

<!-- Optional. Use when an approved spec is amended after tasks are in flight.
| Date | What changed | Why | Affected tasks |
|------|-------------|-----|----------------|
| YYYY-MM-DD | Description of change | Reason for amendment | T-XXX, T-YYY |
-->
