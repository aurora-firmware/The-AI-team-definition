---
id: B-010
title: Loops never invoke status-report, leaving the Gate 5 summary orphaned
severity: medium
status: in-progress
created: '2026-06-04'
---

# Loops never invoke status-report, leaving the Gate 5 summary orphaned

## Summary

`dev-loop` and `bug-loop` never invoke the `status-report` skill, so the Gate 5 summary they are
meant to produce is orphaned — each loop hand-rolls its own end-of-run summary while
`status-report` (which is `disable-model-invocation: true`) is unreachable. The Claude export
fixed this by adding `Skill(status-report)` and a Step-8 invocation; the Codex export and the
shared source still leave it unwired. Wire both loops to invoke `status-report` on a drained
queue and add `Skill(status-report)` to both loops' `[claude]` and `[codex]` headers (parity per
the P2 decision). Source: `full_skills_review.md` issue I8. Align after T-058 names
`status-report` as the Gate 5 producer.

## Reproduction Status

Status: confirmed

## Evidence

- Logs / stack traces / failing assertions: n/a (static wiring gap)
- `codex_skills/skills/dev-loop/SKILL.md` `allowed-tools` lacks `Skill(status-report)`; no
  status-report reference in the dev-loop or bug-loop bodies
- `status-report` carries `disable-model-invocation: true` (only invocable by explicit `Skill()`)
- `claude_skills/` already wired it (reference implementation)

## Reproduction Steps

1. Read `dev-loop`/`bug-loop` Step 8 (Loop Complete) in the Codex export.
2. Observe a hand-rolled summary list and no `status-report` invocation.
3. Confirm `status-report` is never reachable from the loops.

## Expected Behavior

WHEN the queue drains, the loop invokes `status-report` to produce the canonical Gate 5 summary.

## Actual Behavior

The loop hand-rolls its own summary; `status-report` never runs.

## Environment

- OS / platform: framework sources (platform-agnostic)
- Branch / commit: dev-agent

## Related

- Source report: `full_skills_review.md` (I8); doc side: `T-058`
- Skills: dev-loop, bug-loop, status-report
- Decision: P2 (keep full frontmatter / `Skill()` wiring) — `T-066`

## Suspected Area

`cli/src/ai_team/init/sources/skills/dev-loop/body.md`,
`cli/src/ai_team/init/sources/skills/bug-loop/body.md`,
`cli/src/ai_team/init/sources/skills/status-report/body.md`, and the `allowed-tools` in
`cli/src/ai_team/init/sources/skills/{dev-loop,bug-loop}/metadata.toml` (both `[claude]` and
`[codex]`). Re-render handled by T-067.

## Fix Verification

