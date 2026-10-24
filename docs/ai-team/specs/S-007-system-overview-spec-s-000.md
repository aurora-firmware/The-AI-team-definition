---
title: System Overview Spec (S-000)
version: '0.2'
status: approved  # draft | review | approved | superseded
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
When it is done, a new project starts with S-000; every later spec covers one S-000 component or a slice of it; the Planner and Architect read S-000 at the start of a session; and the Architect checks each new or changed spec against it.

## Exclusions

- **A separate artifact type or folder for the overview.** S-000 is a spec, so it reuses spec numbering, status, Gate 1 approval, the Amendment Log and the architecture consistency review.
- **A `component` field in spec frontmatter, or a component-to-spec mapping.** The ID `0` is the only marker that a spec is the project overview. A spec names the S-000 component it covers in its Purpose, in prose.
- **Progress tracking inside S-000.** S-000 does not record which components are specified, in progress or done. Pending and completed work is read from specs and tasks.
- **Technology choices and interface contracts in S-000.** S-000 may ask the technology questions, in a development-infrastructure component's Decisions needed; the answers belong in the project's internal development documentation, later specs and ADRs.
- **Mandatory adoption or migration in existing projects.** Projects that already have specs are not required to create S-000, and existing specs are not rewritten to the new template. They can still adopt S-000 through the brownfield path below.
- **A switch to turn the missing-S-000 hint off.** The hint is always on.
- **Changing the rules for how feature specs are decomposed or reviewed**, except where this spec says so below.

## Architecture

### Design Principles

- S-000 must stay abstract enough that it rarely changes: it describes what the project is for and how it is divided, not how any part works.
- S-000 must be readable by a non-technical stakeholder; it uses plain language and names no technology. It may ask which technology to use; it never answers.
- Every rule that treats S-000 differently from other specs must be keyed on the ID `S-000` alone.
- S-000 produces only the project bootstrap tasks for its development-infrastructure components. Feature work always comes from a feature spec, never from S-000.
- Each rule has one owner: the S-000 content contract lives in the spec authoring guide, procedures live in skills, and enforcement lives in the CLI.

### Responsibility Separation

| Component | Responsibility | Notes |
|---|---|---|
| S-000 spec template | Fixed section structure for the overview | Separate from the feature spec template |
| `new-system-overview` skill | Procedure for writing S-000 with the human, from a project description or, in an existing project, from the existing specs, decisions and code; completes S-000 after Gate 1 and hands over to the project bootstrap | Calls the CLI to create the file; Planner-owned |
| Spec authoring guide | Content contract for S-000 and the S-000 versus spec boundary | Single owner of "what goes where" |
| Feature spec template and `new-spec` skill | Cover one component's contract; refer to S-000 for system-wide context | System-wide Architecture parts move out |
| Architecture consistency review | Checks a new or changed spec against S-000 | Standing duty; no new gate |
| CLI | Creates S-000 on request, protects its ID, accepts the bootstrap tasks whose source spec is S-000, hints when S-000 is missing | `spec new`, `task new`, `validate`, `new` and `report` commands |
| Project bootstrap | Tasks created from S-000 after Gate 1 that answer the development-infrastructure Decisions needed and set up the project's environment and internal documentation | Planner-owned; Gate 2 and the development loop as for any task plan |
| `using-ai-team` and `brainstorm` skills | Suggest starting with the system overview when S-000 does not exist | Suggestion only; the human decides |
| Session-start rules | Planner and Architect read S-000 first when it exists | Planner and Architect agent descriptions |

## S-000 content contract

S-000 contains these sections, in this order, written in plain language:

1. **Purpose** — why the project exists and the outcome it must deliver.
2. **Users** — who uses it and in what situations.
3. **Pain points** — what is broken or missing for those users today.
4. **Use cases** — what users must be able to do, each tied to a pain point.
5. **Solution overview** — how the project addresses the pain points, in prose.
6. **Components** — each with a name, the responsibility it owns, its boundary (what it is not responsible for), and which other components it works with, in two groups (below).
7. **Project exclusions** — what the project as a whole will not do.

S-000 does not contain technology choices, interface definitions, configuration, implementation order or per-component status.

