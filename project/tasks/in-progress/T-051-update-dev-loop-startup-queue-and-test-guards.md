---
id: T-051
title: Update dev loop startup queue and test guards
status: pending
priority: high
assigned-role: planner
created: '2026-05-28'
spec: coordinated-process-and-cli-workflow-improvements
---

# Update dev loop startup queue and test guards

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

Update the dev-loop skill so it does not start autonomous task execution unless
the branch baseline is suitable. The loop must use the `ai-team` CLI task-listing
interface for pending queue discovery, discover the documented project test
command from project guidance, run that command before claiming a task, and
escalate to the human when the command is missing, ambiguous, or failing.

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

AC-1: WHEN dev-loop starts without a single-task argument THE SYSTEM SHALL use
the `ai-team` CLI task state filter to discover pending tasks.
AC-2: WHEN dev-loop starts THE SYSTEM SHALL discover the documented baseline
test command before claiming a task.
AC-3: WHEN the documented baseline test command passes THE SYSTEM SHALL allow
the loop to continue to task selection and claiming.
AC-4: IF the documented baseline test command is missing or ambiguous THEN THE
SYSTEM SHALL escalate to the human instead of starting the loop.
AC-5: IF the documented baseline test command fails THEN THE SYSTEM SHALL stop
and report the failing command and output summary.

## Dependencies

- `T-050` — root guidance templates define where project test commands should
  be documented.

## Files to Touch

- `cli/src/ai_team/init/sources/skills/dev-loop/body.md` — update startup,
  queue discovery, and baseline test guard instructions.
- `cli/src/ai_team/init/scaffolds/claude/skills/dev-loop/SKILL.md` —
  regenerated scaffold output for Claude.
- `cli/src/ai_team/init/scaffolds/codex/skills/dev-loop/SKILL.md` —
  regenerated scaffold output for Codex.

## Verification

```bash
cd cli
python scripts/sync_init_scaffolds.py
uv run pytest tests/test_init_scaffolds.py
uv run ruff format --check .
uv run ruff check .
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-05-28

**What was done.** Investigated the CLI surface before writing any code: ran `ai-team list tasks --help` and `ai-team list tasks --state pending` to confirm the correct filter flag is `--state`, not `--status`. Verified the baseline test command location by reading `cli/src/ai_team/init/sources/root/CLAUDE.md`, which has a `## Test` section with a placeholder comment — that is the canonical home the dev-loop must read. Read the existing `body.md` end-to-end and all 14 baseline tests before touching anything.

Followed TDD: wrote five failing tests in `tests/test_init_scaffolds.py` (one per AC) asserting that specific phrases appear in the body source and both scaffolds, confirmed they failed, then made surgical edits to `body.md`.

Changes to `body.md`:
- AC-1: replaced "list all files in `project/tasks/pending/`" with `ai-team list tasks --state pending` in Step 1, and updated the Input Requirements blurb to reference the CLI.
- AC-2–5: inserted a new **Step 2: Baseline Test Guard** that reads the `## Test` section of `CLAUDE.md`, escalates if the section is missing or ambiguous, runs the command, and stops with failure output if it fails. The step is annotated as startup-only (skip on subsequent loop iterations).
- Renumbered the old Steps 2–7 to Steps 3–8, and updated internal cross-references (`go back to **Step 4**` became `**Step 5**`, `Step 2` in Cycle Counter Reset became `Step 3`).

Ran `python scripts/sync_init_scaffolds.py` to regenerate both scaffold files. All 19 tests pass; ruff format and ruff check clean.

**What was tried and rejected.** Considered placing the baseline guard before Step 1 (queue discovery) as a "Step 0", but Step 2 is the natural position: Step 1 determines whether there is work to do at all, and the guard should only run if there is at least one pending task. The skip-on-loop-back annotation prevents redundant re-runs on every task iteration.

**What remains.** Nothing — all five ACs are covered by passing tests and the scaffold regeneration is committed.

**Obstacle for follow-up consideration.** AC-1 in the task spec used the phrase "task state filter" without naming the exact command. The actual CLI is `ai-team list tasks --state pending` (a subcommand of `list`, not `task`). No new surface was invented — documented the existing command.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
