---
id: B-003
title: ai-team task new does not substitute the body title placeholder
severity: medium
status: in-progress
created: '2026-05-15'
---

# ai-team task new does not substitute the body title placeholder

## Summary

`ai-team task new "<title>"` populates the frontmatter `title` correctly but leaves
the document body containing the literal placeholder heading `# [Task Title]`. Every
newly created task needs its H1 fixed by hand. Originally reported as I-007 in
`ai-process-cli-reported-issues.md`.

## Reproduction Status

Status: confirmed

Observed during `/write-plan` for S-001 when creating T-032, T-033, and T-034 on
2026-05-14: all three new task files needed their `# [Task Title]` H1 corrected
manually.

## Evidence

- Logs / stack traces / failing assertions: not error-emitting; the defect is silently
  bad output content.
- Screenshots or recordings: n/a.
- Failing command or test: after running `uv --directory cli run ai-team task new "Some Title" --json`,
  the created file body still contains `# [Task Title]` instead of `# Some Title`.
- First diagnostic step if not yet reproduced: read
  `cli/src/ai_team/commands/task.py` and compare `new_task()` against `new_spec()` in
  `spec.py` and `new_bug()` in `bug.py`, which were corrected by B-001 to perform
  the same H1 substitution.

## Reproduction Steps

1. From a checked-out copy of the repo on `dev-agent`, run
   `uv --directory cli run ai-team task new "Pick any task title" --json`.
2. Read the path returned in the JSON `path` field.
3. Observe that the file's body starts with `# [Task Title]` instead of `# Pick any task title`.

## Expected Behavior

`task new` should substitute the body `# [Task Title]` heading with the provided
title, consistent with `spec new` (`# [Specification Title]`) and `bug new`
(`# [Bug Title]`) after the B-001 fix.

## Actual Behavior

Frontmatter `title` is filled correctly. The body H1 remains `# [Task Title]`. There
is no error or warning; the user is silently shipped a file with a placeholder
heading.

## Environment

- OS / platform: Linux (Debian 13, also reproducible on macOS).
- Language / runtime version: Python 3.14 (as configured in `cli/pyproject.toml`).
- Relevant dependencies: ai-team CLI as built from this repository.
- Branch / commit: observed on `dev-agent` at 2026-05-14; defect predates the
  bug-loop session that fixed B-001.

## Related

- Task: not applicable
- Specification: not applicable
- Prior bug: B-001 (which fixed the same defect class for `spec new` and `bug new`).
- Prior issue note: I-007 in `ai-process-cli-reported-issues.md`.

## Suspected Area

`cli/src/ai_team/commands/task.py` — specifically `new_task()`. The function passes
the loaded template body straight to `write_artifact()` without the
`# [Task Title]` → `# <title>` substitution that `new_spec()` / `new_bug()` perform
in `spec.py` / `bug.py`.

## Fix Verification

```bash
uv --directory cli run ai-team task new "Verify B-003 fix" --json > /tmp/b003.json
python3 -c "import json,re; p=json.load(open('/tmp/b003.json'))['path']; body=open(p).read(); assert '# [Task Title]' not in body, 'placeholder still present'; assert re.search(r'^# Verify B-003 fix$', body, flags=re.M), 'expected H1 not found'; print('OK')"
uv --directory cli run pytest tests/test_task_new.py
```

A regression test analogous to
`test_spec_new_substitutes_body_h1_with_provided_title` should be added in
`cli/tests/test_task_new.py`.

## Diagnosis Log

<!-- Mandatory before implementation. Append one entry before changing production code. Format:
### Diagnosis N — YYYY-MM-DD
Reproduction status:
Evidence captured:
Isolated fault:
Root cause or fault hypothesis:
Planned verification:
-->

### Diagnosis 1 — 2026-05-15

**Reproduction status:** Confirmed. Running `uv --directory cli run ai-team task new "Pick any task title" --json` produced `T-044-pick-any-task-title.md` with frontmatter `title: Pick any task title` (correct) but body line `# [Task Title]` (placeholder, not substituted). Artifact cleaned up after capture.

**Evidence captured:** File body line 10 of the created artifact contained the literal string `# [Task Title]` instead of `# Pick any task title`. No error or warning was emitted. The command exited with code 0 and returned valid JSON.

**Isolated fault:** `cli/src/ai_team/commands/task.py`, `new_task()` function, between line 172 (`body = _template_body(template)`) and line 184 (`write_artifact(dest, model, body, overwrite=False)`). The `body.replace("# [Task Title]", f"# {title}", 1)` call is missing entirely.

**Root cause or fault hypothesis:** When B-001 was applied to fix the same placeholder-substitution defect in `new_spec()` (spec.py line 75) and `new_bug()` (bug.py line 124), `new_task()` in task.py was not touched. All three functions share the same pattern: extract template body via `_template_body()`, then pass `body` to `write_artifact()`. In `spec.py` and `bug.py` a `body = body.replace("# [<Type> Title]", f"# {title}", 1)` line was inserted between those two calls; in `task.py` that insertion was simply omitted. The root cause is an incomplete application of the B-001 fix — not a logic error in the existing code, but a missing line.

**Planned verification:** After adding `body = body.replace("# [Task Title]", f"# {title}", 1)` at line 173 (after `body = _template_body(template)` and before the `Task(...)` model construction), re-run the fix verification commands from the bug file: a fresh `ai-team task new` invocation followed by the assertion script, plus `uv run pytest tests/test_task_new.py` after adding the regression test analogous to `test_spec_new_substitutes_body_h1_with_provided_title`.

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
