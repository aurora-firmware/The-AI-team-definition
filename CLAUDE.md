# The AI Team Definition

> **This is a META-PROJECT.** Its output is processes, templates, agent definitions, and workflow structures — not software. Deliverables from this repo serve as the operating framework for projects built entirely by AI agent teams.

---

## Using This Framework in a New Project

To adopt this framework for your own project:
1. **Quick setup**: Run `/bootstrap-project` in your new repo — it creates the full structure automatically.
2. **Manual setup**: Follow `docs/guides/setup-guide.md` for step-by-step instructions.
3. **Customization**: See `docs/guides/customization-guide.md` for what to adapt vs. keep as-is.

---

## Repository Map

| Folder | Purpose |
|---|---|
| `specifications/` | Technical specifications for features and systems |
| `tasks/` | Task tracking with status directories: `pending/`, `in-progress/`, `completed/`, `blocked/` |
| `bugs/` | Bug reports with status directories: `open/`, `in-progress/`, `resolved/` |
| `decisions/` | Architecture Decision Records (ADRs) |
| `templates/` | Reusable document formats: handoff notes (used when implementer hands off to reviewer) |
| `docs/architecture/` | System architecture documentation |
| `docs/guidelines/` | Coding standards, review checklists, markdown conventions |
| `docs/processes/` | Workflow definitions, quality gates, escalation procedures |
| `.claude/agents/` | Agent role definitions (planner, architect, implementer, reviewer, integrator) |
| `.claude/skills/` | Skills: procedures (brainstorm, tdd, code-review, debug, conflict-resolution, write-plan) and actions (/new-spec, /new-task, /new-bug, /new-adr, /status-report, /bootstrap-project) |

---

## How to Work Here

### Creating Documents
- **Always use the TEMPLATE file** in the target directory when creating a new document.
- All documents must be **Markdown with YAML frontmatter** (at minimum: `title`, `status`, `created`).
- Use skills for convenience: `/new-spec`, `/new-task`, `/new-bug`, `/new-adr`, `/status-report`.

### Task Lifecycle

Tasks move between directories to reflect their status.
Move the file (not copy) when status changes.
Update the `status` field in the frontmatter to match.

| Transition | Trigger | Moved by |
|-----------|---------|----------|
| `pending/ → in-progress/` | Agent starts work on the task | Implementer |
| `in-progress/ → blocked/` | Cannot proceed (missing dependency, ambiguous requirement, repeated failure) | Implementer |
| `blocked/ → in-progress/` | Blocker is resolved | Implementer |
| `in-progress/ → completed/` | Code review passed (Gate 3) AND integration tests passed (Gate 4) | Integrator |

A task is **not** completed when the implementer finishes coding — it is completed when it survives review and integration.
The integrator is the only agent that moves tasks to `completed/`.

### Bug Lifecycle

Bugs move between directories to reflect their status.
Move the file (not copy) when status changes.
Update the `status` field in the frontmatter to match.

| Transition | Trigger | Moved by |
|-----------|---------|----------|
| `open/ → in-progress/` | Agent starts working on the fix | Implementer |
| `in-progress/ → resolved/` | Fix verified (verification command passes) | Implementer |
| `in-progress/ → open/` | Fix attempt failed, needs a different approach | Implementer |

### Specification Lifecycle

Specifications track their status in the `status` frontmatter field.
Move specifications to `specifications/archive/` only when superseded and no in-flight tasks reference them.

| Transition | Trigger | Changed by |
|-----------|---------|------------|
| `draft → review` | Planner finishes the brainstorm skill output | Planner |
| `review → approved` | Human passes Gate 1 (Spec Approval) | Human |
| `review → draft` | Human rejects at Gate 1 with feedback | Planner (after revision) |
| `approved → superseded` | A new specification replaces this one | Planner (new spec must reference the old one) |
| Move to `archive/` | Spec is `superseded` AND no tasks in `pending/` or `in-progress/` reference it | Planner |

### Decision Records
Any decision that affects the project structure, workflow, or conventions **must** be recorded as an ADR in `decisions/`. Use the template and number sequentially (`001-`, `002-`, etc.).

### Self-Contained Documents
Every document must be **readable on its own** without requiring the reader to open other files. Include enough context inline. Use relative file paths for cross-references when additional detail exists elsewhere.

---

## Quality Standards

### Templates
- Practical, not bureaucratic — include only fields that provide real value.
- Every field must have a clear purpose. If you cannot explain why a field exists, remove it.

### Agent Definitions
Must specify: purpose, capabilities (tools and skills), decision authority, escalation triggers, interaction patterns (receives from / hands off to), and quality bar.

### Skill Definitions
Must include: trigger conditions, input requirements, step-by-step procedure, output format, quality criteria, and common pitfalls.

### Specifications
Must include: purpose, architecture (with diagrams where helpful), components, workflow, configuration, implementation order, and explicit exclusions (what we do not build).

---

## Conventions

### File Naming
- **Lowercase with hyphens**: `my-document-name.md` (never underscores, never spaces).
- **ADRs**: numbered sequentially — `001-short-title.md`, `002-short-title.md`.
- **Tasks**: descriptive slug — `implement-auth-flow.md`, `fix-routing-bug.md`.
- **Bugs**: descriptive slug — `crash-on-empty-input.md`.

### YAML Frontmatter
All documents include frontmatter. Minimum fields:
```yaml
---
title: Document Title
status: draft
created: YYYY-MM-DD
---
```
Additional fields depend on the document type (see each TEMPLATE file).

### Markdown Style
- Follow the conventions in `docs/guidelines/markdown-conventions.md`.
- Use ATX headings (`#`, `##`, `###`). Do not skip heading levels.
- Use fenced code blocks with language identifiers.
- One sentence per line in source (for cleaner diffs).

---

## Boundaries

### Do
- Create documents using the established templates and folder structure.
- Record architectural decisions as ADRs.
- Keep documents self-contained and up to date.

### Do Not
- Place implementation code in this repo — this repo defines processes, not software.
- Create documents outside the defined folder structure.
- Modify templates without first recording the change as an ADR.
- Delete completed tasks or resolved bugs — they serve as reference history.
