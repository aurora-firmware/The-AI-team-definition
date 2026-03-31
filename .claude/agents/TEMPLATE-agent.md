---
name: [agent-name]
description: [One-sentence description of this agent's role — used by Claude Code to decide when to delegate.]
tools: Read, Write, Edit, Glob, Grep, Bash
---

# [Agent Role Name]

## Purpose

One-sentence description of this agent's role in the team.

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

## Temperature Guidance

- **Creative tasks:** 0.7 (brainstorming, exploring alternatives)
- **Structured tasks:** 0.2 (JSON output, precise formatting)
- **Execution tasks:** 0.3 (writing code, following procedures)
- **Review tasks:** 0.4 (critical analysis, finding issues)

Select the appropriate temperature based on the current activity.
