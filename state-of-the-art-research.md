---
title: "State of the Art: Spec-Driven Development with AI Agents"
status: reference
created: 2026-04-17
sources: 40+ (Anthropic docs, Amazon Kiro, GitHub spec-kit, arXiv papers, practitioner guides)
---

# State of the Art: Spec-Driven Development with AI Agents

Research synthesis covering best practices for planning, specification, human oversight, and failure prevention when using AI coding agents.
Synthesised from 40+ sources including Anthropic engineering, Amazon Kiro, GitHub spec-kit, arXiv papers, and practitioner guides (April 2026).

---

## The Universal Workflow Shape

Every serious tool and methodology converges on the same structure:

```
Interview → Specify → Plan → Decompose → Implement → Verify
```

The critical insight is that **Interview** precedes **Specify**.
The spec must be the *output* of a human-AI dialogue, not a document handed to the human for cold review.
Thoughtworks named spec-driven development one of the most important engineering practices of 2025.

---

## 1. The Planning Process

### 1.1 Interview-First Pattern (Anthropic's recommendation)

Before writing anything, the Planner should drive a structured interview with the human.
Practitioners who used this pattern reported Claude surfaced **40+ requirements they never would have documented upfront** — edge cases, rollback scenarios, concurrent access behaviour.

Recommended prompt structure:
```
I want to build [brief description]. Interview me with focused questions
before writing anything. Ask about: requirements, scope boundaries,
constraints, edge cases, and verification. Don't ask about implementation
details. Keep asking until the design is unambiguous, then confirm the
approach before writing the spec.
```

Start a *fresh session* to execute the spec — the brainstorm session context can introduce drift.

### 1.2 The 4Ws Problem Canvas

Use the 4Ws to frame any feature before diving into requirements:

| W | Questions |
|---|---|
| **Who** | Stakeholders, users, affected systems |
| **What** | The nature of the problem, the success condition |
| **Where** | Context, surfaces, environments where the solution operates |
| **Why** | The purpose, business case, what changes if we don't build this |

### 1.3 Structured Question Categories

Use these categories during the clarification phase to ensure nothing is missed:

**Scope & Requirements**
- What triggers this behaviour?
- What explicitly is NOT included in this task?
- What does success look like in concrete user steps?
- Real-time or batched? What is the latency tolerance?

**Technical Constraints**
- Expected volume (10/day vs 10,000/hour changes the architecture entirely)
- What existing systems must this integrate with?
- What is in the approved tech stack? What is prohibited?
- Are there delivery guarantees needed?

**Users & Surfaces**
- Who is the primary user? Are there secondary users?
- What does the user see when this fails?
- What does a successful interaction look like in concrete steps?

**Edge Cases & Error Handling**
- What happens on null/empty inputs?
- What happens when downstream dependencies fail?
- What are the boundary values?
- How should concurrent access be handled?
- What is the rollback strategy if this fails after deployment?

**Prior Decisions**
- What architectural choices are already settled that the agent must not re-litigate?
- Which patterns in the existing codebase should be followed?
- What third-party libraries are approved? Prohibited?

**Verification**
- What is the test command that proves this works?
- What does the acceptance test look like in pseudocode?
- Are there performance benchmarks that must be met?

### 1.4 GitHub spec-kit Seven-Step Workflow

The most widely adopted open-source SDD toolkit (88.5K stars):

1. **Constitution** — establish immutable project-wide principles
2. **Specify** — define *what* to build (focus on outcomes, not tech stack)
3. **Clarify** — structured questioning to resolve ambiguities
4. **Plan** — generate technical approach (tech stack specifics go here)
5. **Cross-review** — validate the plan against the spec
6. **Tasks** — break into discrete implementation units
7. **Implement** — execute

The **Constitution** is the key innovation: a project-wide file of immutable rules that override all other instructions in every session.

### 1.5 Amazon Kiro's Three-Document Architecture

Kiro (AWS agentic IDE, 2025) uses three levels of context:

