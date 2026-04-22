---
title: "Agent Template"
status: draft
created: 2026-04-22
---

# Agent Template

Use this template when creating or updating an agent for this framework.
Agents are **roles**: they define identity, authority, scope, handoffs, and output expectations.
Step-by-step procedures belong in skills.

This template applies the subagent best practices from `anthropic_agents_course.md`: specific descriptions, structured output, obstacle reporting, and limited tool access.

## Agent File Template

````markdown
---
name: agent-name
description: Role-specific description that tells the caller exactly when to use this agent and what inputs to provide. Use for [specific workflow point]. Caller must provide [artifact/path/branch/context].
tools: Read, Glob, Grep
model: claude-sonnet-4-6
skills: skill-one skill-two
---

## Purpose

One short paragraph describing the role this agent plays in the AI team.
State what outcome this agent is responsible for.
Do not include step-by-step procedure logic here.

## Delegation Contract

The caller must provide:

- **Work item:** `project/.../<file>.md`
- **Branch or target:** `branch-name` or `none`
- **Expected output:** [verdict, document, code handoff, guidance, merge result]
- **Relevant constraints:** [spec, ADRs, files to review, test command, escalation context]

If required input is missing, ask for it or return `BLOCKED` instead of guessing.

## Capabilities

### Tools

- `Read`, `Glob`, `Grep` — use for context gathering.
- `Bash` — use only when this role must inspect git state, diffs, tests, or branch status.
- `Write`, `Edit` — use only when this role is allowed to change files.

Keep tool access narrow.
Do not grant write tools to read-only roles.

### Skills

- `skill-one` — when this role uses it.
- `skill-two` — when this role uses it.

Skills define procedures.
This agent invokes them but does not duplicate their steps.

## Decision Authority

### Can Decide Alone

- [Decision this role owns]
- [Decision within approved spec/task/bug scope]

### Must Escalate

- [Condition requiring Architect]
- [Condition requiring Human]
- [Condition requiring approved spec change]

## Interaction Pattern

### Receives Work From

- **[Role/process/human]** — what is received and in what state.

### Hands Off To

- **[Role/process/human]** — what is delivered and where it is recorded.

## Folder Scope

| Access | Paths |
|---|---|
| Read | [paths] |
| Write / Edit | [paths or `none`] |
| Never touch | [paths] |

## Quality Bar

- [Done criterion 1]
- [Done criterion 2]
- [Evidence expected]
- [Scope constraint]

## Output Format

Return this structure at the end of every assignment:

```text
Result: PASS | FAIL | BLOCKED | ESCALATE

Summary:
- <brief statement of what was reviewed, created, changed, or decided>

Artifacts:
- <files created/updated/read as primary evidence>

Evidence:
- <commands run, checks performed, logs reviewed, verdict location, or "not run" with reason>

Obstacles Encountered:
- <setup issue, missing input, workaround, special command flag, dependency/import issue, environment quirk, or "none">

Next Owner:
- <Developer | Reviewer | Architect | Planner | Integrator | Human | Loop | none>

Next Action:
- <specific follow-up required, or "none">
```

## Escalation Format

When escalating, use:

```text
Problem: [what went wrong]
Attempted: [what was tried, including retry count or review cycle]
Failed because: [why it did not work]
Question: [specific decision or guidance needed]
```

## Anti-Patterns

- Do not include detailed procedural steps; put them in a skill.
- Do not claim generic expertise as the reason this agent exists.
- Do not run hidden test-runner work when the caller needs full test output.
- Do not split tightly coupled sequential work across multiple agents.
- Do not modify files outside the folder scope.
````

## Description Guidance

The `description` is loaded before the full agent file.
It controls when the agent is selected and shapes the prompt the caller gives it.

A good description includes:

- The role's concrete responsibility.
- The workflow point where it should be used.
- The exact inputs the caller should provide.
- The output the caller should expect.

Example:

```yaml
description: Reviews completed task or bug-fix work after Developer handoff. Caller must provide the task or bug file, source branch, relevant diff or changed files, and expected verdict location.
```

Avoid vague descriptions such as:

```yaml
description: Expert code reviewer.
```

## Tool Guidance

Start with the narrowest viable tool set:

- Research or structural read-only roles: `Read, Glob, Grep`
- Review roles that inspect git diffs or run verification: `Read, Glob, Grep, Bash`
- Roles that write verdicts or documents: add `Write, Edit`
- Roles that modify code or resolve conflicts: add `Write, Edit, Bash`

If a role has broad tools for platform reasons, restate path restrictions in `Folder Scope` and `Quality Bar`.

## Fit With This Repo

Use these defaults for the AI team:

| Agent | Expected Tool Shape | Main Skills |
|---|---|---|
| Planner | Read/write docs and tasks; no source edits | `brainstorm`, `write-plan`, `new-spec`, `new-task` |
| Architect | Read broadly; edit pending tasks and ADRs only | `gate-2-preflight`, `escalation-consultation`, `new-adr` |
| Developer | Edit source/tests and assigned work logs | `debug`, `tdd`, `new-bug` |
| Reviewer | Read source/tests; write verdicts only | `code-review`, `new-bug` |
| Integrator | Git/test/conflict tools; write only integration-owned state | `integrate`, `conflict-resolution` |

Keep agents stable and small.
When behavior becomes a repeatable sequence, create or update a skill instead of expanding the agent file.
