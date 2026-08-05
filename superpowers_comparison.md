# Superpowers vs. The AI Team — Skill Comparison and Adoption Plan

> Analysis date: 2026-08-03
> Sources compared:
> - `../superpowers` — 14 skills, ~3,200 lines of `SKILL.md` plus supporting prompt templates, scripts, and technique references
> - `the-ai-team-definition` — 18 skills in `cli/src/ai_team/init/sources/skills/`, ~2,250 lines, plus `ai-process/processes/` (workflow, quality gates, escalation) and 5 role agents

---

## 1. Executive summary

**Superpowers optimizes the inner loop:** how thoroughly one unit of work gets designed,
executed, reviewed, and verified inside a session.

**The AI Team optimizes the outer loop:** how a project's stated truth stays coherent
across many features and many sessions.

Everything else follows from that difference.

Superpowers' artifacts are dated snapshots — `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`,
a single plan file, a progress ledger that gets `rm -rf`'d once the branch is finished. They are
accurate on the day they are written and never again.

The AI Team's artifacts are a live state machine — `project/specs/S-NNN` with an Amendment Log,
ADRs with a supersede chain, task files that physically move through
`pending/ → in-progress/ → completed/`, and canonical lifecycle state pinned to `dev-agent`.

The second structural difference is **enforcement style**:

| | Superpowers | The AI Team |
|---|---|---|
| Mechanism | Psychological | Structural |
| Devices | Iron Laws, red-flag lists, rationalization tables, "violating the letter is violating the spirit" | Numbered gates, role separation, verdict vocabularies, branch rules, mandatory output envelopes |
| Effect | Argues the agent out of cheating | Makes cheating not fit through the pipe |

The two are complementary, not competing. Most of what is worth importing is process discipline
and context engineering, which is orthogonal to the durable-truth property.

---

## 2. Skill inventories

### Superpowers (14)

| Skill | Lines | Role |
|---|---|---|
| `using-superpowers` | 62 | Meta — forces skill invocation before any response |
| `brainstorming` | 151 | Design dialogue → spec document |
| `writing-plans` | 168 | Spec → bite-sized task plan |
| `executing-plans` | 64 | Inline plan execution |
| `subagent-driven-development` | 503 | Orchestrated execution: ledger, fix loop, model selection |
| `dispatching-parallel-agents` | 167 | Parallel fan-out over independent problems |
| `test-driven-development` | 320 | RED-GREEN-REFACTOR discipline |
| `systematic-debugging` | 283 | Four-phase root-cause investigation |
| `requesting-code-review` | 95 | Dispatch a reviewer subagent |
| `receiving-code-review` | 205 | How to react to review feedback |
| `verification-before-completion` | 120 | Evidence before claims |
| `finishing-a-development-branch` | 201 | Merge / PR / keep menu, worktree cleanup |
| `using-git-worktrees` | 167 | Workspace isolation |
| `writing-skills` | 679 | Meta — TDD applied to process documentation |

Supporting assets worth noting: `implementer-prompt.md`, `task-reviewer-prompt.md`,
`re-review-prompt.md`, `code-reviewer.md`, `spec-document-reviewer-prompt.md`,
`plan-document-reviewer-prompt.md`, `writing-good-tests.md`, `root-cause-tracing.md`,
`defense-in-depth.md`, `condition-based-waiting.md`, `testing-skills-with-subagents.md`,
plus executable scripts (`sdd-workspace`, `task-brief`, `review-package`).

### The AI Team (18)

| Category | Skills |
|---|---|
| Artifact creation (CLI wrappers) | `new-spec`, `new-task`, `new-bug`, `new-adr`, `change-request` |
| Planning | `brainstorm`, `spec-breakdown` |
| Gates and reviews | `spec-breakdown-review` (Gate 2), `architecture-consistency-review`, `code-review` (Gate 3) |
| Execution | `tdd`, `debug` |
| Orchestrators | `dev-loop`, `bug-loop` |
| Integration | `integrate` (Gate 4), `merge-conflicts`, `git-conventions` |
| Reporting | `status-report` (Gate 5) |
| Escalation | `escalation-review` |

