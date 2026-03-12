---
name: brainstorm
description: Explore solution space for a feature request or problem. Use when a new feature needs a design before implementation, or when an existing approach was rejected and alternatives need exploration.
allowed-tools: Read, Grep, Glob, Write
---

# Brainstorm

## Input Requirements

- **Feature request or problem description** — what needs to be solved and why.
- **Existing specifications and decisions** — context from `project/specifications/` and `project/decisions/` to avoid contradictions.
- **Constraints** — any technical, time, or scope constraints stated by the human.

## Procedure

### Step 1: Understand the Problem
Read the feature request thoroughly.
Identify the core problem (what is broken or missing) vs. the surface request (what was asked for).
List any assumptions that need validation.

### Step 2: Explore the Solution Space
Generate at least two distinct approaches to solving the problem.
For each approach, describe:
- How it works at a high level.
- What components or changes are needed.
- Key trade-offs (complexity, performance, maintainability).

Do not self-censor during this step. Include approaches that seem impractical — they may contain useful ideas.

### Step 3: Evaluate Trade-offs
Compare the approaches against the stated constraints.
Identify which approach best balances the trade-offs.
Document why the rejected approaches were not chosen.

### Step 4: Produce the Design Document
Write a specification following `.claude/skills/new-spec/assets/TEMPLATE-specification.md`.
Include the recommended approach, the alternatives considered, and the rationale.
Clearly state what is excluded from scope.

## Output Format

- A specification document in `project/specifications/` following the template.
- The document is ready for human review at Gate 1 (Spec Approval).

## Quality Criteria

- At least two alternatives were genuinely considered (not strawmen).
- The recommended approach has a clear rationale tied to the stated constraints.
- Exclusions are explicit — the reader knows what this spec does NOT cover.
- The document is self-contained (readable without opening other files).

## Common Pitfalls

- **Anchoring on the first idea** — force yourself to generate at least one meaningfully different alternative before committing.
- **Solving the wrong problem** — re-read the feature request after generating alternatives to verify you are addressing the actual need.
- **Scope creep** — if an alternative requires significantly more work than the others, flag it as a future roadmap item rather than including it in the current spec.
- **Missing constraints** — check existing decision records in `project/decisions/` before proposing something that contradicts a prior decision.
