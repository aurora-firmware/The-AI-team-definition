---
id: B-016
title: Developer role has no enforced boundary against committing lifecycle 
  files on task branches
severity: medium
status: in-progress
created: '2026-08-05'
---

# Developer role has no enforced boundary against committing lifecycle files on task branches

## Summary

The rule that task and bug files are canonical on `dev-agent` and must not be
edited from an implementation branch exists only as prose spread across the
`tdd`, `debug`, `git-conventions`, and `dev-loop` sources. The Developer agent
definition's own Folder Scope table — the one place that states hard boundaries
for the role — does not list `project/tasks/` or `project/bugs/` under "Never
touch". In practice the prose has been ignored: a Developer committed a Work Log
into the canonical task file and added a `completed/` copy on the task branch.
The only thing that catches this is `integrate` Step 3.4, which is detection
after the fact and hard-stops the integration.

## Reproduction Status

Status: confirmed by source inspection, plus a field incident

The reporting project observed it during `dev-loop` processing of T-115: the
Developer returned a Work Log *and* wrote it to disk and `git add`ed the task
file on the task branch (commit `4540185`). The loop had to reset the source
branch to the source-only commit and re-record the Work Log on `dev-agent`
before review and integration could proceed.

## Evidence

- Logs / stack traces / failing assertions: n/a
- Screenshots or recordings: n/a
- Failing command or test: n/a — the failure mode is a violated boundary that
  surfaces as an `integrate` hard stop, not a test failure.
- Source inspection:
  - `cli/src/ai_team/init/sources/agents/claude/developer.md:54` — the "Never
    touch" row lists only `project/specs/`, `project/decisions/`,
    `project/docs/`. `project/tasks/` and `project/bugs/` are absent, and the
    Write/Edit row grants `project/bugs/open/` via `new-bug`.
  - `cli/src/ai_team/init/sources/skills/tdd/body.md:9-10` and
    `.../skills/debug/body.md:14-15` carry only the prose "return new log content
    as a handoff … instead of editing lifecycle files directly".
  - `cli/src/ai_team/init/sources/skills/dev-loop/body.md:100` passes the single
    line "Do not edit the task lifecycle file on the task branch" in the
    Developer prompt.
  - `cli/src/ai_team/init/sources/skills/git-conventions/body.md:68` lists
    "Merging lifecycle-file edits from an implementation branch" under *Common
    Pitfalls*, not under *Hard Rules*.
  - `git log -S` confirms the tdd/debug and dev-loop guard wording is unchanged
    since commit `483ea74` (2026-05-14) — i.e. no hardening was added in response
    to the incident.
  - The detection that did fire, `cli/src/ai_team/init/sources/skills/integrate/body.md:67`
    (Step 3.4), stops integration rather than preventing the commit.

## Reproduction Steps

1. Run `/dev-loop` and let it reach Step 5, spawning the Developer for a task.
2. Let the Developer complete implementation and produce its Work Log handoff.
3. Inspect the task branch: `git diff dev-agent...task/T-NNN-… -- project/tasks/`.
4. Observe that nothing in the Developer's own definition or tooling prevents a
   lifecycle-file edit and `git add` from appearing there; when it does,
   `integrate` Step 3.4 hard-stops.

## Expected Behavior

The Developer must not be able to commit lifecycle files from an implementation
branch, and the boundary should be stated where the role's other hard boundaries
live. Either:

- (a) the Developer agent definition adds `project/tasks/` and `project/bugs/`
  (except `project/bugs/open/` via the `new-bug` skill) to "Never touch" and
  forbids `git add`/commit under those paths, and `git-conventions` promotes the
  rule from *Common Pitfalls* to *Hard Rules*; and/or
- (b) `dev-loop` and `bug-loop` strip lifecycle-path changes from the source
  branch before handing it to review, so the violation cannot reach `integrate`.

## Actual Behavior

