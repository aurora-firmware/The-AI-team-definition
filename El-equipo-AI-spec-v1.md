# El-equipo-AI — Technical Specification v1.0

## Purpose

An autonomous coding system that takes a feature description, produces a validated spec and task plan, executes tasks in parallel via AI agents, reviews the output, and delivers tested, working code — with minimal human intervention.

Built as a thin glue layer on top of two battle-tested open-source tools, not as a monolithic framework. The less code we own, the less we maintain.

-----

## 1. Architecture

### 1.1 Design Principle

**Delegate everything that already exists. Only build what doesn't.**

```
┌─────────────────────────────────────────────────────────┐
│                    CONTAINER (sandbox)                    │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │            El-equipo-AI Glue Code                │    │
│  │         (~900 lines Python, 6 components)        │    │
│  ├──────────────┬──────────────┬────────────────────┤    │
│  │  Provider    │  Integration │  Task Manifest     │    │
│  │  Router      │  Test Phase  │  Bridge            │    │
│  │              │              │                    │    │
│  │  Stall       │  Notifier    │  Logger            │    │
│  │  Detector    │  (webhooks)  │  (JSONL)           │    │
│  └──────┬───────┴──────┬───────┴────────┬───────────┘    │
│         │              │                │                │
│  ┌──────▼──────┐ ┌─────▼──────┐ ┌──────▼──────────┐    │
│  │ Superpowers  │ │Vibe Kanban │ │  Host Agents    │    │
│  │ (methodology)│ │(execution) │ │ (Claude Code,   │    │
│  │              │ │            │ │  OpenCode,       │    │
│  │ brainstorm   │ │ worktrees  │ │  Codex, etc.)   │    │
│  │ plan writing │ │ task board │ │                  │    │
│  │ TDD          │ │ agent life │ │  Native tools:   │    │
│  │ code review  │ │ diff review│ │  Glob, Grep,     │    │
│  │ debugging    │ │ MCP server │ │  Edit, Read...   │    │
│  └──────────────┘ └────────────┘ └──────────────────┘    │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │         ANY Model Provider (OpenAI-compatible)    │    │
│  │   NVIDIA NIM │ OpenAI │ Anthropic │ Ollama │ ... │    │
│  └──────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Responsibility Separation

| Layer | Responsibility | Maintained by |
|---|---|---|
| **Superpowers** | Methodology — HOW agents think and work (brainstorm, TDD, review discipline, debugging, skill framework) | obra + community (28k stars) |
| **Vibe Kanban** | Execution infra — WHERE agents work (parallel worktrees, task board, agent lifecycle, diff review, MCP server) | BloopAI (YC-backed) |
| **Host Agents** | Tool execution — WHAT tools agents use (Glob, Grep, Edit, Read — native to each agent platform) | Agent platforms (Anthropic, OpenAI, etc.) |
| **Provider Router** | Brain selection — WHICH model fulfills each role (priority lists, fallback, quota handling) | Us (~900 lines) |
| **Model Providers** | Intelligence — the API endpoints (NVIDIA NIM, OpenAI, Anthropic, Ollama) | Provider companies |

### 1.3 Custom Components (what we build)

| # | Component | Est. size | Purpose |
|---|---|---|---|
| 1 | **Provider Router** | ~200 lines | Multi-provider model routing via OpenAI SDK with swappable `base_url`. Role-based model assignment with ordered fallback chains. |
| 2 | **Fallback + Quota Management** | ~300 lines | Reactive provider swap on rate limit / quota exhaustion. Cooldown timers. Graceful mid-task handoff. Stall detection. |
| 3 | **Task Manifest Bridge** | ~200 lines | Translates Superpowers' plan output into Vibe Kanban tasks via VK's MCP interface. |
| 4 | **Integration Test Phase** | ~150 lines | Post-approval merge orchestration: integration branch, dependency-order merge, test, bisect on failure. |
| 5 | **Config + Notifier** | ~80 lines | YAML config loader. Webhook notifications for human-in-the-loop events. |
| 6 | **Container Definition** | Dockerfile + compose | Single deployment unit. Contains everything. IS the sandbox. |

-----

## 2. End-to-End Workflow

```
Human describes feature
    ↓
