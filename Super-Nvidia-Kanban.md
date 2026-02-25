# NIMFlow — Unified Spec-to-Ship Orchestrator

## Technical Specification v1.0

**Purpose:** A single CLI/web tool that merges Superpowers’ spec-driven planning with Vibe Kanban’s parallel agent execution, using NVIDIA NIM endpoints as the model backend. The result: describe what you want → get a validated spec → get a task plan → N agents execute in parallel worktrees → human reviews diffs → ship.

-----

## 1. System Architecture

### 1.1 Three-Layer Design

```
┌─────────────────────────────────────────────────┐
│                  NIMFlow CLI / Web UI            │
│         (thin orchestration + config layer)      │
├──────────────┬──────────────┬───────────────────┤
│   PLANNER    │   EXECUTOR   │   MODEL ROUTER    │
│  (Superpowers│  (Vibe Kanban│  (NIM endpoint     │
│   workflow)  │   engine)    │   manager)         │
├──────────────┴──────────────┴───────────────────┤
│              Shared Task Schema (JSON)           │
├─────────────────────────────────────────────────┤
│   Git repo   │  Worktrees   │  GitHub/GitLab    │
└─────────────────────────────────────────────────┘
```

### 1.2 Core Components

|Component       |Responsibility                                    |Source                                           |
|----------------|--------------------------------------------------|-------------------------------------------------|
|**Planner**     |Brainstorm → Spec → Task Plan                     |Superpowers skills (brainstorming, writing-plans)|
|**Executor**    |Parallel worktrees, agent lifecycle, diff review  |Vibe Kanban engine (Rust binary + MCP)           |
|**Model Router**|Endpoint selection, fallback chains, rate limiting|New — NIMFlow core                               |
|**Task Schema** |Contract between Planner and Executor             |New — the glue                                   |

-----

## 2. NVIDIA NIM Model Strategy

### 2.1 Available Models (as of Feb 2026)

|Model               |NIM ID                       |Params (active)      |Context|Best For                                               |
|--------------------|-----------------------------|---------------------|-------|-------------------------------------------------------|
|**GLM-5**           |`z-ai/glm5`                  |744B (40B)           |205K   |Planning, complex reasoning, long-horizon agentic tasks|
|**Kimi K2.5**       |`moonshotai/kimi-k2.5`       |MoE (3.2% activation)|256K   |Agent Swarm, multimodal, tool calling                  |
|**MiniMax M2.1**    |`minimaxai/minimax-m2.1`     |230B (10B)           |128K   |Code execution, SWE tasks (74% SWE-bench)              |
|**MiniMax M2.5**    |`minimaxai/minimax-m2.5`     |230B                 |205K   |Latest iteration, balanced cost/quality                |
|**Kimi K2 Instruct**|`moonshotai/kimi-k2-instruct`|MoE                  |256K   |Fast code tasks, tool calling                          |

### 2.2 Model Role Assignments

```yaml
model_roles:
  planner:
    primary: "z-ai/glm5"           # Best reasoning + 205K context for specs
    fallback: "moonshotai/kimi-k2.5"
    config:
      thinking: true                 # Enable reasoning traces
      temperature: 0.7
      max_tokens: 16384

  executor:
    primary: "minimaxai/minimax-m2.1"  # Best SWE-bench, cheapest per-token
    fallback: "moonshotai/kimi-k2-instruct"
    config:
      thinking: false                # Instant mode for speed
      temperature: 0.3
      max_tokens: 8192

  reviewer:
    primary: "z-ai/glm5"            # Needs reasoning for code review
    fallback: "moonshotai/kimi-k2.5"
    config:
      thinking: true
      temperature: 0.5
      max_tokens: 4096
```

### 2.3 NIM API Configuration

```yaml
nim:
  base_url: "https://integrate.api.nvidia.com/v1"
  api_key: "${NVIDIA_API_KEY}"
  # OpenAI-compatible — all calls use /v1/chat/completions
  # Tool calling supported on all models
  # Rate limits: ~1000-2000 requests on free tier
  
  # For self-hosted (your MiniNano lab):
  local:
    enabled: false
    base_url: "http://localhost:8000/v1"
    # Deploy via: docker run --gpus all nvcr.io/nim/minimaxai/minimax-m2.1:latest
```

