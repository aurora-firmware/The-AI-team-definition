---
name: bootstrap-project
description: Set up the AI team framework directory structure and files in the current project
disable-model-invocation: true
allowed-tools: Read, Glob, Write, Bash(mkdir *), Bash(touch *), Bash(cp *)
---

Bootstrap the AI team framework in the current project.

This skill sets up the full directory structure and copies framework templates into the current repository.

1. Create the directory structure:
   ```
   specifications/archive
   tasks/pending tasks/in-progress tasks/completed tasks/blocked
   bugs/open bugs/resolved
   decisions
   templates
   docs/architecture docs/guidelines docs/processes docs/guides
   .claude/agents
   .claude/skills
   ```

2. Add `.gitkeep` files to empty status directories:
   - `specifications/archive/`
   - `tasks/pending/`, `tasks/in-progress/`, `tasks/completed/`, `tasks/blocked/`
   - `bugs/open/`, `bugs/resolved/`

3. Check if template files already exist before copying. For each file that does NOT already exist, create it from the framework's template content. The required template files are:
   - `specifications/TEMPLATE-specification.md`
   - `tasks/TEMPLATE-task.md`
   - `bugs/TEMPLATE-bug.md`
   - `decisions/TEMPLATE-adr.md`
   - `templates/roadmap.md`
   - `templates/test-plan.md`
   - `templates/test-report.md`
   - `templates/handoff-note.md`
   - `templates/progress-report.md`

4. Copy all agent definitions to `.claude/agents/` if they do not already exist:
   - planner.md, architect.md, implementer.md, reviewer.md, tester.md, integrator.md

5. Copy all skill definitions to `.claude/skills/<name>/SKILL.md` if they do not already exist:
   - brainstorm, write-plan, code-review, tdd, debug, conflict-resolution
   - new-spec, new-task, new-bug, new-adr, status-report

6. Copy all process and guideline docs to `docs/` if they do not already exist:
   - `docs/processes/workflow-overview.md`
   - `docs/processes/quality-gates.md`
   - `docs/processes/escalation-procedure.md`
   - `docs/guidelines/coding-standards.md`
   - `docs/guidelines/review-checklist.md`
   - `docs/guidelines/markdown-conventions.md`
   - `docs/architecture/system-overview.md`
   - `docs/architecture/component-map.md`

7. If `CLAUDE.md` does not exist, ask the user for the project name, a one-sentence purpose, and the tech stack (language, framework, test command, build command). Then generate a starter CLAUDE.md following the template in `docs/guides/setup-guide.md` Step 3.

8. If `CLAUDE.md` already exists, do not overwrite it. Inform the user that they should review `docs/guides/customization-guide.md` to adapt the framework to their project.

9. Print a summary of what was created and what already existed (skipped). Remind the user to:
    - Customize `CLAUDE.md` if it was just generated
    - Adapt `docs/guidelines/coding-standards.md` for their language
    - Run `/status-report` to verify the setup