Plus five role agents — `planner`, `architect`, `developer`, `reviewer`, `integrator` — and the
gate model in `ai-process/processes/quality-gates.md`.

---

## 3. Function-by-function map

| Function | Superpowers | The AI Team | Verdict |
|---|---|---|---|
| Meta / skill dispatch | `using-superpowers` | — (role agent definitions + CLAUDE.md) | Superpowers only |
| Design dialogue | `brainstorming` | `brainstorm` | Both strong, different bets |
| Spec authoring contract | Inline, no template | `new-spec` + template + `spec-authoring-guide` | **AI Team much stronger** |
| Decomposition to work units | `writing-plans` (one plan file) | `spec-breakdown` + `new-task` (task files) | Different unit — see §4 |
| Plan validation | Self-review checklist, optional reviewer prompt | `spec-breakdown-review` = **Gate 2**, Architect subagent, mandatory | **AI Team stronger** |
| Execution orchestration | `subagent-driven-development` / `executing-plans` | `dev-loop` / `bug-loop` | **Superpowers far more developed** |
| Parallel fan-out | `dispatching-parallel-agents` | — (deliberately sequential) | Superpowers only |
| TDD | `test-driven-development` | `tdd` | Superpowers on discipline, AI Team on integration |
| Debugging | `systematic-debugging` + 3 technique refs | `debug` (diagnosis-only, fix contract) | Split — see §4 |
| Code review (requesting) | `requesting-code-review`, `code-reviewer.md`, `task-reviewer-prompt.md` | `code-review` = **Gate 3** | Superpowers on calibration, AI Team on gating |
| Code review (receiving) | `receiving-code-review` | — | **Superpowers only — gap** |
| Verification discipline | `verification-before-completion` | — | **Superpowers only — gap** |
| Branch finish / integration | `finishing-a-development-branch` (human menu) | `integrate` + `merge-conflicts` + `git-conventions` (**Gate 4**, automated) | **AI Team far stronger** |
| Workspace isolation | `using-git-worktrees` | — (branches only) | Superpowers only |
| Escalation | Ad-hoc `BLOCKED` status | `escalation-review` + frozen 4-field block + Phase-2 human report template | **AI Team far stronger** |
| Architecture decisions | — | `new-adr` + `architecture-consistency-review` | **AI Team only** |
| Lightweight change intake | — | `change-request` | AI Team only |
| Status / sign-off | — | `status-report` (Gate 5) | AI Team only |
| Authoring skills | `writing-skills` (TDD for docs) | `guides/skill_template.md` (format contract) | **Superpowers only as a method** |

---

## 4. Where they overlap but diverge

### 4.1 Brainstorm

| | Superpowers `brainstorming` | AI Team `brainstorm` |
|---|---|---|
| Question pacing | One question per message, multiple choice preferred | ~5 questions per round |
| Coverage discipline | Purpose / constraints / success criteria | Six mandated internal categories: scope, technical constraints, users & surfaces, edge cases, prior decisions, verification |
| Alternatives | 2–3 approaches, lead with recommendation | ≥2 genuinely distinct, no strawmen |
| Scope triage | **Yes** — flags multi-subsystem requests before questioning, decomposes into sub-projects | **No** |
| Design presentation | Section by section, approval after each | Single 2–3 sentence confirmation at Step 6 |
| Exclusions | Implicit (YAGNI) | **Explicit and required** |
| Document quality | Self-review checklist inline | Delegated to `new-spec`: content-boundary rule, per-section recipes, pre-submission checklist |
| Post-write gate | User reviews written spec | `[TODO]` resolution loop → Architecture Consistency Review → Gate 1 |
| Hard gate against implementation | **Yes**, explicit `<HARD-GATE>` | Implied by role separation |

