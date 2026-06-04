# Codex Skills Review

This report explains the reasons for the `codex_skills/skills` updates made during the process review. The goal was to optimize the AI-team process represented by the skills, reduce duplicated instructions, and close handoff gaps between cooperating roles.

## Review Method

The review used four parallel subagent passes with `skill-creator`, each focused on a distinct process slice:

- Planning and reporting skills.
- Debugging, TDD, and code review skills.
- Development loop, bug loop, integration, merge conflict, and git convention skills.
- Cross-role escalation handling.

The final pass reconciled the subagent changes, fixed cross-skill contract mismatches, and added the missing `new-bug` update so every skill in `codex_skills/skills` participates coherently in the process.

## Main Problems Found

### Duplicated Ownership Rules

Several skills repeated branch, lifecycle, handoff, and commit rules independently. This made it easy for the process to drift: a loop could say one thing, integration another, and git conventions a third.

Reason for change: centralize shared rules in `git-conventions` and have loops and integration reference it as the source of truth.

### Weak Evidence Chain For Bug Fixes

The original bug flow let diagnosis, implementation, and review overlap too much. `debug` both diagnosed and described fixing; `tdd` did not require a complete diagnosis contract; `code-review` could approve based on tests without forcing the diagnosis-to-fix chain to be explicit.

Reason for change: make `debug` diagnosis-only, require a Diagnosis Log with a fix contract, make `tdd` implement that contract, and make `code-review` validate the evidence chain.

### Review And Integration Could Trust Chat Too Much

The loops and integration flow did not consistently require committed lifecycle evidence before moving forward. That left room for a branch to be integrated based on an uncommitted reviewer summary or missing Work Log/Review Verdict state.

Reason for change: require committed Review Verdict entries, committed Developer handoffs, canonical lifecycle files on `dev-agent`, and explicit integration evidence.

### Planning Handoffs Were Blurry

`brainstorm`, `new-spec`, `spec-breakdown`, `new-task`, and `spec-breakdown-review` overlapped in what they considered responsible for. That duplication made it unclear where product direction ends, where spec writing begins, and where technical task-plan validation starts.

Reason for change: clarify process boundaries:

- `brainstorm` owns direction-setting and alternatives.
- `new-spec` owns Gate 1-ready spec shape.
- `spec-breakdown` owns full-plan coverage, dependencies, and task boundaries.
- `new-task` owns per-task shape.
- `spec-breakdown-review` owns Gate 2 technical readiness.

### Escalation Was Not Clearly A Single Process

Escalation rules existed in multiple places, but the process did not clearly define when a role should keep recovering locally, when an Architect should decide, when an ADR is warranted, and when a human must decide.

Reason for change: make `escalation-review` the single cross-role impasse handler and define artifact flow for unresolved risks.

## Changes By Process Area

## Planning And Gate 1/Gate 2

Updated:

- `codex_skills/skills/brainstorm/SKILL.md`
- `codex_skills/skills/new-spec/SKILL.md`
- `codex_skills/skills/spec-breakdown/SKILL.md`
- `codex_skills/skills/spec-breakdown-review/SKILL.md`
- `codex_skills/skills/new-task/SKILL.md`
- `codex_skills/skills/new-adr/SKILL.md`

Reasons:

- Reduce repeated spec/task guidance by pointing each skill to the owning skill for detailed rules.
- Make `brainstorm` stop at confirmed direction and only hand off to `new-spec` after human confirmation.
- Make `new-spec` explicitly prepare a Gate 1-ready draft and identify `[TODO]` items that block approval.
- Make `spec-breakdown` stop when unresolved scope or architecture `[TODO]` items remain instead of inventing details.
- Make `spec-breakdown-review` check spec coverage before dependency and file-conflict checks.
- Fix the `new-adr` input contract so callers use `title`, `description`, `status`, and optional `supersedes`, not a stale `context` field.

Process effect:

Planning now has clearer gates. Product direction is confirmed before spec writing, approved specs are decomposed without re-litigating product scope, and Gate 2 validates technical readiness rather than acting as another product review.

## Bug Diagnosis, TDD, And Review

Updated:

- `codex_skills/skills/debug/SKILL.md`
- `codex_skills/skills/tdd/SKILL.md`
- `codex_skills/skills/code-review/SKILL.md`

Reasons:

- Remove implementation ownership from `debug`; it now produces diagnosis evidence only.
- Add a required fix contract to bug diagnosis so implementation has a narrow target.
- Make `tdd` consume the diagnosis contract and return red/green/verification evidence in the Work Log.
- Make `code-review` fail missing evidence instead of reconstructing intent from the diff.

