---
title: "Escalation Procedure"
status: approved
created: 2026-03-10
---

# Escalation Procedure

## Overview

Escalation is a two-stage safety net that prevents agents from spinning indefinitely on unsolvable problems.
It separates **agent-level retries** (the agent tries to fix the problem itself) from **escalation** (asking for outside help).

```
Agent encounters problem
    ↓
Phase 1: Agent Self-Recovery (agent retries within its own threshold)
    ↓ threshold exceeded
Phase 2: Escalation Chain
    ├── Step 1: Architect Consultation (one attempt)
    │       ├── Resolved → Agent continues
    │       └── Not resolved ↓
    └── Step 2: Human Escalation
                Human decides next action
```

## Phase 1: Agent Self-Recovery

Before escalating, every agent must make a reasonable effort to solve the problem on its own.
Each agent definition specifies its own retry threshold (see the agent's Escalation Triggers section).
These retries happen **before** entering the escalation chain.

| Agent | Self-recovery threshold |
|-------|------------------------|
| Implementer | Three consecutive failed attempts to make tests pass |
| Reviewer | One review cycle — if fundamental design issues exist, escalate immediately |
| Integrator | One bisect cycle — if the root cause spans multiple tasks, escalate immediately |

Once the agent exceeds its threshold, it stops retrying and enters Phase 2.

## Phase 2: Escalation Chain

### Step 1: Architect Consultation

- **Who:** The architect agent.
- **How:** The blocked agent sends a structured request describing the problem, what was attempted, and why it failed.
- **Scope:** The architect provides advice only — it does not modify code or make implementation decisions.
- **Limit:** One consultation attempt per issue. The agent applies the architect's guidance and tries once more. If it still fails, proceed to Step 2.

**Architect request format:**
```
Problem: [What went wrong]
Attempted: [What the agent tried, including number of retries]
Failed because: [Why it did not work]
Question: [Specific question for the architect]
```

### Step 2: Human Escalation

- **Who:** A human operator.
- **How:** A notification is sent with the full context (original task, agent's self-recovery attempts, architect's advice, and why it was insufficient).
- **Outcome:** The human chooses one of the following actions:

| Human decision | What happens next | Agent responsible |
|---------------|-------------------|-------------------|
| Revise the spec | Planner edits spec in-place, adds entry to the spec's Amendment Log section, identifies affected tasks, adds a note to each affected `in-progress/` task referencing the amendment. | Planner |
| Modify the task | Task file is updated directly with new or changed requirements. Implementer re-reads the task and continues. | Human or Planner |
| Provide guidance | The blocked agent applies the guidance and continues. No document changes needed. | Blocked agent |
| Defer the work | Task moves to `blocked/` with the reason noted. The spec issue is not addressed now. | Implementer |

## When to Escalate

An agent enters the escalation chain when it **cannot complete its assigned task** after exhausting its self-recovery threshold. Specific triggers:

- **Implementer:** Tests fail repeatedly (3 attempts). Requirements are ambiguous or untestable. Conflicting constraints make the task impossible as specified.
- **Reviewer:** Code has fundamental design issues that cannot be fixed without changing the specification.
- **Integrator:** Merge conflicts that cannot be resolved without understanding both sides' intent. Integration tests fail and bisect points to multiple interacting causes.

## Rules

1. **Retry first, then escalate** — agents must exhaust their self-recovery threshold before entering the escalation chain. Once in the chain, the architect gets one consultation attempt. If that fails, escalate to human immediately. Do not loop.
2. **Always include context** — every escalation must carry the full chain of what was attempted. The receiving party should never need to ask "what did you try?"
3. **Do not skip steps** — always consult the architect before escalating to human, unless the architect agent is the one that is stuck.
4. **No silent failures** — if an agent is stuck, it must escalate. Doing nothing is not acceptable.
