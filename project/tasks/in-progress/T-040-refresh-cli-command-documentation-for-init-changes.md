---
id: T-040
title: Refresh CLI command documentation for init changes
status: pending
priority: medium
assigned-role: developer
created: '2026-05-14'
---

# Refresh CLI command documentation for init changes

<!--
Task Quality Rules (see the new-task skill for full details):
  - Atomic — one clear outcome.
  - One-shottable — ≤ 3–4 files touched, ≤ 5 ACs, Description ≈ 20 lines.
  - Verifiable — concrete Verification command or explicit manual steps.
  - Self-contained — Description is enough to start without follow-up questions.
  - EARS — every AC matches one of the five patterns below.
  - Dependency-honest — list every prior task this one reads from or modifies.
-->

## Description

Update the CLI-owned documentation after the init command contract changes. Regenerate
the command reference so `--include-ai-process` disappears, and update the CLI usage
guide to describe Claude/Codex scaffolding from package-owned assets with no ai-process
export option.

This task owns `cli/docs/` only. Broader repository and ai-process documentation updates
are T-041.

## Acceptance Criteria

AC-1: WHEN the command docs are regenerated THE SYSTEM SHALL NOT list `--include-ai-process`.
AC-2: The system shall document that `ai-team init --tools codex` scaffolds `.codex/agents/` and `.codex/skills/`.
AC-3: The system shall document that `ai-team init` never copies `ai-process/`.
AC-4: The system shall document the package-owned scaffold source/generator maintenance flow in `cli/docs/usage.md`.

## Dependencies

- `T-035` — CLI docs must describe the package-owned scaffold generator that actually exists
- `T-036` — CLI docs must reflect the package-owned skill source layout and generated Codex skills
- `T-037` — CLI docs must reflect the package-owned agent source layout and generated Codex agents
- `T-042` — CLI docs must reflect generated Codex skill scaffold output
- `T-043` — CLI docs must reflect generated Codex agent scaffold output
- `T-038` — command docs must reflect the updated init command
- `T-039` — docs should match the verified init behavior

## Files to Touch

- `cli/docs/commands.md` — regenerate command reference
- `cli/docs/usage.md` — update init and maintainer scaffold sections

## Verification

```bash
cd cli
bash scripts/gen_docs.sh
! grep -q -- '--include-ai-process' docs/commands.md
grep -q '.codex/agents' docs/usage.md
grep -q 'never copies `ai-process/`' docs/usage.md
uv run pytest tests/test_usage_guide.py
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
