---
id: "T-003"
title: "Implement frontmatter parser and artifact data models"
status: pending
priority: high
assigned-role: developer
created: 2026-05-10
---

# Implement frontmatter parser and artifact data models

## Description

Implement `ai_team.core.models` providing dataclasses for the four artifact types — `Task`, `Bug`, `Spec`, `Adr` — parsed from YAML frontmatter using `ruamel.yaml` in round-trip mode (preserves comments and key order, which we want when rewriting frontmatter via lifecycle commands).

Each model holds the common fields (`id`, `title`, `status`, `created`) plus type-specific fields:
- `Task`: `priority`, `assigned-role`, optional `spec` reference
- `Bug`: `severity`, optional `task` reference
- `Spec`: `version`, `author`
- `Adr`: `status` (proposed | accepted | superseded), optional `supersedes`

Provide `parse_task(path)`, `parse_bug(path)`, `parse_spec(path)`, `parse_adr(path)`, and a generic `dump_frontmatter(model, body) -> str`. Raise `FrontmatterError` naming the missing or invalid field on parse failure. Pure module; no I/O beyond reading the supplied path.

## Acceptance Criteria

AC-1: WHEN `parse_task(path)` runs on a task file with valid frontmatter THE SYSTEM SHALL return a `Task` instance with all common and type-specific fields populated.
AC-2: WHEN `dump_frontmatter(model, body)` runs THE SYSTEM SHALL produce output that round-trips through the matching `parse_*` to an equal model.
AC-3: IF a required frontmatter field is missing or has an invalid value THEN THE SYSTEM SHALL raise `FrontmatterError` whose message names the field and the source path.
AC-4: The system shall preserve YAML comments and key order across parse/dump cycles.

## Dependencies

- `T-001` — needs the `ai_team` package and `ruamel.yaml` declared in `pyproject.toml`

## Files to Touch

- `cli/src/ai_team/core/models.py` — dataclasses, parsers, dumper, `FrontmatterError`
- `cli/tests/test_models.py` — round-trip and error-path tests

## Verification

```bash
cd cli && uv run pytest tests/test_models.py -q
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. -->

### Session 1 — 2026-05-10

Implemented `ai_team.core.models` from scratch using TDD. Read the task file, spec at `project/specs/ai-team-python-cli.md` (Component 5 and Responsibility Separation), and all four artifact templates (TEMPLATE-task.md, TEMPLATE-bug.md, TEMPLATE-specification.md, TEMPLATE-adr.md) to establish the exact frontmatter shapes.

One design decision required reconciliation: the TEMPLATE-adr.md uses `number` as the identifier key while the task description specifies `id`. I used `id` for the `Adr` dataclass because the task description is explicit about it and `id` is the consistent naming convention across all other artifact types. The ADR template uses `number: 0` (an integer placeholder), so real ADR files in this project that follow the task description would use `id: "ADR-001"` as shown in the test fixtures.

For the `Bug` model: the `source_branch` field from the template was intentionally omitted from the dataclass because it is a lifecycle-operational field (used by the bug-fix loop to track which branch a task-regression bug came from), not a semantic data field that commands and validators need to reason about. The task description's type-specific fields list for Bug does not include `source_branch`. This is a trade-off: if future components need to read `source_branch`, the model will need extending.

The `dump_frontmatter` function uses `ruamel.yaml` round-trip mode with a `CommentedMap` to guarantee insertion-order preservation. Optional fields (`spec` for Task, `task` for Bug, `supersedes` for Adr) are omitted from output when `None` to keep dumped files clean. The `assigned-role` YAML key maps to `assigned_role` Python attribute to satisfy Python naming conventions while preserving the hyphenated YAML key form that templates use.

All 35 tests pass covering AC-1 through AC-4: parsing all four artifact types, round-trip fidelity, `FrontmatterError` on missing/invalid fields (field name and path in message), and key-order preservation across parse/dump cycles. The full prior test suite (59 total) also passes with no regressions.

### Session 2 — 2026-05-10

Fixed AC-4 comment preservation per the cycle-1 Reviewer FAIL verdict. Two changes in `cli/src/ai_team/core/models.py` and `cli/tests/test_models.py`.

The root cause was `_parse_yaml_frontmatter` returning `dict(data)`, which stripped the `CommentedMap` ruamel.yaml builds in round-trip mode and discarded all inline comments before they could ever reach `dump_frontmatter`.

Fix threads the `CommentedMap` end-to-end:
1. `_parse_yaml_frontmatter` returns the `CommentedMap` directly. `_require` and dict `.get()` calls work unchanged because `CommentedMap` supports the standard mapping interface.
2. Each dataclass gains a `_source_map: CommentedMap | None` field declared with `field(default=None, compare=False, repr=False)` so it is invisible to `==` and repr — existing round-trip equality tests are unaffected.
3. Each `parse_*` function passes `_source_map=data` when constructing the dataclass.
4. `dump_frontmatter` checks `model._source_map`. When present, it updates field values in-place on the source map (using `source_map.pop(key, None)` for optional fields that are `None`) and dumps that map, so all inline comments survive. When absent (model constructed by hand), the fallback path builds a fresh `CommentedMap` from `_MODEL_FIELDS` ordering — key-order preservation for programmatically-created models is unaffected.

Added `test_dump_frontmatter_preserves_inline_comments` in `tests/test_models.py`: writes a task fixture with `status: pending  # workflow state`, parses it, calls `dump_frontmatter`, asserts `"# workflow state"` appears in the dumped output. Test failed before the fix and passes after.

