---
title: "EARS Acceptance Criteria in Task Template"
version: "0.1"
status: approved
created: 2026-04-18
author: "planner"
---

# EARS Acceptance Criteria in Task Template

## Purpose

Free-form acceptance criteria like "the login should work" are ambiguous.
The Planner, the implementer, and the reviewer each interpret them, and the interpretations routinely diverge.
The state-of-the-art research (Section 8.1 of `state-of-the-art-research.md`) identifies EARS — Easy Approach to Requirements Syntax, Rolls-Royce 2009, adopted by Amazon Kiro — as the industry standard for AI-readable acceptance criteria.
EARS criteria are **independently testable by construction**: the agent can self-verify, and the reviewer can objectively pass or fail each one.

Today the task template uses a checkbox bullet list with generic guidance ("specific, measurable outcome") and `write-plan/SKILL.md` Step 3 offers no notation discipline at all.
This specification replaces both with strict EARS: every acceptance criterion in every task must match one of the five EARS patterns, and the template itself carries the pattern reference so it sits next to the thing it governs.

## Exclusions

- **Plain-English fallback.** Every criterion must fit one of the five EARS patterns. No escape hatch for edge cases in this version; if strict EARS creates awkward phrasings in practice, a follow-up spec will relax the rule.
- **Changes to `ai-process/guidelines/review-checklist.md`.** Process information stays in templates and skills; the checklist remains a downstream reader. Reviewer continues to evaluate "all acceptance criteria met" against whatever format the task file presents.
- **Migration of existing tasks.** Tasks currently in `project/tasks/pending/`, `in-progress/`, `blocked/`, or `completed/` keep their current format. Only tasks authored after the change lands go through the updated template.
- **Automated EARS conformance validation.** There is no linter or parser that checks an AC actually matches one of the five patterns. Conformance relies on Planner discipline, reviewer eyes, and the pattern reference embedded in the template.
- **Keeping the `- [ ]` checkbox format.** The AC list becomes a numbered list (`AC-1`, `AC-2`, ...). Reviewer tooling expectations change.
- **Duplicating the EARS pattern reference in the skill.** The template is the single source of truth for the pattern reference; the skill links to it.
- **Changes to the reviewer or implementer agent definitions.** Both agents already read the task file for acceptance criteria; the format change is transparent to them once the template is updated.
- **Task-level out-of-scope or verification-example fields.** Research items 8.6 and 8.4 — deferred from this pass.

## Architecture

### Design Principles

- **Strict EARS.** Every acceptance criterion must match one of the five EARS patterns. Awkward phrasing is a signal that the task has not been decomposed atomically enough.
- **Template as reference.** The pattern reference lives in the template's Acceptance Criteria section, where Planner, implementer, and reviewer all encounter it in the course of their normal work.
- **Skill as authoring guide.** `write-plan/SKILL.md` Step 3 instructs *how* to author EARS criteria; the template shows *what* the five patterns look like.
- **Numbered criteria, not checkboxes.** `AC-1`, `AC-2`, …, so reviewer verdicts can reference specific criteria unambiguously (`AC-3 failed`).
- **Co-located pattern reference and authoring rule.** The skill links to the template — there is no duplicated pattern list to drift out of sync.

### System Diagram

```
/write-plan Step 3
  │  "Author each AC using one EARS pattern;
  │   see TEMPLATE-task.md for the pattern reference"
  ↓
TEMPLATE-task.md  (source of truth for EARS patterns)
  │
  │  ## Acceptance Criteria
  │  <!-- EARS pattern reference
  │       1. Ubiquitous:        The system shall X
  │       2. Event-driven:      WHEN E THE SYSTEM SHALL X
  │       3. Unwanted-behaviour: IF F THEN THE SYSTEM SHALL X
  │       4. State-driven:      WHILE S THE SYSTEM SHALL X
  │       5. Optional:          WHERE feature THE SYSTEM SHALL X
  │  -->
  │  AC-1: ...
  │  AC-2: ...
  ↓
Implementer reads task → knows what to build and verify
Reviewer reads task → Gate 2 Stage 1 check per AC-N
```

### Responsibility Separation

| Component | Responsibility | Notes |
|---|---|---|
| `TEMPLATE-task.md` Acceptance Criteria section | Numbered `AC-N` list; embedded EARS pattern reference with one example per pattern | Sole source of truth for the EARS patterns within the process |
| `write-plan/SKILL.md` Step 3 | Instruct the Planner to author every AC using one of the five patterns; point at the template for reference | Also updates the skill's Quality Criteria and Common Pitfalls to reflect EARS |
| Implementer / Reviewer | Consume the numbered ACs from the task file as-is | No agent-definition changes needed; the format change is transparent |

