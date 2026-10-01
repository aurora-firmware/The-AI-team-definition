---
id: T-107
title: Port filesystem layer and slug generation
status: in-progress
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Port filesystem layer and slug generation

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 3**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P30 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- port core/fs.py (read, atomic write, move, update status, ArtifactExists/ArtifactNotFound messages) and python-slugify-equivalent slugs incl. transliteration; test slugs against every T-089 title.

## Acceptance Criteria

AC-1: slugs equal fixture filenames (SC-5).
AC-2: atomic writes.
AC-3: existing destination error equals Python's.
AC-4: V-PI passes (SC-9).

## Dependencies

- `T-089` — Seed fixtures for artifact-creation commands
- `T-106` — Port frontmatter models and byte-identical YAML dump

## Files to Touch

- pi/src/core/{fs,slug}.ts
- tests

## Verification

```bash
# V-PI.
# V-PI: cd pi && npm ci && npm run typecheck && npm test   # after V-SYNC
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-10-01
Done: I ported slug generation and the filesystem layer to TypeScript.
- `pi/src/core/slug.ts` is a python-slugify-equivalent `slugify`, using the `transliteration` package plus the full HTML 4 entity table.
- `pi/src/core/fs.ts` has the two error classes and `readArtifact`, `writeArtifact`, `moveArtifact` and `updateStatus`. Messages are copied from Python. Writes are atomic through a `.tmp~` sibling file and a rename, which is cleaned up on failure.
- `updateStatus` infers the artifact kind with the same field-name heuristic as Python.
- Tests cover every `*-new--*` fixture title against its created filename, the `*--artifact-exists` fixture messages, and the move and status behaviours.
- `typecheck` and `npm test` pass, and the cli pytest and ruff checks are clean.

Tried and rejected:
- I first assumed apostrophes are dropped (`dont-stop`). Python gives `don-t-stop`, because quotes become hyphens first and are stripped afterwards, so the test was corrected.
- I did not add a table of text-unidecode and `transliteration` differences. The euro sign gives "EU" instead of "EUR". Nothing in the fixtures hits it, and I documented it in `slug.ts`.

Remaining and follow-ups:
- The T-106 follow-ups are still open. A standalone comment after an unknown collection key is dropped on rewrite. A `>-` block scalar on a known field throws `FrontmatterError` where Python parses it. Unusual frontmatter keys throw `RangeError`, which `readArtifact` and `updateStatus` do not convert to `FrontmatterError`. All three are in `frontmatter.ts` and `scalar-emitter.ts`, outside this task's files, and still need a separate task.
- `readArtifact` accepts `change-request` as a kind, which Python's fs does not. `updateStatus` infers a change request as an ADR, as Python does, which is harmless because the fields are the same.
- Divergences from Python: `readArtifact` and `updateStatus` catch ENOENT instead of checking `exists()` first (same message, no race); `moveArtifact` resolves symlinks on the existing part of a path like `Path.resolve()`.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
