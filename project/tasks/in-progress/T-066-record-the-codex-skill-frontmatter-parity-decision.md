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

### Session 1 — 2026-06-05

Picked up T-066 with an empty Work Log. Both acceptance criteria required documentation artifacts (ADR + guide update) with automated tests following the T-064/T-065 precedent.

**What was done:**

Ran `ai-team adr new "Codex skill frontmatter retains full parity with Claude" --status accepted --json` to create the skeleton ADR at `project/decisions/ADR-001-codex-skill-frontmatter-retains-full-parity-with-claude.md`. Wrote the failing test file `cli/tests/test_t066_codex_frontmatter_parity_decision.py` first (9 tests: 6 failing, 3 trivially passing due to the skeleton ADR having "parity" in title and "accepted" in frontmatter). Then implemented the green step: filled in the ADR with Context, Decision, Consequences, and Alternatives Considered sections covering the full frontmatter key set (`allowed-tools`, `argument-hint`, `effort`, `disable-model-invocation`), the `Skill()` wiring implication, and the rationale for full parity. Updated `guides/skill_template.md` by adding a `### Codex frontmatter parity (ADR-001)` subsection under Frontmatter Guidance. Ran `ruff format` to satisfy the linter. All 366 tests pass; ruff format and check both clean.

**What was tried and rejected:**

Considered adding the Codex parity note to the `## Pre-Publication Checklist` section of the skill template instead, but the Frontmatter Guidance section is where all key-level policy lives — that was the more natural placement and keeps the checklist focused on mechanical verification rather than policy statements.

**What remains:**

Nothing. Both ACs are satisfied, tests pass, and lint is clean. Task is ready for review.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
