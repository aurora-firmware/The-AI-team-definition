---
id: B-015
title: integrate post-merge regression check reuses the task-scoped verification
  command
severity: medium
status: in-progress
created: '2026-08-05'
---

# integrate post-merge regression check reuses the task-scoped verification command

## Summary

The `integrate` skill derives one verification command set from the work item's
`## Verification` / `## Fix Verification` section and uses it for both the
pre-merge run on the source branch and the post-merge regression check on the
destination branch. A task whose contract change affects code outside its own
declared verification scope can therefore merge a regression that the post-merge
check is structurally incapable of seeing, leaving the destination branch red
until the next loop iteration trips over its baseline guard.

## Reproduction Status

Status: confirmed by source inspection, plus a field incident

The reporting project hit this with T-101: its `## Verification` was
`cargo test -p pi-agent-supervisor && cargo test -p bob`, while the change broke
five `admin-rpc` dispatch tests. The project's real CI gate is
`cargo test --workspace`. Integration passed both Step 4 and Step 6 and left
`dev-agent` red; the breakage surfaced later as B-013 in that project.

## Evidence

- Logs / stack traces / failing assertions: n/a (the defect is that no failure is
  produced when one should be)
- Screenshots or recordings: n/a
- Failing command or test: the post-merge check in `integrate` Step 6 passes
  while the project's documented baseline suite fails on the destination branch.
- Source inspection (`cli/src/ai_team/init/sources/skills/integrate/body.md`):
  - Step 2, item 7 (line 40) sets the lookup order with the work item's
    `## Verification` section first, project guidance (`CLAUDE.md`, coding
    guidelines, README, build config) only as a fallback.
  - Step 2, item 8 (line 44) states the discovered set is used "for both pre-merge
    and post-merge verification unless the work item or project guidance
    explicitly defines separate source-branch and destination-branch checks" — so
    the default behaviour is a task-scoped post-merge check.
  - Step 6 (line 108) runs "the discovered destination-branch verification
    command set", which in the default case is the same task-scoped command.
- Related gap: `cli/src/ai_team/init/sources/skills/spec-breakdown/body.md:39`
  asks only for "a shell command that proves the task is done" — nothing directs
  the Planner to widen `## Verification` when a task alters a shared or
  cross-module contract.

## Reproduction Steps

1. Create a task whose `## Verification` section names a narrow, module-scoped
   test command.
2. Implement a change on the task branch that alters a shared or public interface
   consumed by a module outside that scope, breaking its tests.
3. Run `integrate` for the task branch.
4. Observe Step 4 (pre-merge) and Step 6 (post-merge) both pass, the merge lands,
   and the project-wide baseline suite is red on the destination branch.

## Expected Behavior

