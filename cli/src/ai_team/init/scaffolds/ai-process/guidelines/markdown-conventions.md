---
title: "Markdown Conventions"
status: approved
created: 2026-03-10
---

# Markdown Conventions

Generated project artifacts are Markdown.
These conventions apply to bugs, tasks, specs, ADRs, and role/procedure outputs created by the AI team.

## Frontmatter

Every document starts with YAML frontmatter enclosed in `---` fences:

```yaml
---
title: "Document Title"
status: draft
created: 2026-01-15
---
```

Additional fields depend on document type. See each `TEMPLATE-*.md` for the required fields.

## Headings

- Use ATX-style headings (`#`, `##`, `###`).
- Do not skip levels (no `#` followed directly by `###`).
- One `#` heading per file (the document title).
- Leave a blank line before and after headings.

## Text

- Use one sentence per line in the source file.
- Use blank lines to separate paragraphs.
- Do not use trailing spaces for line breaks — use blank lines instead.

## Lists

- Use `-` for unordered lists.
- Use `1.` for ordered lists (actual numbers, not all `1.`).
- Use `- [ ]` for checklists.
- Indent nested lists with 2 spaces.

## Code

- Use fenced code blocks with language identifiers:
  ````
  ```python
  def example():
      pass
  ```
  ````
- Use inline code (`backticks`) for file paths, variable names, and short code references.

## Tables

- Use pipe tables with header separators.
- Align columns for readability in source (optional, but preferred).
- Always include a header row.

```markdown
| Column A | Column B | Column C |
|---|---|---|
| Value | Value | Value |
```

## Links and References

- Use relative paths for cross-references within the repo: `[Quality Gates](ai-process/processes/quality-gates.md)`.
- Use descriptive link text — not "click here" or bare URLs.

## Diagrams

- Use ASCII art in fenced code blocks for diagrams.
- Use box-drawing characters or simple ASCII (`|`, `-`, `+`, `→`, `↓`).
- Label all components clearly.

## File Naming

- Lowercase with hyphens: `my-document-name.md`.
- Templates are prefixed with `TEMPLATE-`: `TEMPLATE-task.md`.
- ADRs are numbered: `001-short-title.md`.