[Superpowers brainstorm] ← planner_creative role (temp 0.7)
    Explores ideas, asks questions, produces design doc
    ↓
Human approves spec ← GATE
    ↓
[Superpowers write-plan] ← planner_structured role (temp 0.2)
    Produces task breakdown with file paths, deps, verification
    ↓
Human reviews task plan ← GATE
    ↓
[Task Manifest Bridge]
    Translates plan → VK tasks via MCP
    ↓
[Vibe Kanban executes]
    Parallel worktrees, agent dispatch
    Each agent uses Superpowers methodology (TDD, debugging)
    Provider Router assigns brains per role
    Stall detector monitors for loops
    ↓
[Superpowers code review]
    Two-stage: spec compliance + code quality
    ↓
[Integration Test Phase] ← our glue code
    Merge all approved branches (dependency order)
    Run full test suite once (optimistic)
    If fail: bisect to find breaking merge
    If conflict: create fix task in VK via MCP
    ↓
Human final approval ← GATE
    ↓
Merge to main. Ship.
```

**Human gates:** Spec approval, task plan review, final merge approval. Everything between gates is autonomous.

-----

## 3. Provider Router

### 3.1 Design

Provider-agnostic. All model providers are accessed via OpenAI-compatible API (`/v1/chat/completions`). Swapping providers is a config change, not a code change.

```python
from openai import OpenAI

# All providers use the same SDK — just different base_url
client = OpenAI(
    base_url=provider.base_url,  # nvidia, openai, anthropic, ollama...
    api_key=provider.api_key
)
response = client.chat.completions.create(
    model=role.current_model,
    messages=conversation,
    temperature=role.temperature
)
```

### 3.2 Role-Based Model Assignment

Each role has an ordered priority list of provider+model pairs. Provider Router picks the highest-priority available provider for each task.

Roles: `planner_creative`, `planner_structured`, `executor`, `tester`, `reviewer` (expandable).

Cross-model diversity is a natural consequence — assign different models to different roles in config. No special logic needed.

### 3.3 Quota Handling

**Reactive, not proactive.** The API tells us when we're out — we don't predict or count.

| Signal | Response |
|---|---|
| Rate limit (429, short cooldown) | Wait and retry. Don't swap providers for a 60-second pause. |
| Quota exhausted (credits gone) | Swap to next provider in priority list. Set back-to-action timer. |
| All providers exhausted for a role | Notify human (action-required). Wait until first provider recovers. |

**Provider swap rules:**
- Never swap mid-task for a "better" provider. Finish what you started.
- When preferred provider recovers, it becomes active for the NEXT task.
- Graceful handoff when provider warns (e.g., Anthropic): agent summarizes progress, new agent continues from worktree state.
- Abrupt handoff when provider gives no warning: new agent reads worktree state and infers progress. QA layer catches inconsistencies.

**NOTE FOR CODING AGENT:** Before implementing, research online each provider's specific behavior: quota warning signals, rate limit headers (`Retry-After`, `X-RateLimit-Reset`), error response formats. Each provider is different.

### 3.4 Temperature Defaults

```yaml
roles:
  planner_creative:    { temperature: 0.7 }  # brainstorming — explore
  planner_structured:  { temperature: 0.2 }  # JSON manifest — be precise
  executor:            { temperature: 0.3 }  # code writing — deterministic
  tester:              { temperature: 0.3 }  # test writing — deterministic
  reviewer:            { temperature: 0.4 }  # review — think critically
