---
title: "Project Coding Guidelines"
status: draft
created: 2026-03-12
---

# Project Coding Guidelines

This document extends the framework coding standards in `ai-process/guidelines/coding-standards.md` with project-specific conventions.

Framework guidelines cover general principles, error handling, security, and file organization. This document specifies how those principles apply to this project's technology stack and conventions.

## Naming

- Use the naming convention of the project's language (e.g., `camelCase` for JavaScript, `snake_case` for Python).
- Names should describe purpose, not implementation: `get_active_users()` not `query_db_filter_active()`.
- Boolean variables start with `is`, `has`, `can`, `should`: `is_valid`, `has_permission`.
- Constants use `UPPER_SNAKE_CASE`.

**Project-specific rules:**
- (Add language/framework-specific naming conventions here)

## Functions

- Do one thing. If a function does multiple things, split it.
- Keep functions short — aim for under 30 lines. If longer, check if it can be decomposed.
- Limit parameters to 3-4. If more are needed, use a configuration object or data class.
- Return early to reduce nesting.

**Project-specific rules:**
- (Add language/framework-specific function patterns here)

## Dependencies

- Minimize external dependencies. Prefer standard library when it meets the need.
- Pin dependency versions in lock files.
- New dependencies require justification in the task notes or a decision record.

**Project-specific rules:**
- (Add approved dependency list or restrictions here)