1. **Steering documents** — project-wide: architecture decisions, coding standards, naming conventions, compliance requirements. Referenced for every code generation, not just the current task.
2. **Spec documents** — feature-specific: user stories with EARS acceptance criteria, technical design, task list.
3. **Agent hooks** — event-driven automations triggered on file save/create/delete (e.g., update tests when a component is saved).

---

## 2. Writing Effective Specifications

### 2.1 The Six Essential Spec Elements (Addy Osmani / O'Reilly)

A spec is a contract that defines what to build, what not to build, and how to verify the work.
Six elements are required for an AI-ready spec:

1. **Outcomes** — what and why. Focus on goals, not implementation.
2. **Scope boundaries** — in-scope AND explicitly out-of-scope.
3. **Constraints** — existing tech stack decisions, performance requirements, things the agent must not do.
4. **Prior decisions** — existing ADRs and patterns to follow. Prevents agents from re-litigating settled choices.
5. **Task breakdown** — discrete, independently-implementable units with clear interfaces.
6. **Verification criteria** — testable acceptance criteria with concrete test cases.

### 2.2 Out-of-Scope Lists Are As Important As In-Scope Lists

AI agents fill spec gaps with plausible assumptions.
An agent implementing authentication will add OAuth because most apps have OAuth — unless the spec explicitly states "OAuth is out of scope."

**The spec must define what NOT to build.**
Omitting exclusions is not neutral — it is an implicit instruction to add the missing feature.

### 2.3 EARS Notation for Acceptance Criteria

Amazon Kiro adopted EARS (Easy Approach to Requirements Syntax, Rolls-Royce, 2009) as the standard for AI-readable acceptance criteria because it produces criteria that are **independently testable by construction**.

Base format:
```
WHEN [precondition or trigger] THE SYSTEM SHALL [observable outcome]
```

Five patterns:

| Pattern | Format | Use for |
|---|---|---|
| Ubiquitous | `The system shall [X]` | Invariants always true |
| Event-driven | `WHEN [event] THE SYSTEM SHALL [X]` | Triggered behaviour |
| Unwanted behaviour | `IF [fault] THEN THE SYSTEM SHALL [X]` | Error handling |
| State-driven | `WHILE [state] THE SYSTEM SHALL [X]` | Ongoing conditions |
| Optional feature | `WHERE [feature included] THE SYSTEM SHALL [X]` | Conditional features |

**Why EARS matters for agents:** "the login should work" is ambiguous.
"WHEN a user submits valid credentials THE SYSTEM SHALL redirect to the dashboard within 200ms" is directly machine-verifiable.
Agents can self-check; reviewers can objectively pass or fail.

### 2.4 Inline Test Cases in Specs

The highest-leverage verification technique: include specific inputs and expected outputs directly in the spec alongside each acceptance criterion.

Empirical finding: specs with concrete inline test cases cause agents to write passing code on the first implementation attempt rather than requiring correction rounds.

### 2.5 The Three-Tier Constraint System

Structure constraints at three tiers (applies to both the project constitution and per-spec constraints):

- **"Always do"** — invariants (write tests before committing, use parameterised queries)
- **"Ask first"** — actions requiring human approval before proceeding (modifying database schemas, changing public API contracts, infrastructure changes)
- **"Never do"** — hard stops (commit secrets, push to `main`, modify files outside task scope)

### 2.6 The SCOPE Method

A practitioner-oriented structure for spec sections:

- **S**tructure — overall architecture and directory organisation
- **C**onstraints — tech stack, API limits, performance requirements
- **O**utcomes — acceptance criteria as testable "done" conditions
- **P**hases — ordered phases; foundations before building on them
- **E**xamples — sample test cases inline with specific inputs and expected outputs

### 2.7 Structural Formatting for AI Parsing

Anthropic engineering research recommends using distinct labelled sections (analogous to `<background>`, `<instructions>`, `<output_format>`) rather than flat bullet lists.

Key finding: as the number of instructions increases, model adherence to later instructions drops significantly.
Hierarchical sections with clear labels outperform flat bullet lists.

**Practical limit:** LLMs reliably follow approximately 150–200 instructions before adherence degrades.
This is the empirical basis for short, phased specs and the ≤5 acceptance criteria per task rule.

---

## 3. Keeping Humans in the Loop

