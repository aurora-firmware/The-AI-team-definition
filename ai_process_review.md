---
title: "Review: ai-process"
date: 2026-04-22
scope: "ai-process only"
---

# Review: ai-process

This review covers only `ai-process/`.
It ignores implementation folders and focuses on inconsistencies, contradictions, and unnecessary process complexity in the process specification.

## Findings

### 1. Integration failure recovery is internally inconsistent

`workflow-overview.md` says integration failure leaves the task branch preserved, keeps `dev-agent` clean, files bugs, then the human starts the bug-fix loop.
Later, the bug-fix loop says bug branches are created from `dev-agent`.

Relevant locations:
- `ai-process/processes/workflow-overview.md:151`
- `ai-process/processes/workflow-overview.md:161`
- `ai-process/processes/workflow-overview.md:168`

Problem: if the regression only appears when the task branch is merged, a bug branch created from clean `dev-agent` may not contain the failing change.
The process needs to say whether regressions are fixed on the original task branch, on a bug branch based from the task branch, or on `dev-agent` before retrying integration.

### 2. Escalation allows both multiple rounds and one attempt

`escalation-procedure.md` says the Architect may provide multiple rounds of guidance until resolved.
The same document later says the Architect gets one consultation attempt and then escalation must go to the human immediately.

Relevant locations:
- `ai-process/processes/escalation-procedure.md:48`
- `ai-process/processes/escalation-procedure.md:83`

Problem: these define different escalation models.
Pick one: either Architect consultation is a bounded multi-round process, or it is a single attempt.

### 3. Developer input ownership conflicts across docs

`system-overview.md` says the Development Loop assigns work to the Developer.
`component-map.md` says the Developer receives work from the Task directory.

Relevant locations:
- `ai-process/architecture/system-overview.md:90`
- `ai-process/architecture/component-map.md:17`

Problem: this blurs whether roles pull from directories directly or processes assign work.
The cleaner model is: the Development Loop reads the Task Board, moves task state, and assigns the Developer.
The Developer receives a task assignment from the Development Loop, not directly from the Task directory.

### 4. Gate 2 blurs Planner and Architect ownership

Gate 2 lets the Architect create corrective tasks or return the task plan to the Planner.

Relevant locations:
- `ai-process/processes/quality-gates.md:34`
- `ai-process/processes/workflow-overview.md:97`

Problem: this makes the Architect both evaluator and author of the task plan.
That weakens the Planner's ownership of structured task decomposition.

Recommended model:
- Planner owns task creation and task edits.
- Architect evaluates Gate 2.
- On failure, Architect returns required corrections.
- Planner updates the task plan.
- Architect re-evaluates Gate 2.

### 5. Testing gates are duplicated

Gate 3 requires tests to exist and pass.
Gate 4 also requires pre-merge unit tests and post-merge tests.
The review checklist also says all tests must pass and pre-existing failures are not exempt.

Relevant locations:
- `ai-process/processes/quality-gates.md:50`
- `ai-process/processes/quality-gates.md:61`
- `ai-process/guidelines/review-checklist.md:27`

Problem: test enforcement appears in three places.
This may be intentional defense-in-depth, but the current wording does not distinguish responsibility clearly.

Recommended model:
- Gate 3 verifies that appropriate tests were added and that the Developer reported passing local evidence.
- Gate 4 owns authoritative test execution before and after merge.
- The review checklist supports Gate 3, but does not duplicate Gate 4's integration-test authority.

### 6. Review checklist assumes task fields not defined by the process

The review checklist requires an Exclusions section and a "Files to Touch" list.
The process docs say task files exist, but do not define the required task schema.

Relevant locations:
- `ai-process/guidelines/review-checklist.md:16`
- `ai-process/guidelines/review-checklist.md:17`

Problem: the Reviewer can fail a task for missing fields that `ai-process` does not define as required.
Either define the task file contract in the process layer or remove checklist requirements that are not guaranteed.

### 7. Final merge sign-off depends on an undefined status summary

Gate 5 requires a status summary, but `ai-process` does not define who produces it, when it is produced, what it contains, or where it lives.

Relevant locations:
- `ai-process/processes/quality-gates.md:75`
- `ai-process/processes/workflow-overview.md:154`

Problem: Gate 5 depends on an artifact that has no process owner or required format.
Add a "Status Summary" procedure or make the Development Loop produce the summary when the queue is empty.

### 8. Markdown conventions are not followed by ai-process docs

The markdown convention requires one sentence per line.
Several `ai-process` docs use multiple sentences per source line.

Relevant locations:
- `ai-process/guidelines/markdown-conventions.md:34`
- `ai-process/processes/workflow-overview.md:76`
- `ai-process/architecture/system-overview.md:11`

