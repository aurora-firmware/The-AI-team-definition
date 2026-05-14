---
id: T-036
title: Migrate shared skill sources into the CLI package
status: pending
priority: medium
assigned-role: developer
created: '2026-05-14'
---

# Migrate shared skill sources into the CLI package

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

Using the generator contract from T-035, create the package-owned shared skill source
tree under `cli/src/ai_team/init/sources/skills/`. Each exported skill must have one
canonical body source plus metadata needed to generate Claude and Codex skill files.

This task owns only canonical skill sources and source-level parity/idempotence tests.
It must not update the generated scaffold output trees; T-042 owns generating
`scaffolds/claude/skills/**` and `scaffolds/codex/skills/**`.

Do not change skill procedure semantics while moving the source copy.

## Acceptance Criteria

AC-1: The system shall store each exported skill body exactly once under `cli/src/ai_team/init/sources/skills/`.
AC-2: The system shall store tool-specific skill metadata separately from the shared skill body text.
AC-3: WHEN source-level scaffold tests run THE SYSTEM SHALL verify every exported skill has shared body text and metadata required by the generator.
AC-4: The system shall not modify `cli/src/ai_team/init/scaffolds/claude/skills/` or `cli/src/ai_team/init/scaffolds/codex/skills/` in this task.
AC-5: The system shall preserve the existing exported skill procedure semantics in the package-owned source files.

## Dependencies

- `T-035` — package-owned scaffold source generator must exist first

## Files to Touch

- `cli/src/ai_team/init/sources/skills/**` — canonical shared skill bodies and metadata
- `cli/tests/test_init_scaffolds.py` — source-level coverage for required skill source files and metadata

## Verification

```bash
cd cli
uv run pytest tests/test_init_scaffolds.py
uv run ruff check tests/test_init_scaffolds.py
git diff --name-only -- src/ai_team/init/scaffolds/claude/skills src/ai_team/init/scaffolds/codex/skills
# final git diff command should print nothing for this task
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-05-14
Implemented T-036 by migrating every currently exported skill into package-owned canonical sources at `cli/src/ai_team/init/sources/skills/<skill>/` with exactly one `body.md` plus separate `metadata.toml` holding per-tool headers (`[claude].header`, `[codex].header`). The source body text was copied from existing scaffold skill procedure content to preserve behavior semantics, while tool-specific frontmatter moved into metadata for generator consumption.

Used TDD: first added a failing source-level test in `tests/test_init_scaffolds.py` that required the new source tree and validated per-skill body/metadata presence plus parity with existing exported Claude scaffold skill content. Then implemented the source tree migration and made the test pass. Refactor step fixed Ruff line-length issues in the new test without changing behavior.

What I tried and rejected: I did not modify generated scaffold output trees (`scaffolds/claude/skills/**`, `scaffolds/codex/skills/**`) because AC-4 forbids it in this task; I also avoided embedding headers into `body.md` to keep metadata separated per AC-2.

What remains: append this Work Log entry to the canonical task file on `dev-agent`, then proceed to reviewer cycle.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
