---
title: "AI Process Full Review Report"
status: draft
created: 2026-04-21
---

# AI Process Full Review Report

## Process Flow with Findings

```
+-----------------------------------------------------------------------------+
|                         AI TEAM PROCESS FLOW                                |
|                                                                             |
|  +=====================================================================+    |
|  |                    PLANNING PHASE (human + AI)                       |   |
|  |                                                                      |   |
|  |   Human                                                              |   |
|  |     |                                                                |   |
|  |     |  feature request                                               |   |
|  |     v                                                                |   |
|  |   +----------------------+                                           |   |
|  |   |  PLANNER: Brainstorm |  <-- brainstorm skill                     |   |
|  |   |  (interactive with   |    Human shapes the spec through          |   |
|  |   |   human dialogue)    |    Q&A, alternatives, confirmation        |   |
|  |   +----------+-----------+                                           |   |
|  |              |  spec ready                                           |   |
|  |              v                                                       |   |
|  |   +----------------------+                                           |   |
|  |   |  * GATE 1: Spec      |  Human approves spec                      |   |
|  |   |    Approval (human)  |  (should be quick -- human shaped it)     |   |
|  |   +----------+-----------+                                           |   |
|  |              |  approved                                             |   |
|  |              v                                                       |   |
|  |   +----------------------+                                           |   |
|  |   |  PLANNER: Write-Plan |  <-- write-plan skill                     |   |
|  |   |  Decompose spec into |    Creates task files in pending/         |   |
|  |   |  atomic tasks        |                                           |   |
|  |   +----------+-----------+                                           |   |
|  |              |                                                       |   |
|  |              |  !! C2: Stale section says "human approves task plan" |   |
|  |              |       but no human gate exists here anymore           |   |
|  |              |                                                       |   |
|  |              |  !! M3: Write-plan spawns Architect inline (tight     |   |
|  |              |       coupling -- Planner stays alive during preflight)|  |
|  |              v                                                       |   |
|  |   +----------------------+                                           |   |
|  |   |  ARCHITECT: Preflight|  Automated, no human gate                 |   |
|  |   |  - Dependencies OK?  |                                           |   |
|  |   |  - File conflicts?   |  !! M2: Called "advisory" in component-map|   |
|  |   |  - ADR consistency?  |       but actually has decision authority |   |
|  |   |  - Task atomicity?   |                                           |   |
|  |   +----+---------+-------+  !! M8: "Atomicity" criteria defined in   |   |
|  |        |         |               skill/agent but NOT in the spec     |   |
|  |        | OK      | issues                                            |   |
|  |        |         +-------> Planner (revise) ---> re-preflight        |   |
|  |        v                                                             |   |
|  |   Plan approved -- human invokes /dev-loop                           |   |
|  +=====================================================================+    |
|                                                                             |
|  +=====================================================================+    |
|  |                EXECUTION PHASE (fully autonomous)                    |   |
|  |                                                                      |   |
|  |   +-------------------------------------------------------------+    |   |
|  |   |                    /dev-loop                                |    |   |
|  |   |                                                             |    |   |
|  |   |  +---------------+                                          |    |   |
|  |   |  | Pick next task| <-- priority -> dependency -> age        |    |   |
|  |   |  | from pending/ |                                          |    |   |
|  |   |  +-------+-------+                                          |    |   |
|  |   |          | move to in-progress/, create branch              |    |   |
|  |   |          v                                                  |    |   |
|  |   |  +---------------+                                          |    |   |
|  |   |  |  IMPLEMENTER  | <-- tdd + debug skills                   |    |   |
|  |   |  |  Write tests  |   Commits on task/T-NNN-... branch       |    |   |
|  |   |  |  Write code   |                                          |    |   |
|  |   |  |  Append log   |                                          |    |   |
|  |   |  +-------+-------+                                          |    |   |
|  |   |          | done                                             |    |   |
|  |   |          v                                                  |    |   |
|  |   |  +---------------+  * GATE 2: Code Review                   |    |   |
|  |   |  |   REVIEWER    |  Stage 1: Spec compliance                |    |   |
|  |   |  |               |  Stage 2: Code quality                   |    |   |
|  |   |  +---+---+---+---+                                          |    |   |
|  |   |      |   |   |                                              |    |   |
|  |   |      |   |   |  !! C5: Agent says "hands off to Integrator" |    |   |
|  |   |      |   |   |       but should hand verdict to /dev-loop   |    |   |
|  |   |      |   |   |                                              |    |   |
|  |   |      |   |   |  !! M5: Agent escalates on security findings |    |   |
|  |   |      |   |   |       but spec says FAIL + feedback instead  |    |   |
|  |   |      |   |   |                                              |    |   |
|  |   |  PASS|   |FAIL   ESCALATE                                   |    |   |
|  |   |      |   |   |                                              |    |   |
|  |   |      |   |   |  !! C3: Retry policy unclear --              |    |   |
|  |   |      |   |   |       spec says "one cycle" for ESCALATE     |    |   |
|  |   |      |   |   |       loops allow 3 cycles for FAIL          |    |   |
|  |   |      |   |   |                                              |    |   |
|  |   |      |   |   +-------> move to blocked/ ---> STOP           |    |   |
|  |   |      |   |                                    |             |    |   |
|  |   |      |   +--> back to IMPLEMENTER             |             |    |   |
|  |   |      |        (up to 2 retries, 3 total)      |             |    |   |
|  |   |      v                                        |             |    |   |
|  |   |  +---------------+  * GATE 3: Integration     |             |    |   |
|  |   |  |   integrate   |  Tests                     |             |    |   |
|  |   |  |   skill       |                            |             |    |   |
|  |   |  | - Pre-merge   |                            |             |    |   |
|  |   |  |   tests       |  !! M1: Integrator agent   |             |    |   |
|  |   |  | - Merge to dev|       claims write access  |             |    |   |
|  |   |  | - Post-merge  |       to completed/ but    |             |    |   |
|  |   |  |   regression  |       only skill should    |             |    |   |
|  |   |  |   check       |                            |             |    |   |
|  |   |  +---+-------+---+                            |             |    |   |
|  |   |      |       |                                |             |    |   |
|  |   |   OK |    REGRESSION                          |             |    |   |
|  |   |      |       |                                |             |    |   |
|  |   |      |       +--> revert merge                |             |    |   |
|  |   |      |       +--> file bugs via /new-bug      |             |    |   |
|  |   |      |       +--> STOP                        |             |    |   |
|  |   |      |              |                         |             |    |   |
|  |   |      |              |  !! M7: Nobody tells    |             |    |   |
|  |   |      |              |  human to run /bug-loop |             |    |   |
|  |   |      |              |                         |             |    |   |
|  |   |      v              v                         v             |    |   |
|  |   |  move task    +----------------------------------+          |    |   |
|  |   |  to completed/|         LOOP STOPS               |          |    |   |
|  |   |  delete branch| - Queue empty -> Gate 4          |          |    |   |
|  |   |      |        | - Task blocked -> human resolves |          |    |   |
|  |   |      |        | - Escalation -> human decides    |          |    |   |
|  |   |      |        | - Regression -> bugs filed       |          |    |   |
|  |   |      |        |                                  |          |    |   |
|  |   |      |        |  !! C1: Table says "Gate 5" here |          |    |   |
|  |   |      |        |       but Gate 4 everywhere else |          |    |   |
|  |   |      |        +----------------------------------+          |    |   |
|  |   |      |                                                      |    |   |
|  |   |      +--> pick next task (loop back to top)                 |    |   |
|  |   +-------------------------------------------------------------+    |   |
|  +===================================================================== +   |
|                                                                             |
|  +======================================================================+   |
|  |              BUG-FIX PHASE (autonomous, but disconnected)            |   |
|  |                                                                      |   |
|  |   !! C4: This entire phase is NOT documented in workflow-overview.md |   |
|  |                                                                      |   |
|  |   +-------------------------------------------------------------+    |   |
|  |   |                    /bug-loop                                |    |   |
|  |   |                                                             |    |   |
|  |   |  Same pattern as /dev-loop but for bugs:                    |    |   |
|  |   |  pick bug -> Implementer -> Reviewer -> integrate -> resolved|   |   |
|  |   |                                                             |    |   |
|  |   |  Key differences:                                           |    |   |
|  |   |  - Branches from dev as bug/B-NNN-...                       |    |   |
|  |   |  - No blocked/ state for bugs                               |    |   |
|  |   |  - Escalation includes inline Architect consultation        |    |   |
|  |   |                                                             |    |   |
|  |   |  !! M4: Setup guide omits bugs/in-progress/ directory       |    |   |
|  |   |        -- bug-loop will fail in new projects                |    |   |
|  |   +-------------------------------------------------------------+    |   |
|  +======================================================================+   |
|                                                                             |
|  +======================================================================+   |
|  |                    RELEASE PHASE (human)                             |   |
|  |                                                                      |   |
|  |   +----------------------+                                           |   |
|  |   |  * GATE 4: Final     |  Human reviews /status-report             |   |
|  |   |    Merge Sign-off    |  Confirms outcome matches spec intent     |   |
|  |   |    (human)           |  Not a code review -- a sign-off          |   |
|  |   +----------+-----------+                                           |   |
|  |              |                                                       |   |
|  |              v                                                       |   |
|  |        merge dev -> main                                             |   |
|  |              |                                                       |   |
|  |              v                                                       |   |
|  |           DONE                                                       |   |
|  +======================================================================+   |
|                                                                             |
|  +======================================================================+   |
|  |                    ESCALATION (cross-cutting)                        |   |
|  |                                                                      |   |
|  |   Any agent blocked                                                  |   |
|  |     |                                                                |   |
|  |     |  !! L6: Contradicts itself -- "one attempt" in Rules           |   |
|  |     |       vs. "multiple rounds" in Step 1 description              |   |
|  |     v                                                                |   |
|  |   +----------------------+                                           |   |
|  |   |  ARCHITECT            |  Can: adjust tasks, add deps, advise     |   |
|  |   |  (consultation)       |  Cannot: change spec, touch src/tests    |   |
|  |   +----+---------+-------+                                           |   |
|  |        |         |                                                   |   |
|  |   resolved    can't resolve (needs spec change)                      |   |
|  |        |         |                                                   |   |
|  |        |         v                                                   |   |
|  |        |  +----------------------+                                   |   |
|  |   agent|  |  HUMAN ESCALATION    |                                   |   |
|  |   cont-|  |  - Revise spec       |  !! M6: No skill/procedure for    |   |
|  |   inues|  |  - Modify task       |       spec amendments. Planner    |   |
|  |        |  |  - Provide guidance  |       told to "edit in-place"     |   |
|  |        |  |  - Defer the work    |       but no format defined.      |   |
|  |        |  +----------------------+                                   |   |
|  |        |                                                             |   |
|  |        v                                                             |   |
|  |   back to /dev-loop or /bug-loop                                     |   |
|  +======================================================================+   |
|                                                                             |
|  HUMAN TOUCHPOINTS (only 2 mandatory gates):                                |
|    * Gate 1 -- approve spec (beginning)                                     |
|    * Gate 4 -- approve final merge (end)                                    |
|    + invoke /dev-loop (one command)                                         |
|    + invoke /bug-loop if regressions (!! M7: not told to do this)           |
|    + resolve escalations (when agents get stuck)                            |
+-----------------------------------------------------------------------------+
```