```

Enable JSON mode for `planner_structured` if supported by the model.

-----

## 4. Stall Detection

Agents in tool-calling loops can spin forever. The Provider Router monitors tool call patterns and intervenes.

### 4.1 Two-Layer Protection

**Layer 1 — Stall detector (primary):**

Provider Router tracks tool calls per task via sliding window. Detects:
- Same command run N+ times with identical output
- Same file read N+ times without edits in between
- Edit-test-revert cycles without meaningful variation
- Identical errors repeating

On detection: inject a wrap-up message into the next API call:

> "You have attempted the same approach multiple times without progress. Stop trying to fix this. Summarize: (1) what you tried, (2) what's failing and why, (3) your best guess at the root cause. Then call task_complete with status=failed."

Agent gets `grace_calls_after_signal` more API calls to wrap up. If ignored: force-kill.

**Layer 2 — Hard timeout (backstop):**

Absolute wall-clock limit per task. Should rarely fire. When hit: also graceful — inject wrap-up message, give `grace_timeout` to summarize and exit. Force-kill only after grace period.

### 4.2 Config

```yaml
stall_detection:
  repeat_threshold: 3
  grace_calls_after_signal: 5
  hard_timeout_minutes: 30
  grace_timeout_minutes: 2
```

### 4.3 Failure Output

Both layers produce a structured failure report: what was tried, what failed, agent's analysis. This feeds into the escalation pipeline (Section 7).

-----

## 5. Integration Test Phase

### 5.1 Purpose

Individual task tests pass in isolation. The integration phase verifies the **combined** result works.

### 5.2 Pipeline

After all tasks are reviewed and approved in VK:

1. Create integration branch from main.
2. Merge all approved worktree branches sequentially in **dependency order**.
3. Use **merge commits** (not rebase) — preserves per-agent history, easier to revert.
4. Run full `project.test_command` **once** (optimistic approach).
5. If **pass**: present to human for final approval → merge to main.
6. If **fail**: **bisect** — binary search across merges to find the breaking one (max log2(N) test runs).

### 5.3 Conflict Resolution

When branch N conflicts with already-merged branches 1..N-1:

1. Glue code detects the git conflict.
2. Creates a NEW fix task in VK via MCP, with conflict diff attached as context.
3. VK dispatches an agent to resolve the conflict in a new worktree.
4. Agent resolves, passes verification.
5. Glue code retries the integration merge from the point of failure.

### 5.4 Separation of Concerns

- **VK** handles individual task branch merges (single-task scope).
- **Our glue code** runs git merge operations for multi-branch integration.
- Clean separation: VK = single-task dispatch, El-equipo-AI = multi-task coordination.

-----

## 6. Task Manifest Bridge

### 6.1 Purpose

Translates Superpowers' plan output (task breakdown from the `writing-plans` skill) into Vibe Kanban tasks via VK's MCP server interface.

### 6.2 Flow

```
Superpowers produces plan (markdown with structured tasks)
    ↓
Bridge parses plan output
    ↓
For each task: calls VK MCP create_task with:
  - title, description, dependencies
  - role assignment (executor, tester, etc.)
  - verification command
    ↓
VK board populated, ready for execution
```

### 6.3 Risk

This is the riskiest custom component — it depends on both Superpowers' output format and VK's MCP input format. Mitigated by:
- Keeping the bridge as a thin adapter with clear input/output types.
- Pinning dependency versions.
- Testing the bridge as part of the dependency update process (Point 13).

-----

## 7. Escalation Pipeline

When a task fails after all retries:

```
Agent fails task (retries exhausted)
    ↓
Step 1: Architect consultation (automatic, one try)
    Send failure context to planner/architect model (read-only query):
    "Simple fix or scope problem?"
    ↓
    ├─ Simple fix → create new task in VK with revised instructions
    │                → dispatch agent → if fails again → Step 2
    │
    └─ Scope problem → Step 2
    ↓
Step 2: Escalate to human
    Notify via configured channels (webhooks)
    Include: original task, failure logs, architect analysis
    System waits. Other independent tasks continue.