The prohibition exists only as prose in skills the Developer may or may not
consult, and is contradicted in spirit by a Folder Scope table that enumerates
three other protected paths but not this one. The violation is caught only at
integration time, after the loop has already spent a review cycle.

## Environment

- OS / platform: Linux
- Language / runtime version: `ai-team` CLI 0.10.1 (agent and skill sources are
  language-agnostic)
- Relevant dependencies:
  `cli/src/ai_team/init/sources/agents/{claude/developer.md,codex/developer.toml}`,
  `.../skills/{tdd,debug,dev-loop,bug-loop,git-conventions}/body.md`
- Branch / commit: `dev-agent`, inspected 2026-08-05

## Related

- Task: n/a
- Specification: n/a
- External evidence: `/home/daneel/projects/the-intern/ai-process-cli-reported-issues.md`,
  entry dated 2026-06-30
- Prior art: B-002 fixed the equivalent boundary for the Reviewer by making
  `code-review` switch to `dev-agent` before recording a verdict.

## Suspected Area

`cli/src/ai_team/init/sources/agents/claude/developer.md` Folder Scope table and
its Codex counterpart; `git-conventions` Hard Rules; the Developer prompt in
`dev-loop`/`bug-loop`.

## Fix Verification

Documentary, since the fix is a change to role and skill definitions:

- The Developer agent definition names `project/tasks/` and `project/bugs/` as
  out of bounds for Write/Edit and for `git add`/commit, with the `new-bug`
  exception stated explicitly.
- `git-conventions` lists lifecycle-file commits from an implementation branch
  under Hard Rules.
- Both Claude and Codex Developer definitions carry the same boundary.
- Regenerate and confirm exports stay in sync:

```bash
cd cli && python scripts/sync_init_scaffolds.py && uv run pytest
git status --porcelain cli/src/ai_team/init/scaffolds   # must be empty after regeneration
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

### Diagnosis 1 — 2026-08-06

Reproduction status: Confirmed by direct source inspection (not a runtime/test
reproduction — the defect is an absent boundary in role/skill definitions, and the
bug report's own reproduction status of "confirmed by source inspection, plus a
field incident" was independently re-verified line by line against the current
`dev-agent` source tree).

Evidence captured:
- `cli/src/ai_team/init/sources/agents/claude/developer.md:54` — Folder Scope "Never
  touch" row reads exactly `project/specs/`, `project/decisions/`, `project/docs/`.
  `project/tasks/` and `project/bugs/` are absent. Line 53 grants Write/Edit access to
  `project/bugs/open/` via `new-bug`, with no corresponding restriction stated for
  `project/tasks/` or the rest of `project/bugs/`.
- `cli/src/ai_team/init/sources/agents/codex/developer.toml:43` — Codex "Never touch"
  line carries the identical three-path list, same omission. Line 42 carries the same
  `project/bugs/open/` exception with no matching restriction.
- `cli/src/ai_team/init/sources/skills/git-conventions/body.md:68` — "Merging
  lifecycle-file edits from an implementation branch" is listed under `## Common
  Pitfalls` (advisory), not under `## Hard Rules` (lines 57-62, which cover
  `--no-verify`, force-push, amending pushed commits, and secrets — none of which
  mention lifecycle-file commits).
- `cli/src/ai_team/init/sources/skills/tdd/body.md:9-10` and
  `cli/src/ai_team/init/sources/skills/debug/body.md:14-15` — both carry only the
  prose "return new log content/diagnosis content as a handoff … instead of editing
  lifecycle files directly," with no cross-reference to a Folder Scope or Hard Rule.
- `cli/src/ai_team/init/sources/skills/dev-loop/body.md:100` — single-line guard `>
  Do not edit the task lifecycle file on the task branch.` inside a blockquote, not a
  boundary in the Developer's own definition.
- `git log --oneline -S "instead of editing lifecycle files directly" -- .../tdd/body.md
  .../debug/body.md` returns only `483ea74` (2026-05-14, the sources migration commit)
  — confirms this guard wording predates and is unchanged by the T-115 field incident,
  i.e. no hardening was added in response.
