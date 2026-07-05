---
id: T-074
title: Add uninterrupted change-request continuation to source skills
status: pending
priority: high
assigned-role: developer
created: '2026-07-05'
---

# Add uninterrupted change-request continuation to source skills

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

Update the source change-request and architecture consistency review skills so
change-request intake continues through the S-004 process without unnecessary
human interruption.

The change-request skill must resolve each human-answerable TODO with relevant
context, get human approval of the TODO-free CR, then continue into architecture
consistency review. Planner-owned amendments and consistency fixes should
iterate using the approved CR as authoritative intent; only findings that would
change that approved intent stop for human decision.

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

AC-1: WHEN change-request creates or updates a CR THE SYSTEM SHALL resolve each
human-answerable `[TODO]` marker one at a time before asking for approval.
AC-2: WHEN the human approves a TODO-free CR THE SYSTEM SHALL continue to
architecture consistency review without returning only a passive next-owner
handoff.
AC-3: WHEN architecture consistency findings require Planner-owned spec
amendments THE SYSTEM SHALL route them to the Planner using the approved CR as
authoritative intent.
AC-4: IF a consistency finding would change the approved CR intent THEN THE
SYSTEM SHALL stop and ask the human to revise, reject, or reaffirm the CR.
AC-5: The system shall preserve the Architect boundary: the Architect reports
findings and routing, and does not edit specs directly.

## Dependencies

- `T-075` — process docs define approved CR authority and stopping conditions.

## Files to Touch

- `cli/src/ai_team/init/sources/skills/change-request/body.md` — add TODO
  resolution, human approval, automatic review continuation, and Planner
  iteration behavior.
- `cli/src/ai_team/init/sources/skills/architecture-consistency-review/body.md`
  — clarify approved CR intent authority and when findings route to Planner vs
  Human.

## Verification

```bash
rg -n "TODO|approved CR|change-request|Planner|Human|Architecture Consistency" cli/src/ai_team/init/sources/skills/change-request/body.md cli/src/ai_team/init/sources/skills/architecture-consistency-review/body.md
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
