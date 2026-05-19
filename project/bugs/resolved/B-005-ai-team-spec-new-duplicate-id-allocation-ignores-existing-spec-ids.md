---
id: B-005
title: ai-team spec new duplicate-ID allocation ignores existing spec IDs
severity: medium
status: resolved
created: '2026-05-19'
---

# ai-team spec new duplicate-ID allocation ignores existing spec IDs

## Summary

`ai-team spec new` can allocate `S-001` even when `project/specs/` already
contains `the-intern-agent-service-architecture.md` with `id: S-001` and
`bob-service-shell-architecture.md` with `id: S-002`. The allocator appears to
scan filenames instead of spec frontmatter, so spec files whose names do not
encode the ID are invisible to the lookup. Originally reported as I-009 and
I-010 in `ai-process-cli-reported-issues.md`.

## Reproduction Status

Status: confirmed | intermittent | not yet reproduced

Confirmed on 2026-05-16 and again on 2026-05-19. Both observations produced a
new spec artifact with `id: S-001` while existing specs in `project/specs/`
already used `S-001` and `S-002`.

## Evidence

- Logs / stack traces / failing assertions:
  - `ai-team spec new --json --author planner --status draft "Bob Service Shell Architecture"`
    returned `{"id": "S-001", ...}` while `project/specs/the-intern-agent-service-architecture.md`
    already had `id: S-001`.
  - `ai-team spec new --json --author planner --status draft "JS extension for pi-agent event forwarding"`
    returned `{"id": "S-001", ...}` while `project/specs/` already contained specs
    with `id: S-001` and `id: S-002`.
- Screenshots or recordings:
- Failing command or test: `ai-team spec new --json --author planner --status draft "<title>"`
- First diagnostic step if not yet reproduced: inspect `cli/src/ai_team/core/ids.py`
  and compare the scan scope with the spec frontmatter IDs already present in
  `project/specs/`.

## Reproduction Steps

1. Confirm `project/specs/the-intern-agent-service-architecture.md` has `id: S-001`
   and `project/specs/bob-service-shell-architecture.md` has `id: S-002`.
2. Run `ai-team spec new --json --author planner --status draft "Some new spec"`
   from a checkout that already has specs with `S-001` and `S-002`.
3. Observe the returned JSON uses `id: S-001` instead of the next available ID.

## Expected Behavior

`spec new` should assign the next available spec ID after scanning existing spec
frontmatter, so the same checkout should receive `S-003` instead of reusing
`S-001`.

## Actual Behavior

The command returns `S-001` again, creating a duplicate identifier and forcing a
manual frontmatter fix before the new spec can be referenced safely.

## Environment

- OS / platform: Linux (Debian 13)
- Language / runtime version: Python 3.14 (as configured in `cli/pyproject.toml`)
- Relevant dependencies: ai-team CLI, `project/specs/`
- Branch / commit: observed on `dev-agent` on 2026-05-16 and 2026-05-19

## Related

- Task: `T-008` (ID allocator implementation)
- Specification: not applicable
- Prior issue notes: I-009 and I-010 in `ai-process-cli-reported-issues.md`
- Affected workflow: `ai-team spec new`

## Suspected Area

`cli/src/ai_team/core/ids.py`, specifically `next_spec_id()` / `_next_id()`.
The helper scans filenames under `project/specs/` and `project/specs/archive/`
but does not inspect spec frontmatter, so files like
`the-intern-agent-service-architecture.md` are skipped even when they already
consume `S-001`.

## Fix Verification

```bash
cd /home/daneel/projects/The-AI-team-definition
UV_CACHE_DIR=/tmp/uv-cache uv --directory cli run ai-team spec new --json --author planner --status draft "Verification Spec"
python3 - <<'PY'
from pathlib import Path
import re

spec = Path("project/specs/verification-spec.md")
text = spec.read_text()
match = re.search(r"^id:\s*(S-\d{3})$", text, flags=re.M)
assert match, "missing frontmatter id"
assert match.group(1) != "S-001", "duplicate id reused"
print(match.group(1))
PY
UV_CACHE_DIR=/tmp/uv-cache uv --directory cli run pytest tests/test_ids.py tests/test_spec_new.py
```

## Diagnosis Log

<!-- Mandatory before implementation. Append one entry before changing production code. Format:
### Diagnosis N — YYYY-MM-DD
Reproduction status:
Evidence captured:
Isolated fault:
Root cause or fault hypothesis:
Planned verification:
-->

### Diagnosis 1 — 2026-05-19

Reproduction status:
Confirmed.

