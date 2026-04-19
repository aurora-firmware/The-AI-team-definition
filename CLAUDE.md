# The AI Team Definition

> **This is a META-PROJECT.** Its output is processes, templates, agent definitions, and workflow structures — not software.

The **ai-process** is the authoritative description of the rules the AI team must follow.
The **skills** (`.claude/skills/`) and **agents** (`.claude/agents/`) are the *implementation* of those rules.
When they conflict, the ai-process wins.

---

## Repository Map

| Folder | Purpose |
|---|---|
| `project/specs/` | Technical specifications for features and systems |
| `project/tasks/` | Task tracking with status directories: `pending/`, `in-progress/`, `completed/`, `blocked/` |
| `project/bugs/` | Bug reports with status directories: `open/`, `in-progress/`, `resolved/` |
| `project/decisions/` | Architecture Decision Records (ADRs) |
| `ai-process/architecture/` | System architecture documentation |
| `ai-process/guidelines/` | Coding standards, review checklists, markdown conventions |
| `ai-process/processes/` | Workflow definitions, quality gates, escalation procedures |
| `guides/` | Human-facing guides for setup and customization (not part of the ai-process itself) |
| `.claude/agents/` | Agent role definitions (planner, architect, implementer, reviewer, integrator) |
| `.claude/skills/` | Skills: procedures (brainstorm, tdd, code-review, debug, conflict-resolution, write-plan) and actions (/new-spec, /new-task, /new-bug, /new-adr, /status-report, /bootstrap-project) |

---

## The Spec–Implementation Relationship

```
ai-process/          ← specification layer (the rules)
  processes/         defines workflows, gates, transitions
  guidelines/        defines coding, git, and markdown standards
  architecture/      describes the AI team's structure

.claude/             ← implementation layer (the executors)
  agents/            each agent implements a role defined in ai-process
  skills/            each skill implements a procedure defined in ai-process
```

**Reviewing this project** means checking that every agent and skill faithfully implements what the ai-process specifies.
**Changing this project** means either updating the ai-process first (the spec), then updating the agents/skills that implement the changed rules — or updating both atomically.
Never update an agent or skill in a way that contradicts the ai-process without also updating the ai-process.

---

## How to Work Here

### Creating Documents
- **Use the corresponding skill** to create new documents: `/new-spec`, `/new-task`, `/new-bug`, `/new-adr`.
- Templates live in `.claude/skills/<skill-name>/assets/` — skills apply them automatically.
- All documents must be **Markdown with YAML frontmatter** (at minimum: `title`, `status`, `created`).

### Task Lifecycle

Tasks move between directories to reflect their status.
Move the file (not copy) when status changes.
Update the `status` field in the frontmatter to match.

| Transition | Moved by | Receives (precondition) | Delivers (postcondition) |
|-----------|----------|------------------------|--------------------------|
| `pending/ → in-progress/` | Implementer | Task file with all dependencies in `completed/` | Task file moved, branch created as `task/<slug>` |
| `in-progress/ → blocked/` | Implementer | Blocker identified (missing dep, ambiguous req, 3 failed attempts) | Task file moved, blocker described in Work Log |
| `blocked/ → in-progress/` | Implementer | Blocker resolved (architect guidance or human input received) | Task file moved, resolution noted in Work Log |
| `in-progress/ → completed/` | Integrator (via `integrate` skill) | Gate 2 passed (code review) AND Gate 3 passed (integration tests) | Task file moved, branch merged to `dev` |

A task is **not** completed when the implementer finishes coding — it is completed when it survives review and integration.
The `integrate` skill is the only component that moves tasks to `completed/`.

### Bug Lifecycle

Bugs move between directories to reflect their status.
Move the file (not copy) when status changes.
Update the `status` field in the frontmatter to match.

| Transition | Moved by | Receives (precondition) | Delivers (postcondition) |
|-----------|----------|------------------------|--------------------------|
| `open/ → in-progress/` | Implementer | Bug file with reproduction steps verified | Bug file moved, fix branch created |
| `in-progress/ → resolved/` | Implementer | Fix verification command passes | Bug file moved, fix committed |
| `in-progress/ → open/` | Implementer | Fix attempt failed | Bug file moved, failed approach noted in bug file |

### Specification Lifecycle

Specifications track their status in the `status` frontmatter field.
Move specifications to `project/specs/archive/` only when superseded and no in-flight tasks reference them.

| Transition | Changed by | Receives (precondition) | Delivers (postcondition) |
|-----------|------------|------------------------|--------------------------|
| `draft → review` | Planner | Completed brainstorm output | Spec with all sections filled, status updated |
| `review → approved` | Human | Spec passes Gate 1 (Spec Approval) | Spec status updated to `approved` |
| `review → draft` | Planner | Human rejects at Gate 1 with feedback | Spec revised per feedback, status back to `draft` |
| `approved → superseded` | Planner | New spec created that replaces this one | Old spec references new one, status updated |
| Move to `archive/` | Planner | Spec is `superseded` AND no tasks in `pending/` or `in-progress/` reference it | Spec moved to `project/specs/archive/` |

### Decision Records
Any decision that affects the project structure, workflow, or conventions **must** be recorded as an ADR in `project/decisions/`.
Use the template and number sequentially (`001-`, `002-`, etc.).

### Self-Contained Documents
Every document must be **readable on its own** without requiring the reader to open other files.
Include enough context inline.
Use relative file paths for cross-references when additional detail exists elsewhere.

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
- Follow the conventions in `ai-process/guidelines/markdown-conventions.md`.
- Use ATX headings (`#`, `##`, `###`). Do not skip heading levels.
- Use fenced code blocks with language identifiers.
- One sentence per line in source (for cleaner diffs).