**Net:** The AI Team produces a much better *document*. Superpowers runs a better *conversation*,
and it has one thing the AI Team lacks entirely — scope triage before questioning.

### 4.2 Decomposition

Fundamentally different units of work.

**Superpowers `writing-plans`** produces one plan file containing:
- A `Global Constraints` header with exact values copied verbatim from the spec
- Tasks with `Files:` (create / modify / test) and an **`Interfaces: Consumes / Produces`** block
- Literal code in every step ("Write the failing test" with the actual test body)
- A "No Placeholders" list of banned phrasings that count as plan failures
- Self-review: spec coverage, placeholder scan, **type/name consistency across tasks**

The `Interfaces` block exists because *"a task's implementer sees only their own task; this block
is how they learn the names and types neighboring tasks use."*

**AI Team `spec-breakdown` + `new-task`** produces independent task files containing:
- EARS-pattern acceptance criteria (Ubiquitous, Event-driven, Unwanted-behaviour, State-driven, Optional)
- Declared dependencies on other task IDs
- Files to touch
- A verification command
- One-shottable heuristics: ≤3–4 files, ≤5 ACs, description ≤~20 lines

Plus clean ownership boundaries: `spec-breakdown` owns plan coverage and dependency ordering,
`new-task` owns per-task shape, `spec-breakdown-review` owns Gate 2 readiness.

**Net:** AI Team tasks survive sessions and carry lifecycle state. Superpowers tasks carry
cross-task type contracts. Neither has both.

### 4.3 Debugging

**AI Team `debug`** is diagnosis-only and terminates in a five-field **fix contract**:
reproduction status, evidence captured, isolated fault, planned fix, planned verification.
`code-review` then refuses to review a bug fix without a complete evidence chain
(*"do not infer intent from the diff"*). That is a stronger artifact than anything in superpowers.

**Superpowers `systematic-debugging`** has the richer investigative technique library:
- Iron Law: no fixes without root-cause investigation first
- Diagnostic instrumentation at **every component boundary** before hypothesizing, run once to
  gather evidence showing *where* it breaks
- Backward data-flow tracing (`root-cause-tracing.md`)
- **After 3 failed fixes, question the architecture, not the hypothesis** — *"this is NOT a failed
  hypothesis, this is a wrong architecture"*
- Signals from the human that you are doing it wrong ("Is that not happening?", "Stop guessing")

### 4.4 Execution orchestration — the widest gap

`subagent-driven-development` (503 lines) carries machinery `dev-loop` has no equivalent of:

- **Ledger file for compaction recovery.** *"Controllers that lost their place have re-dispatched
  entire completed task sequences — the single most expensive failure observed."*
- **Explicit model-selection policy.** *"Always specify the model explicitly when dispatching a
  subagent — an omitted model inherits your session's model, often the most capable and most
  expensive."* Plus: *"turn count beats token price"* — the cheapest models take 2–3× the turns on
  multi-step work.
- **Artifacts handed over as files, never pasted.** Task briefs, review packages, report files.
  *"Everything you paste into a dispatch prompt stays resident in your context for the rest of the
  session and is re-read on every later turn."*
- **No history in dispatches.** *"A real session's dispatch hit 42k chars of which 99% was pasted
  history."*
- **Five-round fix loop with a capability ladder.** Rounds 1–3 resume the original implementer
  (context intact); rounds 4–5 dispatch a *fresh* implementer on a *more capable* model —
  *"a loop that survives three resumes usually means the implementer cannot see its own problem —
  fresh eyes and a capability bump in one move."*
- **A breaker at the cap.** Forces explicit adjudication of every open finding, parked with a
  written ruling. *"Every adjudication is a ledger entry — a silent discard is forbidden."*
- **BASE sha recorded before dispatch.** *"Never `HEAD~1`, which silently drops all but the last
  commit of a multi-commit task."*