```

**No infinite loops.** Maximum one automatic retry via architect. Second failure = human, always.

-----

## 8. Notifications

### 8.1 Two Tiers

| Tier | When | Delivery |
|---|---|---|
| **Info** | Progress updates, non-blocking events | stdout only |
| **Action-required** | System is BLOCKED waiting for human | All configured webhook channels |

### 8.2 v1 Behavior

- Info → stdout.
- Action-required → one-way webhook to all configured channels (Telegram, Discord, Slack, etc.). Message includes what happened + link to VK dashboard. Human inspects and acts via VK. System waits (only the blocked task; independent tasks continue).

### 8.3 v2 Roadmap

- Two-way interactive replies via messaging channel (/retry, /skip, /approve, /abort).
- Any-responder: first reply from any channel wins.
- "Handled" broadcast to all other channels.
- VK dashboard remains fallback for complex instructions.

-----

## 9. Logging

### 9.1 Purpose

Debug and insight for our glue code's infrastructure events. Not real-time monitoring (VK handles that).

### 9.2 Format

Append-only JSONL file. One JSON object per line.

```jsonl
{"ts": "...", "type": "provider_call", "role": "executor", "provider": "nvidia", "model": "kimi-k2.5", "status": "ok"}
{"ts": "...", "type": "provider_swap", "from": "nvidia", "to": "openai", "reason": "quota_exhausted", "reset_at": "..."}
{"ts": "...", "type": "stall_detected", "task": "task-3", "pattern": "command_loop", "action": "wrap_up_signal"}
{"ts": "...", "type": "integration_merge", "branch": "nimflow/task-3", "status": "conflict", "action": "escalated_to_vk"}
{"ts": "...", "type": "architect_consult", "task": "task-7", "verdict": "simple_fix"}
```

### 9.3 Size Management

```yaml
logging:
  file: "el-equipo-ai.log"
  max_size_mb: 10
  max_rotated_files: 3
```

Rotate on size. Max 3 rotated files. Total max disk: ~40MB.

-----

## 10. Configuration

### 10.1 Full Config Reference

```yaml
# el-equipo-ai.yaml

# --- Model Providers ---
providers:
  - name: nvidia
    base_url: "https://integrate.api.nvidia.com/v1"
    api_key_env: "NVIDIA_API_KEY"
  - name: anthropic
    base_url: "https://api.anthropic.com/v1"
    api_key_env: "ANTHROPIC_API_KEY"
  - name: openai
    base_url: "https://api.openai.com/v1"
    api_key_env: "OPENAI_API_KEY"
  - name: local
    base_url: "http://localhost:11434/v1"
    api_key_env: null

# --- Roles (each with ordered fallback chain) ---
roles:
  planner_creative:
    temperature: 0.7
    models:
      - { provider: nvidia, model: "z-ai/glm5" }
      - { provider: anthropic, model: "claude-sonnet-4.6" }

  planner_structured:
    temperature: 0.2
    json_mode: true   # if supported by model
    models:
      - { provider: nvidia, model: "z-ai/glm5" }
      - { provider: anthropic, model: "claude-sonnet-4.6" }

  executor:
    temperature: 0.3
    models:
      - { provider: anthropic, model: "claude-sonnet-4.6" }
      - { provider: nvidia, model: "minimaxai/minimax-m2.1" }

  tester:
    temperature: 0.3
    models:
      - { provider: openai, model: "gpt-4o" }
      - { provider: anthropic, model: "claude-sonnet-4.6" }

  reviewer:
    temperature: 0.4
    models:
      - { provider: openai, model: "gpt-4o" }
      - { provider: nvidia, model: "z-ai/glm5" }

# --- Stall Detection ---
stall_detection:
  repeat_threshold: 3
  grace_calls_after_signal: 5
  hard_timeout_minutes: 30
  grace_timeout_minutes: 2

# --- Notifications ---
notifications:
  action_required:
    - type: webhook
      name: "my-telegram"
      url_env: "TELEGRAM_WEBHOOK_URL"
    - type: webhook
      name: "collaborator-discord"
      url_env: "DISCORD_WEBHOOK_URL"

# --- Logging ---
logging:
  file: "el-equipo-ai.log"
  max_size_mb: 10
  max_rotated_files: 3

# --- Project ---
project:
  test_command: "npm test"     # or pytest, cargo test, etc.
  setup_script: "npm install"  # runs in each worktree before agent starts
