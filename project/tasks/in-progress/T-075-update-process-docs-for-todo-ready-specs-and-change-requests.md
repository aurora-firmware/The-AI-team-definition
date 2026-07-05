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

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
