---
name: [agent-name]
description: [One-sentence description of this agent's role — used by Claude Code to decide when to delegate.]
tools: Read, Write, Edit, Glob, Grep, Bash
---

# [Agent Role Name]

## Purpose

One-sentence description of this agent's role in the team.
Agents describe role identity, authority, handoffs, and quality bar.
Do not put step-by-step procedures here; procedures belong in skills.

## Capabilities

### Tools
- Tool 1 — what it is used for
- Tool 2 — what it is used for

### Skills
- `skill-name` — when this skill is applied
- `skill-name` — when this skill is applied

## Decision Authority

### Can Decide Alone
- Decision type 1
- Decision type 2

### Must Escalate
- Decision type 1 — escalate to [whom]
- Decision type 2 — escalate to [whom]

## Escalation Triggers

Conditions that require this agent to stop and escalate:
- Trigger 1
- Trigger 2

## Interaction Pattern

### Receives Work From
- [Agent or process] — what is received

### Hands Off To
- [Agent or process] — what is delivered

## Quality Bar

What "done" looks like for this agent's work:
- Criterion 1
- Criterion 2

## Model and Effort

Specify model and effort in frontmatter — these are the supported Claude Code fields:

```yaml
model: claude-opus-4-6   # heavier reasoning: architect, reviewer
model: claude-sonnet-4-6 # code execution, structured tasks: developer, integrator, planner
effort: high             # analytical/review agents that benefit from deeper reasoning
effort: max              # Opus 4.6 only — reserved for highest-stakes decisions
```

Do NOT add a "temperature" field; temperature is not configurable in Claude Code agent definitions.
