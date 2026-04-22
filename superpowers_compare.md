# Comparison: The AI Team Definition vs. obra/superpowers

## Structural Philosophy

| Dimension | This project | superpowers |
|---|---|---|
| **Core metaphor** | A formal organization with a constitution | A methodology/playbook |
| **Authority layer** | `ai-process/` is the spec; agents/skills implement it | Skills ARE the process; no separate spec layer |
| **Primary concern** | Governance, correctness, auditability | Execution speed, isolation, verification |

---

## Workflow Phases

Both follow roughly the same shape: brainstorm → plan → implement → review → integrate.
The key differences are in structure and enforcement.

**This project:**
1. Brainstorm (Planner + human interactive)
2. Spec approval (Gate 1 — hard human stop)
3. Architect Preflight (automated structural validation)
4. `/dev-loop` (autonomous Developer → Reviewer → Integrator cycles)
5. Final merge sign-off (Gate 4 — hard human stop)

**superpowers:**
1. Brainstorming (interactive, one-question-at-a-time)
2. Git worktree setup (isolated workspace)
3. Writing plans (concrete, code-level tasks, 2–5 min each)
4. Subagent-driven development (parallel or serial dispatch)
5. TDD (per-task enforcement)
6. Finishing a development branch (test → 4 options: merge/PR/keep/discard)

**Key gap in superpowers:** No explicit "Gate 4" equivalent — no formal final human sign-off step before merging to main.
The `finishing-a-development-branch` skill presents options but does not mandate human approval.

**Key gap in this project:** No git worktree isolation.
Superpowers treats worktrees as a first-class isolation primitive; this project uses feature branches but does not enforce worktree-based workspace separation.

---

## Agent Model

**This project:** 5 named, specialized agents with explicit decision authority, folder scope, escalation thresholds, and quality bars:
Planner, Architect (advisory/preflight), Developer, Reviewer, Integrator.

**superpowers:** 1 defined agent (`code-reviewer.md`).
All other roles are executed by invoking skills against the active session — no distinct agent personas for Planner, Developer, etc.
The human or orchestrator uses skills directly.

**Implication:** This project's multi-agent model makes accountability explicit (who can touch what files, who escalates to whom).
Superpowers is lighter-weight but less traceable — there is no formal record of which "agent" made a decision.

---

## Skills Comparison

| Capability | This project | superpowers |
|---|---|---|
| Brainstorming | `brainstorm` (batched questions, 6-category checklist) | `brainstorming` (one question at a time, visual companion offered) |
| Planning | `write-plan` (EARS-format ACs, YAML frontmatter tasks) | `writing-plans` (concrete code-level steps, 2–5 min each) |
| TDD | `tdd` | `test-driven-development` (stronger "Iron Law" framing) |
| Code review | `code-review` (2-stage: spec compliance + quality) | `requesting-code-review` + `receiving-code-review` |
| Debugging | `debug` | `systematic-debugging` |
| Integration | `integrate` (diff verification, regression detection, revert) | `finishing-a-development-branch` (simpler: test + 4 options) |
| Conflict resolution | `conflict-resolution` (explicit intent-preservation) | — (not a separate skill) |
| Parallel agents | — | `dispatching-parallel-agents` |
| Workspace isolation | — | `using-git-worktrees` |
| Verification gate | Embedded in `code-review` + `integrate` | `verification-before-completion` (standalone, emphatic) |
| Orchestration | `dev-loop`, `bug-loop` | `subagent-driven-development`, `executing-plans` |
| Task tracking | `new-task`, `new-bug`, `new-spec`, `new-adr`, `status-report` | Plan docs in `docs/superpowers/plans/` (no state machine) |
| Skill authoring | — | `writing-skills` |

---

## Task/State Tracking

**This project:** File-system state machine.
Tasks live in `pending/ → in-progress/ → completed/` (or `blocked/`).
Moving the file IS the state change.
Frontmatter `status` field mirrors it.
Full Work Log in each task file.

**superpowers:** Plan documents in `docs/superpowers/plans/YYYY-MM-DD-*.md`.
No formal state transitions, no blocked state, no dependency graph in the task files.
Tasks are concrete implementation steps within a plan document, not independent trackable units.

**Verdict:** This project's approach is better for team coordination and asynchronous handoffs.
Superpowers' approach is better for single-session solo work — lower ceremony, faster to start.

---

## Quality Gates & Enforcement

**This project** has 4 explicit numbered gates with pass/fail criteria defined in `quality-gates.md`:
- Gate 1 (Spec Approval): human
- Architect Preflight: automated structural validation
- Gate 2 (Code Review): Reviewer agent, 2-stage
- Gate 3 (Integration Tests): automated, with revert on regression
- Gate 4 (Final Merge): human

