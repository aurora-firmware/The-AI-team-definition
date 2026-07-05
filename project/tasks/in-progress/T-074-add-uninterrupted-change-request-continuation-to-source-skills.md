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

### Session 1 — 2026-07-05

Implemented T-074 by adding a focused source-body test for the new change-request continuation contract, then updating the two source skill bodies to match it. The change-request skill now requires human-answerable `[TODO]` markers to be resolved one at a time with context before approval, requires approval of the TODO-free CR, and then continues directly into Architecture Consistency Review instead of stopping with only a passive handoff. The architecture-consistency-review skill now treats an approved change-request as authoritative intent for Planner-owned consistency fixes, routes those fixes to the Planner when they preserve that intent, and stops for Human decision only when a finding would change the approved change-request intent. The Architect boundary stays explicit: findings and routing only, never direct spec edits.

For the red step, I created `cli/tests/test_t074_change_request_continuation.py` and ran it in isolation. The first attempt failed for environment reasons because `uv` tried to write to a read-only cache path, so I reran with `UV_CACHE_DIR` under `/tmp`; that produced the intended red state with four failing assertions across the new acceptance criteria. After patching the source files, the new test file passed, the existing T-068 change-request body test still passed, and the task verification grep succeeded. I also regenerated the bundled scaffold skill outputs with `python scripts/sync_init_scaffolds.py` so the generated init assets stay aligned with the source-of-truth skill bodies, and then committed the cycle on the task branch.

I rejected two things while working: first, relying only on the task grep as the acceptance harness, because the repository already has a clear pattern of source-body tests and this change needed behavior-level assertions; second, leaving the scaffold outputs stale after changing source skill bodies, because that would break the repo’s source-of-truth and generated-output convention. Nothing remains on the implementation branch. The next step is for the loop to append this entry to the canonical task file on `dev-agent` and hand the task to review.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-07-05
PASS

Summary:
- Reviewed T-074 on `task/T-074-add-uninterrupted-change-request-continuation-to-source-skills` at `16994e5`; Stage 1 acceptance and Stage 2 quality checks both passed.

Artifacts:
- Canonical task file updated on `dev-agent`: `project/tasks/in-progress/T-074-add-uninterrupted-change-request-continuation-to-source-skills.md`
- Diff reviewed from `16994e5` across the two requested source skill bodies, the focused test, and regenerated scaffold outputs
- Primary files inspected: `cli/src/ai_team/init/sources/skills/change-request/body.md`, `cli/src/ai_team/init/sources/skills/architecture-consistency-review/body.md`, `cli/tests/test_t074_change_request_continuation.py`

Evidence:
- Stage 1: AC-1 and AC-2 are satisfied in `change-request/body.md` by the one-at-a-time human `[TODO]` resolution loop, TODO-free approval gate, and direct continuation into Architecture Consistency Review
- Stage 1: AC-3, AC-4, and AC-5 are satisfied in `architecture-consistency-review/body.md` by treating the approved change-request as authoritative intent, routing Planner-owned amendments without changing that intent, stopping for Human decision when intent would change, and restating that the Architect reports findings and never edits specs directly
- Stage 1: scope matched the task request; the only extra files were the focused source-body test and regenerated scaffold outputs implied by the repo conventions
- Stage 2: `UV_CACHE_DIR=/tmp/uv-cache-t074 uv run pytest tests/test_t074_change_request_continuation.py` passed (`5 passed`)
- Stage 2: `UV_CACHE_DIR=/tmp/uv-cache-t074 uv run pytest tests/test_t068_change_request_common_pitfalls.py` passed (`5 passed`)
- Stage 2: `UV_CACHE_DIR=/tmp/uv-cache-t074 uv run ruff check tests/test_t074_change_request_continuation.py` passed
- Stage 2: `UV_CACHE_DIR=/tmp/uv-cache-t074 uv run ruff format --check tests/test_t074_change_request_continuation.py` passed
- Stage 2: `rg -n "TODO|approved CR|change-request|Planner|Human|Architecture Consistency" cli/src/ai_team/init/sources/skills/change-request/body.md cli/src/ai_team/init/sources/skills/architecture-consistency-review/body.md` confirmed the required contract language
- Stage 2: `git diff --check dev-agent..HEAD` returned clean

Obstacles Encountered:
- None during review

Next Owner:
- Development Loop

Next Action:
- Integrate `task/T-074-add-uninterrupted-change-request-continuation-to-source-skills` into `dev-agent`
