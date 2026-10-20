# New System Overview

Create the S-000 system overview spec with `ai-team spec new --overview --json`, then fill its seven sections by interviewing the human. S-000 says what the project is, who it serves, and which components make it up. It is written in plain language for a reader who has never seen the project.

The section contract is owned by `guides/spec-authoring-guide.md` (section "The system overview spec (S-000)"). Read it before drafting and follow it; do not restate it here.

## Input Requirements

- `project name` — optional; use `$ARGUMENTS` when it is the only input, otherwise ask the human.
- Whether the project already has specs, ADRs, docs, or code. If it does, follow **Brownfield adoption** (below) for step 4.

## Procedure

1. Check whether an S-000 already exists: run `ai-team list specs`.
   If S-000 is listed, stop. Tell the human it exists and offer to amend it instead; do not create a second overview.

2. Open the planning branch.
   Follow **Opening a Planning Branch** in the `git-conventions` skill, running the command in step 3 as its allocation step.

3. Run `ai-team spec new --overview --json` and parse the response for `id` (S-000) and `path`.

4. Fill the seven sections in the order the content contract gives: Purpose, Users, Pain points, Use cases, Solution overview, Components, Project exclusions.
   Interview the human for:
   - the purpose of the project and the outcome it delivers;
   - who the users are and what each needs;
   - the concrete pain points those users have today;
   - the main use cases, each as one short scenario from the user's point of view;
   - the split into components, with each component's responsibility, boundary, and collaborators.
   Write the Solution overview and Project exclusions from those answers, asking the human to confirm the exclusions. Leave anything still unanswered marked `[TODO]`.

5. Run the **pre-submission checklist** (below). Fix every unchecked item.

6. Inspect the draft for human-answerable `[TODO]` markers. If any remain, report the blocker and stop instead of handing the draft on.

7. Commit the draft on the planning branch (`docs(specs): add S-000 draft`). Commit every later revision on the same branch, never on `{{integration_branch}}`.

8. Hand the draft to the Architect for an Architecture Consistency Review (Next Owner: Architect). The Architect checks it against existing approved specs and accepted ADRs and returns findings without amending the draft. Revise on those findings until the Architect and Planner agree it is consistent.

9. Present the revised draft to the human for Gate 1 approval. S-000 is not approved until the human says so.

## Pre-submission checklist

- [ ] **Plain language.** A reader who has never seen the project can follow it.
- [ ] **No technology or interfaces.** No technology choices, interface definitions, configuration, implementation order, or per-component status.
- [ ] **Every use case is tied to a pain point.** Each use case removes at least one named pain point.
- [ ] **Every component has a boundary and a responsibility.** Each states what it is for, what it is not responsible for, and which components it works with.
- [ ] **All seven sections are present, in order.**
- [ ] **No `[TODO]` markers remain** that the human can answer.

## Brownfield adoption

Use this path when the project already has specs, ADRs, docs, or code. The goal is to unify the project towards the ai-team process without rewriting what is already approved.

1. Read the approved specs, accepted ADRs, and project docs first.
2. Inspect the code only to learn what exists: which components are present and what each does. Do not infer requirements from implementation details.
3. Draft S-000 in plain language through the same procedure above (steps 1 to 6), using what you learned to prefill the interview and asking the human to confirm or correct it.
4. Compare the draft with the existing specs and ADRs. Report every overlap, gap, and disagreement as a finding in your handoff, naming the spec or ADR concerned. Examples: two specs covering one component, a component with no spec, a spec whose scope contradicts the component split.
5. Never amend an approved spec yourself to resolve a finding. Amending an approved spec is a separate change that goes through its own Gate 1 approval; the human decides which side of each disagreement changes.
6. Go through the same Architect review and human Gate 1 as a greenfield S-000 (steps 8 and 9).
