---
name: brainstorm
description: Explore solution space for a feature request or problem. Use when a new feature needs a design before implementation, or when an existing approach was rejected and alternatives need exploration.
allowed-tools: Read, Grep, Glob, Write, Skill(new-spec)
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

Use these internal categories to plan coverage. Do not expose category names or `[Category]` labels in the questions you ask the human.

**Internal categories:**
- **Scope & Requirements** — clarify required outcomes, boundaries, and the prominent exclusions question: "What is explicitly NOT included in this feature?"
- **Technical Constraints** — identify constraints such as performance targets, backwards compatibility, integrations, rollout strategy, security, or operational limits.
- **Users & Surfaces** — clarify who is affected, which interfaces or workflows change, and what each user type must experience.
- **Edge Cases & Error Handling** — surface failure modes, unusual inputs, partial states, rollback needs, and expected handling.
- **Prior Decisions** — check existing specifications, decision records, and project conventions for constraints or contradictions.
- **Verification** — clarify how success will be observed, tested, reviewed, or accepted.

**Example question pool:**
- What outcome must this feature guarantee for the user?
- What is explicitly NOT included in this feature?
- Which existing behavior must remain unchanged?
- Are there performance, compatibility, rollout, or operational constraints I should account for?
- Which user types or workflows are affected first?
- Are there surfaces where this should not appear, even if they seem related?
- What should happen when the required data is missing, stale, or contradictory?
- What failure mode would be most damaging if we handled it poorly?
- Are there prior specs, decisions, or conventions this must follow?
- Has any approach already been rejected or ruled out?
- What would make the first version acceptable enough to ship?
- How should we verify that the change works as intended?
- What evidence should reviewers look for before approving the spec or implementation?
- If requirements conflict, which priority should decide the trade-off?

**Rules:**
- Aim for about five focused questions per round as a recommendation, not a hard cap.
- Coverage of all six internal categories is the binding constraint. If one round cannot cover the material unknowns clearly, ask another round before moving on.
- Silent skip is acceptable when a category has no material unknown for this request. Do not ask filler questions.
- Avoid details that belong in the implementation phase, such as exact naming or file structure, unless they materially change the solution space.
- Ask the human and **stop**. Do not continue until answers are received.

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
- An exclusions line with one or more concrete exclusions, or the exact statement "no exclusions apply" when the human confirms there are none
- Any constraints it assumes

Ask the human: "Does this match your intent? I'll write the spec based on this."

**Stop and wait for confirmation before proceeding to Step 7.**
If the human corrects something, update the summary and confirm again.

### Step 7: Produce the Specification

Invoke the `new-spec` skill to create the specification file. Provide the full required input set in the invocation text:
- `title`: the confirmed spec title
- `description`: a concise summary of the confirmed approach, exclusions, and constraints from Step 6
- `author`: `planner` unless the human provided a different author
- `status`: `draft`

The `new-spec` skill handles template loading, filename slugification, and frontmatter scaffolding. Because all required fields are provided here, it should not ask follow-up questions.

Once the file exists, fill it in with:
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

- **Writing the spec before aligning** — producing a full document, then waiting for approval. The goal is to arrive at the spec *together*.
- **Asking too many questions in one round** — aim for about five per round. If the six internal categories cannot be covered materially within that budget, run a second round rather than stretching a single round indefinitely.
- **Anchoring on the first idea** — always generate at least one meaningfully different alternative before committing to a direction.
- **Solving the wrong problem** — re-read the original request after generating alternatives to verify you are addressing the actual need.
- **Scope creep** — if an alternative requires significantly more work, record it as an explicit exclusion in the spec's Exclusions section rather than folding it into the current scope.
- **Missing constraints** — check `project/decisions/` before proposing anything that contradicts a prior decision.