**What a component is.** A component is a part of the software solution, or something that affects the solution's use, delivery or deployment. A component can be software, documentation (internal or for end users), delivery and deployment (pipelines, scripts), or tooling (development environment, debugging interfaces, test harnesses). Each component passes three checks: it serves at least one use case, or, in the infrastructure group, affects the solution's use, delivery or deployment; one spec could own its contract; and its boundary would hold if the implementation were reorganised.

**Component groups.** Components fall into two groups:

- **Solution** — the software delivered to the end user that removes the pain points.
- **Development infrastructure** — everything the project needs to build, check, document and deliver the solution; it is not delivered to the end user. Each infrastructure component also has a **Decisions needed** field: the questions that must be answered before development starts, such as the language and version, how the environment is reproduced, the test harness, the continuous-integration service, and where decisions are recorded. S-000 asks these questions and never answers them.

**Users scope.** Users names the users of the solution. The people and agents who develop the project are served by the development infrastructure and are not listed unless they also use the solution.

An S-000 written before these groups existed, with a single flat Components list, stays valid; the groups and Decisions needed apply when S-000 is created or amended.

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
Planner sets S-000 to approved and merges its planning branch into dev-agent
  ↓
Brownfield only: Planner proposes a change request aligning existing specs with S-000
  ↓
Planner creates the project bootstrap tasks from S-000
  ↓
★ Architect checks the bootstrap task plan (Gate 2) → development loop
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
2. **Bootstrap tasks only.** The only tasks S-000 produces are the project bootstrap tasks (requirement 12), which cover only its development-infrastructure components. The CLI accepts a task whose source spec is S-000 and `validate` does not report it. Spec breakdown accepts S-000 for the bootstrap tasks only, and refuses, saying why, when asked to plan solution work from S-000.
3. **Session start.** When S-000 exists and is approved, the Planner and the Architect read it at the start of a session before reading other specs. The Developer, Reviewer and Integrator do not read it at session start; they work from their own agent descriptions and the task or bug they are given. A design-review task may name S-000 as a reference in its Verification section; the Developer and Reviewer then read it when they run or check that review, not at session start. The Planner and Architect agent descriptions say so.
4. **Planner.** For a project with no specs, the Planner proposes writing S-000 first. For a project that already has specs, S-000 stays optional and the Planner does not require it.
5. **Missing-S-000 hints.** When no S-000 exists (in the specs folder or its archive), the CLI prints a one-line hint, pointing to the way to create it, from `validate`, from every command that creates an artifact (`spec new`, `task new`, `bug new`, `adr new`, `change-request new`) and from the report commands. The hint is always on and not configurable. It is advisory: it never changes the exit code, never blocks the command, and goes to the error stream so that `--json` output on the standard stream stays valid. Creating S-000 itself does not print the hint.
6. **Skill suggestions.** The `using-ai-team` skill and the `brainstorm` skill tell the agent, when S-000 does not exist, to suggest to the human starting with the system overview before writing a feature spec. The human may decline, in which case the work continues as before and the agent does not repeat the suggestion in the same session.
7. **Architecture review.** When S-000 exists, the architecture consistency review confirms that a new or changed spec stays within S-000's purpose and respects each component's boundary and responsibility, and reports a violation as drift per the existing finding rules.
8. **Feature spec template.** The system-wide parts of the Architecture section move out of the feature spec template; the spec keeps principles specific to its own scope and refers to S-000 for the rest. Existing approved specs stay valid unchanged.
9. **Quality gate.** Gate 1 criteria apply to S-000 with its own pass criteria: plain language, no technology or interfaces, every use case tied to a pain point, every component with a boundary and responsibility, components in the solution and development-infrastructure groups, every infrastructure component with its Decisions needed, and no unresolved `[TODO]`. These replace, rather than add to, the Gate 1 criterion that the architecture is detailed enough to derive tasks, which S-000 cannot meet by design.
10. **Completion review.** The pre-Gate-5 completion review (ADR-002) does not include S-000. Its bootstrap tasks answer questions S-000 only asks, so S-000 makes no assertion for that work to drift from.
11. **Completing S-000.** After Gate 1, the Planner sets S-000 to `approved` and merges its planning branch into `dev-agent` with `--no-ff`. S-000's own planning branch does not wait for Gate 2 (only its bootstrap task plan does), so this merge is the one exception to merging a planning branch after Gate 2.
12. **Project bootstrap.** After S-000 is approved, the Planner creates the bootstrap tasks from S-000; there is no bootstrap spec. The task plan passes Gate 2 and runs through the development loop. The tasks produce: the answers to every Decisions needed, in internal development documentation; the development environment configuration (container or environment manager, environment variables and settings); a confirmed check of access to the remote repository; the project's coding guidelines; placeholders for the remaining internal documentation; the project guidance for agents, populated with the common rules and the build, test, lint and run commands; and the README's project description, written from S-000. In a brownfield project the bootstrap covers only what is missing, and the human may skip items that already exist. While no baseline test command exists yet, the development loop runs the bootstrap tasks after the human confirms that no automated baseline is available.
13. **Internal development documentation.** By default the bootstrap tasks write the answers to a repository-root `docs/development/` folder, in two fixed files: `architecture.md` (high-level design of the solution components) and `tech-stack.md` (the answers to every Decisions needed). When the project already has rules about where such documents go, those rules win, and the task records the chosen location in the project guidance so every agent finds it.
14. **Brownfield findings.** After Gate 1 of a brownfield S-000, the Planner proposes a change request that brings the existing specs in line with S-000's components, from the overlaps, gaps and disagreements the draft reported. The human decides which side of each disagreement changes.