Finding clusters:
- **Planning-to-execution transition** (C2, M3, M8): stale section, tight coupling, undefined criteria.
- **Reviewer junction** (C3, C5, M5): handoff, retry, and escalation ambiguity.
- **Dev-loop to bug-loop handoff** (C4, M7): biggest gap for autonomous flow.

---

## Scope

Full review of the AI team process definition, covering:
- `ai-process/` -- the spec layer (processes, guidelines, architecture)
- `.claude/agents/` -- agent role definitions
- `.claude/skills/` -- skill implementations
- `guides/` -- human-facing onboarding guides
- `project/` -- placeholder structure and templates
- `CLAUDE.md` -- root project instructions

Each finding was verified against the actual file contents.
Findings are rated by impact: **Critical** (process breaks or contradicts itself), **Moderate** (unclear or suboptimal but not broken), **Low** (polish or minor inconsistency).

---

## Critical Findings

### C1. Gate Numbering Conflict in `workflow-overview.md` -- FIXED

**Files:** `ai-process/processes/workflow-overview.md` lines 58-59, 159, 169, 172, 199-208 vs. `ai-process/processes/quality-gates.md` lines 68-79 vs. `ai-process/architecture/system-overview.md` line 109.

**What's wrong:** The workflow overview's "When `/dev-loop` stops" table (line 159) calls the final merge "Gate 5":

