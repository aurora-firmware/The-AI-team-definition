---
title: "Customization Guide"
status: approved
created: 2026-03-10
---

# Customization Guide

This guide explains what to adapt when adopting the AI team framework for your project.

## What to Copy As-Is

These files are generic and work for any project without modification:

| Category | Files |
|---|---|
| **Agent definitions** | All files in `.claude/agents/` — roles are universal |
| **Skill definitions** | All files in `.claude/skills/` — procedures are language-agnostic |
| **Process docs** | `ai-process/processes/workflow-overview.md`, `quality-gates.md`, `escalation-procedure.md` |
| **Review checklist** | `ai-process/guidelines/review-checklist.md` |
| **Markdown conventions** | `ai-process/guidelines/markdown-conventions.md` |
| **Architecture docs** | `ai-process/architecture/system-overview.md`, `component-map.md` |
| **All templates** | `TEMPLATE-*.md` files in `.claude/skills/*/assets/` and `ai-process/templates/` |
| **Action skills** | Action skills in `.claude/skills/` (with `disable-model-invocation: true`) |

## What to Customize

### Must Customize

**`CLAUDE.md`** — Your project's identity:
- Replace the project name and purpose description.
- Add your tech stack (language, framework, test runner, build commands).
- Add project-specific conventions or constraints.
- Keep the Repository Map, How to Work Here, and Conventions sections — update paths if your source code layout differs.

**`README.md`** — Your project's README:
- Write a new README describing your actual project, not the framework.
- Reference the framework workflow in a "Development Process" section.

**`ai-process/guidelines/coding-standards.md`** — Language-specific rules:
- The existing file covers universal principles (clarity, naming, functions, error handling, testing, security).
- Add sections specific to your language and framework. Examples:
  - Python: type hints, import ordering (isort), docstring format (Google/NumPy), Black formatting.
  - TypeScript: strict mode, ESLint config, interface naming, barrel exports.
  - Go: error wrapping conventions, package naming, struct tags.
  - Rust: ownership patterns, error handling (thiserror vs. anyhow), clippy lints.

### Optional Customization

**Agent subset** — Not every project needs all 5 agents:

| Team Size | Recommended Agents |
|---|---|
| Solo (1 agent) | Developer (combines all roles) |
| Small (2-3 agents) | Planner + Developer + Reviewer |
| Standard (4 agents) | Planner + Developer + Reviewer + Integrator |
| Full (5 agents) | All agents including Architect |

To reduce the team: keep only the agent files you need. The workflow still works — agents whose roles are absent have their responsibilities absorbed by adjacent agents (e.g., without an integrator, the implementer handles merges).

**Quality gate criteria** — Adjust `ai-process/processes/quality-gates.md`:
- For prototypes or MVPs: relax coverage requirements, reduce review stages.
- For production systems: add security review stage, require performance benchmarks.
- For regulated domains: add compliance checks, audit trail requirements.

**Temperature guidance** — In agent definitions:
- The defaults (creative 0.7, structured 0.2, execution 0.3, review 0.4) work well for most cases.
- Lower temperatures for safety-critical code.
- Higher temperatures for creative or design-heavy work.

**Escalation thresholds** — In `ai-process/processes/escalation-procedure.md`:
- Default: architect consultation after failure, then human escalation.
- For faster iteration: skip architect, escalate directly to human.
- For more autonomy: allow two architect consultations before human escalation.

## Extending the Framework

### Adding New Agent Roles

Use `.claude/agents/TEMPLATE-agent.md`. Common additions:
- **DevOps agent** — manages CI/CD, deployment, infrastructure.
- **Documentation agent** — writes user-facing docs, API references.
- **Security agent** — dedicated security review, dependency auditing.

### Adding New Skills

Create a new directory under `.claude/skills/<name>/` with a `SKILL.md` file. Common additions:
- **Database migration** — schema changes with rollback procedures.
- **API design** — REST/GraphQL endpoint design following project conventions.
- **Performance profiling** — identify and fix performance bottlenecks.

### Adding New Action Skills

Create a new directory under `.claude/skills/<name>/` with a `SKILL.md` file. Add the `disable-model-invocation: true` frontmatter field if the skill should be user-invocable only (not triggered by the model). Reference existing skills as examples.

## Retrofitting Into an Existing Project

If you have an existing codebase:

1. Follow the setup guide to create the directory structure alongside your existing code.
2. Your existing source code stays where it is — the framework directories are additive.
3. Migrate existing issues/tasks by creating task files in `project/tasks/pending/` for each open item.
4. Write a specification for the current system state in `project/specs/` — this becomes the baseline.
5. Create an ADR in `project/decisions/` documenting the decision to adopt this framework.
