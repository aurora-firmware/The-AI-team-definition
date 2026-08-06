---
id: B-017
title: ai-team task/bug/spec new leaves an untracked .ai-team.lock sentinel with
  no gitignore guidance
severity: low
status: open
created: '2026-08-06'
---

# ai-team task/bug/spec new leaves an untracked .ai-team.lock sentinel with no gitignore guidance

## Summary

B-014's fix (project-local `allocation_lock`) creates a sentinel file
`<project_dir>/.ai-team.lock` the first time any of `ai-team task new`,
`bug new`, or `spec new` runs, and intentionally leaves it on disk forever
(the design note in B-014's fix contract calls this "harmless to leave on
disk indefinitely" since `flock` locks are released by the kernel on process
exit, so there is nothing to clean up). Nothing in `ai-team init`'s scaffold
or documentation tells a consuming project to ignore this file, so every
consuming project's `git status` will show an untracked `.ai-team.lock`
under its project directory (e.g. `project/.ai-team.lock` or
`docs/ai-team/.ai-team.lock`) the first time an artifact is created after
adopting the fixed CLI. This is not a functional defect — confirmed during
B-014 review that no scanner (`validate`, `status`, `report`,
`check-layout`) globs the project directory root or matches non-`.md`
files, so nothing trips over the sentinel — but it is a persistent,
unexplained git-status hygiene rough edge with no first-party mitigation.

## Reproduction Status

Status: confirmed

Reproduced directly during B-014 code review.

## Evidence

- Logs / stack traces / failing assertions: n/a (not a crash; a hygiene gap)
- Screenshots or recordings: n/a
- Failing command or test: n/a — reproduced manually
- Source inspection:
  - `cli/src/ai_team/core/lock.py` `allocation_lock` creates
    `<project_dir>/.ai-team.lock` via `os.open(lock_path, os.O_CREAT | os.O_RDWR)`
    and never removes it.
  - `cli/src/ai_team/init/sources/` and `cli/src/ai_team/init/scaffolds/`
    contain no `.gitignore` template for scaffolded consuming projects at
    all (grep for `gitignore` under `cli/src/ai_team/` returns nothing), so
    there is no existing mechanism this fix could have extended.
  - Manual repro: `ai-team init` a scratch project, run `ai-team task new
    "X" --json` once, then `git status --short` inside the scratch project
    shows `?? project/.ai-team.lock` alongside the new task file, and the
    lock file remains after the command exits successfully.

## Reproduction Steps

1. `ai-team init --no-interactive --tools claude` in an empty git repo.
2. `git add -A && git commit -m init` (or just note the clean `git status`).
3. Run `ai-team task new "Anything" --json` once.
4. Run `git status --short` and observe `?? project/.ai-team.lock` in
   addition to the expected new task file.

## Expected Behavior

Running `ai-team task new` / `bug new` / `spec new` should not leave
unexplained untracked files in a consuming project's working tree. Either
the sentinel file should be excluded from version control by a
first-party mechanism (e.g. a scaffolded `.gitignore` entry, or `ai-team
init` writing/appending one), or the CLI should document that this file is
expected, safe to ignore, and how to exclude it.

## Actual Behavior

`.ai-team.lock` appears as an untracked file in `git status` after the
first artifact creation and is never removed or documented, with no
supplied `.gitignore` entry anywhere in the framework's `init` scaffold.

## Environment

- OS / platform: Linux
- Language / runtime version: Python 3.14, `ai-team` CLI (post-B-014 fix,
  branch `bug/B-014-concurrent-id-allocation`)
- Relevant dependencies: `cli/src/ai_team/core/lock.py`,
  `cli/src/ai_team/init/sources/`, `cli/src/ai_team/init/scaffolds/`
- Branch / commit: discovered reviewing `bug/B-014-concurrent-id-allocation`
  against `dev-agent`, 2026-08-06

## Related

- Task: n/a
- Specification: n/a
- Prior art: B-014 (`Concurrent ai-team task new calls allocate duplicate
  IDs`) introduced the sentinel file as part of its fix; this bug is a
  follow-up hygiene gap noted during that fix's code review, deliberately
  scoped out of B-014 since it does not affect ID-allocation correctness.

## Suspected Area

`cli/src/ai_team/init/` scaffold sources (no `.gitignore` template exists
for consuming projects) and/or `cli/src/ai_team/core/lock.py` (the sentinel
file itself). Fix could scaffold a `.gitignore` entry, document the file in
a guide, or both.

## Fix Verification

```bash
# In a scratch project created with `ai-team init`, run one artifact
# creation and confirm no untracked, unexplained files remain:
ai-team task new "Anything" --json
git status --short
# .ai-team.lock must either not appear, or be covered by a tracked
# .gitignore entry so it never shows as untracked.
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