```

-----

## 11. Tech Stack

| Layer | Technology | Rationale |
|---|---|---|
| Language | Python 3.11+ | OpenAI SDK native, MCP client libraries, fast to ship |
| API Client | `openai` Python SDK | All providers are OpenAI-compatible |
| Config | `pyyaml` | Standard YAML parsing |
| Git ops | `subprocess` (shell git) | Simple, reliable, no library needed |
| State | JSON file | One file for provider cooldowns + swap log. SQLite is overkill. |
| Packaging | Docker (Dockerfile + compose) | Single container = deployment unit = sandbox |
| Framework | None | ~900 lines doesn't need a framework |

-----

## 12. Deployment

### 12.1 Single Container

The entire system runs in one container:
- Vibe Kanban
- Superpowers (installed as plugin)
- Host agents (Claude Code, OpenCode, Codex — configured per user)
- El-equipo-AI glue code
- Git, Python, Node.js runtimes

The container IS the sandbox. Agents operate freely inside it. No agent-level isolation needed.

### 12.2 What Goes In, What Comes Out

- **In:** Feature description + human approvals at gates.
- **Out:** Tested, reviewed, working code on a branch ready to merge.

-----

## 13. Dependency Management

### 13.1 Pinned Versions

Superpowers and Vibe Kanban versions are pinned in config/lockfile. Never auto-update.

### 13.2 Update Process

All updates happen in a **dedicated branch**:

1. Create branch `updates/superpowers-vX.Y` or `updates/vibe-kanban-vX.Y`
2. Update the dependency version
3. Run full test suite (including integration tests)
4. If tests pass: merge to main
5. If tests fail: fix glue code to adapt, re-test, then merge

### 13.3 Release Notes Audit

The update process MUST read the dependency's release notes and check whether new features overlap with our custom code. If upstream adds something we built (e.g., provider routing, integration testing), notify the user to evaluate replacing our code with the upstream feature.

**Goal: keep custom code as small as possible over time.** If upstream provides it, delete ours.

-----

## 14. What We Don't Build (and why)

| Deliberately excluded | Reason |
|---|---|
| Custom tool-calling loop | Host agents bring their own tools (Glob, Grep, Edit). Superpowers guides usage. |
| Custom worktree management | VK handles this. |
| Custom task board / UI | VK provides kanban board + diff viewer. |
| Custom planning prompts | Superpowers provides brainstorming, plan-writing, TDD skills. |
| Agent-level sandboxing | Container is the sandbox. |
| Token budget tracking (v1) | Using fixed subscriptions / free tiers. Reactive quota handling is sufficient. |
| File-change validation (v1) | VK isolation + Superpowers review + integration merge covers this. Revisit in v2. |
| Two-way notification replies (v1) | One-way webhooks + VK dashboard. Two-way in v2. |
| Escalation ladder for notifications (v1) | Notify and wait. Escalation in v2. |

-----

## 15. v2 Roadmap

Items explicitly deferred from v1:

- [ ] Post-execution file-change validation (declared vs actual scope)
- [ ] Two-way interactive notifications (reply /retry, /skip from messaging app)
- [ ] Multi-channel any-responder + "handled" broadcast
- [ ] Notification escalation ladder (Telegram → SMS → phone call)
- [ ] Role personality naming (Graeber's "Bullshit Jobs" categories as role labels)
- [ ] Token budget enforcement per task (if moving to pay-per-token providers)

-----

## 16. Implementation Order

### Phase 1: Foundation
- [ ] Config file schema + loader (`el-equipo-ai.yaml`)
- [ ] Provider Router: multi-provider, role-based model selection, basic API calls
- [ ] Container definition (Dockerfile + compose with VK + Superpowers + agents)

### Phase 2: Core Pipeline
- [ ] Task Manifest Bridge: Superpowers plan → VK tasks via MCP
- [ ] Provider quota handling: reactive swap, cooldown timers, graceful handoff
- [ ] Stall detector: pattern tracking, wrap-up signal injection

### Phase 3: Integration + Quality
- [ ] Integration test phase: merge orchestration, test, bisect
- [ ] Conflict resolution: detect conflicts, create fix tasks in VK via MCP
- [ ] Escalation pipeline: architect consultation, human notification

### Phase 4: Polish
- [ ] Webhook notifier (action-required events)
- [ ] JSONL logger with rotation
- [ ] Dependency update process documentation + test script
- [ ] End-to-end test: full workflow from feature description to merged code