-----

## 3. Shared Task Schema

This is the contract between Planner and Executor. Every task the Planner produces must conform to this schema. Every task the Executor consumes must be in this format.

### 3.1 Task Manifest Schema

```jsonc
{
  "$schema": "nimflow-task-manifest-v1",
  "project": {
    "name": "string",
    "repo": "string",              // git remote URL
    "branch_prefix": "nimflow/",   // worktree branch naming
    "setup_script": "string|null", // runs before each agent starts
    "test_command": "string"       // validation command
  },
  "spec": {
    "id": "uuid",
    "title": "string",
    "description": "string",       // full approved spec from Planner
    "acceptance_criteria": ["string"],
    "constraints": ["string"],
    "approved_at": "ISO8601",
    "spec_file": "path"            // .md file in repo
  },
  "tasks": [
    {
      "id": "uuid",
      "title": "string",
      "description": "string",     // Detailed enough for "junior engineer"
      "type": "implement|test|refactor|bugfix",
      "priority": 1,               // execution order (1 = first)
      "estimated_minutes": 5,      // Superpowers targets 2-5 min tasks
      "dependencies": ["task-id"], // blocks until these complete
      "files": {
        "modify": ["path"],        // files this task touches
        "create": ["path"],
        "delete": ["path"]
      },
      "verification": {
        "command": "string",       // e.g., "npm test -- --grep 'auth'"
        "expected": "pass|output_contains|exit_0"
      },
      "tdd": {
        "test_file": "path|null",  // write test first
        "test_description": "string"
      },
      "agent_config": {
        "model_role": "executor",  // maps to model_roles config
        "model_override": null,    // optional specific model
        "system_prompt_append": "" // task-specific instructions
      },
      "status": "todo|in_progress|review|done|failed",
      "worktree": {
        "branch": "string|null",   // assigned at execution time
        "path": "string|null"
      },
      "result": {
        "diff": "string|null",
        "tests_passed": "boolean|null",
        "review_notes": "string|null",
        "attempts": 0
      }
    }
  ],
  "parallelism": {
    "max_concurrent": 4,           // how many agents run at once
    "strategy": "dependency_aware", // respects task.dependencies
    "conflict_detection": true      // warns if tasks touch same files
  }
}
```

### 3.2 Parallelism Rules

Tasks can run in parallel if:

1. No dependency relationship exists between them
1. Their `files.modify` sets don’t overlap
1. `max_concurrent` hasn’t been reached

The Executor assigns each parallel task its own git worktree (Vibe Kanban’s core isolation model).

-----

## 4. Planner Module (Superpowers Workflow)

### 4.1 Planning Pipeline

```
User input → Brainstorm → Spec Document → Human Approval → Task Plan → Manifest JSON
```

Each phase is a separate NIM API call with a Superpowers-style skill prompt.

### 4.2 Phase Details

#### Phase 1: Brainstorm

- **Trigger:** User provides rough idea via CLI or web UI
- **Model:** `planner.primary` (GLM-5) with thinking mode ON
- **Skill prompt:** Superpowers `brainstorming` skill — Socratic questioning, explores alternatives, presents design in digestible chunks
- **Output:** Design document (markdown), saved to `docs/specs/{id}.md`
- **Gate:** Human must approve before proceeding

#### Phase 2: Write Plan

- **Trigger:** Human approves spec
- **Model:** `planner.primary`
- **Skill prompt:** Superpowers `writing-plans` skill — breaks into 2-5 minute tasks, includes file paths, verification steps, TDD test descriptions
- **Input context:** Approved spec + codebase summary (file tree, key files)
- **Output:** Task manifest JSON conforming to §3.1 schema
- **Gate:** Human reviews task breakdown, can reorder/remove/add tasks

#### Phase 3: Conflict Analysis

