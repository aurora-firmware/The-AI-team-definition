---
id: T-066
title: Record the Codex skill-frontmatter parity decision
status: pending
priority: low
assigned-role: unassigned
created: '2026-06-04'
---

# Record the Codex skill-frontmatter parity decision

## Description

Source: `full_skills_review.md` issue P2. Decision confirmed with the human: Codex skill
frontmatter keeps full parity with Claude — the `[codex]` headers retain `allowed-tools`,
`argument-hint`, `effort`, and `disable-model-invocation`, and skill-to-skill wiring (e.g.
`status-report`) stays expressed via `Skill()` in `allowed-tools`. Record this durable decision
so future skill-creator passes do not strip Codex frontmatter. Create an ADR via
`ai-team adr new` and note the policy in the skill-authoring guide.

## Acceptance Criteria

AC-1: An ADR in `project/decisions/` SHALL record that Codex skill frontmatter retains full
      parity with Claude, with rationale and the `Skill()`-wiring implication.
AC-2: The skill-authoring guide (`guides/skill_template.md`) SHALL state that `[codex]` headers
      keep the full frontmatter key set.

## Dependencies

- None

## Files to Touch

- `project/decisions/` — new ADR recording the parity decision (via `ai-team adr new`)
- `guides/skill_template.md` — note the Codex frontmatter-parity policy

## Verification

```bash
ls project/decisions/ | grep -iE "frontmatter|codex|parity"
grep -niE "codex" guides/skill_template.md
```

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
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
