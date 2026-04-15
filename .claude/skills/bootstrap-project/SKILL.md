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
   project/specs/archive
   project/tasks/pending project/tasks/in-progress project/tasks/completed project/tasks/blocked
   project/bugs/open project/bugs/in-progress project/bugs/resolved
   project/decisions
   project/docs/reports
   ai-process/templates
   ai-process/architecture ai-process/guidelines ai-process/processes
   .claude/agents
   .claude/skills
   ```

2. Add `.gitkeep` files to empty status directories:
   - `project/specs/archive/`
   - `project/tasks/pending/`, `project/tasks/in-progress/`, `project/tasks/completed/`, `project/tasks/blocked/`
   - `project/bugs/open/`, `project/bugs/in-progress/`, `project/bugs/resolved/`

3. Check if template files already exist before copying. For each file that does NOT already exist, create it from the framework's skill assets. The template sources are:
   - `.claude/skills/new-spec/assets/TEMPLATE-specification.md`
   - `.claude/skills/new-task/assets/TEMPLATE-task.md`
   - `.claude/skills/new-bug/assets/TEMPLATE-bug.md`
   - `.claude/skills/new-adr/assets/TEMPLATE-adr.md`
   - `.claude/skills/write-plan/assets/roadmap.md`
   - `.claude/skills/tdd/assets/test-plan.md`
   - `.claude/skills/tdd/assets/test-report.md`
   - `ai-process/templates/handoff-note.md`
   - `.claude/skills/status-report/assets/progress-report.md`

4. Copy all agent definitions to `.claude/agents/` if they do not already exist:
   - planner.md, architect.md, implementer.md, reviewer.md, integrator.md

5. Copy all skill definitions to `.claude/skills/<name>/SKILL.md` if they do not already exist:
   - brainstorm, write-plan, code-review, tdd, debug, conflict-resolution
   - dev-loop, integrate, bug-loop
   - new-spec, new-task, new-bug, new-adr, status-report
   - **Note:** `bootstrap-project` is intentionally excluded. This skill belongs to the meta-framework, not to bootstrapped projects. A bootstrapped project's purpose is to build software, not to bootstrap other projects.

6. Copy all process and guideline docs to `ai-process/` if they do not already exist:
   - `ai-process/processes/workflow-overview.md`
   - `ai-process/processes/quality-gates.md`
   - `ai-process/processes/escalation-procedure.md`
   - `ai-process/guidelines/coding-standards.md`
   - `ai-process/guidelines/review-checklist.md`
   - `ai-process/guidelines/markdown-conventions.md`
   - `ai-process/guidelines/git-conventions.md`
   - `ai-process/architecture/system-overview.md`
   - `ai-process/architecture/component-map.md`

7. If `CLAUDE.md` does not exist, ask the user for the project name, a one-sentence purpose, and the tech stack (language, framework, test command, build command). Then generate a starter CLAUDE.md following the template in `guides/setup-guide.md` Step 3.

8. If `CLAUDE.md` already exists, do not overwrite it. Inform the user that they should review `guides/customization-guide.md` to adapt the framework to their project.

9. Print a summary of what was created and what already existed (skipped). Remind the user to:
    - Customize `CLAUDE.md` if it was just generated
    - Adapt `ai-process/guidelines/coding-standards.md` for their language
    - Run `/status-report` to verify the setup