- **Trigger:** Plan approved
- **Automated:** No LLM needed — static analysis of `files.modify` across tasks
- **Output:** Parallelism map showing which tasks can run simultaneously
- **Action:** Updates `task.dependencies` and `parallelism` in manifest

### 4.3 Codebase Context Strategy

Before planning, gather context for the Planner model:

```bash
# Generate codebase summary (fits in GLM-5's 205K context)
nimflow context \
  --repo . \
  --include "src/**,tests/**,package.json,tsconfig.json" \
  --exclude "node_modules,dist,.git" \
  --max-tokens 50000 \
  --output context.md
```

This produces a structured summary:

- File tree
- Key file contents (entry points, config, existing tests)
- README/docs
- Recent git log (last 20 commits)

-----

## 5. Executor Module (Vibe Kanban Engine)

### 5.1 Execution Pipeline

```
Manifest JSON → Worktree Creation → Agent Dispatch → Monitor → Review → Merge
```

### 5.2 Integration with Vibe Kanban

Two options (implement Option A first, Option B later):

**Option A: API bridge** — NIMFlow creates Vibe Kanban issues from the task manifest via VK’s MCP server interface, then VK handles worktree creation and agent lifecycle.

```
nimflow execute manifest.json \
  --vk-url http://localhost:3000 \
  --agent opencode              # or claude-code, codex, gemini-cli
```

**Option B: Native execution** — NIMFlow manages worktrees and agent processes directly, bypassing VK. Simpler for single-user, Docker-first deployments.

```
nimflow execute manifest.json \
  --mode native \
  --max-parallel 4
```

### 5.3 Agent Dispatch (Native Mode)

For each task ready to execute:

1. **Create worktree:** `git worktree add /tmp/nimflow/{task-id} -b nimflow/{task-id}`
1. **Run setup:** Execute `project.setup_script` in worktree
1. **Compose prompt:** Combine task description + TDD instructions + file context
1. **Call NIM API:** Use `executor.primary` model with tool calling enabled
1. **Execute code changes:** Agent uses bash/editor tools via the coding agent (OpenCode, Claude Code, etc.) OR via direct NIM API tool-calling loop
1. **Verify:** Run `task.verification.command`
1. **If fail:** Retry up to 3 times with error context appended
1. **If pass:** Move to `review` status

### 5.4 Tool Calling Loop (Direct NIM Mode)

For deployments without a local coding agent CLI, NIMFlow can run a tool-calling loop directly against NIM:

```python
# Simplified tool loop
tools = [
    {"type": "function", "function": {
        "name": "read_file", "parameters": {"path": "string"}}},
    {"type": "function", "function": {
        "name": "write_file", "parameters": {"path": "string", "content": "string"}}},
    {"type": "function", "function": {
        "name": "run_command", "parameters": {"command": "string"}}},
    {"type": "function", "function": {
        "name": "task_complete", "parameters": {"summary": "string"}}}
]

while not complete:
    response = nim_client.chat.completions.create(
        model=task.agent_config.model,
        messages=conversation,
        tools=tools,
        tool_choice="auto"
    )
    # Execute tool calls, append results, loop
```

This enables running entirely on NIM without Claude Code or other proprietary agents.

-----

## 6. Review Module

### 6.1 Two-Stage Review (from Superpowers)

**Stage 1: Spec Compliance** — automated

- Model: `reviewer.primary` (GLM-5, thinking mode)
- Input: Original task spec + generated diff
- Output: Pass/Fail + notes
- Checks: Does the diff implement what was asked? Nothing extra? Tests present?

**Stage 2: Code Quality** — automated, then human

- Model: `reviewer.primary`
- Input: Diff + project coding standards + test results
- Output: Issues by severity (critical/warning/info)
- Critical issues block merge; warnings shown to human

**Stage 3: Human Review**

- Diff viewer (VK’s built-in, or CLI `git diff`)
- Human approves, requests changes, or discards
- If approved: merge worktree branch → main

### 6.2 Review Prompt Template

