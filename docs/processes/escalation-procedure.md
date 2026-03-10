---
title: "Escalation Procedure"
status: approved
created: 2026-03-10
---

# Escalation Procedure

## When to Escalate

An agent should escalate when it **cannot complete its assigned task** after a reasonable attempt. Specific triggers:

- **Implementer:** Tests fail repeatedly after multiple fix attempts. Requirements are ambiguous. Conflicting constraints make the task impossible as specified.
- **Reviewer:** Code has fundamental design issues that cannot be fixed without changing the specification.
- **Tester:** Cannot create a meaningful test due to unclear requirements or untestable architecture.
- **Integrator:** Merge conflicts that cannot be resolved without understanding both sides' intent. Integration tests fail and bisect points to multiple interacting causes.

## Escalation Chain

```
Agent encounters problem
    ↓
Step 1: Architect Consultation (automatic, one attempt)
    ↓
    ├── Resolved → Agent continues with architect's guidance
    ↓
    └── Not resolved
            ↓
        Step 2: Human Escalation
            ↓
            Human decides next action
```

### Step 1: Architect Consultation

- **Who:** The architect agent.
- **How:** The blocked agent sends a structured request describing the problem, what was attempted, and why it failed.
- **Scope:** The architect provides advice only — it does not modify code or make implementation decisions.
- **Limit:** One automatic consultation per issue. If the architect's guidance does not resolve the problem, proceed to Step 2.

**Architect request format:**
```
Problem: [What went wrong]
Attempted: [What the agent tried]
Failed because: [Why it did not work]
Question: [Specific question for the architect]
```

### Step 2: Human Escalation

- **Who:** A human operator.
- **How:** A notification is sent with the full context (original task, agent's work, architect's advice, and why it was insufficient).
- **Outcome:** The human may revise the specification, modify the task, provide direct guidance, or decide to defer the work.

## Rules

1. **Maximum one automatic retry** — do not loop. If the architect's advice does not work, escalate immediately to human.
2. **Always include context** — every escalation must carry the full chain of what was attempted. The receiving party should never need to ask "what did you try?"
3. **Do not skip steps** — always consult the architect before escalating to human, unless the architect agent is the one that is stuck.
4. **No silent failures** — if an agent is stuck, it must escalate. Doing nothing is not acceptable.