After fix: 36 `test_models.py` tests pass; 60 total tests pass (no regressions). Commit on task branch: `e464eec fix(core): preserve YAML comments across parse/dump cycles`.

## Review

<!-- Reviewer: append verdict here after each review cycle. -->


### Review Verdict — 2026-05-10 (Cycle 1)

FAIL

**Stage 1 — Acceptance Criteria**

AC-1 (parse_task returns a Task with all fields): PASS — all common and type-specific fields are populated correctly. All four parse functions are present and work.

AC-2 (dump_frontmatter round-trips to an equal model): PASS — all four artifact types round-trip cleanly. Tests confirm.

AC-3 (FrontmatterError names the field and path): PASS — `_require` includes both the key name and the path in the message. Tests cover missing-field paths for all types.

AC-4 (YAML comments and key order preserved): FAIL — **key order is preserved, but YAML comments are not.**

The root cause is in `_parse_yaml_frontmatter` (line 82 of `cli/src/ai_team/core/models.py`): `return dict(data)` converts the `ruamel.yaml` `CommentedMap` to a plain Python dict, stripping all comment annotations. `dump_frontmatter` then builds a brand-new `CommentedMap` from the dataclass fields, so no comments can ever survive the parse→dump cycle. A manual test confirms: a file with `status: pending  # this is a comment` loses the comment after `dump_frontmatter`.

The test suite does not exercise comment preservation either: all four tests in the AC-4 section check key order and optional-field omission, but none writes a fixture with an inline YAML comment and asserts the comment is present in the dumped output.

**Stage 2 — Code Quality**

Stage 2 is skipped per procedure because Stage 1 has a failing criterion.

**Issues to Fix**

1. **File:** `cli/src/ai_team/core/models.py`, line 82.
   **What is wrong:** `return dict(data)` discards the `CommentedMap` returned by `ruamel.yaml` round-trip mode, losing all inline comments. AC-4 explicitly requires comment preservation.
   **What should change:** Return the `CommentedMap` directly (or keep a reference to it), and thread it through to `dump_frontmatter` so the serialiser can re-use the parsed map (with comments) rather than building a fresh one. One approach: `_parse_yaml_frontmatter` returns a `CommentedMap`; `dump_frontmatter` accepts an optional `source_map` argument and uses `yaml.dump(source_map, stream)` after updating field values in-place instead of creating a new `CommentedMap` from scratch.