> `Queue empty | All in completed/ | Human approves final merge to main (Gate 5)`

Every other reference in the entire project -- including the ASCII diagram on line 58 of the same file, the summary table on lines 199-208, the quality-gates doc (line 68), and system-overview (line 109) -- calls it **Gate 4**.

**Impact:** An agent following the table will look for a "Gate 5" that doesn't exist elsewhere. This is a typo in one cell of one table.

**Fix:** Change `Gate 5` to `Gate 4` on line 159.

---

### C2. Duplicate Section Heading in `workflow-overview.md` -- FIXED

**Files:** `ai-process/processes/workflow-overview.md` lines 85-91 vs. lines 93-107.

**What's wrong:** Two consecutive sections both numbered "### 2. Task Breakdown":
- Lines 85-91: a short version that ends with "Human approves the task plan."
- Lines 93-107: a longer version titled "### 2. Task Breakdown + Architect Preflight" that replaces the first.

The first section is a leftover from before the Architect Preflight was added.
It also contains a stale claim: "Ends when: Human approves the task plan" -- the current process has no human gate on the task plan (the Architect Preflight replaced it).

**Impact:** Agents reading top-to-bottom will hit the stale section first and may believe human approval of the task plan is required, directly contradicting the intended autonomous flow.

**Fix:** Delete lines 85-91 entirely. Rename the remaining section to "### 2. Task Breakdown + Architect Preflight" (already its title).