Process effect:

Bug fixes should be less speculative. The process now distinguishes "we know what failed and why" from "we implemented and verified the fix", which should reduce brittle fixes and review churn.

## Loops, Integration, And Git Rules

Updated:

- `codex_skills/skills/git-conventions/SKILL.md`
- `codex_skills/skills/dev-loop/SKILL.md`
- `codex_skills/skills/bug-loop/SKILL.md`
- `codex_skills/skills/integrate/SKILL.md`
- `codex_skills/skills/merge-conflicts/SKILL.md`

Reasons:

- Centralize lifecycle ownership and shared handoff contracts in `git-conventions`.
- Require active loops to stop when active slots are already occupied.
- Require committed Developer Work Log or Diagnosis Log handoffs before review.
- Require committed Review Verdict entries before integration.
- Require `integrate` to verify the latest canonical `PASS` verdict before merging.
- Prevent implementation branches from carrying task or bug lifecycle-state edits into integration.
- Remove routine forced branch deletion; safe deletion failure is reported instead.
- Tighten merge conflict handling around preserving both work items' intent.

Process effect:

The process now has better traceability and safer git behavior. A later agent can resume from committed lifecycle files and integration evidence instead of relying on chat history.

## Escalation

Updated:

- `codex_skills/skills/escalation-review/SKILL.md`

Reasons:

- Define escalation as a cross-role impasse handler, not a replacement for normal Developer, Reviewer, Integrator, or Planner work.
- Check whether the caller exhausted its own recovery path before escalating further.
- Route unresolved risks to the correct artifact: Work Log, Diagnosis Log, Review Verdict, task amendment, bug amendment, ADR, spec amendment, or human escalation report.
- Make ADR creation appropriate only for durable architecture-affecting decisions.
- Define a single Phase 2 human escalation report template.

Process effect:

Escalations should become more actionable and less circular. The Architect has one place to decide whether work continues, gets recorded as an ADR, goes back to a role, or needs human direction.

## Reporting And Bug Creation

Updated:

- `codex_skills/skills/status-report/SKILL.md`
- `codex_skills/skills/new-bug/SKILL.md`

Reasons:

- Make `status-report` CLI-first, with manual scanning used only as fallback or discrepancy validation.
- Update `new-bug` so integration regression bugs include evidence, source branch, expected/actual behavior, and fix verification.

Process effect:

Gate 5 reporting should be more consistent, and regression bugs filed during integration should contain enough information for `bug-loop` to start diagnosis without chat reconstruction.

## Redundancy Reductions

The biggest redundancy reduction was moving shared contracts to owning skills:

- Branch model, lifecycle ownership, handoffs, commit rules, destructive-git restrictions, and integration evidence now live in `git-conventions`.
- Per-task quality lives in `new-task`; plan-wide correctness lives in `spec-breakdown` and `spec-breakdown-review`.
- Spec section rules live in `new-spec`; brainstorming only supplies confirmed direction and alternatives.
- Cross-role blocked-work handling lives in `escalation-review`.

This keeps each skill smaller in responsibility even when some skills still cite the owning rules for safety.

## Gaps Closed

- Missing fix contract between diagnosis and implementation.
- Missing Gate 2 spec coverage check.
- Missing committed `PASS` verdict requirement before integration.
- Missing lifecycle-file protection during integration.
- Missing safe handling of occupied `in-progress` slots.
- Missing artifact routing for escalation outcomes.
- Missing evidence requirements for integration-created regression bugs.

## Remaining Considerations

- The copied skills include extra frontmatter fields such as `allowed-tools`, `argument-hint`, and `effort`. I preserved them because these copied skills appear to model the source process format, even though system `skill-creator` guidance says Codex-triggered skills normally use only `name` and `description`.
- These edits were made in `codex_skills/skills` only. The repository source-of-truth scaffolds were not updated.
- No `agents/openai.yaml` files exist under `codex_skills/skills`, so there was no UI metadata to regenerate.

## Verification

Commands run:

```bash
git diff --check -- codex_skills/skills
cd cli && UV_CACHE_DIR=/tmp/uv-cache uv run pytest
cd cli && UV_CACHE_DIR=/tmp/uv-cache uv run ruff format --check .
cd cli && UV_CACHE_DIR=/tmp/uv-cache uv run ruff check .
```

Results:

- `git diff --check` passed.
- `pytest` passed: 292 tests.
- `ruff format --check` passed.
- `ruff check` passed.
