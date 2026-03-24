---
name: agent-name
description: "When to use this agent — drives automatic delegation."
tools: Read, Write, Edit, Grep, Glob, Bash
# disallowedTools: Write, Edit  # for read-only agents
# skills:                        # only inject skills used EVERY session
#   - primary-skill
---

# [Agent Role Name]

## Purpose

One-sentence description of this agent's role.

## Decision Authority

- **Autonomous:** [what this agent can decide alone]
- **Escalate:** [what requires escalation] — to [whom]

## Escalation Triggers

- Trigger 1
- Trigger 2

## Interaction Pattern

- **From:** [agent/process] — [what is received]
- **To:** [agent/process] — [what is delivered]

## Quality Bar

- Criterion 1
- Criterion 2

## On-Demand Skills

Reference skills not injected via frontmatter:
- `skill-name` — when to invoke it