## Brownfield adoption

In a project that already has specs, code or decisions, the agent can use `new-system-overview` to write S-000 from that existing material, to unify the project towards the ai-team process: S-000 becomes the shared description of its purpose and components, so that the process holds everything an agent needs to work on the project autonomously. The skill:

- Reads the existing approved specs, accepted ADRs and project documentation, and inspects the code only to learn what exists, not to describe how it works. It derives the components from the use cases and from what the existing material says the system is for, never from the code or folder layout, and checks each one against the three component checks.
- Drafts S-000 under the same content contract, in plain language, describing what the project is for and how it divides, not how it is built today.
- Reports every place where existing specs overlap, leave a gap, or disagree with the drafted components, as findings for the human, the Planner and the Architect. It does not amend approved specs itself; after Gate 1 the findings become a proposed change request (requirement 14), and amendments follow the normal amendment flow.
- Goes through the same Architect review and human Gate 1 approval as any S-000.

## Implementation Order

| Phase | What | Depends On |
|---|---|---|
| 1 | Authoring guide: S-000 content contract and S-000 versus spec boundary | Nothing |
| 2 | S-000 template, `ai-team spec new` creation path, ID and duplicate protection | Phase 1 |
| 3 | `new-system-overview` skill, including the brownfield path; breakdown refusal; CLI refusal and `validate` check for tasks from S-000; missing-S-000 hints in the CLI | Phase 2 |
| 4 | Feature spec template and `new-spec` skill changes; Planner and session-start rules; `using-ai-team` and `brainstorm` suggestions; Gate 1 criteria; architecture consistency review check | Phases 1–3 |
| 5 | Regenerate scaffolds and CLI docs; update the component map | Phase 4 |

## Amendment Log

| Date | What changed | Why | Affected tasks |
|------|-------------|-----|----------------|
| 2026-10-20 | Requirement 3: a design-review task may name S-000 as a reference; the Developer and Reviewer read it when they run or check that review, not at session start. Driven by CR-003 §2 and Architecture Consistency Review finding F2. | CR-003 introduces design-review verification against the source spec, accepted ADRs and S-000, which the session-start rule for Developer and Reviewer did not allow for. | None in flight |
| 2026-10-24 | Content contract: component definition and checks, solution and development-infrastructure groups, Decisions needed, Users scope. Exclusions and Design Principles: S-000 asks technology questions and produces only bootstrap tasks. Workflow, Requirements 2, 9 and 10 restated; Requirements 11–14 added (post-Gate-1 completion, project bootstrap, internal development documentation, brownfield findings). Brownfield adoption: components from use cases; findings become a CR. Driven by CR-004 items 1–9. | Writing this repository's S-000 needed a component model and a post-approval step the contract did not define (CR-004). | None in flight |
| 2026-10-24 | Workflow: the brownfield change request comes before the bootstrap tasks, matching `new-system-overview`; Requirement 11 reworded ("S-000's own planning branch does not wait for Gate 2"). In-flight CR-004 amendment from the PR #48 review. | The diagram and the skill gave different orders, and "S-000 has no Gate 2" read as contradicting the bootstrap plan's Gate 2. | None in flight |
