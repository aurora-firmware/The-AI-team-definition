---
id: B-008
title: new-adr callers pass unsupported 'context' field instead of 'description'
severity: high
status: in-progress
created: '2026-06-04'
---

# new-adr callers pass unsupported 'context' field instead of 'description'

## Summary

The `new-adr` skill consumes `title`, `description`, `status`, and optional `supersedes`. Two
callers — the `spec-breakdown-review` skill and the `escalation-review` skill — instruct the
Architect to invoke `new-adr` with a `title` + `context` field that `new-adr` does not accept.
`description` is therefore left empty and `status` is never supplied, so the created ADR body is
not populated as intended. The Codex export already fixed this (its `escalation-review` passes a
rich `description`); the Claude export and the shared source still pass `context`. Source:
`full_skills_review.md` issue I6. Fix at source so both exports re-render correctly.

## Reproduction Status

Status: confirmed

Static caller/callee contract mismatch, visible by reading the files.

## Evidence

- Logs / stack traces / failing assertions: n/a (static contract defect)
- Callers (Claude export): `claude_skills/skills/spec-breakdown-review/SKILL.md:47` and
  `claude_skills/skills/escalation-review/SKILL.md:67` pass `- context:`
- Callee: `claude_skills/skills/new-adr/SKILL.md` Input Requirements list
  `title`/`description`/`status`/`supersedes` — no `context`
- Source of truth carries the same defect:
  `cli/src/ai_team/init/sources/skills/spec-breakdown-review/body.md`,
  `cli/src/ai_team/init/sources/skills/escalation-review/body.md`

## Reproduction Steps

1. Read `new-adr` Input Requirements (title/description/status/supersedes).
2. Read the `new-adr` invocation block in `spec-breakdown-review` and `escalation-review`.
3. Observe both callers pass `context` (a field `new-adr` never reads) and neither passes `status`.

## Expected Behavior

Callers invoke `new-adr` with `title`, `description` (folding the spec path, affected task IDs,
relevant ADRs, and durability rationale into the description prose), and `status`.

## Actual Behavior

Callers pass `title` + `context`. `new-adr` ignores `context`, leaving `description` empty and
`status` unset, so the generated ADR body is not populated.

## Environment

- OS / platform: framework sources (platform-agnostic)
- Branch / commit: dev-agent

## Related

- Source report: `full_skills_review.md` (I6)
- Skills: new-adr, spec-breakdown-review, escalation-review

## Suspected Area

`cli/src/ai_team/init/sources/skills/spec-breakdown-review/body.md` and
`.../escalation-review/body.md` — the `new-adr` invocation input list. Re-render to both exports
is handled by T-067.

## Fix Verification

```bash
for f in cli/src/ai_team/init/sources/skills/spec-breakdown-review/body.md \
         cli/src/ai_team/init/sources/skills/escalation-review/body.md; do
  grep -nA6 "new-adr" "$f" | grep -q "context:" && echo "STILL BROKEN: $f" || echo "ok: $f"
done
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
