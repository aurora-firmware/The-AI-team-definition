---
title: Handoff Note vs. claude-progress.txt — Audit
status: reference
created: 2026-04-18
---

# Handoff Note vs. `claude-progress.txt` — Audit

Decision memo framing the 8.7-variant brainstorm.
Answers the question: *extend, replace, or skip?*

---

## Recommendation

**Extend.**
These are two different artifacts solving two different problems, and the framework currently covers only one of them. Keep the handoff note for inter-agent boundaries and add a separate intra-agent cross-session continuity artifact.

---

## What the current handoff note actually is

| Aspect | Current behaviour |
|---|---|
| Template | `ai-process/templates/handoff-note.md` |
| Sections | What Was Done / What Remains / Current State of Files / Known Issues / Context for the Next Agent |
| Storage | Appended inline to the task file under `### Handoff Note — [date]` (dev-loop), or to a bug file's Notes section (bug-loop) — not a standalone file |
| Written by | Implementer, at the end of their work on a task |
| Read by | Reviewer (verifies criteria + handoff), Integrator (verifies spec compliance before merge) |
| Lifecycle | One-shot. Produced once per task/bug, at the agent boundary |
| Scope | Single-task. Describes a completed (or attempted) unit of work |

**Enforcement hooks:**
- `review-checklist.md:16` — any file modified outside the task's "Files to Touch" list must be justified in the handoff note or it is a **Fail**.
- `dev-loop/SKILL.md:61–62` and `bug-loop/SKILL.md:61` — implementer prompt explicitly instructs appending the handoff.
- `implementer.md:53` — documented as the deliverable to the reviewer.
- `integrate/SKILL.md:36` — the integrator reads the Notes/Handoff section as part of spec verification.

**What the handoff note is optimized for:** the *reviewer's* first read. It answers "what did the previous agent do and what do I need to know to evaluate or continue?"

## What `claude-progress.txt` is (research Section 5.1)

| Aspect | Pattern behaviour |
|---|---|
| Template | `Completed / In Progress / Next / Decisions Made` |
| Storage | Standalone file at task branch root, named `claude-progress.txt` |
| Written by | Initializer on first session; same coding agent appends at end of every subsequent session |
| Read by | The same coding agent, at the start of every subsequent session, before doing anything else |
| Lifecycle | Living document. Grows across sessions until the task is complete |
| Scope | Multi-session. Describes a work-in-progress unit that has not yet finished |

**What `claude-progress.txt` is optimized for:** the *same agent's* next session, after its context window resets. It answers "where am I, what did I already decide, and what was I about to do next?"

## Where they overlap, where they don't

**Overlap** — both record "what was done" and "decisions made." Any multi-session progress file that exists at the end of a task contains most of what the handoff also contains.

**Do not overlap:**
- Handoff note has no **In Progress** or **Next** sections. It assumes the work is finished.
- Handoff note is not read by the author themselves — it is an outbound message. `claude-progress.txt` is read by the author — it is working memory.
- Handoff note is inline in the task file. `claude-progress.txt` lives on the branch as a separate artifact so the agent can find it with a predictable path at session start.
- Handoff note is triggered by the dev-loop prompt at a single moment. `claude-progress.txt` is triggered at every session boundary.

**The gap the framework currently has:** no mechanism for an implementer to persist their own state mid-task across a context reset. If an implementer hits the context limit partway through a task, they must reconstruct state from `git log` plus whatever is in the task file. The handoff note does not fill this gap because it is not written (and not expected to be written) until the implementer is done.

## Implications for 8.7 brainstorm

The 8.7 spec should **add** a multi-session continuity mechanism without removing or restructuring the handoff note.

**User decision (2026-04-18):** the task file itself is the work log. Do **not** introduce a separate `claude-progress.md` file. The same pattern applies to bugs — the bug file serves as its own work log.

Implied shape (to confirm in the brainstorm):

- The task (and bug) file gains a **Work Log** section — a running, dated append-only log of what the agent did each session, what it tried that failed, and what it intends to do next.
- The implementer writes a work-log entry at the end of every session and reads the Work Log before doing anything else at the start of every subsequent session.
- The final handoff note remains as today, written once at task completion. It is distinct from the running log — the log is for the *same* agent; the handoff is for the *next* agent.
- No new template or file to manage; everything stays inside the task or bug file.
- Downstream skills (TDD, dev-loop, bug-loop) gain a step: "If the task/bug file has a Work Log section, read it before starting."

Open questions to resolve in the 8.7 brainstorm:
- Is the Work Log mandatory for every task/bug, or only when the agent actually resumes after a session break?
- Entry format — free prose, or structured (date / did / tried / next)?
- Where in the task file does it sit — before or after Notes? Before or after Handoff Note?
- Does the integrator preserve the log in `completed/`, or strip it on merge?
