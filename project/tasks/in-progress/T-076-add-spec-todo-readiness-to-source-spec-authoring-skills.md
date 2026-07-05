---
id: T-076
title: Add spec TODO readiness to source spec-authoring skills
status: pending
priority: high
assigned-role: developer
created: '2026-07-05'
---

# Add spec TODO readiness to source spec-authoring skills

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

Update the source skill definitions that create specs so they follow S-004's
pre-review TODO readiness rule.

The brainstorm flow should still collect enough context before writing the spec,
but after the spec exists it must scan for `[TODO]` markers and ask the human one
contextual question at a time until human-answerable TODOs are resolved. The
direct new-spec flow must not hand a spec to Architect consistency review while
human-answerable TODOs remain.

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

AC-1: WHEN brainstorm creates a spec THE SYSTEM SHALL scan the created spec for
`[TODO]` markers before setting or treating the spec as review-ready.
AC-2: WHEN brainstorm finds a human-answerable `[TODO]` marker THE SYSTEM SHALL
ask the human one contextual question and update the spec with the answer before
continuing to the next marker.
AC-3: IF human-answerable `[TODO]` markers remain in a created spec THEN THE
SYSTEM SHALL NOT hand the spec to Architect consistency review or Gate 1
approval.
AC-4: WHEN new-spec prepares a draft for architecture consistency review THE
SYSTEM SHALL require human-answerable TODOs to be resolved first or explicitly
report the blocker.

## Dependencies

- `T-075` — process docs define the TODO readiness rule and review handoff.

## Files to Touch

- `cli/src/ai_team/init/sources/skills/brainstorm/body.md` — add the
  post-creation TODO resolution loop before review readiness.
- `cli/src/ai_team/init/sources/skills/new-spec/body.md` — prevent direct
  new-spec handoff to architecture review while human-answerable TODOs remain.

## Verification

```bash
rg -n "TODO|Architecture Consistency|Gate 1|review" cli/src/ai_team/init/sources/skills/brainstorm/body.md cli/src/ai_team/init/sources/skills/new-spec/body.md
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-07-05

Implemented T-076 by adding a focused pytest file for the brainstorm/new-spec TODO-readiness rules, then updating the two source skill bodies so brainstorm scans created specs for `[TODO]` markers before review readiness, resolves human-answerable markers one contextual question at a time, and blocks Architecture Consistency Review plus Gate 1 while such markers remain. I also updated new-spec so human-answerable `[TODO]` markers are an explicit blocker before Architecture Consistency Review, then regenerated the Claude and Codex skill scaffolds from source.

I first wrote the new test with case-sensitive phrase checks, but rejected that exact-match approach after the post-implementation failures showed the wording was present and only capitalization differed; the final assertions keep the behavior contract while avoiding that noise. I also hit two environment/tooling issues during verification: `uv` initially failed because its default cache path was not writable in this sandbox, and the commit hook rejected the new test file until `ruff format` was run. Nothing remains on the task branch. The next step is for the loop to append this entry to the canonical task file on `dev-agent` and continue into review.

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

Result: PASS

Summary:
- Reviewed T-076 against all four acceptance criteria plus Stage 2 quality checks; the brainstorm and new-spec source skill bodies now gate review readiness on resolving human-answerable `[TODO]` markers, and the focused tests plus regenerated scaffolds align with that behavior.

Artifacts:
- Updated canonical task file: `project/tasks/in-progress/T-076-add-spec-todo-readiness-to-source-spec-authoring-skills.md`
- Reviewed diff from commit `103bcfb` on branch `task/T-076-add-spec-todo-readiness-to-source-spec-authoring-skills`
- Primary files inspected: `cli/src/ai_team/init/sources/skills/brainstorm/body.md`, `cli/src/ai_team/init/sources/skills/new-spec/body.md`, `cli/tests/test_t076_spec_todo_readiness.py`, and the regenerated Claude/Codex scaffold skill files

Evidence:
- Stage 1 acceptance review: verified AC-1 through AC-4 directly in the reviewed source text, including the TODO scan, one-question-at-a-time resolution loop, review-handoff blocking, and explicit new-spec blocker behavior
- Scope review: confirmed the change set is limited to the requested source files plus focused tests and regenerated scaffolds
- Commands run on the implementation branch: `env UV_CACHE_DIR=/tmp/uv-cache-t076 uv run pytest tests/test_t076_spec_todo_readiness.py` (`5 passed`), `env UV_CACHE_DIR=/tmp/uv-cache-t076 uv run pytest tests/test_t064_skill_bodies_canonical.py` (`19 passed`), `env UV_CACHE_DIR=/tmp/uv-cache-t076 uv run pytest tests/test_init_scaffolds.py -k tool_skill_scaffolds_from_shared_body` (`1 passed`), `env UV_CACHE_DIR=/tmp/uv-cache-t076 uv run ruff check tests/test_t076_spec_todo_readiness.py`, and `rg -n "TODO|Architecture Consistency|Gate 1|review" cli/src/ai_team/init/sources/skills/brainstorm/body.md cli/src/ai_team/init/sources/skills/new-spec/body.md`

Obstacles Encountered:
- none

Next Owner:
- Development Loop

Next Action:
- none
