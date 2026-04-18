---
id: "T-001"
title: "Restructure spec template — Exclusions first, delete Future Roadmap"
status: pending
priority: high
assigned-role: implementer
created: 2026-04-18
spec: project/specs/out-of-scope-first-class.md
---

# Restructure spec template — Exclusions first, delete Future Roadmap

## Description

Per spec `out-of-scope-first-class.md` (8.3), move the `## Exclusions` section in `TEMPLATE-specification.md` from position 7 to position 2 (immediately after Purpose, before Architecture).
Delete the `## Future Roadmap` section entirely.
Tighten the Exclusions section's example bullets to the format `- **title** Body.` (bold short title, period, prose body stating the reason). Bare bullet lists must be discouraged through the example itself.
Do not reorganise any other section of the template.

## Acceptance Criteria

AC-1: The `TEMPLATE-specification.md` file shall contain an `## Exclusions` section positioned immediately after `## Purpose` and immediately before `## Architecture`.
AC-2: The `TEMPLATE-specification.md` file shall not contain any `## Future Roadmap` section or heading.
AC-3: The `## Exclusions` section example bullets shall use the format `- **title** Body.` with a bold short title, a period, and a prose body stating the reason.
AC-4: The ordering of `## Architecture`, `## Components`, `## Workflow`, `## Configuration`, `## Implementation Order`, and `## Amendment Log` shall remain unchanged relative to each other.
AC-5: WHEN a human opens `TEMPLATE-specification.md` THE SYSTEM SHALL present Exclusions as the second top-level section.

## Dependencies

- None

## Files to Touch

- `.claude/skills/new-spec/assets/TEMPLATE-specification.md` — move Exclusions to position 2, delete Future Roadmap, update example bullet format

## Verification

```bash
# Exclusions must come before Architecture
awk '/^## /{print NR": "$0}' .claude/skills/new-spec/assets/TEMPLATE-specification.md | head -20
# Must not contain Future Roadmap
! grep -q '^## Future Roadmap' .claude/skills/new-spec/assets/TEMPLATE-specification.md
# Example bullet format present
grep -q '^- \*\*' .claude/skills/new-spec/assets/TEMPLATE-specification.md
```

## Notes

Reference: spec 8.3, Component 1.

## Review

<!-- Reviewer appends verdict here after each review cycle. -->
