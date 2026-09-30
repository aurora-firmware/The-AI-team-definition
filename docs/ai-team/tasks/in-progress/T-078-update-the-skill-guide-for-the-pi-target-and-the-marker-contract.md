---
id: T-078
title: Update the skill guide for the pi target and the marker contract
status: in-progress
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Update the skill guide for the pi target and the marker contract

<!--
Task Quality Rules (see the new-task skill for full details):
  - Atomic — one clear outcome.
  - One-shottable — ≤ 3–4 files touched, ≤ 5 ACs, Description ≈ 20 lines.
  - Verifiable — concrete Verification command or explicit manual steps.
  - Self-contained — Description is enough to start without follow-up questions.
  - EARS — every AC matches one of the five EARS patterns below.
  - Dependency-honest — list every prior task this one reads from or modifies.
-->

## Description

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 0**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P1 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- pi as third render target; three marker kinds and per-target rendering (command marker call vs mention form by required-positional presence; `{{ai-team-flag}}` renders "set `<field>`" or bare field inside backticks; `{{ai-team-cli|cc|pi}}`); fence rules (markers-only fence becomes prose for pi, mixed fence fails); call-form placeholders checked by field name/presence not value; inline-context rule; markers allowed in [claude]/[codex] headers; pi header derived from [claude] name/description, no [pi] section (ADR-002); how Skill(<name>), the self-contained .claude/ rule and allowed-tools apply to pi; orchestrators (dev-loop, bug-loop, integrate) rendered but excluded from pi manifest until sub-project 5; command map is the single command surface (ADR-004). Out of scope: skill sources, sync, tests, other guides.

## Acceptance Criteria

AC-1: guide defines syntax and per-target rendering of all three kinds, incl. call/mention selection and fence rules (SC-1, marker contract).
AC-2: pi header derivation, no [pi] section, noun markers render pi text (SC-1, ADR-002).
AC-3: pi applicability of Skill(), .claude/ rule, allowed-tools (SC-1).
AC-4: orchestrators rendered but not shipped (SC-10).
AC-5: command map named as single source (ADR-004).

## Dependencies

- None

## Files to Touch

- guides/skill_template.md

## Verification

```bash
# grep for ai-team-flag / ai-team-cli / mention form / [claude] in the guide; V-PY.
# V-PY: cd cli && uv run pytest && uv run ruff format --check . && uv run ruff check .   # set UV_CACHE_DIR under /tmp if uv cannot write its cache
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