```markdown
You are reviewing a code change against its specification.

## Task Specification
{task.description}

## Acceptance Criteria
{task.verification}

## Generated Diff
```diff
{diff_content}
```

## Test Results

{test_output}

Review for:

1. Does the diff fully implement the specification?
1. Are there any unintended side effects?
1. Is the code clean, tested, and follows project conventions?
1. Are there security or performance concerns?

Respond with JSON: {“verdict”: “pass|fail”, “severity”: “none|info|warning|critical”, “notes”: “string”}

```
---

## 7. CLI Interface

### 7.1 Commands

```bash
# Initialize project
nimflow init --repo . --test-cmd "npm test"

# Configure NIM models
nimflow config set nim.api_key "nvapi-xxx"
nimflow config set models.planner "z-ai/glm5"

# Full workflow
nimflow plan "Add JWT auth with refresh tokens"    # → Brainstorm → Spec → Plan
nimflow execute                                     # → Parallel agents
nimflow review                                      # → Review pending diffs
nimflow status                                      # → Dashboard of all tasks

# Granular control
nimflow plan --spec-only "Add rate limiting"        # Stop after spec
nimflow plan --from-spec docs/specs/rate-limit.md   # Plan from existing spec
nimflow execute --task task-3                        # Run single task
nimflow execute --dry-run                            # Show what would happen
nimflow models test                                  # Benchmark NIM models on sample task
```

### 7.2 Configuration File

`nimflow.yaml` in project root:

```yaml
version: 1
project:
  name: "my-app"
  repo: "."
  test_command: "npm test"
  setup_script: "npm install"
  branch_prefix: "nimflow/"

nim:
  base_url: "https://integrate.api.nvidia.com/v1"
  api_key_env: "NVIDIA_API_KEY"  # env var name
  
  # Optional: self-hosted fallback
  local:
    enabled: false
    base_url: "http://mininano.local:8000/v1"

models:
  planner:
    primary: "z-ai/glm5"
    fallback: "moonshotai/kimi-k2.5"
    thinking: true
    temperature: 0.7
  executor:
    primary: "minimaxai/minimax-m2.1"
    fallback: "moonshotai/kimi-k2-instruct"
    thinking: false
    temperature: 0.3
  reviewer:
    primary: "z-ai/glm5"
    fallback: "moonshotai/kimi-k2.5"
    thinking: true
    temperature: 0.5

execution:
  max_parallel: 4
  max_retries: 3
  mode: "native"           # or "vibe-kanban"
  vk_url: null             # set if mode=vibe-kanban
  agent: null              # "claude-code"|"opencode"|"codex"|null (direct NIM)

review:
  auto_review: true        # run AI review before human
  auto_merge: false        # never auto-merge without human
  require_tests: true
```

-----

## 8. Docker Compose Deployment

Single service alongside existing lab stack:

```yaml
# docker-compose.nimflow.yaml
version: "3.8"

services:
  nimflow:
    build: ./nimflow
    container_name: nimflow
    volumes:
      - ./projects:/workspace          # mount project repos
      - /var/run/docker.sock:/var/run/docker.sock  # for spawning agent containers
      - nimflow-data:/data             # manifests, state
    environment:
      - NVIDIA_API_KEY=${NVIDIA_API_KEY}
      - NIMFLOW_CONFIG=/workspace/nimflow.yaml
    ports:
      - "3100:3100"                    # web UI
    networks:
      - lab-network

  # Optional: Vibe Kanban alongside
  vibe-kanban:
    image: ghcr.io/bloopai/vibe-kanban:latest
    container_name: vibe-kanban
    volumes:
      - ./projects:/workspace
    ports:
      - "3000:3000"
    environment:
      - VK_ALLOWED_ORIGINS=http://localhost:3100
    networks:
      - lab-network

volumes:
  nimflow-data:

networks:
  lab-network:
    external: true
```

-----

## 9. Implementation Plan

### Phase 1: Core (Week 1-2)

- [ ] Task Schema definition + JSON Schema validator
- [ ] Model Router with NIM API client (OpenAI SDK compatible)
- [ ] CLI skeleton (`nimflow init`, `nimflow config`)
- [ ] Planner module: brainstorm + write-plan phases
- [ ] Context gatherer (file tree + key files → markdown)

