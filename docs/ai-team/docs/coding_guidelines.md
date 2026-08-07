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

## The Zen of python

Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
Complex is better than complicated.
Flat is better than nested.
Sparse is better than dense.
Readability counts.
Special cases aren't special enough to break the rules.
Although practicality beats purity.
Errors should never pass silently.
Unless explicitly silenced.
In the face of ambiguity, refuse the temptation to guess.
There should be one-- and preferably only one --obvious way to do it.
Although that way may not be obvious at first unless you're Dutch.
Now is better than never.
Although never is often better than *right* now.
If the implementation is hard to explain, it's a bad idea.
If the implementation is easy to explain, it may be a good idea.
Namespaces are one honking great idea -- let's do more of those!