## Components

### Component 1: Task template — Acceptance Criteria restructure

**Purpose:** Replace the checkbox bullet list with a numbered `AC-N` list; embed the EARS pattern reference as a template comment inside the section.
**Estimated size:** S (approximately 25 line-diff, one file).
**Interfaces:** Consumed by `/new-task`, by the Planner running `/write-plan`, by implementer and reviewer during task execution.

Section shape after the change:

```markdown
## Acceptance Criteria

<!-- EARS pattern reference. Every criterion must match one pattern:
  1. Ubiquitous            — The system shall [outcome]
  2. Event-driven          — WHEN [trigger] THE SYSTEM SHALL [outcome]
  3. Unwanted-behaviour    — IF [fault] THEN THE SYSTEM SHALL [outcome]
  4. State-driven          — WHILE [state] THE SYSTEM SHALL [outcome]
  5. Optional              — WHERE [feature included] THE SYSTEM SHALL [outcome]

Examples:
  AC-1: WHEN the user submits valid credentials THE SYSTEM SHALL
        redirect to /dashboard within 200ms.
  AC-2: IF the password is incorrect THEN THE SYSTEM SHALL return 401
        and display "Invalid credentials".
  AC-3: The system shall log every authentication attempt with user id
        and outcome.
-->

AC-1: ...
AC-2: ...
AC-3: ...
```

### Component 2: Write-plan skill — Step 3 authoring rule

**Purpose:** Replace the current "Acceptance criteria: Specific, measurable, checkable outcomes" guidance with an explicit EARS instruction.
Update the skill's Quality Criteria section to add "Every AC uses one of the five EARS patterns".
Update the Common Pitfalls section to replace "Vague acceptance criteria" with "Criteria that do not match an EARS pattern — if a criterion resists EARS, the task is probably not atomic".
**Estimated size:** S (approximately 15 line-diff, one file).
**Interfaces:** Read by the Planner when decomposing an approved spec.

## Workflow

```
Approved spec lands
  ↓
Planner runs /write-plan
  ↓
Step 3 — Write Task Files
  │  Planner opens TEMPLATE-task.md for reference
  │  Planner authors ACs using EARS patterns:
  │   - Event-driven for triggered behaviour
  │   - IF/THEN for error handling
  │   - Ubiquitous for invariants
  ↓
Task file saved with AC-1, AC-2, ... in EARS form
  ↓
/dev-loop picks up task
  ↓
Implementer reads EARS ACs → writes tests that match → implements
  ↓
Reviewer Gate 2 Stage 1 → ticks each AC-N independently
```

## Configuration

Not applicable — this is a documentation/process change with no runtime configuration.

## Implementation Order

| Phase | What | Depends On |
|---|---|---|
| 1 | Update `.claude/skills/new-task/assets/TEMPLATE-task.md` — restructure Acceptance Criteria section with numbered format and embedded EARS pattern reference | Nothing |
| 2 | Update `.claude/skills/write-plan/SKILL.md` — Step 3 authoring rule, Quality Criteria addition, Common Pitfalls replacement | Phase 1 (skill points at template) |

Phase 2 has a soft dependency on Phase 1: the skill links to the template, so the template section must exist in its new form before the skill references it. The files can still be edited in parallel if both tasks are assembled as one patch and reviewed together.

## Alternatives Considered

- **Approach B: Skill-centric pattern reference.** Pattern reference lives in `write-plan/SKILL.md` Step 3; template has a minimal AC section with a pointer to the skill. Rejected: the template is what implementer and reviewer read during task execution; keeping the pattern reference in the template avoids a hop to the skill file during Stage 1 review.
- **Approach C: Duplicated compact reference in both files.** Rejected: two copies drift over time, and there is no enforcement mechanism to keep them in sync.
- **Plain-English fallback with justification.** Rejected by explicit user decision: strict EARS. The user's view is that awkward phrasing is a signal the task is not atomic enough, not a signal EARS is too rigid.
- **Subset of EARS patterns (only Event-driven + Unwanted-behaviour).** Rejected: State-driven and Optional are rare but exist in legitimate cases (long-running state, feature flags); embedding all five up front is cheap.
- **Keeping the `- [ ]` checkbox format alongside EARS.** Rejected by explicit user decision: numbered `AC-N` lets reviewer verdicts reference specific criteria unambiguously.
- **Expanding scope to also update `review-checklist.md`.** Rejected by explicit user principle: process information stays in templates and skills. The checklist remains a downstream reader.

## Amendment Log

<!-- Left empty for now. Populate if amended after tasks are in flight.
| Date | What changed | Why | Affected tasks |
|------|-------------|-----|----------------|
-->
