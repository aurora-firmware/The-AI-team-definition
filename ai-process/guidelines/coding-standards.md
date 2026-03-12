---
title: "Coding Standards"
status: approved
created: 2026-03-10
---

# Coding Standards

These standards apply to any implementation code produced by AI agents using this framework.
They are intentionally language-agnostic.
When bootstrapping a new project, extend them with language-specific conventions, examples, and tooling rules relevant to your stack.
Project-specific overrides should be documented in the project's own guidelines.

**For naming conventions, function patterns, and dependency policies**, see `project/docs/coding_guidelines.md` (when working within a project). Each project should maintain its own extensions to these framework standards.

## General Principles

1. **Clarity over cleverness.** Code should be immediately understandable. Avoid tricks, obscure idioms, or unnecessarily compact expressions.
2. **Minimal scope.** Implement exactly what the task specifies. Do not add features, refactor unrelated code, or "improve" things that were not asked for.
3. **Self-documenting code.** Use descriptive names for variables, functions, and types. Comments explain *why*, not *what*.
4. **Fail explicitly.** When something goes wrong, surface a clear error rather than silently continuing with bad state.


## Error Handling

- Handle errors at the boundary where they can be meaningfully addressed.
- Do not catch and silently ignore exceptions.
- Include context in error messages: what failed, what input caused it, and what the caller can do about it.

## Testing

- Every task that produces code must also produce tests.
- Follow the TDD skill: write the test first, verify it fails, implement, verify it passes.
- Test behavior, not implementation details.
- Each test should be independent — no shared mutable state between tests.
- Name tests descriptively: `test_returns_empty_list_when_no_users_match_filter`.

## Security

- Never hardcode credentials, API keys, or secrets.
- Validate all external input (user input, API responses, file contents).
- Use parameterized queries for database access — never string concatenation.
- Follow the principle of least privilege for file access, network calls, and permissions.


## File Organization

- One module per file (unless the language convention differs).
- Keep files under 300 lines. If larger, consider splitting.
- Group related files in directories with clear purpose.
