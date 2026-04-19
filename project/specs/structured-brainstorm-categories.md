---
title: "Structured Brainstorm Question Categories"
version: "0.1"
status: approved
created: 2026-04-18
author: "planner"
---

# Structured Brainstorm Question Categories

## Purpose

The brainstorm skill currently gives the Planner generic guidance during Step 2: "ask about ambiguities, scope boundaries, constraints, priority trade-offs."
Without a structure, agents ask about what comes to mind and routinely skip whole problem areas — most often edge cases, rollback strategy, and prior decisions.
The state-of-the-art research (Section 1.3 of `state-of-the-art-research.md`) reports practitioners who adopted a structured interview surfaced 40+ requirements they would not have captured upfront.

This specification restructures Step 2 around six named categories, with the Exclusions item highlighted as the prominent item inside the first category.
The Planner must cover all six categories materially; the five-question recommendation per round stays but is no longer a hard cap.
Categories are internal scaffolding — the Planner uses them to plan its questions, but does not label questions with category tags in the output.

## Exclusions

- **Labelled questions** — categories are internal scaffolding; questions are plain prose, not prefixed with `[Category]` tags.
- **Seven peer categories with Exclusions as its own top-level category** — Exclusions remains prominent inside Scope & Requirements rather than being elevated to a peer category. Rationale: preserves the research taxonomy and avoids duplicating the effect of spec 8.3, which already elevated the exclusion question standalone within Step 2.
- **Grouping example questions by category** — the example pool is flat. A question may draw on more than one category, so fixing it to one would be misleading.
- **Hard five-question cap** — demoted to a recommendation. If five cannot cover all categories materially, the Planner asks more in a second round.
- **Changes to Step 6 (confirmation)** — spec 8.3 already scheduled the exclusions-line requirement for Step 6. This spec preserves that and does not add further Step 6 changes.
- **Changes outside `brainstorm/SKILL.md`** — no edits to the spec template, task template, agent files, or other skills. The restructure is scoped to Step 2 of one file.
- **Retrofitting existing brainstorm transcripts or specs** — only brainstorms initiated after the change lands operate under the new Step 2.
- **Updating the plan's Phase 4 dry-run check wording** (the plan says "seven categories"; the reality is six with Exclusions inside Scope). This will be reconciled during Phase 5 rollout, not here.

## Architecture

### Design Principles

- **Internal scaffolding, external simplicity** — the Planner holds six categories in mind; the human sees plain questions.
- **Coverage beats count** — recommended five questions per round, but coverage of all six categories is the binding constraint, not the count.
- **Silent skip** — if a category has no material unknown, the Planner does not ask a filler question. Silent skip is acceptable.
- **Examples as a pool, not a matrix** — the skill file includes a flat bank of example questions. They are inspiration, not a 1:1 mapping to categories.
- **Compose with spec 8.3** — the Exclusions question 8.3 schedules for Step 2 survives as the prominent item inside the Scope & Requirements category.

### System Diagram

```
Planner enters /brainstorm Step 2
  │
  ├─ Internal scan: six categories
  │     1. Scope & Requirements  (includes the Exclusions question from 8.3)
  │     2. Technical Constraints
  │     3. Users & Surfaces
  │     4. Edge Cases & Error Handling
  │     5. Prior Decisions
  │     6. Verification
  │
  ├─ Draft questions (recommended ≤5; more if needed)
  │     drawn from / inspired by the inline example pool
  │     plain prose, no category labels
  │
  └─ Ask human → stop → receive answers → if any category
        has unresolved material unknowns, run another round
```

### Responsibility Separation

| Component | Responsibility | Notes |
|---|---|---|
| `brainstorm/SKILL.md` Step 2 — category list | Name the six categories with one-line purpose each | Exclusions is the first prominent sub-item inside Scope & Requirements |
| `brainstorm/SKILL.md` Step 2 — example question pool | Flat bank of ~12–15 illustrative questions | Drawn from research Section 1.3; not grouped by category |
| `brainstorm/SKILL.md` Step 2 — rules block | Recommended question count, coverage rule, silent-skip rule, multi-round permission | Replaces current "Ask about / Do not ask about" bullet lists |

