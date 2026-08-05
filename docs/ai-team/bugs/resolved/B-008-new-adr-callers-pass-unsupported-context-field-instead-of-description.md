---
id: B-008
title: new-adr callers pass unsupported 'context' field instead of 'description'
severity: high
status: resolved
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
# NOTE: the field is rendered as `context` (backtick-wrapped), so the grep pattern
# must include the backticks — a bare "context:" never matches and yields a false "ok".
for f in cli/src/ai_team/init/sources/skills/spec-breakdown-review/body.md \
         cli/src/ai_team/init/sources/skills/escalation-review/body.md; do
  grep -nA6 "new-adr" "$f" | grep -q '`context`' && echo "STILL BROKEN: $f" || echo "ok: $f"
  grep -nA8 "new-adr" "$f" | grep -q '`description`' && echo "description present: $f" || echo "MISSING description: $f"
  grep -nA8 "new-adr" "$f" | grep -q '`status`' && echo "status present: $f" || echo "MISSING status: $f"
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

### Diagnosis 1 — 2026-06-04

**Reproduction status:** Confirmed. Static caller/callee contract mismatch, visible by direct file inspection; no runtime execution required.

**Evidence captured:**
- Callee `cli/src/ai_team/init/sources/skills/new-adr/body.md` (Input Requirements) accepts `title`, `description`, `status` (`proposed`/`accepted`/`superseded`), and optional `supersedes`. It does NOT accept `context`.
- Caller `cli/src/ai_team/init/sources/skills/spec-breakdown-review/body.md` line 40: `` - `context`: the approved spec path... `` — `description` absent, `status` absent.
- Caller `cli/src/ai_team/init/sources/skills/escalation-review/body.md` line 41: `` - `context`: the escalation request... `` — `description` absent, `status` absent.
- Both exports are broken (not just Claude): `.claude/skills/{spec-breakdown-review,escalation-review}/SKILL.md` and `.codex/skills/{spec-breakdown-review,escalation-review}/SKILL.md` all carry the same `` `context` `` field. The bug report's claim that the Codex export was already fixed is NOT borne out by current file state. (Export re-render is owned by T-067, not this bug.)
- The original Fix Verification script gave a FALSE NEGATIVE: it greps `context:` but the text is `` `context`: `` (backtick before the colon), so the bare substring `context:` never matches and the script printed `ok` for both files even while broken. Verified live: original pattern → `ok: ...` (both); backtick-aware pattern `` `context` `` → `STILL BROKEN: ...` (both). The Fix Verification section has been corrected accordingly.

**Isolated fault:** In the `new-adr` invocation input lists of `spec-breakdown-review/body.md` (line 40) and `escalation-review/body.md` (line 41), the field `` `context` `` appears where `` `description` `` is required, and the required `` `status` `` field is omitted.

**Root cause:** When the `new-adr` caller blocks were authored, `context` was used as the field name (describing the contextual info to supply) instead of mapping to `new-adr`'s actual `description` input, and `status` was never added. Neither caller was aligned to the `new-adr` callee contract, so an Architect following these skills invokes `new-adr` with an unrecognised `context` and no `status`, leaving the ADR body unpopulated.

**Planned verification:** In both source files, replace `` `context`: <…> `` with `` `description`: <…> `` (folding the spec path / affected task IDs / relevant ADRs / durability rationale into description prose) and add a `` `status`: `` entry. Then run the corrected Fix Verification block: it must report `ok`, `description present`, and `status present` for both files. Export re-render is out of scope (T-067).

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-06-04

Read the bug file and the three relevant source files (`new-adr/body.md`, `spec-breakdown-review/body.md`, `escalation-review/body.md`) to confirm the diagnosis contract. Ran the corrected backtick-aware verification script and confirmed the red state: both callers showed `STILL BROKEN`, `MISSING description`, and `MISSING status`.

Applied two surgical edits — one per caller source file — replacing the `` - `context`: … `` bullet with `` - `description`: … `` (preserving the instructional prose verbatim) and adding a `` - `status`: `accepted` — … `` bullet. Chose `accepted` over `proposed` because in both caller contexts the Architect is issuing a concrete architectural resolution (adopting the decision now), not proposing one for later human approval; this matches `new-adr`'s own description of when each status value applies.

After the source edits the verification script went green for both files (`ok` / `description present` / `status present`). Then ran `uv run pytest -q`, which failed on `test_package_owned_skill_sources_include_body_and_required_metadata` because that test validates the CLI-internal scaffolds (`cli/src/ai_team/init/scaffolds/`) match their source bodies. Regenerated them with `scripts/sync_init_scaffolds.py` (mandated by CLAUDE.md whenever sources change), after which the full suite passed 292/292.

Scope decision: regenerated only the CLI-internal scaffolds under `cli/src/ai_team/init/scaffolds/` (a build artifact the test suite enforces). The repo-root `.claude/` and `.codex/` hand-copied exports were deliberately left untouched — re-rendering those is owned by T-067. Six files committed on the bug branch (2 sources + 4 scaffolds, claude+codex variants of both skills) as `34d35d6`.

Nothing remains beyond Reviewer approval and integration.

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

**Stage 1 — Bug Criteria**

- Diagnosis Log is present and complete: reproduction status (confirmed, static contract mismatch), evidence captured (callee Input Requirements vs caller field names, false-negative in original Fix Verification grep corrected with explanation), isolated fault (lines named), root cause documented, planned verification stated.
- Fix is scoped exactly to the isolated cause: in both `cli/src/ai_team/init/sources/skills/spec-breakdown-review/body.md` and `cli/src/ai_team/init/sources/skills/escalation-review/body.md` the `` `context` `` bullet is replaced by `` `description` `` and a `` `status`: `accepted` `` bullet is added. No unrelated behavior was introduced.
- `accepted` is a valid `new-adr` status value (confirmed against `cli/src/ai_team/init/sources/skills/new-adr/body.md`: `proposed`, `accepted`, or `superseded`). The rationale — the Architect is issuing a concrete resolution now — fits both caller contexts correctly.
- Fix Verification (corrected backtick-aware script) ran and passed: all six checks (`ok`, `description present`, `status present`) green for both files.

**Scope Decision**

- CLAUDE.md mandates "update source of truth first, then regenerate scaffolds" — confirmed.
- `scripts/sync_init_scaffolds.py` ran on the bug branch and produced no further diff (idempotent).
- Implementation commit `34d35d6` touches exactly 6 files: 2 sources + 4 scaffolds (claude + codex for each skill). Repo-root `.claude/` and `.codex/` exports were not modified (owned by T-067). The bug lifecycle file was not modified on the implementation commit.

**Stage 2 — Code Quality**

- Changes are surgical text substitutions; logic, tests, security, and performance criteria are not applicable beyond the text correctness check above.
- 292 tests pass (`uv run pytest -q` from `cli/`).
- No dead code, no hardcoded secrets, no readability issues introduced.
