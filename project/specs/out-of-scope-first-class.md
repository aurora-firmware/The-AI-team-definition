---
title: "Out-of-Scope as a First-Class Section"
version: "0.1"
status: approved
created: 2026-04-18
author: "planner"
---

# Out-of-Scope as a First-Class Section

## Purpose

Agents fill spec gaps with plausible assumptions.
An agent implementing authentication will add OAuth because most apps have OAuth, unless the spec explicitly says otherwise.
The state-of-the-art research (Section 8.3 of `state-of-the-art-research.md`) identifies explicit exclusions as one of the highest-leverage defences against scope expansion and gold-plating.

Today the spec template has an `Exclusions` section but buries it at position 7 of 9 — after Architecture, Components, Workflow, Configuration, and Implementation Order.
The brainstorm skill treats exclusions as one bullet in Step 2's "ask about" list and one summary line in Step 6.
Neither makes exclusions feel mandatory.

This specification promotes exclusions to a prominent early section in the spec template, deletes the overlapping `Future Roadmap` section, and tightens the brainstorm flow so exclusions are actively elicited during Step 2 and reaffirmed during Step 6.
Enforcement is **soft**: the brainstorm asks, the template requires, the reviewer flags absence — but Gate 1 does not auto-reject a spec that has no exclusions worth listing.

## Exclusions

- **Task-level out-of-scope fields.** The task template does not gain an `Out of Scope` field — that is research item 8.6, deferred from this pass.
- **Verification Examples / inline test cases.** Research item 8.4, deferred from this pass.
- **Hard Gate 1 rejection for specs without exclusions.** Soft enforcement only — reviewer flags absence, human decides at Gate 1.
- **Minimum count of exclusions per spec.** No prescribed minimum; the template implies the shape but does not require a specific quantity.
- **Categorisation of exclusions by type.** Free-form bullets are acceptable; no mandatory taxonomy (features / users / environments / adjacent systems).
- **New "Scope" wrapper section** that combines In-Scope and Out-of-Scope into one. Purpose and Exclusions remain two distinct sections.
- **Migration of existing specs in `project/specs/`.** Only new specs go through the updated template. Existing drafts and approved specs keep their current ordering until they are superseded or amended for unrelated reasons.
- **Changes to `new-spec/SKILL.md`.** The skill itself already reads the template; no logic changes are needed beyond the template it reads.

## Architecture

### Design Principles

- **Soft enforcement** — template formatting plus skill prompts, not a hard Gate 1 block.
- **Reasons required per exclusion** — the template example uses `- **title** Body.` format (bold short title, period, prose body); bare bullet lists are discouraged.
- **No minimum count** — if a feature genuinely has no material exclusions, an explicit "no exclusions apply" confirmation from the human is acceptable.
- **Minimum structural change** — move one section, delete one section, add two focused prompts; do not reorganise the template beyond that.

### System Diagram

```
/brainstorm
  ├─ Step 2: explicit "What is explicitly NOT included?" question
  └─ Step 6: confirmation summary includes exclusions line
        ↓
/new-spec
  └─ reads TEMPLATE-specification.md
        ├─ position 1: Purpose
        ├─ position 2: Exclusions   ← promoted from position 7
        ├─ position 3: Architecture
        └─ ...rest of template...
        ↓
Gate 1 review (human)
  └─ review-checklist: soft flag if Exclusions empty
```

### Responsibility Separation

| Component | Responsibility | Notes |
|---|---|---|
| `TEMPLATE-specification.md` | Document structure for specs | Exclusions moved to position 2; Future Roadmap deleted; Exclusions section requires reason per bullet |
| `brainstorm/SKILL.md` | Interactive design dialogue | Step 2 asks an explicit exclusions question; Step 6 confirmation summary must include an exclusions line |
| `review-checklist.md` | Reviewer Stage 1 quality checks | Soft flag when Exclusions section is absent or empty |