- **Scoped re-reviews.** The re-reviewer verdicts each finding ADDRESSED / NOT ADDRESSED and flags
  new breakage in the fix diff only; out-of-scope observations become deferred minors.

`dev-loop` wins on queue management, dependency-ordered task selection, the baseline test guard,
canonical lifecycle commits, and real automated integration. It says nothing about context budget,
cost, model tiering, or diff ranges.

---

## 5. Adoption plan

Sorted by value. Each item is anchored to the file that would own it.

### Tier 1 — take these, no conflict with the truth property

#### 1.1 Rationalization tables in the enforcement skills
**Owner:** `tdd`, `debug`, `integrate`, `code-review`, `git-conventions`

The single most transferable superpowers technique. The AI Team's "Common Pitfalls" sections are
*descriptive*:

> "Writing implementation first — this defeats the purpose of TDD."

Superpowers' are *pre-emptive counter-arguments* to the specific sentence the model is about to
generate:

> "Deleting X hours is wasteful" → Sunk cost fallacy — that time is already spent either way. The
> real choice: rewrite with TDD (high confidence) vs. keep it and bolt tests on after (low
> confidence, likely bugs). Keeping code you can't trust is the waste.

Cheap to write, and it is the mechanism by which superpowers gets compliance without a gate.
Highest yield in `tdd` (test-first), `debug` (no fix without root cause), `integrate` (never skip
the post-merge run).

#### 1.2 "Evidence before claims" as a first-class rule
**Owner:** new shared skill + the five role output envelopes

The AI Team has no cross-cutting verification discipline. Every role's Output Format already has an
`Evidence:` field — that is the right slot. Make it contractually required to contain **a command
and its actual output**, and add superpowers' gate function:

```
1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
5. ONLY THEN: Make the claim
```

This upgrades a structural slot that already exists rather than bolting on a parallel mechanism.
It is also what makes every gate verdict trustworthy rather than merely asserted.

Worth importing verbatim: the "Common Failures" table (claim → what it requires → what is not
sufficient), especially the row *"Agent completed → requires VCS diff showing changes → agent
reporting 'success' is not sufficient."*

#### 1.3 Context and cost engineering in the loops
**Owner:** `dev-loop`, `bug-loop`, `code-review`

- **Review packages.** The Reviewer is currently told to read the canonical file and derive the
  diff itself. Have the loop write `git log --oneline` + `git diff --stat` + `git diff -U10` for the
  range into a single file and pass the path. The diff never enters the orchestrator's context and
  the reviewer gets everything in one Read.
- **Record BASE before dispatching the Developer.** `code-review` has no diff-range discipline at
  all; a multi-commit task reviewed off `HEAD~1` silently loses commits.
- **Model selection per dispatch.** The five agent definitions do not set models. Adopt tiering:
  cheap for transcription-shaped tasks, standard for integration work, most capable for Architect
  consultation and the Gate 5 review — and state the model explicitly at every spawn.
- **Never paste prior-task history into a dispatch.** Cheap rule, large effect.

#### 1.4 Review calibration
**Owner:** `code-review`, and the Reviewer dispatch prompt in `dev-loop`

Five imports, all of which fit the existing shape:

1. **Severity taxonomy** — Critical / Important / Minor, with Important defined as *"this task
   cannot be trusted until it is fixed."* Today PASS/FAIL means every quality nit is either
   blocking or invisible.
2. **"Do not trust the report"** — treat the Work Log as unverified claims about the code.
   *"A stated rationale never downgrades a finding's severity."*
3. **Do not re-run tests the Developer already ran** — the Work Log carries the evidence. Fits the
   handoff model perfectly and saves a full suite run per review.
4. **`⚠️ Cannot verify from diff`** as a reportable category, routed back to the loop, which holds
   the cross-task context the reviewer lacks. Today a reviewer facing this must guess PASS or FAIL.
