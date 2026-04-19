---
title: "Work Log in Task and Bug Files (Handoff / Progress Unification)"
version: "0.1"
status: approved
created: 2026-04-18
author: "planner"
---

# Work Log in Task and Bug Files (Handoff / Progress Unification)

## Purpose

The framework has no mechanism for an agent to resume its own work across a context-window reset mid-task.
If the implementer hits the context limit partway through, the next session reconstructs state from `git log` plus whatever is in the task file — decisions that never made it into code are lost.
The handoff note does not fill this gap: it is written once at the end of the work for the *next* agent (the reviewer), not for the author's own next session.

The state-of-the-art research (Section 5.1 and 8.7 of `state-of-the-art-research.md`) documents Anthropic's `claude-progress.txt` pattern — external memory that survives context limits.
The Phase 0 audit (`project/docs/handoff-audit.md`) confirmed the gap and resolved that the **task or bug file itself** should serve as the work log, rather than a separate file.

This specification replaces the `## Notes` section of tasks with a `## Work Log` section, adds the same section to bugs, and collapses the Handoff Note concept into the final Work Log entry.
Every session boundary produces a dated entry under a structured heading with free-prose body.
Every session start begins by reading the log.
The integrator preserves the log on merge.

Downstream consequence: every reference to "handoff note" across the repository is reworded to refer to the Work Log. A full-sweep approach is chosen so the framework stays coherent after merge, rather than leaving stale references for a follow-up task.

## Exclusions

- **A separate `claude-progress.md` or similar file.** The task or bug file is the log. No new file is introduced.
- **Retaining a distinct Handoff Note section or template.** The final Work Log entry serves the handoff role. `ai-process/templates/handoff-note.md` is deleted.
- **Structured subheadings within Work Log entries** (Did / Tried / Decisions / Next). The body is free prose under the dated heading.
- **Reviewer-written Work Log entries.** The Work Log belongs to the implementer. Reviewer output stays in the Review Verdict section.
- **Applying the Work Log pattern to specs, ADRs, or other non-work-unit documents.** The pattern is scoped to task and bug files.
- **Automated validation that each session wrote an entry.** Enforcement relies on implementer discipline and the dev-loop/bug-loop prompts, not on tooling.
- **Migration of tasks or bugs currently in flight.** Existing `## Notes` sections in in-progress tasks stay as-is until the task completes. New tasks and bugs created after the change go through the updated templates.
- **Changes to the integrator skill's merge behaviour.** The integrator does nothing new to the Work Log — preserve-as-is is literally no-op compared to today's handling of Notes.
- **Changes to what the reviewer reads.** The reviewer consumes the last Work Log entry in place of the old Handoff Note; the review process is unchanged otherwise.

## Architecture

### Design Principles

- **One file per work unit.** The task or bug file holds all of: description, acceptance criteria, files-to-touch, verification, Work Log (implementer), Review Verdict (reviewer). No sidecar files.
- **Mandatory, dated, free-prose entries.** Every session boundary produces an entry. The dated heading is structured; the body is free.
- **The last entry is the handoff.** Removing the separate Handoff Note keeps the history continuous — the reviewer reads the tail of the same log the implementer wrote.
- **Preserved on merge.** The Work Log stays in `completed/` and `resolved/` as archaeological record. No compression, no stripping.
- **Session start reads the log.** The first action of every implementer session is to read the Work Log before reading anything else. Even on the first session (where the log is empty) this rule is safe.
- **Full-sweep reference update.** Every repo-wide mention of "handoff note" is updated in this spec, so the framework is coherent at merge time.

### System Diagram

```
Session N starts
  │
  ├─ Step 0 (tdd skill): read the Work Log
  │
  ├─ Do work: red → green → refactor → commit
  │
  └─ Session N ends
        │
        └─ Append entry:
              ### Session N — YYYY-MM-DD
              <free prose: what was done, what was tried and rejected,
               decisions made, what's next>

Final session before review
  │
  └─ The last Work Log entry IS the handoff.
     Reviewer reads it in lieu of the former Handoff Note.

Integrator on merge
  │
  └─ Move task to completed/ (or bug to resolved/).
     Preserve the Work Log as-is. No edits.
```

### Responsibility Separation

