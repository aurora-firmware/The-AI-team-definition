---
id: T-106
title: Port frontmatter models and byte-identical YAML dump
status: in-progress
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Port frontmatter models and byte-identical YAML dump

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 3**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P29 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- port core/models.py parse/dump for all five artifact kinds with the same required-field and FrontmatterError messages; dump byte-identical to ruamel round-trip (key order, quoting, Unicode, folding width); pin with golden strings from T-089 after trees.

## Acceptance Criteria

AC-1: the dump of every artifact in the T-089 after-trees equals the fixture bytes (SC-5). [G2 B2]
AC-2: malformed/missing-key errors equal Python messages.
AC-3: same folding width.
AC-4: V-PI passes (SC-9).

## Dependencies

- `T-089` — Seed fixtures for artifact-creation commands
- `T-100` — Pi package skeleton

## Files to Touch

- pi/src/core/{models,frontmatter}.ts
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
Done: ported the five frontmatter models and parsers, `FrontmatterError`, `splitFrontmatter` and `dumpFrontmatter`. The dump is byte-identical to the Python ruamel round-trip. The key piece is `pi/src/core/scalar-emitter.ts`, a port of ruamel 0.19's block-mapping scalar emitter (`analyze_scalar`, style choice, plain, single-quoted and double-quoted writers, width 80, and comment-column handling). I chose that over the `yaml` package because its quoting and folding rules differ from ruamel's. `yaml` is used only to parse and to re-render collections under unknown keys.

A parsed model keeps a source map holding key order, comments, blank lines and unknown keys, like Python's `_source_map`. In-place updates and optional-key removal and append follow Python. A hand-built model dumps in canonical order.

Verification:
- I built a throwaway differential harness against ruamel (1,536 scalars including random strings, plus 11 documents) and it found zero diffs.
- A curated subset is pinned as inline goldens.
- AC-1 is covered by a test that dumps every CLI-written artifact in all T-089 after-trees and compares bytes. All five artifact kinds appear.
- AC-2 is covered by checking `validate--*` fixture messages against the parser output.

Tried and rejected: `yaml`'s own `stringify` for the dump, because it folds and quotes differently from ruamel.

Not strict red-green: the emitter was written as a port first and then verified differentially. The committed tests came afterwards.

Known divergences, none exercised by fixtures:
- YAML parse-error text after the "YAML parse error in frontmatter of <path>:" prefix differs, because the parser is different.
- A known field whose value is a collection raises FrontmatterError, where Python would run `str()` on it.
- Unusual keys (multiline, empty, or 128 characters or more) throw RangeError, where Python writes an explicit `? ` key.
- Flow-style top-level mappings are not given special handling.
- Collections and block scalars under unknown keys are re-rendered through `yaml`, which loses the original style and inner comments.
- The scalar emitter file is 432 lines, over the 300-line guideline.

Remaining: nothing for T-106. The later port of `fs.py` (`read_artifact`, `update_status`, `write_artifact`) can use `parseXText`, `extractBody` and `dumpFrontmatter` directly.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