```bash
grep -niE "status-report" cli/src/ai_team/init/sources/skills/dev-loop/body.md \
                          cli/src/ai_team/init/sources/skills/bug-loop/body.md
grep -niE "status-report" cli/src/ai_team/init/sources/skills/dev-loop/metadata.toml \
                          cli/src/ai_team/init/sources/skills/bug-loop/metadata.toml
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

### Diagnosis 1 — 2026-06-04

**Reproduction status:** Confirmed. Static wiring gap; no runtime execution required. Both Fix Verification greps returned zero matches (the expected broken state — `status-report` is referenced nowhere in either loop's body or metadata).

**Evidence captured:**
- `cli/src/ai_team/init/sources/skills/dev-loop/body.md` Step 8 "Loop Complete" (lines ~174-181): hand-rolled bullet summary (tasks completed/merged, already-completed, blocked, integration failures); no `Skill(status-report)` invocation.
- `cli/src/ai_team/init/sources/skills/bug-loop/body.md` Step 8 "Loop Complete" (lines ~169-174): hand-rolled bullet summary (bugs resolved/merged, escalated, integration failures); no `Skill(status-report)` invocation.
- `cli/src/ai_team/init/sources/skills/dev-loop/metadata.toml` — `allowed-tools` in BOTH `[claude]` and `[codex]` is `Read, Glob, Grep, Bash, Agent, Skill(integrate), Skill(git-conventions)`; `Skill(status-report)` absent.
- `cli/src/ai_team/init/sources/skills/bug-loop/metadata.toml` — same absence in both sections.
- `cli/src/ai_team/init/sources/skills/status-report/metadata.toml` — both sections carry `disable-model-invocation: true`, so the skill is reachable only via an explicit `Skill(status-report)` call. With it absent from both loops' `allowed-tools` AND uncalled in both bodies, `status-report` is completely unreachable.
- `cli/src/ai_team/init/sources/skills/status-report/body.md` — runs `ai-team status`, counts artifacts, reads active specs/blocked tasks, inspects integration evidence, produces a canonical Gate 5 markdown summary, and writes a full report to `project/docs/reports/progress-report-[date].md`. Materially richer than the loops' hand-rolled bullets.
- Doc alignment: `ai-process/processes/workflow-overview.md:178` already names `status-report` as the Gate 5 producer (landed via T-058). The loop bodies are behind the documented contract, not the reverse.
- Syntax reference: `cli/src/ai_team/init/sources/skills/integrate/metadata.toml` uses `Skill(merge-conflicts), Skill(new-bug), Skill(git-conventions)` — confirms the `Skill(name)` token format for `allowed-tools`.

**Isolated fault:** Two identical wiring failures in each loop — (a) Step 8 hand-rolls an inline summary instead of invoking `Skill(status-report)`; (b) `allowed-tools` in both `[claude]` and `[codex]` omits `Skill(status-report)`, making the skill inaccessible even if the body called it.

**Root cause:** `status-report` is a `disable-model-invocation: true` skill that was never wired into the loops: neither loop lists it in `allowed-tools`, and neither Step 8 calls it. Both gaps must be fixed together for the skill to be reachable and used. The documented contract (workflow-overview.md:178) already expects the loops to invoke it.

**Planned verification:** Fix four source files (eight edits): append `Skill(status-report)` to the `[claude]` and `[codex]` `allowed-tools` in both `dev-loop/metadata.toml` and `bug-loop/metadata.toml` (parity per P2 / T-066); and in both `dev-loop/body.md` and `bug-loop/body.md` Step 8, invoke `Skill(status-report)` on a drained queue to produce the Gate 5 summary (folding/retaining the loop-specific items — blocked tasks, integration failures — as supplemental context). Post-fix, both Fix Verification greps must match in all four files. CLI scaffold regeneration (`scripts/sync_init_scaffolds.py`) follows so the test suite stays green; repo-root `.claude/`/`.codex/` export re-render is owned by T-067.

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-06-04

Single red→green cycle. Confirmed the red state first (both Fix Verification greps returned empty), then made four source edits:
- `cli/src/ai_team/init/sources/skills/dev-loop/metadata.toml` — appended `, Skill(status-report)` to `allowed-tools` in both `[claude]` and `[codex]` (identical, for parity per P2 / T-066).
- `cli/src/ai_team/init/sources/skills/bug-loop/metadata.toml` — identical append in both sections.
- `cli/src/ai_team/init/sources/skills/dev-loop/body.md` — Step 8 now invokes `Skill(status-report)` as the canonical Gate 5 summary producer; loop-specific run details (task IDs + merge commits, already-completed tasks, blocked tasks, integration failures) retained as supplemental context after the status-report output.
- `cli/src/ai_team/init/sources/skills/bug-loop/body.md` — same pattern; bug-loop-specific details (resolved bug IDs + merge commits, escalated bugs still in-progress, integration failures) retained as supplemental context.

Step 8 wording was informed by reading `status-report/body.md` first so the prose accurately describes what the skill produces (`ai-team status`, project-state scan, full progress report).

Regenerated the CLI-internal scaffolds with `uv run python scripts/sync_init_scaffolds.py` (bare `python` is not on PATH; used `uv run python`), producing the four `{claude,codex}/skills/{dev-loop,bug-loop}/SKILL.md` files. Repo-root `.claude/`/`.codex/` exports deliberately untouched — re-render is owned by T-067.

Verification: post-edit greps match in all four sources; `uv run pytest -q` → 292 passed; `uv run ruff check .` clean; `uv run ruff format --check .` clean. Eight files committed on the bug branch (4 sources + 4 scaffolds) as `1e8a149`. Nothing remains beyond review and integration.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that diagnosis, fix, verification, and code quality passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-06-04

PASS

Both stages passed.

**Stage 1 — Bug criteria:**
- Diagnosis Log records confirmed reproduction status (static analysis, no runtime needed), evidence captured (all four source files inspected, absent `Skill(status-report)` entries quoted), isolated fault (two wiring gaps: body Step 8 hand-rolls summaries; `allowed-tools` omits `Skill(status-report)` in both sections of both loops), and root cause. All required fields are present.
- Fix addresses both halves of the isolated fault: `Skill(status-report)` appended to `allowed-tools` in both `[claude]` and `[codex]` sections of `dev-loop/metadata.toml` and `bug-loop/metadata.toml` (sections are identical — parity maintained per P2 / T-066); Step 8 in both `dev-loop/body.md` and `bug-loop/body.md` now invokes `Skill(status-report)` as the authoritative Gate 5 summary producer, with loop-specific run details retained as supplemental context.
- Fix Verification greps ran and returned matches in all four files (body.md and metadata.toml for both loops).
- No unrelated behavior added.

**Stage 2 — Code quality:**
- Step 8 prose accurately describes what `status-report` does (`ai-team status`, project-state scan, full progress report) and is consistent with `ai-process/processes/workflow-overview.md:178` which already names `status-report` as the Gate 5 producer.
- `[claude]` and `[codex]` metadata sections are identical in both `dev-loop/metadata.toml` and `bug-loop/metadata.toml` — parity requirement satisfied.
- `status-report/metadata.toml` carries `disable-model-invocation: true` in both sections — the `allowed-tools` entry is genuinely required for reachability, and it is now present.
- Implementation commit (`1e8a149`) contains exactly 8 files: 4 sources + 4 scaffolds. The bug lifecycle file was touched in a prior commit (branch setup), not the implementation commit. Repo-root `.claude/` and `.codex/` exports are untouched, per the T-067 ownership constraint.
- Scaffold regeneration is idempotent: re-running `scripts/sync_init_scaffolds.py` produced no further diff.
- `uv run pytest -q`: 292 passed. `uv run ruff check .` and `uv run ruff format --check .`: both clean.