### 3.1 The Three Oversight Modes

The field has converged on three distinct modes:

| Mode | How | When to use |
|---|---|---|
| **Human-in-the-loop (HITL)** | Humans approve/correct agent actions *before* they take effect | High-stakes, ambiguous, compliance-sensitive decisions |
| **Human-on-the-loop (HOTL)** | Humans supervise *after* completion; review outcomes and flag exceptions | Moderate-risk, well-scoped operations |
| **Human-out-of-the-loop (HOOTL)** | Full autonomy with monitoring | Low-risk, well-tested, well-defined scenarios |

Organisations implementing HITL report accuracy up to 99.9% vs 92% for AI-only systems.

### 3.2 Decision Classification by Risk

Before a session begins, classify decisions by risk level:

- **Routine / low-risk** → full automation (formatting, linting, test generation)
- **Medium-risk** → HOTL supervision (code implementation, refactoring)
- **High-risk** → HITL approval (database schema changes, security-sensitive code, infrastructure changes, public API contracts)

Design **circuit breakers** — predetermined stopping conditions — into agentic workflows for all high-risk actions.

### 3.3 GitHub Copilot Workspace Gate Model

Copilot Workspace makes human review explicit at each phase transition:

1. **Task → Topic**: human reviews the distilled question before proceeding
2. **Topic → Current Spec**: human validates that AI correctly understood existing behaviour
3. **Current Spec → Proposed Spec**: human reviews success criteria before planning
4. **Proposed Spec → Plan**: human reviews file-level changes before implementation
5. **Plan → Code**: human can edit any generated code before accepting

All outputs are "fully editable and regeneratable" at every stage.

### 3.4 When to Intervene (Claude Code's Official Guidance)

**Intervene immediately when:**
- The agent is going in a direction you did not intend (press Esc; context is preserved)
- You have corrected the same issue twice — the context is polluted; `/clear` and write a better prompt
- You are more than two failed corrections in on the same problem

**Let agents run for:**
- Tasks with clear success criteria and automated verification
- Well-scoped, single-responsibility tasks
- Tasks using auto mode (a classifier model reviews commands, blocking scope escalation)

---

## 4. Common Failure Modes

Source: Columbia DAPLab analysis of real agent PRs (January 2026).

| Failure Mode | Description | Prevention |
|---|---|---|
| **Scope expansion (gold-plating)** | Agent implements unrequested features it decides would be helpful | Explicit out-of-scope section in spec |
| **Context loss** | Long sessions cause early instructions to be forgotten as context fills | `/clear` between unrelated tasks; short re-loadable specs; `claude-progress.txt` |
| **Cascading errors** | One hallucinated fact triggers downstream errors across multiple systems | Schema validation; scoped tool access |
| **Silent failures** | Agent catches an error but continues, treating absent output as success | Explicit error-handling requirements; verification criteria requiring errors to be surfaced |
| **Wrong abstraction** | Agent duplicates code instead of abstracting, or over-engineers simple problems | "Follow the patterns in [file]" plus code style examples in spec |
| **Spec drift** | Agent gradually interprets instructions in ways that diverge from original intent | Living specs re-read at session start; progress files |
| **Context poisoning** | An early hallucination enters context and is repeatedly referenced | Fast-fail verification criteria; `/rewind` to restore pre-error state |
| **Over-specification** | Spec describes *how* to implement rather than *what* outcome is needed | Outcome-based acceptance criteria; let the agent choose implementation |
| **Prompt injection** | Agent reads a file containing adversarial instructions that override directives | Scoped tool permissions; sandboxing |

### The "Vibe Coding" Root Cause

When a developer prompts "Add photo sharing," the agent must guess format, permissions model, size limits, storage type, and compression.
The result is "plausible-looking code that makes dozens of unstated assumptions — many of them wrong."
Specs eliminate this guessing.

---

## 5. Multi-Session Context Management

### 5.1 The claude-progress.txt Pattern (Anthropic Engineering)

For tasks spanning multiple sessions, Anthropic's engineering team uses a two-agent harness:

