# Release Notes: 0.6.0

Changes summarized from completed task artifacts included between tags `0.5.0`
and `0.6.0`.

## Included Tasks

1. `T-044` - Update spec breakdown docs and test planning
2. `T-045` - Narrow Gate 2 review to technical criteria
3. `T-046` - Add change request core artifact support
4. `T-047` - Implement change request CLI creation
5. `T-048` - Add change request listing and validation
6. `T-049` - Add project guidance templates to init scaffolds
7. `T-050` - Prompt for root guidance files during init
8. `T-051` - Update dev loop startup queue and test guards
9. `T-052` - Refresh framework docs for workflow improvements
10. `T-053` - Regenerate scaffolds and CLI command documentation
11. `T-054` - Add change request storage and template loading
12. `T-055` - Generate project guidance files in init scaffolds
13. `T-056` - Prefix new spec filenames with S-NNN identifier

## Summary

Version `0.6.0` adds a coordinated set of workflow and CLI improvements for the
AI-team framework.

The planning workflow now treats documentation and test updates as first-class
implementation work during spec breakdown. Gate 2 review has been tightened to
focus on technical task-plan readiness: dependencies, file conflicts,
architectural consistency, atomicity, and verification, rather than reopening
product approval.

This release introduces first-class change-request artifact support in the CLI.
Change requests now have a `CR-NNN` model, parser, dumper, ID allocator, bundled
Markdown template, project-root path, creation command, JSON output, listing
command, and validation support. The documented workflow now describes change
requests as a lighter intake path for smaller changes.

`ai-team init` now has stronger guidance scaffolding. It can create root
`CLAUDE.md` and `AGENTS.md` files for documenting project commands, especially
test commands, and every init run now includes project-level `project/CLAUDE.md`
and `project/AGENTS.md` guidance files explaining the artifact folders.

The `dev-loop` skill now performs safer startup checks. It discovers pending
tasks through the `ai-team` CLI task-state filter and requires a clear baseline
test command from root `CLAUDE.md` before claiming work. Missing, ambiguous, or
failing baseline tests stop the loop and require human action.

Spec creation is now more consistent with other artifacts: new specs are written
as `S-NNN-<slug>.md`, while validation continues to accept legacy `<slug>.md`
spec filenames. `list specs` now reports the frontmatter `S-NNN` ID rather than
the filename stem.

Generated scaffolds and CLI command documentation were refreshed, and the docs
were updated across workflow, setup, customization, usage, and component-map
guidance.

## Additional Notes

One non-task commit also appears in the tag range: it adds CLI pre-commit helper
scripts and a progress report.

Change-request support in this release is CLI/artifact support. The tag range
does not include a generated `change-request` skill.