5. **Never pre-judge findings for the reviewer** — *"if the prompt you are writing contains 'do not
   flag,' 'don't treat X as a defect,' 'at most Minor,' or 'the plan chose' — stop: you are
   pre-judging, usually to spare yourself a review loop."* Applies directly to the `dev-loop` spawn
   prompt.

Plus: **roll up deferred Minor findings** and triage them at Gate 5 via `status-report`.
Superpowers' rule is that a roll-up nobody reads is a silent discard — the AI Team's "note any
minor observations (non-blocking)" currently vanishes into the task file.

#### 1.5 Capability ladder in the FAIL loop
**Owner:** `dev-loop`, `bug-loop`

Today: FAIL → FAIL → FAIL → Architect → Human, respawning an identical Developer each cycle.

Import: cycles 1–2 keep continuity with the same Developer; cycle 3 spawns **fresh on a stronger
model** *before* consuming the Architect consultation.

Also worth stealing: **adjudication with parked findings** at the cap instead of pure escalation.
Caveat — in the AI Team a "parked" finding must become a durable artifact (a filed bug, or a
recorded deviation in the task file), never a ledger line that gets deleted with the workspace.

---

### Tier 2 — take with adaptation

#### 2.1 `Interfaces: Consumes / Produces` in the task template
**Owner:** `cli/src/ai_team/templates/task.md`, `new-task`, `spec-breakdown-review`

Superpowers' best task-format idea, and the AI Team has no equivalent. Gate 2 checks dependencies
and file conflicts but cannot catch Task 3 defining `clearLayers()` while Task 7 calls
`clearFullLayers()`. Add the block to the template; add "type and name consistency across tasks"
to Gate 2's checklist.

**This one actively serves the truth property** — interfaces named in tasks are precisely what
specs describe at the interface level, so it creates a checkable link between spec and plan.

#### 2.2 "No placeholders" as a task quality rule
**Owner:** `new-task`

Superpowers enumerates plan failures — banned phrasings that are never acceptable in a plan step:

- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases"
- "Write tests for the above" (without actual test code)
- "Similar to Task N" (repeat the code — the engineer may be reading tasks out of order)
- References to types, functions, or methods not defined in any task

The AI Team gates `[TODO]` markers in *specs* well, but nothing stops that vagueness from reaching
a task file.

#### 2.3 Scope triage at the top of brainstorm
**Owner:** `brainstorm`

Add a Step 0: before spending clarifying questions, assess whether the request describes multiple
independent subsystems. If so, decompose into sub-projects, then brainstorm the first one; each
sub-project gets its own spec → plan → implementation cycle.

**This is a truth-property multiplier** — an oversized spec is a spec that will need constant
amendment. Right-sized specs stay true longer.

#### 2.4 Section-by-section design approval
**Owner:** `brainstorm`

Keep the ~5-questions-per-round batching — it suits an async human better than one question per
message. But adopt presenting the design *in sections with approval after each*, rather than
compressing to a single Step 6 confirmation. For a document that becomes durable truth, incremental
sign-off is worth the extra turns.

Also adopt: "lead with your recommended option and explain why", and the preference for multiple-
choice questions where possible.

#### 2.5 TDD-for-skills as this repo's own maintenance method
**Owner:** `guides/`

Meta, but this repo's product *is* skills. `guides/skill_template.md` is a format contract with no
test method. Superpowers' `writing-skills` + `testing-skills-with-subagents.md` supplies one:

| TDD concept | Skill creation |
|---|---|
| Write test first | Run the baseline pressure scenario **before** writing the skill |
| Watch it fail (RED) | Dispatch a subagent *without* the skill; record its exact rationalizations verbatim |
| Minimal code | Write the skill addressing those specific violations |
| Watch it pass (GREEN) | Verify the agent now complies |
| Refactor | Find new rationalizations → plug → re-verify |

That is how you would know whether any of the changes in this document actually work.