2. **File:** `cli/tests/test_models.py`, AC-4 section (approximately line 500 onwards).
   **What is wrong:** No test verifies that inline comments survive a parse→dump cycle, which means the gap in AC-4 was not caught.
   **What should change:** Add at least one test that writes a fixture file containing an inline comment (e.g., `status: pending  # workflow state`), calls `parse_task` followed by `dump_frontmatter`, and asserts the comment string appears in the dumped output.

**Design Decisions (both acceptable)**

Decision 1 — ADR `id` vs `number`: The Developer's choice to use `id: str` (e.g., `"ADR-001"`) is acceptable. The task description is explicit about `id` being the field name and `id` is consistent across all other artifact types. The existing template uses `number: 0` as a placeholder that was never adopted in practice. No action needed.

Decision 2 — Bug `source_branch` omitted from dataclass: Acceptable for v1 **with an explicit note**. The bug-loop reads `source_branch` directly from the file's raw frontmatter (bug-loop/SKILL.md Step 3), not through the `Bug` dataclass, so this omission does not break the current loop. Future components that need it (T-007, T-017) will need to either extend the `Bug` dataclass or read it via raw frontmatter — the Developer's Work Log already flags this trade-off. No action required for this task.

### Review Verdict — 2026-05-10 (Cycle 2)

PASS

**Stage 1 — Acceptance Criteria**

AC-1 (parse_task returns a Task with all fields): PASS — unchanged from cycle 1; all four parse functions populate all common and type-specific fields correctly.

AC-2 (dump_frontmatter round-trips to an equal model): PASS — the in-place source-map update path still produces output that parses back to an equal model. All five round-trip tests pass. Key order verified manually: `id → title → status → priority → assigned-role → created` is preserved exactly. No regression from cycle 1.

AC-3 (FrontmatterError names the field and path): PASS — unchanged from cycle 1; `_require` still includes both the key name and source path in the message.

AC-4 (YAML comments and key order preserved): PASS — fix confirmed.

Root cause was correctly identified: `_parse_yaml_frontmatter` was stripping the `CommentedMap` by converting it to a plain dict. Fix returns the `CommentedMap` directly and threads it through each dataclass via `_source_map`. `dump_frontmatter` updates the source map in-place when present so comments survive.

Manual parse→dump cycle confirmed `status: pending  # workflow state` appears in dumped output. New test `test_dump_frontmatter_preserves_inline_comments` passes. All 36 `test_models.py` tests pass; 60 total tests pass with no regressions.

**Stage 2 — Code Quality**

Correctness: Logic is sound. Each `parse_*` call invokes `_parse_yaml_frontmatter` which reads and re-parses the file independently, so `_source_map` instances across separate parse calls are distinct objects — no shared mutable state. Verified: two `parse_task` calls on the same file produce separate `CommentedMap` objects; mutating one does not affect the other. The fallback path (hand-constructed model with `_source_map=None`) still builds a fresh `CommentedMap` with canonical key order.

Tests: 36 tests covering all four artifact types, success and failure paths, round-trip fidelity, key-order preservation, optional-field handling, and now comment preservation. Tests are independent (each uses `tmp_path`). New test exercises the failure-then-pass scenario implicitly by asserting the comment string is present.

Security: No credentials, no external input used directly in queries, no new permissions.

Readability: `_source_map` field is clearly documented with `compare=False, repr=False`. The two code paths in `dump_frontmatter` (source-map present vs absent) are clearly commented. Names are descriptive and follow existing project conventions.

Performance: No unnecessary loops; the in-place update iterates over `ordered_fields` once — same complexity as the previous fresh-build path.

**Minor observations (non-blocking)**

The in-place update in `dump_frontmatter` mutates the `CommentedMap` held by the model. If a caller dumps the same model twice with different field values between dumps, the second dump sees the updated map. This is consistent with the design intent (the map reflects current model state) and is not a correctness issue for the current use cases, but callers who cache models and dump them multiple times should be aware. No action required for this task.