## Components

### Component 1: Spec template update

**Purpose:** Move the Exclusions section to position 2 (directly after Purpose), delete the Future Roadmap section, and tighten the section's template wording so each listed exclusion uses the `- **title** Body.` format (bold short title, period, prose body stating the reason).
**Estimated size:** S (approximately 15 line-diff across one file).
**Interfaces:** Consumed by `/new-spec` when creating a spec; referenced by `brainstorm/SKILL.md` Step 7 when producing the document.

### Component 2: Brainstorm skill update

**Purpose:** Elicit exclusions explicitly during the clarification round and reaffirm them during the confirmation round.
Update Step 2 so "What is explicitly NOT included in this feature?" is a named, standalone question rather than a sub-bullet in an "ask about" list. Update Step 6 so the confirmation summary must include an exclusions line — either one or more concrete exclusions, or an explicit "no exclusions apply" statement.
**Estimated size:** S (approximately 10 line-diff across one file).
**Interfaces:** Invoked by the `/brainstorm` command; Step 7 writes the spec using the template updated in Component 1.

### Component 3: Review checklist update

**Purpose:** Reviewer soft-flag when a spec's Exclusions section is absent or empty.
Add one line to the Stage 1 checklist in `review-checklist.md`: "Exclusions section is present and contains at least the human-confirmed answer (either concrete exclusions or an explicit 'no exclusions apply')."
**Estimated size:** XS (approximately 2 line-diff across one file).
**Interfaces:** Referenced by the code-review skill's Stage 1 review and by the human at Gate 1.

## Workflow

```
Planner starts /brainstorm for a new feature
  ↓
Step 2 clarification round — explicit "What is out of scope?" question
  ↓ (human answers — concrete exclusions or "none apply")
Step 3–5 — solution exploration and direction-setting
  ↓
Step 6 confirmation — summary includes exclusions line
  ↓ (human confirms)
Step 7 — spec written using updated template; Exclusions section populated in position 2
  ↓
Gate 1 — human reviews; reviewer flags if Exclusions empty
```

## Configuration

Not applicable — this is a documentation/process change with no runtime configuration.

## Implementation Order

All three components are independent file edits — no internal ordering is required.
Listed in reading order, not dependency order.

| Phase | What | Depends On |
|---|---|---|
| 1 | Update `.claude/skills/new-spec/assets/TEMPLATE-specification.md` (promote Exclusions, delete Future Roadmap, tighten section format) | Nothing |
| 2 | Update `.claude/skills/brainstorm/SKILL.md` (explicit Step 2 question, Step 6 exclusions line) | Nothing |
| 3 | Update `ai-process/guidelines/review-checklist.md` (Stage 1 soft flag for missing Exclusions) | Nothing |

## Alternatives Considered

- **Approach B: Dedicated brainstorm sub-step.** Add a new Step 2.5 "Scope Boundaries" dedicated entirely to exclusions. Rejected: overkill for simple features; lengthens the brainstorm flow where an inline question achieves the same result.
- **Approach C: Template-heavy enforcement.** Put most of the weight into a highly structured Exclusions section in the template and touch the brainstorm lightly. Rejected: the skill prompts are the stronger lever — an agent working fast will skim the template but will answer a direct question.
- **"Scope" wrapper section combining In-Scope and Out-of-Scope.** Rejected in favour of keeping Purpose and Exclusions as two prominent sequential sections at the top of the document.
- **Hard Gate 1 rejection for missing exclusions.** Rejected by explicit human decision during the brainstorm: risk of manufactured "fluffy" exclusions added purely to satisfy a gate.
- **Minimum count or categorisation of exclusions** (features / users / environments / adjacent systems). Rejected to keep the section lightweight.

## Amendment Log

<!-- Left empty for now. Populate if amended after tasks are in flight.
| Date | What changed | Why | Affected tasks |
|------|-------------|-----|----------------|
-->