Also worth reading from `writing-skills`: the **Skill Discovery Optimization** section, which
documents a real failure — a description that summarized the workflow caused an agent to follow the
description instead of reading the skill, doing one review where the skill's flowchart specified
two. The rule: *descriptions state triggering conditions only, never the process.*

---

### Tier 3 — judgment calls

#### 3.1 Worktrees
`using-git-worktrees`. Interesting fit: AI Team roles constantly `git checkout dev-agent` and back
for lifecycle commits. A task worktree would let the loop hold `dev-agent` in the main tree while
the Developer works elsewhere, removing branch thrash entirely. But it is a structural change to
`git-conventions` and `integrate`. Worth an ADR, not a quick import.

#### 3.2 Parallel dispatch
Do not adopt for `dev-loop` — it collides with the single `in-progress/` slot invariant, which is
load-bearing. The only defensible use is **read-only diagnosis fan-out** in `bug-loop` when one
`integrate` run files several independent regressions: parallel `debug` (which changes no
production code by design), then sequential fixes.

#### 3.3 `receiving-code-review`
No AI Team equivalent. Lower priority than the rest because the AI Team's Reviewer→Developer
handoff is structured (verdict entries with file, what is wrong, what should change) rather than
conversational, so there is less room for performative agreement. Still, the YAGNI check —
*"reviewer suggests implementing properly → grep the codebase for actual usage → if unused, propose
removal"* — is worth folding into the Developer's fix cycle.

---

## 6. What to explicitly *not* take

- **Dated snapshot documents** (`YYYY-MM-DD-<topic>-design.md`)
- **Plan-as-single-markdown-file**
- **`rm -rf <workspace>` after the final review**
- **"The terminal state is invoking writing-plans"** as the only flow out of design

These are exactly what makes superpowers' artifacts historical rather than true. The
`S-NNN` + Amendment Log + ADR supersede chain + standing Architecture Consistency Review is the
better model, and none of the imports above should erode it.

---

## 7. The gap this exercise exposes

Stated separately because it is where the two priorities meet.

AI Team specs stay true **while work is in flight** — the Amendment Log covers scope changes during
execution, and `architecture-consistency-review` fires whenever an artifact changes. But nothing
reconciles the spec against **what was actually built** at the end.

Gate 5's pass criterion is *"the status summary matches the approved specification"* — a human
comparing a summary to a spec, not any check of code against spec.

That is the natural home for superpowers' verification principle applied one level up:

> After the queue drains, before Gate 5 sign-off, the Architect re-reads the approved spec against
> the completed task Work Logs, any ADRs created mid-flight, and the deferred-minor roll-up, then
> either confirms the spec is still true or routes amendments to the Planner.

Same skill, same routing rules, same Amendment Log as `architecture-consistency-review` — just
triggered by *completion* rather than by *artifact change*.

Do that, and "specs and ADRs are always true" stops being a property maintained by discipline
during planning and becomes one enforced by a gate at the end.

---

## 8. Suggested sequencing

| Phase | Items | Rationale |
|---|---|---|
| 1 | 1.1 rationalization tables, 1.4 review calibration | Pure documentation edits to existing skills, no contract change |
| 2 | 1.2 evidence rule, 1.3 context/cost engineering | Touches role output envelopes and loop dispatch prompts |
| 3 | 2.1 Interfaces block, 2.2 no-placeholders | Template and Gate 2 checklist changes — update spec/guide first per CLAUDE.md |
| 4 | 1.5 capability ladder, 2.3 scope triage, 2.4 section approval | Behavioural changes to the loops and brainstorm |
| 5 | §7 spec-truth reconciliation at Gate 5 | New standing duty — needs an ADR and a quality-gates amendment |
| 6 | 2.5 TDD-for-skills | Framework maintenance method; use it to validate phases 1–5 |

Per `CLAUDE.md`: anything that alters the framework contract updates the owning spec or guide
first, then the implementation, then regenerated scaffolds and docs together.