**superpowers** has behavioral enforcement through skills:
- `verification-before-completion`: "NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE"
- `finishing-a-development-branch`: test verification before presenting merge options
- `brainstorming`: hard gate before any implementation action
- No Architect Preflight equivalent
- No formal regression revert logic

---

## What superpowers Has That This Project Lacks

1. **Git worktrees as first-class primitive** — Every feature gets an isolated workspace.
   Prevents accidental cross-contamination, gives a clean baseline test run before any work starts.

2. **`dispatching-parallel-agents`** — Explicit skill for parallelizing independent problem domains.
   The `dev-loop` here is sequential; superpowers acknowledges parallelism as a first-class strategy.

3. **`verification-before-completion`** — A standalone, emphatic skill that enforces fresh evidence before any completion claim.
   This project handles this through checklist items buried inside `code-review` and `integrate`, but it is less forceful as a standalone guarantee.

4. **`writing-skills`** — Meta-skill for creating new skills following best practices.
   This project has no equivalent — skills are created manually.

5. **One-question-at-a-time brainstorming** — Superpowers enforces sequential clarification questions, which produces more focused conversations.
   The `brainstorm` skill here batches ~5 questions, which is efficient but can overwhelm.

6. **Concrete plan steps (2–5 min granularity)** — Superpowers' `writing-plans` produces code-level, copy-pasteable steps with exact commands and expected output.
   The `write-plan` skill here produces higher-level task units with EARS criteria and a verification command — better for multi-agent handoff, but less immediately executable.

7. **Multi-platform support** — Superpowers ships with `.codex/`, `.cursor-plugin/`, `.opencode/`, `GEMINI.md` out of the box.
   This project has `.codex/` symlinks but is primarily Claude Code-native.

---

## What This Project Has That superpowers Lacks

1. **A formal specification layer** (`ai-process/`) — Process rules are specified separately from their implementation.
   When agent behavior and process diverge, the process wins.
   Superpowers has no such separation.

2. **Architecture Decision Records** — Formal ADR workflow in `project/decisions/`.
   No equivalent in superpowers.

3. **Bug lifecycle** — Formal open/in-progress/resolved state machine for bugs with its own templates.
   Superpowers treats bugs as tasks without a separate tracking model.

4. **Architect Preflight** — Before the dev-loop starts, an Architect agent validates structural correctness of the entire task plan (dependency correctness, file conflict risk, architectural consistency).
   No equivalent in superpowers.

5. **Regression detection with revert** — The `integrate` skill explicitly compares pre/post-merge test failures and reverts + files bugs if regressions appear.
   Superpowers' `finishing-a-development-branch` runs tests but has no automated revert logic.

6. **Escalation procedure** — Explicit escalation chain (agent → architect → human) with defined thresholds (3 failed attempts for Developer, etc.).
   Superpowers has less formal guidance on when and how to escalate.

7. **Spec/task lifecycle tracking** — Specifications move through draft → review → approved → superseded.
   Tasks have explicit dependency graphs and frontmatter linking them to specs.
   Superpowers has none of this.

8. **`conflict-resolution` as dedicated skill** — Explicit intent-preservation semantics for merge conflicts.
   Superpowers relies on TDD + `finishing-a-development-branch` to catch problems post-merge.

---

## Summary Assessment

| Axis | Winner |
|---|---|
| Governance & auditability | **This project** |
| Team/multi-agent coordination | **This project** |
| Execution speed & low ceremony | **superpowers** |
| Workspace isolation | **superpowers** |
| Parallelism support | **superpowers** |
| Verification enforcement | **superpowers** (clearer, standalone) |
| State tracking | **This project** |
| Regression safety | **This project** |
| Platform portability | **superpowers** |
| Extensibility / skill authoring | **superpowers** |

The two projects solve adjacent problems.
**superpowers** is optimized for a single developer or session working fast with strong verification habits.
**This project** is optimized for a multi-agent team where accountability, traceability, and safe integration matter more than raw speed.

---

## Actionable Gaps to Consider Closing

1. **Add git worktree support** — Add a `using-git-worktrees` skill or incorporate worktree setup into `dev-loop` as a precondition.

2. **Add `verification-before-completion`** — Either adopt as a standalone skill or reinforce as a top-level directive in each agent definition rather than only a checklist item inside `code-review`.

3. **Add `dispatching-parallel-agents`** — The architecture supports parallel task execution but `dev-loop` does not exploit it.
   Independent tasks with no shared files could run concurrently.

4. **Add `writing-skills`** — A meta-skill for authoring new skills with consistent structure and quality would close the extensibility gap.