---

### C3. Review Retry Count: Spec vs. Skill Contradiction -- FIXED

**Files:** `ai-process/processes/escalation-procedure.md` line 36 vs. `ai-process/processes/workflow-overview.md` lines 127-128, 153 vs. `.claude/skills/dev-loop/SKILL.md` lines 100-101 vs. `.claude/skills/bug-loop/SKILL.md` lines 103-105.

**What's wrong:** The escalation procedure defines the Reviewer's self-recovery threshold as:

> "One review cycle -- if fundamental design issues exist, escalate immediately"

This describes when the *Reviewer* should escalate (ESCALATE verdict) -- it's about the nature of the problem, not the retry count.

Meanwhile, `workflow-overview.md` and both loop skills allow **3 total review attempts** (2 retries) before forcing escalation:

> "On FAIL (cycles 1-2): sends task back to the Implementer" / "On FAIL (cycle 3): treat as ESCALATE"

These are not actually contradictory -- the escalation procedure describes when the Reviewer itself should issue an ESCALATE verdict (immediately, on design issues), while the loop skills describe the orchestrator's retry policy for FAIL verdicts (up to 3 cycles). But the phrasing is confusing because "one review cycle" sounds like it means "one attempt total."

**Impact:** Moderate ambiguity. An agent reading only the escalation procedure could interpret it as "only one review attempt allowed," conflicting with the loop's 3-attempt policy.

**Fix:** Clarify the escalation procedure's Reviewer row. Suggested wording:

> "One review cycle for ESCALATE-worthy issues -- if the code has fundamental design problems that no amount of implementer fixes can address, the Reviewer must issue ESCALATE immediately rather than FAIL. For ordinary quality issues, the Reviewer issues FAIL and the orchestrator allows up to three total review cycles before forcing escalation."

---

### C4. Bug-Loop Missing from the Workflow Specification -- FIXED

**Files:** `ai-process/processes/workflow-overview.md` (entire file) vs. `.claude/skills/bug-loop/SKILL.md` vs. `ai-process/architecture/component-map.md` line 32.

**What's wrong:** The component-map lists `bug-loop` as a skill. The skill itself is fully defined (166 lines). But `workflow-overview.md` -- the authoritative workflow document -- never mentions bug-loop. It references bugs only in passing:

> Line 167: "If integration fails, /dev-loop stops and files a bug -- the task branch is not deleted"

There is no section explaining when bug-loop runs, how it relates to dev-loop, or where it fits in the end-to-end flow.

**Impact:** Bug-loop has no spec authority. The process defines how bugs are *created* (by `integrate`) but not how they are *fixed*. This is a gap in the autonomous flow -- after dev-loop files bugs, the human must know to invoke `/bug-loop`, but the workflow doesn't tell them.