**Initializer agent** (first session only):
- Expands the feature request into a comprehensive list of specific, testable requirements
- Creates `claude-progress.txt` — the cross-session state artifact
- Creates `init.sh` — how to start the dev server and run tests
- Creates an initial git commit establishing a baseline

**Coding agent** (every subsequent session):
- Reads git log and `claude-progress.txt` to reconstruct state
- Runs dev server and tests
- Picks one item from the requirement list
- Commits changes with a clear message
- Appends completion note to `claude-progress.txt`

**Why this works:** the progress file is external memory that survives context limits.
Without it, multi-session tasks require the agent to reconstruct state from git history alone, which is error-prone.

### 5.2 Context Engineering (The 2025 Mental Model Shift)

In 2025, "context engineering" replaced "prompt engineering" as the dominant mental model:

- **Prompt engineering** — what to *say* to the model at a moment in time
- **Context engineering** — what the model *knows* when you say it, and why it should care

Key context engineering practices:
- **Intelligent retrieval** — RAG, file indexing; do not manually stuff context
- **Compression by design** — summaries and progress files, not raw conversation history
- **Isolation** — parallel agents each get focused context for their specific task
- **Persistence** — write discoveries to external storage so they survive context limits

Anthropic research: structured context reduces hallucination rates by over 40% compared to standalone prompts.

---

## 6. The Future Direction: Spec-as-Source

Tessl (founded by Guy Podjarny, creator of Snyk) represents the most radical position: specifications are the *only* artifact humans maintain. Code is generated and marked `// GENERATED FROM SPEC - DO NOT EDIT`.

A Tessl spec has three parts:
1. Description of the software component
2. List of capabilities with linked tests
3. API showing how to use it

The `@generate` annotation triggers code generation from the spec.
Code becomes a build artifact, not a maintained artifact.

This is where the field is heading — specs becoming "the new source code."

---

## 7. Key References