The post-merge regression check must be able to detect regressions outside the
work item's declared verification scope. Concretely, Step 6 should run the
documented project baseline (for example the workspace/full test suite named in
the project's `CLAUDE.md`) in addition to — or in preference to — the
task-scoped command, at minimum whenever the diff touches a shared or public
interface. The Planner-facing guidance should also require `## Verification` to
include the project baseline when a task changes a cross-module contract.

## Actual Behavior

Step 6 re-runs the same narrow command Step 4 ran. Cross-module regressions are
outside the checked scope, so integration reports success and the destination
branch is left broken.

## Environment

- OS / platform: Linux
- Language / runtime version: `ai-team` CLI 0.10.1 (skill sources are
  language-agnostic)
- Relevant dependencies:
  `cli/src/ai_team/init/sources/skills/integrate/body.md`,
  `cli/src/ai_team/init/sources/skills/spec-breakdown/body.md`
- Branch / commit: `dev-agent`, inspected 2026-08-05

## Related

- Task: n/a
- Specification: n/a
- External evidence: `/home/daneel/projects/the-intern/ai-process-cli-reported-issues.md`,
  entry dated 2026-06-23

## Suspected Area

`cli/src/ai_team/init/sources/skills/integrate/body.md` — Step 2 items 7 and 8,
and Step 6. Secondary: the task-authoring guidance in
`cli/src/ai_team/init/sources/skills/spec-breakdown/body.md` and the
`## Verification` guidance in `cli/src/ai_team/templates/task.md`.

## Fix Verification

Documentary, since the fix is a change to skill procedure rather than CLI code:

- `integrate` Step 6 states that the destination-branch check runs the documented
  project baseline, and defines what to do when no baseline is discoverable.
- The Step 2 lookup order distinguishes the source-branch command from the
  destination-branch command rather than defaulting both to the work item's
  section.
- Task-authoring guidance requires `## Verification` to cover the project
  baseline when the change alters a shared or public interface.
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

Reproduction status: confirmed by source inspection. This is a
procedural/documentation defect in skill source text (no automated test executes
skill prose), so reproduction means verifying the described gap exists verbatim in
the current sources on this branch, plus corroborating the field incident cited in
the bug (T-101 / B-013 in the reporting project).

Evidence captured:

- `cli/src/ai_team/init/sources/skills/integrate/body.md` (verified against
  `dev-agent` HEAD `a77d60b`; byte-identical on this branch,
  `git diff dev-agent...HEAD` for this path is empty):
  - Line 40: `7. Determine the verification command set before checking out the
    source branch. Lookup order:` — followed by two ordered sources (work item
    `## Verification`/`## Fix Verification` first, project guidance only as
    fallback). No branch of this lookup ever asks for a project-wide baseline
    command distinct from the task-scoped one.
  - Line 44: `8. Use the discovered command set for both pre-merge and post-merge
    verification unless the work item or project guidance explicitly defines
    separate source-branch and destination-branch checks.` — the single discovered
    set is the default for both checks.
  - Line 108 (`### Step 6: Run Tests on the Destination Branch (Regression
    Check)`) and line 110: `After the merge, on the destination branch, run the
    discovered destination-branch verification command set:` — in the default case
    this is the same task-scoped command Step 4 already ran. A regression outside
    that scope produces no failing test in either Step 4 or Step 6.
  - All three cited line numbers (40, 44, 108) match the bug report exactly — no
    drift since the bug was filed.
- `cli/src/ai_team/init/sources/skills/spec-breakdown/body.md` line 39:
  `- **Verification command**: Shell command that proves the task is done.` —
  confirms the secondary citation. Step 3's surrounding guidance (lines 33-44)
  never instructs the Planner to widen `## Verification` to a project baseline when
  a task changes a shared or public interface.
- Corroborating cross-reference:
  `cli/src/ai_team/init/sources/skills/dev-loop/body.md` line 36 states the
  rationale for not re-running a project baseline between tasks: "post-merge
  regressions are caught by the integrate skill's destination-branch test step;
  re-checking between tasks adds latency without adding coverage." That assumption
  is false under the current `integrate` text, so the dev-loop design relies on a
  guarantee `integrate` does not provide. Flagged as evidence only; no change
  proposed to dev-loop here.
- Parity check across parallel copies — the same gap is replicated everywhere it is
  exported, confirming a single-source defect rather than sync drift:
  - `cli/src/ai_team/init/scaffolds/{claude,codex}/skills/integrate/SKILL.md` —
    both generated from the same source; lines 47, 51, and 117 contain identical
    wording.
  - `cli/src/ai_team/init/scaffolds/{claude,codex}/skills/spec-breakdown/SKILL.md`
    — line 46 contains identical "Verification command" wording.
  - Repo-local `.claude/skills/{integrate,spec-breakdown}/SKILL.md` and `.codex/`
    equivalents — `diff` against the corresponding scaffolds returns no differences
    (exit 0) in all four cases.
  - Source-of-truth vs generated per `CLAUDE.md`:
    `cli/src/ai_team/init/sources/skills/{integrate,spec-breakdown}/body.md` are the
    two files that must change. `cli/src/ai_team/init/scaffolds/**` is generated
    output — never hand-edited, only regenerated via
    `python scripts/sync_init_scaffolds.py`. The repo-local `.claude/` and `.codex/`
    directories are gitignored and untracked (`git ls-files .claude/ .codex/`
    returns 0 files; `.gitignore` lines 2-3 list them), so they are out of scope.
- `git status --short` clean before and after inspection; no production or scaffold
  files were modified during diagnosis.

Isolated fault: `cli/src/ai_team/init/sources/skills/integrate/body.md`, Step 2
items 7-8 (lines 40-44) and Step 6 (lines 108-110). The verification-command lookup
treats "the destination-branch check" as identical to "the source-branch check" by
default, so the post-merge regression check in Step 6 inherits whatever narrow
scope the work item declared. There is no mechanism in `integrate` for discovering
or layering in a project-wide baseline command for the destination-branch check.
Secondary/contributing fault:
`cli/src/ai_team/init/sources/skills/spec-breakdown/body.md` Step 3 (around line
39) gives Planners no instruction to widen `## Verification` to the project
baseline when a task changes a shared or public interface.

Root cause or fault hypothesis: confirmed specification/procedure error, not a
hypothesis. The skill's design conflates two distinct verification concerns —
"does this task's own contract hold" (correctly task-scoped, appropriate for Step 4
pre-merge) and "did merging this task regress anything else on the destination
branch" (must be scoped to the destination branch's full contract, i.e. the
project's documented baseline command). Step 2 item 8 and Step 6 collapse these
into one command set by default, so any task whose declared `## Verification` is
narrower than the project's real CI gate leaves Step 6 structurally blind to
out-of-scope regressions — exactly the T-101/B-013 field incident
(`cargo test -p pi-agent-supervisor && cargo test -p bob` passed while
`cargo test --workspace` was red).

Planned verification (fix contract for the implementation session):

Source-of-truth files to change (both under
`cli/src/ai_team/init/sources/skills/`; nothing under `init/scaffolds/` is
hand-edited):

1. `cli/src/ai_team/init/sources/skills/integrate/body.md`
   - Step 2, items 7-8 (replace lines 40-44): split the single "verification
     command set" into two named outputs of Step 2:
     - `source-branch command` — unchanged lookup order (work item
       `## Verification`/`## Fix Verification` first, project guidance as fallback),
       used only for Step 4.
     - `destination-branch command` — determined by: (a) if the work item or
       project guidance explicitly defines a separate destination-branch/baseline
       check, use it; (b) otherwise discover the project's documented
       baseline/full-suite command using the same discovery order already owned by
       the `dev-loop` skill's Step 2 Baseline Test Guard (root guidance →
       referenced project-local docs → README/build config → smallest documented
       command that verifies the whole project), rather than re-deriving a second
       copy of that algorithm; (c) if the discovered baseline command differs from
       the source-branch command, Step 6 must run both (the baseline subsumes the
       task-scoped command's coverage, but running both preserves a like-for-like
       comparison against Step 4's results); (d) if no project baseline command is
       discoverable at all, Step 6 falls back to the source-branch command but
       Step 2 must record this explicitly as a coverage-gap flag to carry into
       Step 6's report — integrate must not silently treat the narrow command as
       sufficient, and must not block the integration solely because no baseline is
       documented (only a genuinely failing test blocks Step 6).
   - Step 6 (replace lines 108-118): state explicitly that the destination-branch
     check runs the project's documented baseline command (in addition to the
     task-scoped command when they differ), and that when no baseline was
     discoverable the report must say so in plain terms (e.g. "post-merge check
     used the task-scoped command only; no project-wide baseline command was
     discoverable — coverage outside the task's declared scope was not verified")
     rather than reporting success identical to Step 4 without qualification.
   - The "Output Format" verification line (~246) and "Common Pitfalls" section may
     need a one-line addition noting the coverage-gap flag, to keep the skill
     internally consistent — not required by the four Fix Verification bullets.
2. `cli/src/ai_team/init/sources/skills/spec-breakdown/body.md`
   - Step 3 (near line 39, in the `Then fill in the task body so it satisfies:`
     bullet list): add a requirement that `## Verification` must include the
     project's documented baseline/full-suite command — not only a module-scoped
     command — whenever the task changes a shared or public interface (an API,
     schema, shared library function, or contract consumed by code outside the
     task's own module).

Scaffold regeneration (run and verified, not hand-edited):

```bash
export UV_CACHE_DIR=/tmp/claude-uv-cache   # repo default cache is not writable here
cd cli
python scripts/sync_init_scaffolds.py
git status --porcelain src/ai_team/init/scaffolds   # must be empty after regeneration
```

Test verification, given the CLI suite's parity/sync tests:

```bash
cd cli
uv run pytest
```

This must include at minimum `cli/tests/test_init_scaffolds.py` and
`cli/tests/test_t064_skill_bodies_canonical.py` — both compare
`sources/skills/<name>/body.md` content against
`scaffolds/<tool>/skills/<name>/SKILL.md` and would fail if the edited `body.md`
files and the regenerated scaffolds ever diverge, so a green `uv run pytest` after
regeneration is direct proof the two stay in sync. No test targets the procedure
text itself (there is no automated way to execute skill prose), so the fix's
correctness is verified by (a) re-quoting the replaced Step 2 / Step 6 / Step 3 text
and confirming it states the destination-branch baseline behavior, the
no-baseline-discoverable behavior, and the Planner-facing cross-module
`## Verification` requirement, and (b) the existing parity/sync suite passing. The
gitignored, untracked `.claude/`/`.codex/` local copies are out of scope.

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-08-06

Implemented the documentary fix for B-015 per the recorded Diagnosis Log's fix
contract. This is a procedure/prose fix, not code, so the tdd red-green cycle did
not apply directly; instead I treated each of the bug's four Fix Verification
bullets as the target and proved them by quoting the resulting text plus running
the scaffold parity and sync test suites.

In `cli/src/ai_team/init/sources/skills/integrate/body.md`, Step 2 items 7-8
(previously a single "determine the verification command set... use it for both
pre-merge and post-merge" pair) were split into two genuinely distinct lookups.
Item 7 keeps the original lookup order (work item `## Verification`/`## Fix
Verification` first, project guidance as fallback) but is now explicitly scoped to
the source branch and Step 4 only. Item 8 is new: it determines the
destination-branch command by (a) checking for an explicit separate
destination-branch/baseline check in the work item or project guidance, (b)
otherwise discovering the project's documented baseline command using the same
discovery order the `dev-loop` skill's Step 2 Baseline Test Guard already owns — I
quoted that discovery order verbatim rather than re-deriving it, and verified the
cited `dev-loop` section still exists and says what I claim (lines 34-47,
"Discovery Order" list), (c) running both commands in Step 6 when they differ, and
(d) falling back to the source-branch command with an explicit coverage-gap flag
when no baseline is discoverable at all — the flag must be reported but must never
by itself block integration. Step 6 was rewritten to consume item 8's output
directly and to state the coverage-gap disclosure requirement in the report
("post-merge check used the task-scoped command only; no project-wide baseline
command was discoverable..."). I also added one line each to the Output Format
verification bullet and the Common Pitfalls list so the skill stays internally
consistent with the new behavior.

In `cli/src/ai_team/init/sources/skills/spec-breakdown/body.md`, I extended the
Step 3 "Verification command" bullet so Planners are told to include the project's
documented baseline/full-suite command in `## Verification` (not only a
module-scoped command) whenever a task changes a shared or public interface — an
API, schema, shared library function, or contract consumed outside the task's own
module.

I checked `cli/src/ai_team/templates/task.md`'s `## Verification` section as
required. It is a neutral placeholder comment ("# Command(s) to verify the task is
complete") with no narrow-scope framing to correct, and the `new-task` skill's
"Verifiable" quality bullet is similarly neutral (just requires a concrete
command). I decided no change was needed there since the actual authoring rule
change belongs in `spec-breakdown` Step 3, which is where task bodies are filled in
after `new-task` scaffolds the file — duplicating the rule in a second place would
violate the framework's "own it in one place" convention.

I considered folding items (a)-(d) into fewer bullets to keep Step 2 shorter, but
rejected that because the fix contract explicitly calls out four distinct branches
of behavior (explicit override, discovery, dual-run, and no-baseline fallback with
flag), and collapsing them risked losing the "must not silently treat the narrow
command as sufficient" and "must not block on missing baseline alone" nuances that
are the crux of the fix.

Ran `python scripts/sync_init_scaffolds.py` after each source edit and confirmed
`git status --porcelain cli/src/ai_team/init/scaffolds` was empty post-regeneration
each time, so the four scaffold files (`claude`/`codex` × `integrate`/
`spec-breakdown`) are exact derivations. Ran `uv run pytest` (446 passed, including
`test_init_scaffolds.py`, `test_t064_skill_bodies_canonical.py`, and the
pre-existing `test_t063_integration_guards.py` phrase assertions on `integrate`/
`dev-loop`/`bug-loop`, all unaffected) and `uv run ruff format --check . && uv run
ruff check .` (both clean). `cli/docs/commands.md` was not regenerated since neither
CLI command output nor release guidance changed (verified no `integrate`/
`spec-breakdown` references exist there).

Committed in two logical increments on `bug/B-015-integrate-post-merge-baseline`:
`d718b5a fix(skills): give integrate a distinct destination-branch baseline check`
(integrate source + both scaffolds) and `ed72979 fix(skills): require baseline
verification for shared-interface tasks` (spec-breakdown source + both scaffolds).
Nothing remains outstanding against the bug's Fix Verification bullets; ready for
review.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that diagnosis, fix, verification, and code quality passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