- `cli/src/ai_team/init/sources/skills/integrate/body.md:67-72` (Step 3, item 4 —
  the "3.4" cited in the report) — confirms the only check is post-hoc: "Confirm the
  source diff does not modify the canonical task or bug lifecycle file. If it does,
  stop and ask the active loop to move lifecycle log or verdict content to `dev-agent`
  before integration." This runs after implementation and review are already complete.
- `cli/scripts/pre-commit.sh` — inspected as a possible technical control; it only
  runs `ruff format --check .` on `cli/`. No lifecycle-path guard exists at the git
  hook level or anywhere else in the tooling.
- Generated scaffolds mirror the source defect exactly: `grep -n "Never touch"
  cli/src/ai_team/init/scaffolds/claude/agents/developer.md:54` and
  `cli/src/ai_team/init/scaffolds/codex/agents/developer.toml:43` both show the
  identical three-path list; `cli/src/ai_team/init/scaffolds/{claude,codex}/skills/
  git-conventions/SKILL.md:74` both list the pitfall under Common Pitfalls, not Hard
  Rules — so both distributed agent flavors carry the same unenforced boundary.
- `git status --porcelain` before and after inspection: clean — no production code or
  lifecycle files were modified during this diagnosis.

Isolated fault: Three co-located textual gaps, present identically in both the Claude
and Codex Developer sources:
1. `cli/src/ai_team/init/sources/agents/claude/developer.md:54` (Folder Scope,
   "Never touch" row) and `cli/src/ai_team/init/sources/agents/codex/developer.toml:43`
   (Folder scope, "Never touch:" line) omit `project/tasks/` and `project/bugs/`
   (except `project/bugs/open/`, already carved out via `new-bug`).
2. `cli/src/ai_team/init/sources/skills/git-conventions/body.md:68` places the
   lifecycle-file-commit prohibition under `## Common Pitfalls` instead of `## Hard
   Rules`, so it reads as advisory rather than a rule the Developer must obey.

Root cause: The Developer agent definition is the canonical place where the role's
hard boundaries are enumerated (Folder Scope table), and downstream skills (`tdd`,
`debug`, `git-conventions`, `dev-loop`) only carry scattered prose reminders that
presuppose the Developer already respects that boundary. Because the boundary was
never added to the Folder Scope "Never touch" row when `project/tasks/` and
`project/bugs/` write access was scoped for the `new-bug` exception, and because
`git-conventions` still classifies the violation as a "pitfall" rather than a "hard
rule," there is no single authoritative, hard-stated prohibition the Developer is
bound by, and no technical control (pre-commit hook, CI check) backs it up. The only
detection is `integrate` Step 3.4, which fires after implementation and review are
already spent — exactly matching the T-115 field incident (commit `4540185`) where
the Developer both returned a Work Log handoff *and* wrote/`git add`ed it directly on
the task branch. This is a specification/definition gap, not a runtime logic bug —
the fix is confirmed root cause, not a hypothesis, since every cited location was
independently re-verified against current source.

