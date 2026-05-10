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

### Session 1 — 2026-05-10

Implemented `T-006` end-to-end in four small TDD cycles on `task/T-006-implement-show-command`.

I started by adding a failing test for `ai-team show T-001` and then created `ai_team.commands.show` with `NAME = "show"` and a default command path that renders markdown through Rich. I then added a failing `--json` test and implemented JSON output as `{"path","frontmatter","body"}` using the core read/model path so frontmatter keys stay canonical (including `assigned-role`).

While implementing `--json`, I first tried a straightforward callback shape and hit Typer parsing issues for `show <id> --json`. I rejected an empty-name command approach because it broke invocation under mounted sub-typers. I fixed this by keeping callback mode and using a custom Typer group class with `allow_interspersed_args = True`, which preserves `show <id> --json`.

Next, I added failing tests for ambiguous matches and not-found behavior. I updated resolution to scan canonical artifact roots from locator (`tasks/*`, `bugs/*`, `specs`, `decisions`), return non-zero for multi/no matches, print candidate paths to stderr for ambiguity, and print a clear not-found message with searched roots. I also added explicit slug-fragment success coverage.

All task verification tests now pass, and there is no remaining implementation work on this task branch.

## Review

<!-- Reviewer: append verdict here after each review cycle. -->