### Phase 2: Execution (Week 3-4)

- [ ] Native executor: worktree management + agent dispatch
- [ ] Direct NIM tool-calling loop (read/write/run tools)
- [ ] Task state machine (todo → in_progress → review → done/failed)
- [ ] Parallel scheduler (dependency-aware)
- [ ] Retry logic with error context

### Phase 3: Review + Polish (Week 5-6)

- [ ] AI reviewer (two-stage)
- [ ] CLI diff viewer + approval flow
- [ ] Vibe Kanban bridge (Option A — MCP client)
- [ ] Web UI (lightweight — task board + diff viewer)
- [ ] Docker Compose packaging

### Phase 4: Advanced (Week 7+)

- [ ] `nimflow models test` — automated benchmark on sample tasks
- [ ] Local NIM deployment support (self-hosted on MiniNano)
- [ ] MCP server mode (expose NIMFlow as MCP tool for other agents)
- [ ] Kimi K2.5 Agent Swarm mode (model-native parallel decomposition)
- [ ] GitHub Issues/PR sync

-----

## 10. Tech Stack

|Layer     |Technology                  |Rationale                                     |
|----------|----------------------------|----------------------------------------------|
|CLI       |Python (Click/Typer) or Rust|Python for speed-to-ship; Rust if perf matters|
|NIM Client|OpenAI Python SDK           |NIM is OpenAI-compatible; zero custom code    |
|Git ops   |`gitpython` or shell        |Worktree create/delete/merge                  |
|Task state|SQLite or JSON files        |Simple, no external DB needed                 |
|Web UI    |React (optional)            |Reuse VK patterns if integrating              |
|Packaging |Docker                      |Matches existing lab infra                    |

-----

## 11. Key Design Decisions

1. **Schema-first:** The task manifest JSON is the only contract. Planner and Executor never talk directly — they communicate through the manifest. This makes it trivial to swap either side.
1. **Model-agnostic by default:** NIM endpoint is an env var swap. If GLM-5 underperforms on planning, switch to Kimi K2.5 in config. If NVIDIA’s free tier runs out, point to Anthropic/OpenAI with one line change.
1. **Direct NIM mode as first-class:** Don’t require Claude Code or any proprietary agent CLI. The tool-calling loop against NIM endpoints is the simplest path and avoids licensing complexity.
1. **Superpowers skills as prompts, not plugins:** Extract the methodology from Superpowers’ SKILL.md files into prompt templates that work with any model. Don’t depend on Claude Code’s plugin system.
1. **Vibe Kanban as optional, not required:** Native execution mode handles worktrees and parallelism directly. VK integration adds team collaboration and a nicer UI but isn’t a hard dependency.

-----

## 12. Risk & Validation Checklist

|Risk                                                                      |Mitigation                                                                          |
|--------------------------------------------------------------------------|------------------------------------------------------------------------------------|
|NIM free tier rate limits (~1000-2000 calls)                              |Track usage; fall back to local deployment; batch context efficiently               |
|GLM-5/MiniMax may not follow structured planning prompts as well as Claude|`nimflow models test` benchmarks before committing; prompt tuning budget of 2 days  |
|Kimi K2.5 Agent Swarm is model-internal, not exposed via API              |Use standard parallel dispatch instead; revisit when Kimi documents swarm API       |
|Worktree conflicts on file overlap                                        |Static conflict detection in Phase 3 of planning; warn + serialize conflicting tasks|
|NIM thinking mode token overhead                                          |Disable thinking for executor (fast tasks); enable only for planner/reviewer        |

-----

## 13. Success Criteria

1. `nimflow plan "feature X"` produces a valid task manifest in < 2 minutes
1. `nimflow execute` runs 4 parallel agents completing 2-5 min tasks each
1. AI review catches spec deviations before human review
1. Full cycle (plan → execute → review → merge) for a 10-task feature in < 30 minutes
1. Works entirely on NIM endpoints without any proprietary agent dependency
1. Deploys as single Docker Compose service on existing lab infrastructure