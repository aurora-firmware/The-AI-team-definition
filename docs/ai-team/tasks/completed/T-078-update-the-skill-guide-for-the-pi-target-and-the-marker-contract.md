---
id: T-078
title: Update the skill guide for the pi target and the marker contract
status: completed
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

### Session 1 — 2026-09-30

I read the S-005 marker contract and ADR-002 and ADR-004, then added one section ("Render Targets and the CLI Marker Contract") to `guides/skill_template.md`, committed on `task/T-078-pi-skill-guide-marker-contract` as `c83cd77`. The section covers:
- the three render targets;
- the command marker, with pi call versus mention form chosen only by required-positional presence, and `--json` dropped for pi calls;
- the flag marker, where pi renders "set `<field>`" or the bare field name inside backticks;
- the noun marker `{{ai-team-cli|<claude/codex>|<pi>}}`;
- fence rules: a fence containing only markers becomes prose for pi, and a mixed fence fails the sync;
- placeholders checked by field name and presence, not value;
- the inline-context rule;
- markers allowed in the `[claude]` and `[codex]` headers;
- pi header derivation from `[claude]` with no `[pi]` section (ADR-002);
- how `Skill(<name>)`, the self-contained `.claude/` rule and `allowed-tools` apply to pi;
- orchestrators (`dev-loop`, `bug-loop`, `integrate`) rendered but excluded from the pi manifest until sub-project 5;
- the command map as the single command surface (ADR-004).

The spec only says these conventions are "defined by the guide", so I chose the pi applicability readings myself: `Skill()` is not rendered for pi because pi has no `allowed-tools`; in-body skill references stay valid but only to skills that ship to pi; pi tool scoping comes from the process layer. I rejected adding a guide-content test and rejected restating command syntax in the guide, since the command map owns it. Verification: grep hits for each required term (were zero before), pytest 461 passed, ruff format and ruff check clean. Nothing remains for this task. Reviewer should confirm the pi applicability readings above.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-09-30
PASS

Stage 1 (acceptance criteria), checked against the diff `feat/pi-extension...task/T-078-pi-skill-guide-marker-contract` (only `guides/skill_template.md`, +61 lines, in scope):
- AC-1 met: the new section defines syntax and per-target rendering of the command, flag and noun markers, call versus mention selection by required-positional presence, and the fence rules (marker-only fence becomes prose for pi, mixed fence fails). It matches the S-005 "Skill marker contract".
- AC-2 met: the pi header is derived from `[claude]` `name` and `description`, there is no `[pi]` section, noun markers render their pi text, and the guide states it extends ADR-001 (ADR-002).
- AC-3 met: applicability of `Skill()`, the `.claude/` rule and `allowed-tools` to pi is defined.
- AC-4 met: orchestrators (`dev-loop`, `bug-loop`, `integrate`) are rendered but excluded from the pi manifest until sub-project 5.
- AC-5 met: the command map is named as the single command surface (ADR-004).
- No unexpected files changed. The Verification greps hit and `uv run pytest` gives 461 passed (the change is docs-only).

Stage 2 (quality): the section is accurate to the spec, free of duplicated command syntax, and readable. No security or test concerns for a docs-only change.

Pi applicability readings confirmed against S-005 and ADR-001..004:
- `Skill()` not rendered for pi: consistent. ADR-002 says pi gets only `name` and `description`, and pi has no `allowed-tools`.
- In-body references only to skills that ship to pi: consistent with the orchestrator exclusion in S-005. It is a sensible reading of the open "defined by the guide" item.
- No `.claude/` paths in pi output: consistent with S-005 SC-10 and the pi package layout.
- `allowed-tools` not rendered for pi, with tool scoping from the process layer: matches the ADR-002 Negative consequence verbatim.

Non-blocking observations:
- The `.claude/` rule bullet says to use "`${CLAUDE_SKILL_DIR}`-style or skill-relative references that the sync can render per target". The spec does not require a render mechanism for this, so Phase 2 should confirm or adjust it.
- "Pi loads skills by name" is asserted without a spec citation. It is plausible under the Agent Skills spec.

Next owner: Development Loop.