## Components

### Component 1: Category list in Step 2

**Purpose:** Replace the current "Ask about: …" bullet list with a named-category block.
Each category gets one line: category name plus a one-line purpose statement.
Scope & Requirements explicitly calls out the Exclusions question from spec 8.3 as its prominent item.
**Estimated size:** S (approximately 15 line-diff, additive).
**Interfaces:** Consumed by the Planner when drafting Step 2 questions.

### Component 2: Example question pool in Step 2

**Purpose:** Embed a flat list of ~12–15 example questions, drawn from research Section 1.3, as inspiration for the Planner.
Questions are generic and may span categories — they are not grouped or labelled.
**Estimated size:** S (approximately 20 line-diff, additive).
**Interfaces:** Read by the Planner as reference; not a required script.

### Component 3: Rules block in Step 2

**Purpose:** Replace the old "Do not ask about: … more than five questions" paragraph with three new rules:
(1) recommended ≤5 questions per round, not a hard cap;
(2) coverage of all six categories is required — if five cannot cover them, ask more in a follow-up round;
(3) silent skip is acceptable when a category has no material unknown.
**Estimated size:** S (approximately 10 line-diff, net neutral after removing the old paragraph).
**Interfaces:** Governs the Planner's question budget and round behaviour.

## Workflow

```
Planner reaches /brainstorm Step 2
  ↓
Step 2.1: internally scan the six categories against the request
  ↓
Step 2.2: draft questions — aim ≤5; if coverage requires more, plan a second round
  ↓
Step 2.3: phrase questions as plain prose (no [Category] labels)
  ↓
Step 2.4: ask the human → stop → receive answers
  ↓
Step 2.5: if any material unknown remains uncovered, run a second round (same rules)
  ↓
proceed to Step 3 (solution exploration) only once all six categories are materially covered
```

## Configuration

Not applicable — this is a skill-content change with no runtime configuration.

## Implementation Order

| Phase | What | Depends On |
|---|---|---|
| 1 | Compose the new Step 2 content (category list + example pool + rules block) into a single patch | Spec 8.3 implementation merged, so the Exclusions question already exists in Step 2 and can be preserved |
| 2 | Apply the patch to `.claude/skills/brainstorm/SKILL.md` Step 2 | Phase 1 |
| 3 | Cross-check `.claude/agents/planner.md` for references to Step 2 content that might drift | Phase 2 |

Spec 8.3 should be fully landed before this spec is implemented. Both specs touch Step 2, and 8.3's standalone exclusions question is a precondition for this spec's "Exclusions prominent inside Scope & Requirements" design. Task dependencies in Phase 2 should reflect this.

## Alternatives Considered

- **Approach B: Categories with minimal (~5–6) examples.** Rejected: user explicitly asked to embed example questions, and a richer bank (~12–15) makes the skill self-contained so the Planner does not need to open the research doc during a brainstorm.
- **Seven peer categories, with Exclusions elevated.** Rejected: would duplicate work done by spec 8.3 (which already elevates the Exclusions question inside Step 2) and would break from the research taxonomy. Prominence inside Scope & Requirements achieves the visibility goal without restructuring the category set.
- **Raise the five-question maximum to seven to match category count.** Rejected: the original five-question ceiling came from practitioner research on adherence; coverage, not count, is the binding constraint. Demoted to a recommendation instead.
- **Grouping example questions by category inside the skill.** Rejected: a question often draws on more than one category (e.g. "what happens when this fails in production?" touches Edge Cases and Users). Fixing it to one would mislead the Planner.
- **Tagged output (`[Category]` prefixes).** Rejected: brainstorms should read naturally to the human; tags are internal-only.
- **Full Section 1.3 verbatim embed.** Rejected: the research section's per-category grouping conflicts with the chosen flat-pool structure.

## Amendment Log

<!-- Left empty for now. Populate if amended after tasks are in flight.
| Date | What changed | Why | Affected tasks |
|------|-------------|-----|----------------|
-->
