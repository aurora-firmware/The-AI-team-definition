---
id: T-075
title: Update process docs for TODO-ready specs and change requests
status: pending
priority: high
assigned-role: developer
created: '2026-07-05'
---

# Update process docs for TODO-ready specs and change requests

<!--
Task Quality Rules (see the new-task skill for full details):
  - Atomic — one clear outcome.
  - One-shottable — ≤ 3–4 files touched, ≤ 5 ACs, Description ≈ 20 lines.
  - Verifiable — concrete Verification command or explicit manual steps.
  - Self-contained — Description is enough to start without follow-up questions.
  - EARS — every AC matches one of the five EARS patterns below.
  - Dependency-honest — list every prior task this one reads from or modifies.
-->

## Description

Update the process documentation for S-004 so the framework contract states the
new artifact-readiness and change-request continuation rules before skill bodies
implement them.

The workflow docs must say specs and change-requests cannot advance to
Architect review, approval, or task breakdown while human-answerable `[TODO]`
markers remain. They must also say an approved, TODO-free change-request is the
authoritative intended change for procedural consistency fixes, while findings
that would alter that approved intent stop for human decision.

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

AC-1: WHEN the Planner creates or amends a spec THE SYSTEM SHALL document that
human-answerable `[TODO]` markers are resolved before Architect consistency
review or Gate 1 approval.
AC-2: WHEN the Planner creates a change-request THE SYSTEM SHALL document that
human-answerable `[TODO]` markers are resolved one at a time before human
approval.
AC-3: WHEN a human approves a TODO-free change-request THE SYSTEM SHALL document
that the approved change-request is authoritative for Planner-owned consistency
fixes.
AC-4: IF Architect findings would modify the approved change-request intent THEN
THE SYSTEM SHALL document that the process stops for human decision.
AC-5: The system shall keep Gate 2 focused on task-plan readiness and shall not
add a new human review gate for accepted change-requests.

## Dependencies

- None

## Files to Touch

- `ai-process/processes/workflow-overview.md` — add TODO readiness and
  uninterrupted change-request continuation to the documented flow.
- `ai-process/processes/quality-gates.md` — add the pre-review artifact
  readiness rule and accepted change-request consistency semantics.

## Verification

```bash
rg -n "TODO|change-request|Architecture Consistency|Gate 1|Gate 2" ai-process/processes/workflow-overview.md ai-process/processes/quality-gates.md
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-07-05

Updated `ai-process/processes/workflow-overview.md` and `ai-process/processes/quality-gates.md` to align the written process contract with S-004. The docs now state that human-answerable `[TODO]` markers must be resolved before a spec goes to Architecture Consistency Review or Gate 1, and before a change-request goes to human approval. They also state that once a TODO-free change-request is approved, the Planner uses that approved request as the authoritative statement of intent for consistency-driven amendments, and the process stops for human decision if an Architect finding would alter that approved intent.

I used the task verification grep as the red/green acceptance harness because the task scope only allowed touching the two process-doc files. I checked the current workflow and quality-gate text first, compared it against the approved S-004 spec language, and rejected adding any new Gate 2 approval step because the task explicitly forbids that. After the wording update, I re-ran the verification command, checked the diff for scope and clarity, and committed the cycle on the task branch.

Nothing remains on the implementation branch. The next step is for the loop to append this Work Log entry to the canonical task file on `dev-agent` and send the task to review.

### Session 2 — 2026-07-05

Addressed the reviewer’s Stage 1 finding in `ai-process/processes/quality-gates.md`. The Architecture Consistency Review section now explicitly says that an amended spec must be made TODO-free before Architect consistency review continues, and the check paragraph now states that both draft specs and amended specs must have human-answerable `[TODO]` markers resolved before the Architect runs the consistency check. This keeps AC-1 aligned across both spec creation and spec amendment paths without changing the Gate 2 boundary.

For the red step, I used a narrow text check looking for explicit amended-spec TODO-readiness language and confirmed it was absent. I rejected a broader grep first because it falsely matched lines that happened to contain both “amended” and “TODO” in different clauses. After the patch, I re-ran the narrow check, then the full task verification command, and confirmed the diff stayed limited to the requested file. The fix was committed on the task branch.

Nothing remains on the implementation branch from this fix cycle. The next step is for the loop to append this Session 2 Work Log entry to the canonical task file on `dev-agent` and return the task to review.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-07-05
FAIL

- **File and location** — `ai-process/processes/quality-gates.md`, `Architecture Consistency Review` (`When` and `Check` paragraphs).
- **What is wrong** — The new TODO-readiness rule is explicit for draft specs before Gate 1 and for change-requests before approval, but it is not documented for amended specs before Architect consistency review. AC-1 requires the process docs to state that when the Planner creates or amends a spec, human-answerable `[TODO]` markers are resolved before Architect review or Gate 1 approval.
- **What should change** — Update the spec-amendment wording so the Architecture Consistency Review section also requires amended specs to be TODO-free before the Architect review proceeds, instead of limiting that readiness rule to draft specs.

### Review Verdict — 2026-07-05
PASS

The prior AC-1 gap is resolved: `ai-process/processes/quality-gates.md` now explicitly requires amended specs to be made TODO-free before Architect consistency review continues, and the consistency-check description now covers both draft specs and amended specs. Stage 1 passes for all acceptance criteria, the change remains limited to the expected process-doc files, and Stage 2 passes for correctness, readability, and scope. Docs-only verification was appropriate here; the submitted grep checks and `git diff --check` support the result.
