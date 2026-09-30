---
id: ADR-002
title: Pi skill headers are derived from the Claude header
status: accepted
created: '2026-09-30'
---

# ADR-002: Pi skill headers are derived from the Claude header

## Context

S-005 (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`,
approved v1.0) adds a third render target, `pi`, to `cli/scripts/sync_init_scaffolds.py`.
Every skill in `cli/src/ai_team/init/sources/skills/` has one `body.md` and a
`metadata.toml` with hand-authored `[claude]` and `[codex]` header strings. ADR-001 decided
that the `[codex]` header keeps full frontmatter-key parity with `[claude]`. It rejected
per-target key sets (Alternative A) because they create a two-track authoring burden, and it
rejected separate per-target source files (Alternative B) because of drift.

Pi implements the Agent Skills specification and needs only `name` and `description` in a
skill header. It has no `allowed-tools`, `argument-hint`, `effort` or
`disable-model-invocation`. A pi header therefore can't share ADR-001's full key set. If it
were authored by hand, it would add a third header to every skill and bring back the burden
ADR-001 rejected.

Several current descriptions say "via the ai-team CLI". S-005 requires that pi-rendered text
never refers to running the binary. Its noun marker `{{ai-team-cli|<claude/codex text>|<pi text>}}`
may appear in the `[claude]` and `[codex]` headers. The sync renders each marker for its own
target, so claude and codex headers stay byte-identical to today's.

## Decision

The pi skill header is derived by the sync from the `name` and `description` in each skill's
`[claude]` header. No `[pi]` section is authored in `metadata.toml`. Noun markers in the
description render with their pi text.

This decision extends ADR-001 to a third target. It does not supersede ADR-001 and does not
change it:

- The `[claude]` and `[codex]` headers keep full frontmatter-key parity, exactly as ADR-001
  decides.
- Markers in the `[claude]` and `[codex]` headers render to today's exact text for those
  targets, so neither header's keys nor its bytes change.
- The pi header is a derived subset (`name`, `description`). It is not a parity-bound peer
  of the other two headers, and authors never edit it.

The skill guide (`guides/skill_template.md`, updated in S-005 Phase 0) records this rule,
along with how `Skill(<name>)` references, the self-contained `.claude/` rule and
`allowed-tools` apply to the pi target.

## Consequences

### Positive

- Authors still maintain two headers per skill. Adding the pi target adds no authoring work.
- The pi `name` and `description` can't drift from the Claude ones, because they come from
  the same source.
- ADR-001's claude/codex parity and its skill-to-skill `Skill(<name>)` wiring are untouched.

### Negative

- Pi can't carry a description tuned for pi, except through the noun marker's pi text.
- The sync has to parse the YAML frontmatter inside the `[claude]` header string. Today it
  copies that string verbatim.
- Pi skills have no `allowed-tools` equivalent in their header. Any pi tool-scoping has to
  come from the process layer (S-005 sub-project 4), not from skill metadata.

### Neutral

- ADR-001's note that the sync script "requires no changes" no longer describes the current
  script. ADR-001's decision itself still holds.
- Tests that compare raw `[claude]` headers with scaffold headers move to rendered output
  (S-005 SC-2).

## Alternatives Considered

### Alternative A: Hand-authored `[pi]` section in every `metadata.toml`

**Description:** Add a third header string per skill, written for pi's key set.
**Rejected because:** It is the per-target authoring burden and drift risk that ADR-001
Alternative A rejected, now for a third target, and it adds nothing pi needs beyond `name`
and `description`.

### Alternative B: Emit the full `[claude]` header unchanged for pi

**Description:** Reuse the Claude header as is, including Claude-specific keys.
**Rejected because:** Pi would receive keys it doesn't understand, and descriptions that say
"via the ai-team CLI" would break S-005's rule that pi-rendered text never refers to the
binary.

### Alternative C: Supersede ADR-001 with a three-way parity rule

**Description:** Require every target's header to carry the same full key set.
**Rejected because:** Pi's Agent Skills header doesn't support the Claude-specific keys, so
three-way parity can't be met. Extending ADR-001 leaves its decision intact.