Problem: the standard is not enforced by the docs that define it.
Either relax the convention or reformat the docs to match it.

## Main Simplification

The main simplification I would make is to define three explicit state machines and make every role, process, procedure, and gate refer back to them.
Right now the lifecycle rules are distributed across workflow overview, quality gates, escalation, git conventions, and the component map.
That distribution is the root cause of the drift: branch recovery, task ownership, bug handling, and gate responsibilities are each described in more than one place.

### 1. Task Lifecycle State Machine

Define the task lifecycle once, probably in `workflow-overview.md` or a dedicated `task-lifecycle.md`.

Suggested states:

| State | Owner | Entry condition | Exit condition |
|---|---|---|---|
| `pending/` | Planner | Task created from approved spec | Development Loop selects it |
| `in-progress/` | Development Loop | Task is claimed and branch is created | Reviewer passes, task is blocked, or task is abandoned |
| task branch | Developer | Developer receives assignment | Developer submits for review |
| review pending | Reviewer | Developer reports completion | PASS, FAIL, or ESCALATE verdict |
| integration pending | Integration Procedure | Reviewer returns PASS | Integration succeeds or fails |
| `completed/` | Integration Procedure | Merge and tests pass | Final summary includes task |
| `blocked/` | Development Loop or Escalation Procedure | Max retries, escalation, or unresolved blocker | Human/Planner resolves blocker and returns task to `pending/` or `in-progress/` |

Key rule: the Development Loop owns task state transitions.
The Developer owns code changes on the task branch.
The Reviewer owns verdicts.
The Integration Procedure owns merge and post-merge validation.

### 2. Bug Lifecycle State Machine

Define bug handling separately from task handling.
The current process says regressions produce bug reports, but it is ambiguous about the branch base and whether the bug fix includes the regressing task changes.

Suggested states:

| State | Owner | Entry condition | Exit condition |
|---|---|---|---|
| `open/` | Integration Procedure or Human | Regression or defect is filed | Bug-Fix Loop selects it |
| `in-progress/` | Bug-Fix Loop | Bug branch is created | Reviewer passes, bug is blocked, or escalation occurs |
| bug branch | Developer | Developer receives bug assignment | Developer submits fix for review |
| review pending | Reviewer | Developer reports completion | PASS, FAIL, or ESCALATE verdict |
| integration pending | Integration Procedure | Reviewer returns PASS | Integration succeeds or fails |
| `resolved/` | Integration Procedure or Bug-Fix Loop | Fix is merged and tests pass | Included in status summary |

The branch-base rule must be explicit:
- If a bug is an existing defect on `dev-agent`, create the bug branch from `dev-agent`.
- If a bug is a regression introduced by a task branch that failed integration and was reverted, either fix it on the original task branch or create the bug branch from the preserved task branch.

This single rule would remove the biggest ambiguity in the current process.

### 3. Gate Lifecycle State Machine

Define gates as transitions between lifecycle states, not as separate narrative checkpoints.

Suggested gates:

| Gate | Controls transition | Evaluator | Output |
|---|---|---|---|
| Gate 1: Specification Approval | feature request → approved spec | Human | approved specification |
| Gate 2: Task Plan Preflight | task plan draft → implementation-ready task queue | Architect | approved task queue or correction request |
| Gate 3: Code Review | Developer-complete task → integration-ready branch | Reviewer | PASS, FAIL, or ESCALATE |
| Gate 4: Integration Tests | reviewed branch → completed task/bug | Integration Procedure | merged/completed or regression report |
| Gate 5: Final Merge Sign-off | completed queue → production merge | Human | approval to merge `dev-agent` to `main` |

Each gate should define:
- Input artifact.
- Evaluator.
- Pass output.
- Fail output.
- Who owns the next action.

That removes repeated prose like "human starts loop," "task returns to Developer," and "bug branch is preserved" from multiple places.
Each process can then just say which transition it is performing.

### Resulting Structure

After simplification, the docs could be organized like this:

| Document | Responsibility |
|---|---|
| `workflow-overview.md` | High-level flow and references to the three lifecycle state machines |
| `quality-gates.md` | Gate definitions only: input, evaluator, pass, fail, next owner |
| `escalation-procedure.md` | Escalation state machine only |
| `git-conventions.md` | Branch names, commit ownership, hard git rules |
| `component-map.md` | Roles, processes, procedures, gates, and implementation mapping |
| `review-checklist.md` | Detailed Gate 3 checklist |
| `coding-standards.md` | Code quality rules only |

This would make the process easier to audit.
Instead of checking five files to understand what happens after an integration failure, the reader would look at the task lifecycle, bug lifecycle, and Gate 4 definition.
