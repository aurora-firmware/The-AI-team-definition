---
id: B-010
title: Loops never invoke status-report, leaving the Gate 5 summary orphaned
severity: medium
status: open
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
