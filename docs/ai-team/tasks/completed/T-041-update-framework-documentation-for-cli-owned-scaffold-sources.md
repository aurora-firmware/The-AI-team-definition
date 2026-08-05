---
id: T-041
title: Update framework documentation for CLI-owned scaffold sources
status: completed
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

### Session 1 — 2026-05-15

This session implemented T-041 in full. The task was a docs-only update to bring five files in line with S-001's ownership change: the CLI package sources in `cli/src/ai_team/init/sources/` are the authoritative origin for what `ai-team init` exports, not the repository-root `.claude/` or `.codex/` folders, and `ai-process/` is the spec layer only and is never exported by init.

The verification command (`rg` pattern search) was used as the test harness. The initial run found two stale references in `README.md`: both `--include-ai-process` lines (lines 150 and 153). The `symlinked \.codex/skills` pattern also matched the Agent Platform Compatibility section, which needed rephrasing.

Changes made:

- **README.md**: Removed `--include-ai-process` option block and replaced it with a note that `ai-process/` docs are not exported. Updated the Agent Platform Compatibility section to state `.claude/` and `.codex/` are local project configuration, not product export sources. Updated the repository structure comment for `.codex/`. Updated the maintainer "Changing bundled init content" bullet to name the correct source path (`cli/src/ai_team/init/sources/`). Clarified the `sync_init_scaffolds.py` comment in the local build snippet.

- **guides/setup-guide.md**: Replaced Step 3 "Copy the Framework Files" (which listed individual files to copy manually from the repo root) with "Export the Framework Files" directing users to run `ai-team init`. Added a note in Step 7 clarifying what `sync_init_scaffolds.py` reads from.

- **guides/customization-guide.md**: Renamed "What to Copy As-Is" to "What ai-team init Exports As-Is" and removed the rows that incorrectly listed `ai-process/` docs (process docs, guidelines, architecture docs, and `ai-process/templates/`) as things to copy. Added a clear paragraph stating `ai-process/` is not exported.

- **ai-process/architecture/component-map.md**: Added "(spec layer only — not exported by `ai-team init`)" to the Purpose column for Process Docs, Guidelines, and Architecture Docs. Added a new row for CLI Scaffold Sources pointing to `cli/src/ai_team/init/sources/`.

- **ai-process/architecture/system-overview.md**: Added Design Decision #6 "Spec layer vs. export layer" documenting the separation between the `ai-process/` spec layer and the CLI package export layer.

Nothing was rejected or revisited — the scope was clear from the rg pattern and ACs. All 228 existing pytest tests pass. No intentional historical references remain.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-05-15

PASS

Both Stage 1 (spec compliance) and Stage 2 (code quality) pass.

**Stage 1 — Spec compliance**

- AC-1 met: `README.md` line 117 explicitly states "The authoritative sources that `ai-team init` exports to adopting projects live in the CLI package under `cli/src/ai_team/init/sources/`." Line 150 clarifies "from the CLI package scaffold sources." The maintainer bullet at line 236 names `cli/src/ai_team/init/sources/` as the correct place to edit bundled init content.
- AC-2 met: `README.md` removes the `--include-ai-process` flag and its example block. `guides/setup-guide.md` Step 3 removes the flag entirely — no remaining reference. `guides/customization-guide.md` removes the rows listing `ai-process/` docs as items to copy and adds a clear "not exported" paragraph.
- AC-3 met: `ai-process/architecture/component-map.md` adds "(spec layer only — not exported by `ai-team init`)" to each of Process Docs, Guidelines, and Architecture Docs. `ai-process/architecture/system-overview.md` adds Design Decision #6 explicitly stating `ai-process/` is not exported by `ai-team init`.
- AC-4 met: `guides/setup-guide.md` replaces the manual file-copy list (Step 3) with an `ai-team init` invocation. The verification `rg` command returned no matches (exit 1), confirming all stale root-copy and removed-flag patterns are gone.
- AC-5 met: Workflow steps, gate references, CLAUDE.md guidance, `/dev-loop`, `/bug-loop`, and Gate 1–5 descriptions are unchanged in `guides/setup-guide.md`. Process semantics are preserved throughout.

Files modified by commit `01bdc3c` are exactly the five files listed in the task's "Files to Touch" section. No out-of-scope files were modified by this commit.

**Stage 2 — Code quality**

This is a documentation-only task; no executable code was added or modified. Readability is good: wording is precise, section headings accurately reflect the new content, and no dead or contradictory prose remains. No hardcoded credentials, parameterized queries, or performance concerns are applicable.

The Work Log records the `rg` verification result and 228 pytest tests passing. No intentional stale references remain that would require explanation.