Evidence captured:
- Ran:
  `UV_CACHE_DIR=/tmp/uv-cache uv --directory cli run ai-team spec new --json --author planner --status draft "B005 Repro Spec"`
  Output:
  `{"id": "S-001", "path": "/home/daneel/projects/The-AI-team-definition/project/specs/b005-repro-spec.md"}`
  while existing specs already had `id: S-001`.
- Verified allocator behavior directly:
  `UV_CACHE_DIR=/tmp/uv-cache uv --directory cli run python - <<'PY' ... next_spec_id(root) ...`
  Output included:
  `next_spec_id: S-001`
  and all spec filenames reported `filename_match=False` against `_SPEC_PATTERN`.
- Built isolated temp repro with canonical-style filenames and frontmatter IDs `S-001` and `S-002`, then invoked `spec new` via `CliRunner` from that temp cwd.
  Output:
  `{"id": "S-001", ...}`
  and created file frontmatter:
  `new_spec_frontmatter_id: S-001`.

Isolated fault:
- `next_spec_id()` delegates to `_next_id()` with `_SPEC_PATTERN = ^S-(\d{3})-.*\.md$`.
- `_max_matching_number()` only matches `path.name` and never reads file content/frontmatter.
- `spec new` uses slug filenames (`<slug>.md`), so existing spec files do not match `_SPEC_PATTERN`, keeping max at `0` and reissuing `S-001`.

Root cause or fault hypothesis:
- Root cause: spec ID allocation for `spec new` is incorrectly coupled to filename conventions that are not used by spec artifacts. Because specs are stored as slug filenames, frontmatter IDs are invisible to `_SPEC_PATTERN` filename scanning, causing duplicate ID allocation.

Planned verification:
- Add regression tests that create slug-named specs with frontmatter IDs (`S-001`, `S-002`) in `project/specs`/`archive` and assert `next_spec_id()` returns `S-003`.
- Add command-level regression in `test_spec_new.py` to assert `spec new` allocates next ID from existing spec frontmatter.
- Run:
  `UV_CACHE_DIR=/tmp/uv-cache uv --directory cli run pytest tests/test_ids.py tests/test_spec_new.py`
  and confirm no duplicate `S-001` allocation in the reproduced scenarios.

Obstacles Encountered:
- Initial temp repro attempt used `uv --directory cli` without changing process cwd inside the Python runner, so it resolved project root to this repo. Corrected by `os.chdir(tmpdir)` before invoking `CliRunner`.

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-05-19

Implemented B-005 using a TDD cycle. I first added a regression test in `cli/tests/test_spec_new.py` that creates two existing spec files with slug-based filenames and frontmatter IDs `S-001` and `S-002`, then invokes `ai-team spec new --json` and expects `S-003`. The test failed as expected, proving the duplicate-allocation bug (`S-001` was returned).

I then implemented the minimal fix in `cli/src/ai_team/core/ids.py`: `next_spec_id()` now computes the max from both legacy filename pattern matches (`S-NNN-*.md`) and YAML frontmatter `id: S-NNN` values across `project/specs/` and `project/specs/archive/`. I intentionally did not refactor other ID allocators because the defect scope is spec allocation only.

I considered using `parse_spec()` for frontmatter extraction but rejected it because that parser does not model a spec `id` field; a focused frontmatter regex scan was the most direct fix with least blast radius. After the fix, the regression test passed, related ID tests remained green, and full CLI tests plus Ruff checks passed.

No implementation work remains on this branch. Ready for reviewer cycle and canonical Work Log append on `dev-agent`.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that diagnosis, fix, verification, and code quality passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-05-19
PASS

- Stage 1 passed: Diagnosis Log records reproduction status, concrete evidence, isolated fault, and root cause aligned to `next_spec_id()` filename-only scanning.
- Stage 1 passed: Fix in `cli/src/ai_team/core/ids.py` addresses the isolated cause by incorporating spec frontmatter IDs into allocation while preserving legacy filename matching.
- Stage 1 passed: Fix Verification checks passed in review (`ai-team spec new --json` allocated `S-003` for a fresh verification title; `UV_CACHE_DIR=/tmp/uv-cache uv --directory cli run pytest tests/test_ids.py tests/test_spec_new.py` passed).
- Stage 2 passed: Regression coverage exists in `cli/tests/test_spec_new.py` for slug-named existing specs with `id: S-001` and `id: S-002`, asserting new allocation `S-003`.
- Minor note: the exact verification title `"Verification Spec"` was pre-existing as an untracked file in this workspace, so equivalent verification used a fresh title to avoid path-collision side effects.