| Source | What it covers |
|---|---|
| [Addy Osmani — How to write a good spec for AI agents](https://addyosmani.com/blog/good-spec/) | The six-element spec framework; three-tier constraints |
| [GitHub spec-kit](https://github.com/github/spec-kit) | Open-source SDD toolkit; Constitution concept |
| [Claude Code Best Practices](https://code.claude.com/docs/en/best-practices) | CLAUDE.md, subagents, verification patterns, failure modes |
| [Anthropic — Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | claude-progress.txt pattern for multi-session work |
| [arXiv 2602.00180](https://arxiv.org/abs/2602.00180) | Empirical data: 50% error reduction with human-refined specs |
| [Paul Duvall — AI Development Patterns](https://github.com/PaulDuvall/ai-development-patterns) | 28-pattern library with anti-patterns and team guidance |
| [Kiro Documentation](https://kiro.dev/) | EARS notation; three-document architecture |
| [Thoughtworks Technology Radar — SDD](https://www.thoughtworks.com/en-us/radar/techniques/spec-driven-development) | Industry validation; tool comparison |
| [Columbia DAPLab — 9 Critical Failure Patterns](https://daplab.cs.columbia.edu/general/2026/01/08/9-critical-failure-patterns-of-coding-agents.html) | Empirical failure analysis from real agent PRs |
| [Copilot Workspace User Manual](https://github.com/githubnext/copilot-workspace-user-manual) | Explicit gate model across all phase transitions |
| [EARS Notation Reference](https://alistairmavin.com/ears/) | Full EARS specification; five patterns |
| [Tessl](https://tessl.io/) | Spec-as-source model |
| [DeepLearning.AI — SDD Short Course](https://www.deeplearning.ai/short-courses/spec-driven-development-with-coding-agents/) | Structured curriculum |

---

## 8. Improvements to Apply to This Process

The following changes are derived directly from the research findings.
Each item identifies the exact file to modify, the specific change, the source insight behind it, and the failure mode it prevents.
Items are ordered by impact.

---

### 8.1 EARS Acceptance Criteria in the Task Template

**File:** `.claude/skills/new-task/assets/TEMPLATE-task.md`
**Also affects:** `.claude/skills/write-plan/SKILL.md` (Step 3 instructions)

**Change:** Replace the free-form acceptance criteria bullet list with EARS-format criteria:
```
WHEN [precondition or trigger] THE SYSTEM SHALL [observable outcome]
IF [fault condition] THEN THE SYSTEM SHALL [error behaviour]
```

**Why:** Free-form criteria like "the login should work" are ambiguous — the agent interprets them, the reviewer interprets them, and they often mean different things. EARS criteria are independently testable by construction. The agent can self-verify. The reviewer can objectively pass or fail each one. Adopted by Amazon Kiro as the standard for AI-readable requirements.

**Failure modes prevented:** wrong abstraction, spec drift, silent failures (agent cannot self-check against vague criteria).

---

### 8.2 Structured Question Categories in Brainstorm

**File:** `.claude/skills/brainstorm/SKILL.md` — Step 2 (Clarification Round)

**Change:** Replace the current general guidance ("ask about ambiguities") with the seven structured question categories from Section 1.3 of this document. The Planner should work through each category and ask only the questions with material unknowns.

Categories to cover:
- Scope & requirements (triggers, explicit exclusions, success definition)
- Technical constraints (volume, integrations, approved stack)
- Users & surfaces (primary/secondary users, failure experience)
- Edge cases & error handling (null inputs, downstream failures, rollback)
- Prior decisions (settled architectural choices, patterns to follow)
- Verification (test command, acceptance test pseudocode, benchmarks)

**Why:** Left without structure, agents ask about what comes to mind and skip whole categories. Practitioners using structured interviews surfaced 40+ requirements they would not have captured upfront. The categories mirror the exact inputs the Implementer needs to avoid guessing.

**Failure modes prevented:** scope expansion (missed exclusions), context poisoning (wrong assumptions baked in early), cascading errors (missed edge cases).

---

### 8.3 Explicit Out-of-Scope Section in the Spec Template

**File:** `.claude/skills/new-spec/assets/TEMPLATE-specification.md`
**Also affects:** `.claude/skills/brainstorm/SKILL.md` — Step 2 and Step 6 confirmation

**Change:** Promote out-of-scope to a mandatory first-class section in the spec template, not a sub-bullet under scope. During the brainstorm Step 2 clarification round, add an explicit question: *"What is explicitly NOT included in this feature?"* During Step 6 confirmation, require that the approach summary includes at least one exclusion.

**Why:** Agents fill spec gaps with plausible assumptions. An agent implementing authentication will add OAuth because most apps have it — unless the spec explicitly says otherwise. Multiple independent research sources identified this as one of the most underestimated spec gaps. Out-of-scope lists prevent gold-plating as reliably as in-scope lists prevent omissions.

**Failure modes prevented:** scope expansion (gold-plating), wrong abstraction (agent adds adjacent features).

---

### 8.4 Inline Test Cases in the Spec Template

**File:** `.claude/skills/new-spec/assets/TEMPLATE-specification.md`
**Also affects:** `.claude/skills/write-plan/SKILL.md` — quality criteria

**Change:** Add a **Verification Examples** section to the spec template. For each acceptance criterion, include a concrete example with specific inputs and expected outputs:

```
### Verification Examples

| Scenario | Input | Expected output |
|---|---|---|
| Valid login | email: user@example.com, password: correct | Redirect to /dashboard, session cookie set |
| Invalid password | email: user@example.com, password: wrong | 401 response, error message displayed |
| Empty email | email: "", password: any | Form validation error, no server request |
```

**Why:** Empirical finding — specs with concrete inline test cases cause agents to write passing code on the first implementation attempt rather than requiring correction rounds. The agent has a direct target to verify against rather than interpreting vague criteria. This is the single highest-leverage spec improvement identified across research sources.

**Failure modes prevented:** wrong abstraction, silent failures, spec drift (concrete examples anchor interpretation).

---

### 8.5 Project Constitution

**New file:** `project/docs/constitution.md` (created per-project, not part of the framework templates)
**Also affects:** `.claude/skills/bootstrap-project/SKILL.md` — add constitution generation to the setup step; `CLAUDE.md` — reference it

**Change:** Add a constitution generation step to `bootstrap-project`. The human provides the project's immutable rules; the skill writes `project/docs/constitution.md` with three tiers:

```markdown
## Always Do
- Write tests before committing production code
- Use parameterised queries for all database access
- [project-specific invariants]

## Ask First
- Modifying database schemas
- Changing public API contracts
- Adding new third-party dependencies
- Infrastructure changes

## Never Do
- Commit secrets or API keys
- Push directly to `main`
- Modify files outside the current task's scope
- Skip the integration test suite
```

Load the constitution into every agent's context at session start (via `CLAUDE.md` reference or agent `skills:` frontmatter).

**Why:** The Constitution pattern (from GitHub spec-kit) establishes project-wide invariants that override all other instructions. The three-tier structure formalises the "ask first" behaviour that currently exists implicitly — agents either act or don't; there is no middle tier. Making "ask first" explicit prevents high-risk actions from proceeding silently.

**Failure modes prevented:** scope expansion, cascading errors (agent asks before touching infrastructure), prompt injection (constitution takes precedence over retrieved content).

---

### 8.6 Structured Question Categories in the Task Template

**File:** `.claude/skills/new-task/assets/TEMPLATE-task.md`

**Change:** Add a **Verification Command** field (already present) and a **Verification Examples** field (new) to the task template, mirroring the spec template change in 8.4. Also add an explicit **Out of Scope** field at the task level for task-specific exclusions that supplement the spec-level exclusions.

**Why:** A task file is the Implementer's primary input. If it omits verification examples and explicit exclusions, the Implementer must infer them from the spec — introducing interpretation risk at every task. Grounding each task independently removes this dependency chain.

**Failure modes prevented:** scope expansion per task, silent failures (implementer has no concrete target to self-verify against).

---

### 8.7 claude-progress.txt for Multi-Session Tasks

**File:** `.claude/skills/tdd/SKILL.md` — add a multi-session state management note
**Also affects:** `ai-process/guidelines/coding-standards.md` — add cross-session guidance; `ai-process/templates/` — add `progress.md` template

**Change:** When a task is expected to span multiple agent sessions (flag in task frontmatter: `multi-session: true`), the Implementer creates a `claude-progress.txt` in the task branch root at the start of the first session. At the start of each subsequent session the Implementer reads this file before doing anything else.

Format:
```
## Completed
- [date] Implemented X (commit abc1234)
- [date] Added tests for Y (commit def5678)

## In Progress
- Working on Z — got stuck at [specific point]

## Next
- [ ] Remaining item 1
- [ ] Remaining item 2

## Decisions Made
- Chose approach A over B because [reason]
```

**Why:** Anthropic's own engineering team uses this pattern for long-running agent tasks. Without it, each new session reconstructs state from git history alone, which is incomplete and error-prone. The progress file is the external memory that survives context limits — the agent's equivalent of a developer's notebook.

**Failure modes prevented:** context loss, spec drift (completed decisions are recorded, not re-litigated).

---

### 8.8 Summary Table

| # | What | File(s) to change | Impact | Failure modes prevented |
|---|---|---|---|---|
| 8.1 | EARS acceptance criteria | `TEMPLATE-task.md`, `write-plan/SKILL.md` | **High** | Wrong abstraction, spec drift, silent failures |
| 8.2 | Structured question categories | `brainstorm/SKILL.md` Step 2 | **High** | Scope expansion, context poisoning, cascading errors |
| 8.3 | Out-of-scope as first-class | `TEMPLATE-specification.md`, `brainstorm/SKILL.md` | **High** | Scope expansion, gold-plating |
| 8.4 | Inline test cases in spec | `TEMPLATE-specification.md`, `write-plan/SKILL.md` | **High** | Wrong abstraction, silent failures, spec drift |
| 8.5 | Project constitution | `bootstrap-project/SKILL.md`, `CLAUDE.md`, new `constitution.md` | **Medium** | Scope expansion, cascading errors, prompt injection |
| 8.6 | Verification fields in task template | `TEMPLATE-task.md` | **Medium** | Scope expansion per task, silent failures |
| 8.7 | claude-progress.txt pattern | `tdd/SKILL.md`, `coding-standards.md`, new `progress.md` template | **Medium** | Context loss, spec drift |
