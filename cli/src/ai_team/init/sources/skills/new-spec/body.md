# New Spec

Create a new specification document using `ai-team spec new --json`, then fill its body following the section-by-section recipes below.

## Input Requirements

Provide these values directly when possible:
- `title` — required
- `description` — required (free-form prose: problem, approach, exclusions, constraints; used to fill body sections in step 4 — NOT passed to the CLI)
- `author` — optional; defaults to `AI Agent`
- `status` — optional; defaults to `draft`

When invoked by another skill, the caller should provide every required field in the invocation text and this skill must use them without asking follow-up questions.
When invoked directly by a human and required fields are missing, ask only for the missing fields before proceeding.

## Procedure

1. Resolve inputs:
   - Use the caller-provided `title`, `description`, `author`, and `status` when they are present.
   - If invoked directly and some required fields are missing, ask only for the missing fields.
   - Use `$ARGUMENTS` as the title when it is the only provided input.

2. Build the CLI command:
   - Base: `ai-team spec new "<title>" --json`
   - Add `--author "<author>"` only when `author` is provided; otherwise allow the CLI default.
   - Add `--status "<status>"` only when `status` is provided; otherwise allow the CLI default.
   - Do NOT pass `description` to the CLI — the CLI has no `--description` flag.

3. Execute the command and parse the JSON response to capture:
   - `id` (for example, `S-003`)
   - `path` (absolute path to the created file, named `S-NNN-<slug>.md`)

4. Open the created spec file and fill its body sections from the supplied `description`, using the **content-boundary rule** and the **section recipes** below. Leave any section that still needs exploration marked `[TODO]`.

5. Run the **pre-submission checklist** (below) against the filled spec. Fix any unchecked item before returning. Leave items genuinely unresolvable marked `[TODO]` so the human sees them at Gate 1.

6. Confirm the created file exists and return the CLI response values (`id` and `path`).

7. Remind that the new spec requires human Gate 1 approval unless the caller explicitly says it is already being prepared for that gate.
8. Hand the draft spec to the Architect for an Architecture Consistency Review before Gate 1 (Next Owner: Architect). The Architect checks it against existing approved specs and accepted ADRs and returns findings — like a Gate 2 review, this does not amend the draft. Revise the draft on those findings until the Architect and Planner agree it is consistent; the human then approves at Gate 1 as usual.

---

## Content-boundary rule (strict)

A specification describes **requirements, contracts, and measurable criteria in prose**. It does NOT embed:
- Implementation code (function signatures, class layouts, executable snippets that *are* the implementation).
- Full configuration files, CI manifests, or build files.
- File-by-file plans — those are the `spec-breakdown` skill's output.

Concrete code, config, and manifests belong in the **tasks** that `spec-breakdown` produces and in the **Developer's output**, not in the spec body.

**Rare exception:** a code or config block is acceptable when the block *is itself the contract* — a public API schema, a wire-protocol fragment, an externally-fixed configuration key. Mark such blocks **Contract**, not **Example**. If in doubt, use prose.

If you find yourself pasting a near-complete file into the spec, you are writing the implementation — replace it with prose that describes what the file must guarantee.

---

## Section recipes

Use these recipes to fill each section of `cli/src/ai_team/templates/spec.md`.

### Purpose

Three to four sentences:
1. The problem (what is broken or missing today).
2. Why it matters now (the constraint or trigger that forced the spec).
3. The outcome (what is observably true when the work is done).
4. Optional: the metric that confirms success.

Avoid restating the title. Always name the *why*.

### Exclusions

For every alternative rejected during brainstorm, and every scope-expanding question the human said "no" to, write an explicit exclusion with the reason.

Almost every spec has at least one. `"no exclusions apply"` should be rare and should follow an explicit human confirmation.

### Architecture — Design Principles

Each principle is a **constraint on the design space**, not an implementation choice. State it as a property the design must satisfy.

Good: "Validation must run in under three minutes on the median PR."
Bad: "Use GitHub Actions." (That picks the implementation; reframe as a constraint, e.g. "must integrate with the project's existing PR review surface.")

### Architecture — System Diagram

ASCII boxes and arrows, one screen wide, components labelled. Show data flow, not the call graph. Class diagrams of internal classes do not belong here.

### Architecture — Responsibility Separation

A table. One row per component. Columns: component, responsibility, interface notes (what it exposes and consumes). Stay at the interface level — no method signatures or attribute lists.

### Components

One short block per component, three lines max:
- **Purpose:** one sentence — what it does.
- **Estimated size:** small / medium / large, or rough effort.
- **Interfaces:** exposed and consumed, named at the interface level.

No function lists. No field lists.

### Workflow

End-to-end flow from trigger to completion. Each step is a sentence or short phrase. Mark human gates with `★`. Include error paths only when a failure mode is interesting.

### Configuration Requirements

For each setting, four bullets:
- **What must exist** — the requirement, named.
- **Where it lives** — env var, config file, CI variable, secret store — described, not pasted.
- **Constraints** — allowed range, format, security class.
- **Missing-value behaviour** — default, error, or refuse-to-start.

Do not paste a real configuration file. The Developer writes the file against project conventions; this section tells them what the file must guarantee.

### Implementation Order

Coarse phases (typically two to five). Each phase delivers an observable outcome. State each phase's dependency on the previous ones. A phase is NOT a task — `spec-breakdown` produces the actual tasks from these phases.

### Amendment Log

Leave empty when the spec is first written. Add rows only after Gate 1 approval when scope changes while tasks are in flight.

---

## Measurable success criteria

A criterion is **measurable** when an outside party can run a check (command, observation, metric query) and get an unambiguous pass/fail.

Good: "Every PR targeting `main` shows a `ci/tests` check that has passed or failed within five minutes of opening."
Vague (avoid): "The CI is fast." "The CI works well." "Coverage is high."

If you cannot describe how to verify a criterion, it is not yet measurable — rewrite it.

---

## Pre-submission checklist

Before returning the created spec, confirm every item:

- [ ] **Problem is concrete.** Purpose names the problem, the trigger, and the observable outcome.
- [ ] **At least one exclusion.** Or a human-confirmed "no exclusions apply" statement.
- [ ] **Each design principle is a constraint, not an implementation choice.**
- [ ] **No implementation artefacts.** No full config files, no CI manifests, no function-by-function decompositions. Any literal-value-as-contract block is labelled **Contract**.
- [ ] **Every requirement is measurable.** An outside reader can describe how to verify it.
- [ ] **Components are described at the interface level.** No method signatures, no attribute lists.
- [ ] **Implementation Order has coarse phases**, not tasks.
- [ ] **Amendment Log is empty** (until amendments arrive after Gate 1).

Items genuinely unresolvable at write-time may be left `[TODO]` for the human to address at Gate 1. Everything else must be checked before returning.