| Component | Responsibility | Notes |
|---|---|---|
| `TEMPLATE-task.md` | Defines Work Log section; replaces former Notes section | Renamed, not added; section now mandatory |
| `TEMPLATE-bug.md` | Defines Work Log section | Additive — bugs had no Notes section today |
| `tdd/SKILL.md` | Read the Work Log at session start; append at session end | Adds Step 0 (read) and a Step 8 (append) |
| `dev-loop/SKILL.md` | Implementer prompt refers to Work Log, not Handoff Note | Prompt rewording only |
| `bug-loop/SKILL.md` | Same as dev-loop | Prompt rewording only |
| `implementer.md` agent def | "Hands off to" language refers to final Work Log entry | Removes reference to deleted handoff-note.md |
| `bootstrap-project/SKILL.md` | Does not list `handoff-note.md` as a project asset | Asset list trimmed |
| `guides/setup-guide.md` | Same trim as bootstrap | Documentation coherence |
| `review-checklist.md` | Stage 1 line reworded: out-of-scope file edits must be justified in the **Work Log** | Rule preserved; artifact name changed |
| `workflow-overview.md` | "handoff note appended to the task file" → "Work Log entry appended" | Doc coherence |
| `architecture/system-overview.md` | "Completion signal; handoff note in task file" → "Completion signal; Work Log entry in task file" | Doc coherence |
| `CLAUDE.md` | Template-map line "handoff notes (used when implementer hands off to reviewer)" removed; file deleted from `ai-process/templates/` list | Governance coherence |
| `README.md` | "Reusable document formats (handoff notes, etc.)" reworded | Surface-area coherence |
| `git-conventions.md` | "once more before handoff" → "once more before the final Work Log entry" | Coherence |
| `ai-process/templates/handoff-note.md` | Deleted | Source concept is absorbed into Work Log |

## Components

### Component 1: Task template — Work Log section

**Purpose:** Replace `## Notes` with `## Work Log`. Inside, include a template comment that shows the entry shape:

```markdown
## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

```

**Estimated size:** S (approximately 15 line-diff, one file).
**Interfaces:** Consumed by `/new-task`, by the implementer at every session boundary, by the reviewer (last entry) at Gate 2.

### Component 2: Bug template — Work Log section

**Purpose:** Additive — bug template gains `## Work Log` as a new section.
Positioned after `Fix Verification` and before any future sections.
Same template-comment guidance as Component 1.
**Estimated size:** S (approximately 15 line-diff, one file).
**Interfaces:** Consumed by `/new-bug`, by the implementer, by the reviewer at Gate 2.

### Component 3: TDD skill — session start and session end steps

**Purpose:** Add two procedural steps to `tdd/SKILL.md`:

- **Step 0 — Read the Work Log.** Before reading the acceptance criteria, read every existing entry in the Work Log. This is mandatory even on the first session (the log is empty; the step is a cheap no-op then).
- **Step 8 — Append a Work Log entry.** After refactor and before handing back to the orchestrator, append `### Session N — YYYY-MM-DD` with free-prose body summarising what was done, what was tried and rejected, and what remains. Session number increments monotonically across all sessions on this task or bug.

Also update Quality Criteria to include "The Work Log contains one entry per session boundary" and add a Common Pitfall: "Starting work without reading the Work Log."
**Estimated size:** S (approximately 20 line-diff, one file).
**Interfaces:** Invoked by the implementer during every session.

### Component 4: Dev-loop and bug-loop — implementer prompt rewording

**Purpose:** Rewrite the implementer-spawning prompt in both orchestrators.

- `dev-loop/SKILL.md` Step 4 prompt (today: "append a handoff note ... following the format in ai-process/templates/handoff-note.md") → "append a Work Log entry at session end. The entry's heading is `### Session N — YYYY-MM-DD`; the body is free prose covering what was done, what was tried and rejected, and what remains. The final entry serves as the handoff to the reviewer."
- `bug-loop/SKILL.md` Step 4 prompt — same rewrite, adapted to bugs.

**Estimated size:** S (approximately 10 line-diff across two files).
**Interfaces:** Spawn prompts consumed by the implementer.

### Component 5: Repository-wide reference sweep

**Purpose:** Update every remaining reference to "handoff note" to point at the Work Log. Delete the handoff-note template.

Files:
- `.claude/agents/implementer.md` — "Hands Off To" section
- `.claude/skills/bootstrap-project/SKILL.md` — asset list
- `ai-process/templates/handoff-note.md` — **deleted**
- `ai-process/guidelines/review-checklist.md` — Stage 1 out-of-scope file rule
- `ai-process/guidelines/git-conventions.md` — commit cadence table
- `ai-process/processes/workflow-overview.md` — implementer and reviewer step descriptions
- `ai-process/architecture/system-overview.md` — completion-signal row in communication table
- `CLAUDE.md` — repository map row for `ai-process/templates/`
- `README.md` — `templates/` bullet
- `guides/setup-guide.md` — copy-list for new projects
- `.claude/skills/integrate/SKILL.md` — the "Notes/Handoff sections" reading step (becomes "Work Log section")

