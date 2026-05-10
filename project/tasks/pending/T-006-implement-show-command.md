---
id: "T-006"
title: "Implement ai-team show command"
status: pending
priority: medium
assigned-role: developer
created: 2026-05-10
---

# Implement ai-team show command

## Description

Implement `ai_team.commands.show` exporting a Typer `app` with `NAME = "show"`. The single default command takes an artifact identifier (`T-042`, `B-007`, `S-003`, `ADR-001`, or a slug fragment) and prints the matched file with Rich syntax highlighting for markdown.

Resolve the identifier across all artifact types and state folders by scanning under the project root resolved by the locator. With `--json`, emit `{"path": "...", "frontmatter": {...}, "body": "..."}` and produce no Rich output.

If multiple files match the supplied identifier, list candidate paths to stderr and exit non-zero. If no files match, print a clear "not found" message and exit non-zero.

## Acceptance Criteria

AC-1: WHEN `ai-team show <ID>` runs and exactly one artifact matches THE SYSTEM SHALL print the file with Rich markdown highlighting.
AC-2: WHERE `--json` is supplied THE SYSTEM SHALL emit a JSON object containing `path`, `frontmatter`, and `body` and no Rich output.
AC-3: IF multiple artifacts match the supplied identifier THEN THE SYSTEM SHALL list candidate paths to stderr and exit with a non-zero status.
AC-4: IF no artifact matches THEN THE SYSTEM SHALL print a "not found" message naming the searched roots and exit non-zero.

## Dependencies

- `T-002` — uses locator
- `T-003` — uses models for frontmatter
- `T-004` — uses fs read

## Files to Touch

- `cli/src/ai_team/commands/show.py` — Typer app with single command and identifier resolver
- `cli/tests/test_show.py` — covers single match, multi match, no match, JSON output

## Verification

```bash
cd cli && uv run pytest tests/test_show.py -q
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. -->

## Review

<!-- Reviewer: append verdict here after each review cycle. -->