**Fix:** Add a section to `workflow-overview.md` (after the dev-loop section) describing the bug-fix flow:
- When bug-loop is invoked (after dev-loop stops due to regressions, or independently when bugs exist).
- How it relates to dev-loop (they don't run concurrently; bug-loop fixes regressions before dev-loop can resume).
- The end-to-end picture: dev-loop -> regressions filed -> human invokes bug-loop -> bugs resolved -> human re-invokes dev-loop.

---

### C5. No Content Boundary Rules for Agent Definitions vs. Skill Definitions

**Files:** `ai-process/architecture/system-overview.md` line 108 vs. all `.claude/agents/*.md` vs. all `.claude/skills/*/SKILL.md`.

**What's wrong:** The only guidance on agents vs. skills is one sentence in system-overview.md:

> "Separation of agents and skills -- agents are roles (who), skills are procedures (how)."

There are no rules defining what content belongs in an agent definition vs. a skill definition. In practice this causes redundancy and drift:

- Agent definitions include "Interaction Pattern" sections with "Receives Work From" / "Hands Off To" -- duplicating routing logic that is authoritatively defined in the orchestration skills (`dev-loop`, `bug-loop`, `integrate`).
- The component-map also has `Receives From` / `Hands Off To` columns for each agent, creating a third source.
- When the routing changes (e.g., Architect Preflight replacing a human gate), the skill gets updated but agent definitions and component-map may not -- leading to contradictions like the Reviewer's "Hands Off To: Integrator" (which was wrong because `/dev-loop` is the intermediary).

**Impact:** Multiple sources of truth for the same information. Stale handoff descriptions in agents can mislead the AI reading them at runtime.

**Fix:** Add a "Content Boundaries" section to `system-overview.md` that formalizes what belongs where:

- **Agent definitions** (`.claude/agents/*.md`): identity and constraints -- scope (folder access), decision authority (decide alone vs. escalate), quality bar, available skills. Informational context about typical interaction patterns is acceptable but the orchestration skills are authoritative for routing.
- **Skill definitions** (`.claude/skills/*/SKILL.md`): procedures and orchestration -- step-by-step instructions, input/output contracts, routing logic (who spawns whom, what happens on PASS/FAIL/ESCALATE).
- **Component-map** (`ai-process/architecture/component-map.md`): summary reference -- a quick-lookup table, not the source of truth. Should defer to agent and skill files for details.

**Status:** C5 fix was applied (Reviewer handoff corrected to route through `/dev-loop`). This broader fix would prevent similar drift in all agent definitions going forward. If adopted, the C5 change may need to be revisited -- the "Hands Off To" section could be removed entirely from agent files rather than corrected, since routing belongs in the skills.

---

## Moderate Findings

### M1. Integrator Agent Claims Task-to-Completed Write Access

**Files:** `.claude/agents/integrator.md` line 60 vs. `ai-process/architecture/system-overview.md` line 96 vs. `CLAUDE.md` line 69.

**What's wrong:** The Integrator agent's Folder Scope grants:

> Write / Edit: `project/tasks/` (move tasks to `completed/`)

But both `system-overview.md` and `CLAUDE.md` state that the `integrate` *skill* (not the Integrator *agent*) moves tasks to `completed/`:

> "The integrate skill is the only component that moves tasks to completed/" (CLAUDE.md line 69)

The Integrator agent handles conflict resolution and manual merges. The `integrate` skill handles the automated merge-test-promote flow.

**Impact:** Blurs the line between the agent and the skill. An Integrator agent instance could move tasks to `completed/` directly, bypassing the integrate skill's test verification.

**Fix:** Narrow the Integrator agent's write access to `project/tasks/pending/` (for creating fix tasks only). The `integrate` skill handles `completed/` transitions.

---

### M2. Architect: "Advisory" Label vs. Actual Authority -- FIXED

**Files:** `ai-process/architecture/component-map.md` line 16 vs. `.claude/agents/architect.md` lines 26-29 vs. `ai-process/processes/escalation-procedure.md` line 47.

**What's wrong:** The component-map describes the Architect as an "advisory role" with no skills. But the Architect agent definition and escalation procedure grant it concrete decision authority:

- Can adjust task scope within the bounds of the approved spec.
- Can add clarifying tasks to `pending/`.
- Can amend task descriptions.
- Can create corrective tasks during preflight.
- Gets multiple rounds of guidance per escalation issue.

This is active decision-making authority, not purely advisory.

**Impact:** The "advisory" label undersells the Architect's role and could confuse agents about whether to follow Architect directives or treat them as suggestions.

**Fix:** Update the component-map to describe the Architect as "advisory + structural authority" or similar. The key distinction: the Architect cannot change the spec or touch implementation code, but it *can* modify the task plan within spec bounds.

---

### M3. Write-Plan Orchestrates Architect Preflight Inline

**Files:** `.claude/skills/write-plan/SKILL.md` lines 46-55 vs. `ai-process/processes/workflow-overview.md` lines 100-107.

**What's wrong:** The write-plan skill spawns the Architect agent directly in Step 6 and waits for it to complete. This means the Planner agent must stay alive (consuming context) while the Architect runs its preflight.

The workflow spec describes Planner and Architect as sequential phases in the pipeline, not a caller-callee relationship. The intent is: Planner writes tasks -> Architect reviews -> human invokes dev-loop.

**Impact:** Tight coupling between Planner and Architect. If the Architect finds issues and flags them back to the Planner (write-plan Step 6: "If the Architect requests Planner revisions, address them and re-trigger the preflight"), this creates a retry loop inside a single skill invocation that could consume significant context.

**Recommendation:** This is a design choice, not a bug. The current approach works for small-to-medium plans. For larger plans, consider splitting Architect Preflight into a standalone skill invoked separately after write-plan completes. However, this adds an extra manual step for the human. The tradeoff is acceptable as-is -- flag for future consideration.

---

### M4. Bug Directory Structure: `in-progress/` Exists but Setup Guide Omits It -- FIXED

**Files:** `CLAUDE.md` line 17 vs. `guides/setup-guide.md` line 27 vs. actual filesystem vs. `.claude/skills/bug-loop/SKILL.md` lines 23, 48-49.

**What's wrong:** Three different sources disagree:

| Source | Bug directories listed |
|---|---|
| `CLAUDE.md` line 17 | `open/`, `in-progress/`, `resolved/` |
| `guides/setup-guide.md` line 27 | `open/`, `resolved/` (no `in-progress/`) |
| `guides/setup-guide.md` line 96 (CLAUDE.md template) | `open/`, `resolved/` (no `in-progress/`) |
| Actual filesystem | `open/`, `in-progress/`, `resolved/` (all three exist) |
| `bug-loop/SKILL.md` | Uses all three: `open/`, `in-progress/`, `resolved/` |
| `component-map.md` line 41 | `{open,in-progress,resolved}` |

The bug-loop skill actively uses `in-progress/` (moves bugs there in Step 3). CLAUDE.md and the component-map include it. The setup guide omits it.

**Impact:** A user following the setup guide won't create `project/bugs/in-progress/`, and bug-loop will fail when trying to move a bug file there.

**Fix:** Add `project/bugs/in-progress` to the setup guide's `mkdir` command (line 27) and the `.gitkeep` loop. Also update the CLAUDE.md template in the setup guide (line 96) to include `in-progress/`.

---

### M5. Reviewer Escalation Trigger Not in Spec -- FIXED

**Files:** `.claude/agents/reviewer.md` lines 37-38 vs. `ai-process/processes/escalation-procedure.md` lines 76-79.

**What's wrong:** The Reviewer agent lists this escalation trigger:

> "A security vulnerability is found that requires architectural discussion."

The escalation procedure's Reviewer triggers are:
> - Code has fundamental design issues that cannot be fixed without changing the specification.

Security vulnerabilities are not listed as a Reviewer escalation trigger in the spec. In the current process, a security issue found during review should result in a **FAIL** verdict with specific feedback -- the Implementer fixes it. Only if the security issue requires a spec change should it escalate.

**Impact:** The Reviewer might escalate security findings unnecessarily, halting the autonomous loop when a FAIL + feedback would suffice.

**Fix:** Remove the security escalation trigger from the Reviewer agent. Add a note instead: "Security vulnerabilities are caught during Stage 2 (Code Quality) and result in a FAIL verdict with specific remediation guidance. Only escalate if the vulnerability is architectural -- i.e., cannot be fixed without changing the specification."

---

### M6. No Spec Amendment Skill or Procedure

**Files:** `ai-process/processes/escalation-procedure.md` lines 68-69.

**What's wrong:** When a human decides to revise a spec during escalation, the procedure says:

> "Planner edits spec in-place, adds entry to the spec's Amendment Log section, identifies affected tasks, adds a note to each affected in-progress/ task referencing the amendment."

But there is no skill for this. There is no defined structure for the "Amendment Log section." The spec template (`.claude/skills/new-spec/assets/TEMPLATE-specification.md`) does include an Amendment Log section, but its format and rules are not documented in the process.

**Impact:** When a spec amendment is needed mid-cycle, the Planner has no structured procedure to follow. The amendment could be done inconsistently.

**Fix:** Either (a) add a lightweight `amend-spec` skill that formalizes the steps (edit spec, add Amendment Log entry with date/description/affected tasks, notify affected in-progress tasks), or (b) document the Amendment Log format and procedure in the escalation-procedure itself. Option (b) is simpler and sufficient.

---

### M7. Autonomy Gap: No Auto-Trigger for Bug-Loop After Regressions -- FIXED

**Files:** `.claude/skills/integrate/SKILL.md` lines 96-111 vs. `.claude/skills/dev-loop/SKILL.md` lines 90-94.

**What's wrong:** When integration finds regressions, the integrate skill files bugs via `/new-bug` and dev-loop stops. The human is told:

> "Next step for the human: resolve the filed bugs or unblock the task before re-running the loop."

But the process never tells the human to run `/bug-loop`. The connection between "bugs were filed" and "run bug-loop to fix them" is implicit.

**Impact:** A human unfamiliar with the process might try to fix bugs manually or not know bug-loop exists. The autonomous pipeline breaks at this handoff.

**Fix:** Update dev-loop's integration failure message to explicitly suggest: "Run `/bug-loop` to autonomously fix the filed regressions, then re-run `/dev-loop`." Also add this to the workflow-overview when bug-loop documentation is added (see C4).

---

### M8. Task Atomicity Criteria Undefined

**Files:** `ai-process/processes/quality-gates.md` line 29 vs. `.claude/agents/architect.md` line 56 vs. `.claude/skills/write-plan/SKILL.md` lines 63-66.

**What's wrong:** The Architect checks "task atomicity" during preflight, and write-plan defines atomicity as:

> "touches at most 3-4 files, has at most 5 acceptance criteria, and the description fits in ~20 lines"

This definition exists in write-plan and the planner agent but is NOT in the process spec documents (quality-gates.md or workflow-overview.md). The quality-gates doc just says "task atomicity" without defining it.

**Impact:** Low-moderate. The definition exists in the skill and agent, so it works in practice. But the spec layer should be authoritative -- if someone changes the threshold in write-plan, there's no spec to check it against.

**Fix:** Add the atomicity criteria to quality-gates.md under the Architect Preflight section.

---

## Low Findings

### L1. ADR Lifecycle Not Documented

**Files:** `CLAUDE.md` (no ADR lifecycle table) vs. `.claude/skills/new-adr/assets/TEMPLATE-adr.md`.

**What's wrong:** CLAUDE.md has lifecycle tables for specs, tasks, and bugs, but not for ADRs. The ADR template includes `status: proposed | decided | deprecated | superseded` but there's no transition table defining who changes the status and when.

**Fix:** Add an ADR lifecycle table to CLAUDE.md, similar to the existing ones.

---

### L2. No Example Documents in `project/`

**What's wrong:** All four `project/` directories (specs, tasks, bugs, decisions) are empty except for `.gitkeep` files. New users have no reference for what a correctly filled-out document looks like.

**Fix:** Add one example document per type. Mark them clearly as examples (e.g., prefix with `example-` or place in an `examples/` subdirectory).

---

### L3. Setup Guide Missing `/dev-loop` Stop Condition Explanation

**Files:** `guides/setup-guide.md` lines 167-178.

**What's wrong:** The setup guide's "Start Working" section tells the user to run `/dev-loop` but doesn't explain what happens when it stops (blocked task, escalation, empty queue) or what actions are needed for each.

**Fix:** Add a brief "What happens when `/dev-loop` stops" subsection after Step 6.

---

### L4. Redundant Logic Between Dev-Loop and Bug-Loop

**Files:** `.claude/skills/dev-loop/SKILL.md` vs. `.claude/skills/bug-loop/SKILL.md`.

**What's wrong:** Both orchestrators implement nearly identical patterns:
- Queue checking and priority selection.
- Claim work item (move file, create branch, commit state change).
- Spawn Implementer -> Spawn Reviewer -> Read Verdict cycle.
- PASS/FAIL/ESCALATE handling.
- Cycle counter reset logic.
- Hard stop conditions.

**Impact:** Maintenance burden. A change to the orchestration pattern (e.g., changing the retry count) must be made in two places.

**Recommendation:** This is a style/maintenance concern, not a correctness issue. The two loops differ in details (task vs. bug file paths, bug-loop's inline architect consultation, bug-loop's missing `blocked/` state). Consolidating would require abstracting over these differences, which adds complexity. Accept the duplication for now; revisit if the orchestration pattern changes.

---

### L5. Code-Review Skill Says "Hand Off to Integrator" (Step 4)

**Files:** `.claude/skills/code-review/SKILL.md` line 40.

**What's wrong:** Step 4 says "If all checks pass: PASS. Hand off to integrator." This mirrors the Reviewer agent's incorrect handoff (C5). The skill should say "Record PASS verdict" -- the orchestrator handles routing.

**Fix:** Change to "If all checks pass: **PASS**. Record the verdict."

---

### L6. Escalation Procedure: "One Attempt" Rule Limits Architect Effectiveness

**Files:** `ai-process/processes/escalation-procedure.md` line 83 vs. lines 47-48.

**What's wrong:** Line 83 states:

> "Once in the chain, the architect gets one consultation attempt. If that fails, escalate to human immediately. Do not loop."

But lines 47-48 state:

> "The architect may provide multiple rounds of guidance per issue. It continues until the problem is resolved, or until it determines that resolution requires a spec change or is beyond its authority."

These are contradictory. The first says one attempt; the second says multiple rounds.

**Impact:** Agents will follow whichever statement they read. This is an internal contradiction in a single document.

**Fix:** Reconcile. The intent appears to be: the Architect gets one *consultation engagement* (which may involve multiple rounds of back-and-forth), not one single message. Rewrite the Rules section to match:

> "Once in the chain, the architect engages with the problem (which may involve multiple rounds of guidance). If the architect determines it cannot resolve the issue, it escalates to human. The architect does not re-enter the chain for the same problem after escalation."

---

### L7. Conflict-Resolution Skill: Escalation Ownership Ambiguous

**Files:** `.claude/skills/conflict-resolution/SKILL.md` line 31.

**What's wrong:** Step 3 says "If the changes are incompatible, escalate to the architect" but doesn't clarify whether the *skill* escalates or the *Integrator agent* using the skill escalates. Skills are procedures, not actors -- they don't escalate; agents do.

**Fix:** Reword to: "If the changes are incompatible, stop and report that the conflict requires architectural guidance. The invoking agent (Integrator) is responsible for escalating to the Architect."

---

## Summary

| Severity | Count | Key themes |
|---|---|---|
| **Critical** | 5 | Gate numbering typo, duplicate heading, review retry ambiguity, bug-loop undocumented in spec, reviewer handoff bypasses orchestrator |
| **Moderate** | 8 | Integrator scope, architect label, write-plan coupling, bug dir mismatch, reviewer security trigger, no amendment procedure, no bug-loop auto-trigger, atomicity undefined in spec |
| **Low** | 7 | ADR lifecycle, no examples, guide gaps, loop redundancy, code-review handoff wording, escalation self-contradiction, conflict-resolution ownership |

### Top Priorities for Autonomous Flow

The stated goal is: human at the beginning to define the end result, then autonomous development and verification.

These findings most directly block that goal:

1. **C2 + C4**: The stale "human approves task plan" section and missing bug-loop documentation create confusion about where human intervention is actually needed. Fix both to make clear that only Gate 1 (spec) and Gate 4 (final merge) require humans.

2. **M7**: The pipeline breaks silently after regressions because nobody tells the human to run `/bug-loop`. Make the handoff explicit.

3. **C3 + L6**: The escalation procedure contradicts itself on retry counts and architect rounds. Clarify so agents don't halt prematurely or loop indefinitely.

4. **C1 + C5 + L5**: Mechanical fixes -- gate numbering typo, reviewer handoff wording -- that take minutes to fix and remove noise.

5. **M4**: The setup guide omits `bugs/in-progress/`, which will break bug-loop for any new project.
