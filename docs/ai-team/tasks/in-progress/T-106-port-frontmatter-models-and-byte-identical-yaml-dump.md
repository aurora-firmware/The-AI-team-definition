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

### Review Verdict — 2026-10-01
PASS

Both stages passed. Reviewed `feat/pi-extension...task/T-106-...` (250ba8e, 81ad715): 5 files, `pi/src/core/{frontmatter,models,scalar-emitter}.ts` plus two test files.

Stage 1 (acceptance criteria):
- AC-1 met. `models.test.ts` dumps every CLI-written artifact in all T-089 after-trees (all five kinds, asserted) and compares bytes.
- AC-2 met. The three `frontmatter-invalid` messages in the `validate--*` fixtures (no frontmatter, no fence, missing `title`) are asserted equal to the parser output. `FrontmatterError` messages for unclosed fence and missing/null key match `_require` and `_parse_yaml_frontmatter` text.
- AC-3 met. Width 80 and code-point column arithmetic are ported from ruamel; folding is pinned by goldens and by my independent check below.
- AC-4 met. In a temporary worktree: `sync_init_scaffolds.py` left no tracked diff; `uv run pytest` 1022 passed; `ruff format --check` and `ruff check` clean; pi `npm ci`, `npm run typecheck` clean, `npm test` 164 passed.
- Scope: `scalar-emitter.ts` is outside Files to Touch but is the implementation the task needs (see below). No other unexpected files.

Stage 2 (quality):
- TypeScript checklist: no `any`, no non-null `!`, no `@ts-*` directives, no `eslint-disable`, no `as` assertions in `src/` (the only `as const` are in tests). External YAML input is narrowed with `isScalar`/`isMap`/`typeof` guards; the models use a `kind` discriminant with an exhaustive `switch`. Errors are typed `FrontmatterError`.
- Independent byte-identity check against ruamel (Python `dump_frontmatter` vs TS `dumpFrontmatter`), run by me with a throwaway harness that is not committed:
  - 389 scalars used as title and assigned-role: indicator and quote cases, YAML 1.1/1.2 booleans, null, number, date and timestamp lookalikes, leading/trailing spaces, tabs, newlines, control characters, NBSP, U+2028, combining marks, CJK, emoji, 79/80/81-character runs, multi-space runs, long plain, single-quoted and double-quoted scalars, plus 300 random strings. 0 diffs.
  - Parse, update (`status` and `title` changed to tricky values) and dump over 116 artifacts taken from before/after trees of all parity cases, plus hand-written documents with trailing comments, unknown keys and quoted forms. 0 diffs on all 116 fixture-derived documents.
- Tests cover success and error paths, are independent, and are pinned with inline goldens.

Judgements requested:
- `scalar-emitter.ts` (432 lines, over the 300-line guideline): accept. It is a cohesive port of ruamel's scalar analysis, style choice and three writers; splitting it would separate tightly coupled state and hurt traceability to the Python source. Not a blocker; no task-scope amendment needed since it is the core of the "byte-identical" outcome.
- Port-then-verify instead of red-green: accept, with the process note that it was disclosed. The committed tests pin the contract, and my independent differential run found no diffs. The throwaway differential harness is not committed, so the 1,536-scalar run cannot be repeated by others; non-blocking.
- Known divergences: none is a contract gap for S-005 or the fixtures. The `validate--*` fixtures contain only the three messages above and all match. Everything else is unfixtured and not produced by CLI-written artifacts:
  - YAML parse-error text after the prefix: ruamel's multi-line message cannot reasonably be reproduced from a different parser. Not fixtured.
  - Collection values on known fields: raises `FrontmatterError` rather than Python's `str()` of the collection.
  - Unusual keys throw `RangeError` (Python writes an explicit `? ` key).
  - Flow-style top-level mappings.

Non-blocking observations for follow-up (suggest a bug or a note on the later `validate`/`fs` port task):
1. My probe found that a standalone comment line placed after a collection value under an unknown key is dropped on rewrite (Python keeps it). This is the disclosed "loses inner comments" behaviour, but it is data loss on a hand-edited file once `update_status` is ported. Worth fixing or documenting before the `fs.py` port.
2. A hand-written block-scalar (`>-`) value on a known field, e.g. `title`, raises `FrontmatterError` where Python parses and rewrites it. Same follow-up.
3. `RangeError` for unusual keys should become a `FrontmatterError` or be handled when the `validate` port lands, so one malformed file cannot abort a whole scan.
4. When `validate` is ported, decide how the unfixtured "YAML parse error" message is to be compared across the runners.

Next owner: Development Loop.

