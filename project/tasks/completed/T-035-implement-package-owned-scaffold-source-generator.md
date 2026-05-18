---
id: T-035
title: Implement package-owned scaffold source generator
status: completed
priority: medium
assigned-role: developer
created: '2026-05-14'
---

# Implement package-owned scaffold source generator

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

Spec S-001 requires the CLI package to own exported scaffold sources instead of syncing
from repository-root `.claude/`, `.codex/`, or `ai-process/`. Update the scaffold sync
helper so it reads package-owned sources under `cli/src/ai_team/init/sources/` and writes
generated package data under `cli/src/ai_team/init/scaffolds/`.

This task implements the generator mechanics and tests with minimal fixture data. It
does not migrate the full real framework assets yet; that is T-036 and T-037.

Required generator behavior:
- create the empty `project/` lifecycle skeleton as before;
- generate Claude and Codex skill scaffold files from a shared skill body plus
  tool-specific metadata/frontmatter;
- copy package-owned Claude/Codex agent source files into scaffold output;
- never read repository-root `.claude/`, `.codex/`, or `ai-process/`.

## Acceptance Criteria

AC-1: WHEN `cli/scripts/sync_init_scaffolds.py` is executed THE SYSTEM SHALL populate `cli/src/ai_team/init/scaffolds/project/` with the existing empty lifecycle skeleton.
AC-2: WHEN package-owned shared skill sources exist THE SYSTEM SHALL generate matching Claude and Codex skill scaffold bodies with only tool-specific header metadata differing.
AC-3: WHEN package-owned agent source files exist THE SYSTEM SHALL copy them into the matching Claude and Codex scaffold agent directories.
AC-4: The system shall not read repository-root `.claude/`, `.codex/`, or `ai-process/` while generating scaffold outputs.
AC-5: IF stale scaffold output exists THEN THE SYSTEM SHALL replace it during generation.

## Dependencies

- None

## Files to Touch

- `cli/scripts/sync_init_scaffolds.py` — replace root-snapshot sync with package-source scaffold generation
- `cli/tests/test_init_scaffolds.py` — update tests to cover package-owned source fixtures and no root reads

## Verification

```bash
cd cli
uv run pytest tests/test_init_scaffolds.py
uv run ruff check scripts/sync_init_scaffolds.py tests/test_init_scaffolds.py
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-05-14
Implemented the package-owned scaffold source generator in `cli/scripts/sync_init_scaffolds.py` and rewrote `cli/tests/test_init_scaffolds.py` around package-source fixtures. The generator now reads only `cli/src/ai_team/init/sources/`, regenerates `project/` lifecycle skeleton, generates Claude/Codex skill scaffolds from shared `body.md` plus per-tool TOML headers, copies package-owned Claude/Codex agents into scaffold outputs, and replaces stale generated content on each run.

I worked in two TDD cycles. First cycle added a failing skill-generation/no-root-read test and implemented source-based skill generation plus agent copying; I also removed obsolete root snapshot logic. Second cycle added explicit tests for project skeleton generation and agent subtree replacement. That cycle exposed a real defect where skill regeneration deleted the entire `scaffolds/` root, removing `project/`; I rejected keeping the broad delete and narrowed replacement to per-tool `skills/` directories only. I also rejected relying on hidden-file globbing for `.gitkeep` assertions and switched to `os.walk` for deterministic file collection in tests.

Remaining work in this task branch is complete from a Developer perspective; next step is for the loop to append this entry to the canonical task file on `dev-agent` and proceed to review.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-05-14
PASS

Stage 1 PASS: All acceptance criteria are satisfied by the branch diff in `cli/scripts/sync_init_scaffolds.py` and `cli/tests/test_init_scaffolds.py`, with no unexpected file changes.
Stage 2 PASS: Correctness, test coverage for the required behaviors, readability, and performance/security checks are acceptable for task scope. Verification commands passed on the implementation branch.
