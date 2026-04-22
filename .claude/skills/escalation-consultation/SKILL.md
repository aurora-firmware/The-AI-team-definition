---
name: escalation-consultation
description: Analyse blocked work after a role has exhausted self-recovery. Use when a Developer, Reviewer, Integrator, Development Loop, or Bug-Fix Loop sends a structured escalation request and the Architect must issue guidance or escalate to a human.
allowed-tools: Read, Grep, Glob, Write, Edit, Skill(new-adr)
effort: high
---

# Escalation Consultation

## Input Requirements

- **Structured request** with:
  - Problem
  - Attempted
  - Failed because
  - Question
- **Original work item** — task or bug file.
- **Relevant logs** — Work Log, Diagnosis Log, Review Verdicts, test output, or merge-conflict context.
- **Approved specification and ADRs** when the issue may affect scope or architecture.

## Procedure

### Step 1: Read The Full Context

Read the escalation request, the work item, and all relevant logs.
Read the approved specification and ADRs if the problem may affect scope, architecture, branch flow, task dependencies, or prior decisions.

### Step 2: Classify The Blocker

Classify the blocker as one of:

- **Execution issue** — can be solved within the current task or bug scope.
- **Task or bug description issue** — needs clearer requirements but not a spec change.
- **Architecture issue within spec bounds** — needs structural guidance or an ADR.
- **Specification issue** — requires changing an approved spec.
- **Unresolvable with current evidence** — needs human judgment.

### Step 3: Issue Guidance Or Escalate

If the issue can be resolved within the approved spec, provide a specific directive to the requesting role.
The directive must include what to change, where to apply it, and how to verify it.

If the task or bug file needs clarification within existing scope, recommend the exact amendment and the owner who should make it.

If the issue is architecture-affecting and within the approved spec, use `new-adr` or amend an existing ADR before implementation continues.

If the issue requires changing the approved spec, or cannot be resolved after full analysis, escalate to the human with a compact context package.

## Output Format

Use this structure:

```text
Escalation Verdict: RESOLVED | HUMAN_ESCALATION

Classification: <execution | work-item | architecture | specification | unresolved>

Analysis:
- <root cause of the blocker>

Directive:
- <specific action for the requesting role>

Verification:
- <command or check that proves the directive worked>

Human escalation required because:
- <only when verdict is HUMAN_ESCALATION>
```

## Quality Criteria

- The response addresses root cause, not symptoms.
- Guidance is specific enough for the blocked role to continue without another clarification round.
- The directive stays within the approved specification unless escalating to human.
- ADRs are created or amended only for durable architecture-affecting decisions.
- The human escalation package includes the original work item, attempts, failure reason, Architect analysis, and precise decision needed.

## Common Pitfalls

- Repeating the failed role's troubleshooting without adding structural analysis.
- Giving vague advice such as "refactor" or "simplify".
- Silently changing approved scope.
- Skipping human escalation when the spec must change.
- Creating a loop of repeated Architect consultations instead of resolving or escalating.
