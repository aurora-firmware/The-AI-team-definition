---
id: T-097
title: Move raw-body/raw-header test assertions to rendered output
status: completed
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Move raw-body/raw-header test assertions to rendered output

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 2**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P20 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- tests reading body.md or raw [claude]/[codex] headers assert on rendered output via a helper calling the T-096 renderer. Known: test_t063, t064, t066, t068, t074, t076, test_status_report_invocation, test_bug_evidence_chain, test_b016, test_init_scaffolds (confirm by grep). Out of scope: changing what is asserted.

Size note (accepted at Gate 2, ruling 7): over guideline, mechanical.

## Acceptance Criteria

AC-1: no test reads body.md/raw headers for content (SC-2).
AC-2: same expectations on rendered output.
AC-3: V-PY passes.

## Dependencies

- `T-087` — TS lock entry in skeleton .gitignore; update B-017 tests and usage guide
- `T-096` — Marker parsing and claude/codex rendering in the sync

## Files to Touch

- affected cli/tests/test_*.py and a new shared helper

## Verification

```bash
# V-PY; review that no remaining test asserts on real source body.md or header content (fixture writes and source-structure checks in test_init_scaffolds.py, ~lines 41-66 and 359-389, are legitimate). [G2 N5]
# V-PY: cd cli && uv run pytest && uv run ruff format --check . && uv run ruff check .   # set UV_CACHE_DIR under /tmp if uv cannot write its cache
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-10-01
I added `cli/tests/skill_rendering.py`. It exposes `rendered_skill_body`, `rendered_skill_header` and `rendered_skill_text`. They load `scripts/skill_markers.py` by file path and render through `render_markers` with `command_map.json`, for the claude or codex target. `test_skill_rendering_helper.py` checks that the helper's output equals the generated `SKILL.md` scaffold and that an unsupported target such as `pi` is rejected.

I then converted the tests that read a skill's raw `body.md` or raw `[claude]`/`[codex]` header:
- **Body readers:** t063, t064, t068, t074, t076, `test_bug_evidence_chain`, `test_b016`, `test_init_scaffolds` and the loop-body read in `test_status_report_invocation` now call `rendered_skill_body(...)`.
- **Header readers:** the two header reads in `test_status_report_invocation` now call `rendered_skill_header(...)`.
- **Source-vs-scaffold check:** `test_package_owned_skill_sources_include_body_and_required_metadata` now compares the rendered body and header to the scaffold. It still checks the source structure (one `body.md`, one `metadata.toml`, a non-empty header), which is legitimate.
- **Left alone:** the fixture writes in `test_init_scaffolds.py`, and `test_t066` (which reads docs and ADRs, not skill sources).

I did not touch the scaffold `SKILL.md` reads, because they are already rendered output. The `source` element of the `(source, claude, codex)` tuples now holds rendered claude text, so its assertions partly duplicate the claude ones. I kept both to stay inside "out of scope: changing what is asserted".

I considered giving each test its own target parameter and rejected it, since the current sources contain no markers and the claude and codex renders are identical. Nothing remains for this task. A later task could drop the now-redundant `source` tuple element.

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

Reviewed the triple-dot diff of `task/T-097-...` against `feat/pi-extension` (commits 0186305, 3e321f3).

Stage 1 (acceptance criteria):
- AC-1 met. On the task branch, the only remaining `body.md`/`metadata.toml` reads in tests are fixture writes and source-structure checks (`test_init_scaffolds.py` ~lines 36-66, 351-398, including the presence and non-empty header checks), plus `test_skill_markers.py` fixtures and the `glob("*/metadata.toml")` enumeration in `test_status_report_invocation.py`. None assert on raw content. `test_t066` reads docs and ADRs, not skill sources.
- AC-2 met. Every converted read calls `rendered_skill_body` or `rendered_skill_header` (new `cli/tests/skill_rendering.py`, which renders through `scripts/skill_markers.py` `render_markers` with `command_map.json`). The diff changes no assertion text or expectation. The one semantic adjustment, in `test_package_owned_skill_sources_include_body_and_required_metadata`, compares rendered body/header to the scaffold instead of raw, and is equivalent while sources hold no markers.
- AC-3 met. `UV_CACHE_DIR=/tmp/uvcache uv run pytest` gives 915 passed. `ruff format --check` and `ruff check` are clean.
- No unexpected files were touched. The new helper and its test are within the task's "new shared helper" scope.

Stage 2 (quality): The helper is small, cached and readable. `test_skill_rendering_helper.py` covers scaffold equality for both targets, header-plus-body composition and rejection of an unsupported target. No weakened assertions were found.

Non-blocking observations:
- The `source` element of the `(source, claude, codex)` tuples is now rendered claude text, so its assertions partly duplicate the claude ones. The Developer noted this and left it for a later task.
- The helper has no per-test target parameter on the converted readers, so codex-specific marker differences are not exercised. This is acceptable because the sources currently contain no markers.

Next owner: Development Loop.
