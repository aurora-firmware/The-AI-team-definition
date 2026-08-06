---
id: B-013
title: ai-team validate reports task-spec-missing for spec references the CLI 
  itself creates
severity: high
status: in-progress
created: '2026-08-05'
---

# ai-team validate reports task-spec-missing for spec references the CLI itself creates

## Summary

`ai-team validate` emits `task-spec-missing` for tasks whose `spec:` reference
resolves perfectly well, because the validator indexes specs by **filename stem**
rather than by frontmatter `id`. Since `ai-team spec new` names spec files
`S-NNN-<slug>.md`, neither of the two natural reference forms — the spec id
(`S-002`) nor the plain slug (`coordinated-process-and-cli-workflow-improvements`)
— matches the index. Only the full stem `S-002-coordinated-process-and-cli-workflow-improvements`
resolves. The check therefore fires on the CLI's own happy path, and its findings
cannot be trusted to mean "this task references a spec that does not exist".

## Reproduction Status

Status: confirmed

Reproduced twice: in this repository (`ai-team validate` → 12 findings, all
`task-spec-missing`) and in a clean scratch project built entirely with
`ai-team init` / `ai-team spec new` / `ai-team task new`, where the false
positive appears on the first task ever created.

## Evidence

- Logs / stack traces / failing assertions:

  ```
  $ ai-team spec new --json "First architecture spec"
  {"id": "S-001", "path": ".../project/specs/S-001-first-architecture-spec.md"}

  $ ai-team task new "Implement thing one" --spec S-001 --json
  {"id": "T-001", "path": ".../project/tasks/pending/T-001-implement-thing-one.md"}

  $ ai-team validate --tasks --json
  [{"path": "project/tasks/pending/T-001-implement-thing-one.md",
    "level": "error", "code": "task-spec-missing",
    "message": "Task spec reference 'S-001' does not resolve to an existing spec file."}]
  ```

  Rewriting the reference to the legacy slug `first-architecture-spec` produces
  the same finding. `ai-team show S-001` resolves the spec without issue.

- Screenshots or recordings: n/a
- Failing command or test: `ai-team validate --tasks` in any project whose specs
  use the `S-NNN-<slug>.md` filename convention.
- Source inspection:
  - `cli/src/ai_team/core/validate.py:189` builds the index as
    `spec_slugs = {path.stem for path in _iter_markdown_files(root.specs) ...}`.
  - `cli/src/ai_team/core/validate.py:167` `_spec_reference_exists` matches a
    reference only against a stem, or a stem plus a stripped `.md` suffix. The
    spec frontmatter `id` is never consulted.
  - `root.specs / "archive"` is not indexed either, so any reference to an
    archived spec is also reported missing.

## Reproduction Steps

1. `ai-team init --no-interactive --tools claude` in an empty directory.
2. `ai-team spec new --json "First architecture spec"` → creates
   `project/specs/S-001-first-architecture-spec.md` with `id: S-001`.
3. `ai-team task new "Implement thing one" --spec S-001 --json`.
4. `ai-team validate --tasks`.
5. Observe a `task-spec-missing` finding for `S-001`.

## Expected Behavior

A task whose `spec:` value names an existing spec must not produce a
`task-spec-missing` finding. Resolution should accept at least:

- the spec frontmatter `id` (`S-001`),
- the full filename stem (`S-001-first-architecture-spec`), with or without `.md`,
- the legacy bare slug (`first-architecture-spec`) for specs created before the
  `S-NNN-` filename prefix existed.

Specs under `specs/archive/` should resolve as well, since tasks completed
against a since-archived spec are otherwise permanently flagged.

## Actual Behavior

Only the exact filename stem resolves. Both `spec: S-001` (the form `ai-team
task new --spec` records) and `spec: first-architecture-slug` (the legacy form)
are reported as:

```
error  task-spec-missing  Task spec reference 'S-001' does not resolve to an existing spec file.
```

In this repository the check produces 12 findings, 100% of them false positives.
The reporting project observed 112 of 114 total findings from this one code,
rendering `ai-team validate` unusable as a signal.

## Environment

- OS / platform: Linux
- Language / runtime version: Python 3.14, `ai-team` CLI 0.10.1
- Relevant dependencies: `cli/src/ai_team/core/validate.py`
- Branch / commit: `dev-agent`, inspected 2026-08-05

## Related

- Task: n/a
- Specification: n/a
- External evidence: `/home/daneel/projects/the-intern/ai-process-cli-reported-issues.md`,
  entry dated 2026-08-01

## Suspected Area

`cli/src/ai_team/core/validate.py` — the `spec_slugs` index built in
`validate_project` and the `_spec_reference_exists` matcher.

## Fix Verification

```bash
# In a scratch project created with `ai-team init`:
ai-team spec new --json "First architecture spec"
ai-team task new "Implement thing one" --spec S-001 --json
ai-team validate --tasks --json   # must return []

# Regression coverage in the CLI test suite:
cd cli && uv run pytest
```

Additionally, `ai-team validate` from this repository root must report zero
`task-spec-missing` findings.

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
