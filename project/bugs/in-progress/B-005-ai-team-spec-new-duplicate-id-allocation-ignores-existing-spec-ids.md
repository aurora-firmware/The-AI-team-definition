---
id: B-005
title: ai-team spec new duplicate-ID allocation ignores existing spec IDs
severity: medium
status: in-progress
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
- For PASS: brief confirmation that diagnosis, fix, verification, and code quality passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
