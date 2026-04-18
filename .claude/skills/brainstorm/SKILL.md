---
name: brainstorm
description: Explore solution space for a feature request or problem. Use when a new feature needs a design before implementation, or when an existing approach was rejected and alternatives need exploration.
allowed-tools: Read, Grep, Glob, Write
effort: high
---

# Brainstorm

Interactive design session between the human and the Planner.
The goal is to arrive at a well-understood, agreed direction *before* writing the specification — not to produce a document for the human to approve cold.

## Input Requirements

- **Feature request or problem description** — what needs to be solved and why.
- **Existing specifications and decisions** — context from `project/specs/` and `project/decisions/` to avoid contradictions.
- **Constraints** — any technical, time, or scope constraints stated by the human.

## Procedure

### Step 1: Understand the Request

Read the feature request thoroughly.
Separate what is known from what is unknown or ambiguous:
- **Known**: stated requirements, explicit constraints, referenced existing systems.
- **Unknown**: unstated priorities, scope boundaries, user-facing behaviour details, performance expectations, integration points not mentioned.

Read `project/specs/` and `project/decisions/` to surface any existing decisions that bear on this feature.

### Step 2: Clarification Round

Before exploring solutions, resolve the unknowns that would materially change the solution space.

Formulate focused questions — batch them all together, maximum five.
Ask the human and **stop**. Do not continue until answers are received.

Include this named prompt as a standalone question:
- **Explicit exclusions:** What is explicitly NOT included in this feature?

**Ask about:**
- Core requirements that are genuinely ambiguous (not inferable from context)
- Scope boundaries — what is explicitly out of scope?
- Constraints not yet stated (performance targets, backwards compatibility, rollout strategy)
- Priority trade-offs if requirements conflict

**Do not ask about:**
- Details that belong in the implementation phase (exact naming, file structure)
- Anything that can be reasonably inferred from the request or existing specs
- More than five questions in one round — prioritise the most impactful unknowns

If there are no material unknowns, skip this step and proceed.

### Step 3: Explore the Solution Space

With clarified requirements, generate at least two distinct approaches.
For each approach describe concisely (one short paragraph each):
- How it works at a high level
- What components or changes it requires
- Key trade-offs: complexity, flexibility, implementation effort, alignment with existing architecture

Do not self-censor. Include approaches that seem impractical — they may contain useful ideas or help the human articulate what they *don't* want.

Do not write a full spec at this stage. These are sketches, not blueprints.

### Step 4: Present Alternatives and Get Direction

Present the alternatives to the human in brief.
Ask the human to indicate their preferred direction — or to name any constraint that should decide it.

**Stop and wait for the human's response before continuing.**

If the human picks an approach with modifications, note the modifications.
If the human is undecided, ask one focused question to identify the deciding factor (e.g. "Is extensibility or simplicity the higher priority here?").

### Step 5: Refine (if needed)

If the chosen direction has remaining open questions about scope or behaviour — not about implementation — ask them now.
Maximum one follow-up round.

Skip this step if the direction is clear enough to write the spec.

### Step 6: Confirm the Approach

Before writing the full specification, state the chosen approach in two or three sentences:
- What it does
- What it does not do (explicit exclusions)
- Any constraints it assumes

Ask the human: "Does this match your intent? I'll write the spec based on this."

**Stop and wait for confirmation before proceeding to Step 7.**
If the human corrects something, update the summary and confirm again.

### Step 7: Produce the Specification

Write the specification following `${CLAUDE_SKILL_DIR}/../new-spec/assets/TEMPLATE-specification.md`.

Include:
- The confirmed approach
- Alternatives considered and why they were not chosen
- Explicit exclusions from scope
- Architecture described with enough detail for the Planner to derive tasks

Mark any remaining open details with `[TODO]`.
Update the spec `status` to `review`.

The document is ready for Gate 1 (Spec Approval).
Because the human shaped the spec interactively, Gate 1 should be a quick confirmation — not a cold review.

## Quality Criteria

- Every clarifying question was material — not asked out of habit.
- At least two alternatives were genuinely considered (not strawmen).
- The chosen approach has clear rationale tied to the human's stated priorities.
- Exclusions are explicit.
- The spec is self-contained: readable without opening other files.
- The human confirmed the direction before the spec was written.

## Common Pitfalls

- **Writing the spec before aligning** — producing a full document, then waiting for approval, is the old pattern. The goal is to arrive at the spec *together*.
- **Asking too many questions upfront** — five maximum. Prioritise. Unanswered low-priority questions can be `[TODO]` in the spec.
- **Anchoring on the first idea** — always generate at least one meaningfully different alternative before committing to a direction.
- **Solving the wrong problem** — re-read the original request after generating alternatives to verify you are addressing the actual need.
- **Scope creep** — if an alternative requires significantly more work, flag it as a future roadmap item rather than including it in the current spec.
- **Missing constraints** — check `project/decisions/` before proposing anything that contradicts a prior decision.
