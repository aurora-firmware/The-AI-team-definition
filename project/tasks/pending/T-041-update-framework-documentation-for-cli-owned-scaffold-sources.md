---
id: T-041
title: Update framework documentation for CLI-owned scaffold sources
status: pending
priority: medium
assigned-role: developer
created: '2026-05-14'
---

# Update framework documentation for CLI-owned scaffold sources

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

Update repository-level and process documentation for S-001's ownership change. Docs
must no longer describe repository-root `.claude/` and `.codex/` as the product source
of exported framework definitions. They should say those folders are local project
configuration for this repository, while CLI package sources own what `ai-team init`
exports.

Do not edit `cli/docs/` in this task; T-040 owns CLI docs.

## Acceptance Criteria

AC-1: The system shall document in `README.md` that CLI package scaffold sources are the product source for exported agents and skills.
AC-2: The system shall document in setup/customization guides that `ai-team init` no longer offers `--include-ai-process`.
AC-3: The system shall document in `ai-process/` architecture docs that `ai-process/` is not copied by init.
AC-4: The system shall remove stale instructions that say to sync package scaffolds from repository-root `.claude/` or `.codex/`.
AC-5: The system shall preserve the process semantics while updating only ownership/source-of-truth wording.

## Dependencies

- `T-035` — repository docs must reference the implemented package-source generator flow
- `T-036` — repository docs must reflect the package-owned shared skill source-of-truth
- `T-037` — repository docs must reflect the package-owned Claude/Codex agent source assets
- `T-042` — repository docs must reflect generated Claude/Codex skill scaffold outputs
- `T-043` — repository docs must reflect generated Claude/Codex agent scaffold outputs
- `T-038` — repository docs must reflect the final init contract with no ai-process export
- `T-040` — repository docs should align with the finalized CLI docs wording

## Files to Touch

- `README.md` — update repository map, setup notes, and maintainer scaffold rule
- `guides/setup-guide.md` — remove include-ai-process and root-copy scaffold instructions
- `guides/customization-guide.md` — update customization source-of-truth guidance
- `ai-process/architecture/component-map.md` — update component/source mapping
- `ai-process/architecture/system-overview.md` — update source-of-truth wording

## Verification

```bash
rg -n -- '--include-ai-process|sync_init_scaffolds.py.*\\.claude|sync_init_scaffolds.py.*\\.codex|\\.codex/skills ->|symlinked \\.codex/skills' README.md guides ai-process
uv run pytest
```

The `rg` command should return no stale ownership or removed-option references. If it
returns intentional historical references, the Work Log must explain why they remain.

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