**Estimated size:** M (approximately 30 line-diff across 11 files, most are one-line rewords).
**Interfaces:** These files are read by various agents and humans; coherence after merge is the goal.

## Workflow

```
Session N begins on task T-NNN
  │
  ├─ Implementer reads TEMPLATE-task.md          (skill reference)
  ├─ Implementer reads task file's Work Log      (Step 0)
  │  └─ decisions from prior sessions, what's next
  │
  ├─ Implementer does TDD work
  │  └─ commits per red → green → refactor cycle
  │
  └─ Session N ends (context running low, or task complete)
        │
        └─ Implementer appends:
              ### Session N — 2026-04-18
              Implemented login happy path. Tried
              exception-chained error handling first,
              rejected: too noisy for the unit tests.
              Decided to pass error codes through
              the result wrapper. Next: error paths
              and the "remember me" flag.
        │
        └─ If task is complete, this is also the handoff.
           Orchestrator calls the reviewer; reviewer
           reads the last entry instead of a Handoff Note.

Integrator on PASS
  │
  └─ Move task to completed/ (preserving Work Log);
     or move bug to resolved/ (preserving Work Log).
```

## Configuration

Not applicable — documentation and process change with no runtime configuration.

## Implementation Order

| Phase | What | Depends On |
|---|---|---|
| 1 | Update `TEMPLATE-task.md` (replace Notes with Work Log; add template comment) | Nothing |
| 2 | Update `TEMPLATE-bug.md` (add Work Log section) | Nothing |
| 3 | Update `tdd/SKILL.md` (Step 0 read-log; Step 8 append-entry; Quality Criteria; Common Pitfalls) | Phase 1 |
| 4 | Update `dev-loop/SKILL.md` and `bug-loop/SKILL.md` implementer prompts | Phases 1, 2, 3 |
| 5 | Update `.claude/agents/implementer.md`, `.claude/skills/bootstrap-project/SKILL.md`, `.claude/skills/integrate/SKILL.md` | Phases 1, 2 |
| 6 | Repository-wide sweep: `ai-process/guidelines/review-checklist.md`, `git-conventions.md`, `processes/workflow-overview.md`, `architecture/system-overview.md`, `CLAUDE.md`, `README.md`, `guides/setup-guide.md` | Phases 1–5 landed on the feature branch |
| 7 | Delete `ai-process/templates/handoff-note.md` | Phases 1–6 on branch; no remaining references |

Phase 7 must be last — the template file can only be removed when no other file references it.

## Alternatives Considered

- **Approach A: Minimal blast radius.** Change only the five named files plus delete the handoff-note template; leave all other references stale for follow-up bugs. Rejected: stale references in governance docs (CLAUDE.md, workflow-overview, review-checklist) would cause agent confusion between merge and cleanup.
- **Approach B: Sweep across templates and skills only.** Same as A plus implementer agent, bootstrap-project, setup-guide. Rejected in favour of C after explicit user decision: the user chose full coherence even though it touches guideline and architecture docs.
- **A separate `claude-progress.md` file.** Rejected during the Phase 0 audit by explicit user decision: "Use the task as some work log." A second file is unnecessary and creates a naming-and-storage problem.
- **Keep both Handoff Note and Work Log as distinct artifacts.** Rejected by explicit user decision at Step 2.5 clarification: the final Work Log entry doubles as the handoff. Simpler; one append area per work unit.
- **Opt-in Work Log via `multi-session: true` frontmatter flag.** Rejected by explicit user decision: mandatory on every task/bug. Uniform rules beat predictive flagging.
- **Structured entry format (Did / Tried / Decisions / Next subheadings).** Rejected by explicit user decision: dated heading is structured, body is free prose. Lower ceremony.
- **Reviewer writes into the Work Log too.** Rejected: Review Verdict remains a separate section. Work Log is implementer-only to keep authorship unambiguous.
- **Strip or summarise Work Log on merge.** Rejected by explicit user decision: preserve as-is. The archaeological value of the full log outweighs the tidiness cost.
- **Task-level out-of-scope field, Verification Examples, EARS sweep across other templates.** Out of scope — those belong to research items 8.6, 8.4, and 8.1 respectively and are handled separately (or deferred).

## Amendment Log

<!-- Left empty for now. Populate if amended after tasks are in flight.
| Date | What changed | Why | Affected tasks |
|------|-------------|-----|----------------|
-->