Planned fix (per the bug's Expected Behavior option (a) and Fix Verification section):
- Add `project/tasks/` and `project/bugs/` (except `project/bugs/open/`, via
  `new-bug`) to the "Never touch" row/line in both
  `cli/src/ai_team/init/sources/agents/claude/developer.md` (Folder Scope table) and
  `cli/src/ai_team/init/sources/agents/codex/developer.toml` (Folder scope block),
  and state explicitly that this forbids `git add`/commit under those paths from an
  implementation branch, not just Write/Edit.
- Promote "Merging lifecycle-file edits from an implementation branch" (or an
  equivalently worded Developer-side prohibition) from `## Common Pitfalls` to `##
  Hard Rules` in `cli/src/ai_team/init/sources/skills/git-conventions/body.md`.
- Leave `tdd`, `debug`, and `dev-loop` prose as supporting context; no change to
  their wording is required by the fix contract unless implementation reveals a
  conflict.

Planned verification:
- Documentary/structural checks: confirm the new "Never touch" wording appears
  verbatim (with the `new-bug`/`project/bugs/open/` exception stated) in both
  `cli/src/ai_team/init/sources/agents/claude/developer.md` and
  `cli/src/ai_team/init/sources/agents/codex/developer.toml`, and confirm the
  lifecycle-commit rule appears under `## Hard Rules` in
  `cli/src/ai_team/init/sources/skills/git-conventions/body.md`.
- Run, from `cli/`:
  `python scripts/sync_init_scaffolds.py && uv run pytest`
  then `git status --porcelain cli/src/ai_team/init/scaffolds` — must be empty,
  confirming regenerated scaffolds match source and no existing test asserts on the
  now-changed prose in a way that breaks the suite.
- No new automated test can directly execute "the Developer refuses to commit a
  lifecycle file" since these are prose agent/skill definitions consumed by an LLM,
  not executable code; verification is therefore documentary per the bug's own Fix
  Verification section.

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-08-06

Implemented the B-016 fix contract from the Diagnosis Log without deviation. Changed
three source files: `cli/src/ai_team/init/sources/agents/claude/developer.md` and
`.../agents/codex/developer.toml` both gained `project/tasks/` and `project/bugs/`
(except `project/bugs/open/` via `new-bug`) in their Folder Scope "Never touch" entry,
with wording that explicitly forbids `git add`/commit under those paths from an
implementation branch — not just Write/Edit, matching the bug's stated gap that the
prose-only prohibitions didn't reach the role's own hard-boundary table.
`cli/src/ai_team/init/sources/skills/git-conventions/body.md` had its "Merging
lifecycle-file edits from an implementation branch" line moved (not duplicated) from
`## Common Pitfalls` into `## Hard Rules`, reworded slightly to "Never commit or merge
lifecycle-file edits (task or bug files) from an implementation branch — task and bug
files are canonical on `dev-agent` only" to match the Hard Rules section's imperative
"No .../Never ..." style. Left `tdd`, `debug`, and `dev-loop` prose untouched, per the
fix contract's explicit note that no change was required there.

Before touching source, wrote a new regression test file,
`cli/tests/test_b016_developer_lifecycle_boundary.py`, following the existing
`test_t065_claude_agent_role_files.py` / `test_t064_skill_bodies_canonical.py` pattern
of reading both `sources/` and the corresponding `scaffolds/` copy for each artifact and
asserting on stable substrings. Ran it first to confirm all 8 assertions failed against
the pre-fix source (red), then applied the three source edits, regenerated scaffolds
with `python scripts/sync_init_scaffolds.py`, and reran — all 8 passed (green), and the
full suite (454 tests) passed with no regressions. Confirmed scaffold regeneration is
idempotent: running `sync_init_scaffolds.py` a second time after staging produced no
further diff. Ran `uv run ruff format --check .` and `uv run ruff check .`; ruff
auto-reformatted the new test file once (whitespace/line-wrap only), reran both checks
clean afterward. `uv`'s default cache was unwritable in this sandbox, so `UV_CACHE_DIR`
was pointed at a scratch directory per the repo's documented fallback — no other
environment issues.

Nothing was tried and rejected; the fix contract was unambiguous and matched cleanly to
a single edit per file. No follow-up work remains on this bug from the Developer side —
the boundary is now stated in both Claude and Codex Developer definitions and in
`git-conventions` Hard Rules, scaffolds are in sync, and the full test/lint suite is
green. Everything is committed in one TDD cycle (`d3e7367`) on
`bug/B-016-developer-lifecycle-boundary`; no lifecycle files under `docs/ai-team/bugs/`
or `docs/ai-team/tasks/` were staged or committed from this branch. Ready for review.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that diagnosis, fix, verification, and code quality passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
