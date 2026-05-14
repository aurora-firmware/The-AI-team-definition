---
id: T-042
title: Regenerate Claude and Codex skill scaffold outputs
status: pending
priority: medium
assigned-role: developer
created: '2026-05-14'
---

# Regenerate Claude and Codex skill scaffold outputs

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

Run the package-owned scaffold generator after T-036 has migrated shared skill sources.
This task owns the generated Claude and Codex skill scaffold outputs only. It should
not change canonical skill source files or generator logic.

The generated Codex skill scaffold must be real files/directories, not a symlinked view
of the Claude scaffold. The generated Claude and Codex skill files must have identical
normalized procedure body text.

## Acceptance Criteria

AC-1: WHEN the scaffold generator runs THE SYSTEM SHALL produce Claude skill files under `cli/src/ai_team/init/scaffolds/claude/skills/`.
AC-2: WHEN the scaffold generator runs THE SYSTEM SHALL produce Codex skill files under `cli/src/ai_team/init/scaffolds/codex/skills/` as real files, not symlinks.
AC-3: The system shall preserve identical normalized procedure body text between each generated Claude and Codex skill file.
AC-4: WHEN the scaffold generator runs twice THE SYSTEM SHALL leave no additional diff after the second run.
AC-5: The system shall not modify `cli/src/ai_team/init/sources/skills/**` in this task.

## Dependencies

- `T-035` — package-owned scaffold source generator must exist first
- `T-036` — shared skill source files must exist before output generation

## Files to Touch

- `cli/src/ai_team/init/scaffolds/claude/skills/**` — generated Claude skill output
- `cli/src/ai_team/init/scaffolds/codex/skills/**` — generated Codex skill output

## Verification

```bash
cd cli
python scripts/sync_init_scaffolds.py
test -f src/ai_team/init/scaffolds/claude/skills/tdd/SKILL.md
test -f src/ai_team/init/scaffolds/codex/skills/tdd/SKILL.md
test ! -L src/ai_team/init/scaffolds/codex/skills/tdd/SKILL.md
git diff -- src/ai_team/init/scaffolds/claude/skills src/ai_team/init/scaffolds/codex/skills > /tmp/t042-before.diff
python scripts/sync_init_scaffolds.py
git diff -- src/ai_team/init/scaffolds/claude/skills src/ai_team/init/scaffolds/codex/skills > /tmp/t042-after.diff
cmp /tmp/t042-before.diff /tmp/t042-after.diff
uv run pytest tests/test_init_scaffolds.py
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
