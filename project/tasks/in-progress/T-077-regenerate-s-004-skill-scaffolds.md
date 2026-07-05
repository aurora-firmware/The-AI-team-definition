---
id: T-077
title: Regenerate S-004 skill scaffolds
status: pending
priority: medium
assigned-role: developer
created: '2026-07-05'
---

# Regenerate S-004 skill scaffolds

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

Regenerate the exported Claude and Codex skill scaffolds for every source skill
changed by S-004 after the source bodies are updated.

This task should run the repository's scaffold sync command from `cli/` and
verify that generated scaffolds contain both spec TODO-readiness behavior and
uninterrupted CR continuation with approved-intent routing. Do not edit
repo-local `.codex/` or `.claude/` folders.

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

AC-1: WHEN the scaffold sync command runs THE SYSTEM SHALL update generated
Claude and Codex brainstorm and new-spec scaffolds from their source skill
bodies.
AC-2: WHEN the scaffold sync command runs THE SYSTEM SHALL update generated
Claude and Codex change-request and architecture consistency review scaffolds
from their source skill bodies.
AC-3: The system shall keep generated Claude and Codex procedural body text
aligned with the source skill bodies.
AC-4: IF generated scaffolds are stale after synchronization THEN THE SYSTEM
SHALL fail verification with a visible diff.

## Dependencies

- `T-074` — source change-request and architecture consistency review skill
  bodies contain the CR continuation behavior.
- `T-076` — source spec-authoring skill bodies contain the TODO-readiness rule.

## Files to Touch

- `cli/src/ai_team/init/scaffolds/claude/skills/change-request/SKILL.md` —
  regenerated scaffold output.
- `cli/src/ai_team/init/scaffolds/codex/skills/change-request/SKILL.md` —
  regenerated scaffold output.
- `cli/src/ai_team/init/scaffolds/claude/skills/architecture-consistency-review/SKILL.md`
  — regenerated scaffold output.
- `cli/src/ai_team/init/scaffolds/codex/skills/architecture-consistency-review/SKILL.md`
  — regenerated scaffold output.
- `cli/src/ai_team/init/scaffolds/claude/skills/brainstorm/SKILL.md` —
  regenerated scaffold output.
- `cli/src/ai_team/init/scaffolds/codex/skills/brainstorm/SKILL.md` —
  regenerated scaffold output.
- `cli/src/ai_team/init/scaffolds/claude/skills/new-spec/SKILL.md` —
  regenerated scaffold output.
- `cli/src/ai_team/init/scaffolds/codex/skills/new-spec/SKILL.md` —
  regenerated scaffold output.

## Verification

```bash
cd cli && python scripts/sync_init_scaffolds.py && uv run pytest tests/test_init_scaffolds.py tests/test_t064_skill_bodies_canonical.py tests/test_t066_codex_frontmatter_parity_decision.py
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-07-05

Read the canonical task file and confirmed the Work Log was empty before starting. I reviewed the relevant source skill bodies and scaffold tests to map the acceptance criteria to existing verification coverage, then ran the required scaffold sync command from `cli/` followed by the task verification suite with `UV_CACHE_DIR=/tmp/uv-cache-t077`. The sync completed successfully and the pytest selection passed in full.

I then checked the owned scaffold outputs directly for the S-004 behaviors this task called out: change-request continues into Architecture Consistency Review after a TODO-free approval and preserves approved-intent routing, while brainstorm and new-spec preserve the human-answerable TODO-readiness flow and spec status transition to review. I also verified the task-owned scaffold files remained clean after synchronization with no git diff, which means the generated outputs were already current on this branch and no manual edits or regeneration commits were needed.

I initially probed a tool-specific `sources/claude/...` layout and rejected that path after confirming the generator actually reads shared bodies from `cli/src/ai_team/init/sources/skills/<skill>/body.md`. Nothing remains on the task branch unless the loop wants to record this no-op verification result back on `dev-agent`.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
