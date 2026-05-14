---
id: "T-031"
title: "Link README/setup-guide to cli/docs and add regeneration Contributing rule"
status: pending
priority: medium
assigned-role: "unassigned"
created: 2026-05-14
---

# Link README/setup-guide to cli/docs and add regeneration Contributing rule

## Description

Per spec `project/specs/ai-team-cli-documentation.md` (Phase 5), wire the new `cli/docs/` documentation into the repo's existing entry points and add the maintenance rule that keeps the generated reference current.

Two outcomes:
1. Update the existing CLI mentions in `README.md` and `guides/setup-guide.md` so they link into `cli/docs/` (`usage.md` for the guide, `commands.md` for the reference). Keep these mentions brief — `cli/docs/` is the documentation home; `README.md` and `setup-guide.md` only point to it. Do not relocate or duplicate the CLI documentation into them.
2. Add a Contributing rule — to `README.md`'s "Contributing to This Project" list and/or `CLAUDE.md` — instructing maintainers to run `bash cli/scripts/gen_docs.sh` and commit the updated `cli/docs/commands.md` whenever a CLI command or flag changes. Mirror the wording of the existing `sync_init_scaffolds.py` rule.

## Acceptance Criteria

AC-1: The system shall update the CLI mentions in `README.md` and `guides/setup-guide.md` to link to `cli/docs/usage.md` and `cli/docs/commands.md`.
AC-2: The system shall keep the CLI content in `README.md` and `guides/setup-guide.md` as brief pointers, not relocate or duplicate the `cli/docs/` documentation into them.
AC-3: The system shall add a Contributing rule instructing maintainers to run `bash cli/scripts/gen_docs.sh` and commit the updated `cli/docs/commands.md` when a CLI command or flag changes.
AC-4: WHEN a reader follows the CLI links from `README.md` or `guides/setup-guide.md` THE SYSTEM SHALL resolve them to existing files under `cli/docs/`.

## Dependencies

- `T-027` — `cli/docs/commands.md` and `cli/scripts/gen_docs.sh` must exist before they can be linked and referenced in the rule
- `T-028` — `cli/docs/usage.md` must exist before it can be linked

## Files to Touch

- `README.md` — update CLI mentions to link into `cli/docs/`; add regeneration Contributing rule
- `guides/setup-guide.md` — update CLI mentions to link into `cli/docs/`
- `CLAUDE.md` — add regeneration Contributing rule (if not placed solely in `README.md`)

## Verification

```bash
grep -q "cli/docs" README.md
grep -q "cli/docs" guides/setup-guide.md
grep -q "gen_docs.sh" README.md || grep -q "gen_docs.sh" CLAUDE.md
test -f cli/docs/usage.md && test -f cli/docs/commands.md
```

## Work Log

## Review
