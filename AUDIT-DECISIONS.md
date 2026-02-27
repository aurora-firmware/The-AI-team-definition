# El-equipo-AI — Audit & Decision Log

Each point is debated and resolved before implementation.
Status: PENDING | DECIDED | DEFERRED

---

## Point 0: Project Identity & Architecture (FOUNDATIONAL)
**Problem:** The original spec ("NIMFlow") described building a monolithic system from scratch — planning engine, executor, worktree manager, review UI, model client. This means writing and maintaining thousands of lines of code that duplicates functionality already provided by actively maintained open-source tools (Superpowers, Vibe Kanban). In a field changing weekly, owning that code = permanent maintenance debt.
**Status:** DECIDED
**Decision:**
- **Project name:** "El-equipo-AI" (provisional, until we find something better).
- **Architecture:** Thin glue layer on top of two existing tools, NOT a monolithic framework.
  - **Superpowers** (installed as-is, not forked): provides methodology — brainstorming, plan writing, TDD discipline, code review, skill framework. Maintained by obra + 28k-star community.
  - **Vibe Kanban** (installed as-is, not forked): provides execution infra — parallel worktrees, task board, agent lifecycle, diff review UI, MCP server interface. Maintained by BloopAI (YC-backed).
  - **El-equipo-AI custom code** (~900 lines estimated): ONLY the parts that don't exist anywhere:
    1. **Provider Router** (~200 lines): Multi-provider config (NVIDIA NIM, OpenAI, Anthropic, Ollama) via OpenAI SDK with swappable `base_url`.
    2. **Fallback + quota management** (~300 lines): Auto-switch provider on rate limit / credit exhaustion. Multi-API-key rotation. Usage tracking per key.
    3. **Task manifest bridge** (~200 lines): Translates Superpowers' plan output into Vibe Kanban tasks via VK's MCP interface. The glue between planning and execution.
    4. **Integration test phase** (~150 lines): Merge approved branches in dependency order, run full test suite, bisect on failure (per Point 2).
    5. **Config file** (~50 lines): `el-equipo-ai.yaml` — providers, API keys, fallback chains, model assignments per role.
    6. **Container definition** (Dockerfile + compose): The single deployment unit. Contains VK + Superpowers + host agents + our glue code. This IS the sandbox — no agent-level isolation needed because nothing exists outside the container from the agents' perspective.
- **NVIDIA's role:** Just one of several API providers. Not special. Same as OpenAI/Anthropic/Ollama — an `api_key` + `base_url`. Free tier: ~5000 credits, 40 req/min. Provider-agnostic design means swapping is a config change.
- **Dependency updates strategy:** Updates to Superpowers or Vibe Kanban are handled in a DEDICATED BRANCH. Update the dependency, run the full test suite, validate nothing breaks, then merge back to main. Never update dependencies on the working branch directly.
**Rationale:**
- The less code you own, the less you maintain. Volatile parts (prompt methodology, agent orchestration, platform compatibility) are maintained by their communities. Stable parts (provider routing, config) are what we own.
- When a new model drops: one config line change. When Superpowers adds a skill: free update. When VK supports a new agent: free update. When an AI platform changes pricing: swap `base_url`.
- The task manifest bridge is the riskiest custom piece (depends on both tools' formats). Mitigated by keeping it as a thin adapter with clear types, and pinning dependency versions until updates are tested.

---

## Point 1: Executor Tool Set
**Original problem:** The spec defined a minimal 4-tool set (read_file, write_file, run_command, task_complete) for a custom tool-calling loop. write_file overwrites entire files = merge conflicts + code destruction.
**REFRAMED after Point 0:** El-equipo-AI does NOT implement its own tool-calling loop. Execution is delegated to Vibe Kanban, which dispatches host agents (OpenCode, Codex, etc.). Each host agent brings its own native tools (Glob, Grep, Read, Edit, etc.). Superpowers' methodology guides how agents use those tools effectively.
**Status:** DECIDED — RESOLVED BY POINT 0
**Decision:** No custom tool set needed. Host agents provide their own tools. Superpowers provides the discipline. Section 5.4 of the original spec (Direct NIM tool-calling loop) is dropped entirely.
**Rationale:** Don't rebuild what the agent platforms already provide. OpenCode has Edit (surgical), Glob, Grep, and equivalents across providers. Superpowers' "Search, Don't Index" philosophy applies — use native tools, don't layer custom ones on top.

---

## Point 2: Post-Merge Integration Test Phase
**Original problem:** Individual task tests pass in isolation but combined result is untested.
**REFRAMED after Point 0:** This is one of the ~5 custom components El-equipo-AI actually builds. Vibe Kanban manages individual worktrees but does NOT orchestrate a combined integration test after all tasks merge.
**Status:** DECIDED
**Decision:** Custom code (~150 lines). After all tasks are reviewed/approved in VK: create integration branch from main, merge all approved worktree branches sequentially in DEPENDENCY ORDER, run full test suite ONCE (optimistic). If pass: present to human for final approval → merge to main. If fail: BISECT (binary search, max log2(N) runs to find the breaking merge).
**Rationale:** Optimistic-then-bisect balances speed (1 test run on happy path) with debuggability (targeted reruns on failure). Individual task verification + rigorous planning should make integration pass first try in most cases.

---

## Point 3: Merge Strategy for Parallel Worktrees
**Original problem:** No defined merge order, conflict resolution, or integration branch.
**REFRAMED after Point 0:** Vibe Kanban handles individual worktree merges (`git merge --squash` per task, built-in conflict UI). But VK does NOT orchestrate multi-branch sequential integration. Our glue code runs the integration: sequential merge into integration branch, in dependency order.
**Status:** DECIDED
**Decision:**
- **Merge type:** Merge commits (not rebase). Preserves per-agent history as a unit, easier to revert individual task contributions.
- **Merge order:** Dependency order (same as Point 2).
- **Conflict resolution:** When branch N conflicts with already-merged branches 1..N-1 during integration:
  1. Our glue code detects the conflict.
  2. Creates a NEW fix task in VK via MCP, with the conflict diff attached as context.
  3. VK dispatches an appropriate agent to resolve the conflict in a new worktree.
  4. Agent resolves, passes verification.
  5. Our glue code retries the integration merge from the point of failure.
- **Who runs git:** Our glue code runs the git merge operations for the integration phase. VK handles individual task branch merges. Clean separation: VK = single-task dispatch, El-equipo-AI = multi-task coordination.
**Rationale:** Merge commits preserve traceability. Escalating conflicts back to VK as new tasks leverages the existing agent dispatch pipeline instead of building custom conflict resolution. The MCP interface makes this programmatic — create_task with conflict context, let VK handle the rest.

---

## Point 4: Task Timeout + Agent Token Budget
**Original problem:** No timeout enforcement. Agents can spin forever.
**REFRAMED after Point 0:** Vibe Kanban has agent monitoring (dashboard, manual stop) but no automatic stall detection or timeout-kill. Our Provider Router sees all API calls and can detect stuck agents.
**Status:** DECIDED
**Decision:** Two-layer protection, both graceful:
- **Layer 1 — Stall detector (primary).** Provider Router tracks tool call patterns per task via sliding window. Detects: same command run 3+ times with same output, same file read 3+ times without edits, edit-test-revert cycles, identical errors. On detection: inject a wrap-up message into the next API call instructing the agent to stop trying, summarize what it attempted, explain what's failing, and call task_complete(failed). Agent gets `grace_calls_after_signal` (default 5) more API calls to wrap up. If it ignores the signal and keeps looping, force-kill.
- **Layer 2 — Hard timeout (backstop).** Absolute wall-clock limit per task (default 30 min). Should rarely fire — stall detector catches problems earlier. When hit, ALSO graceful: inject wrap-up message, give agent `grace_timeout` (default 2 min) to summarize and exit. Force-kill only after grace period expires.
- **No token budget enforcement** for v1. Current plan uses fixed subscriptions / free tiers / local agents — token cost is not a per-task concern.
- **Failure output:** Both layers produce a structured failure report (what was tried, what failed, agent's analysis). This feeds directly into Point 11 (feedback loop for re-planning).
- **Config:**
  ```yaml
  stall_detection:
    repeat_threshold: 3        # same action N times = stall
    grace_calls_after_signal: 5 # calls to wrap up after soft signal
    hard_timeout_minutes: 30    # absolute backstop
    grace_timeout_minutes: 2    # time to wrap up after hard timeout
  ```
**Rationale:** Stall detection is smarter than crude timeouts — catches the actual problem (looping) not a proxy (time elapsed). Graceful exit preserves the agent's partial work and produces rich failure context for re-planning, instead of a bare "timeout" with no information. Hard timeout is the safety net for edge cases the stall detector misses. Quality over speed — generous limits, intelligent detection.

---

## Point 5: Post-Execution File-Change Validation
**Original problem:** Planner declares files.modify but LLM declarations are unreliable. Agents may touch undeclared files.
**REFRAMED after Point 0:** Three existing layers already cover this risk: (1) VK worktree isolation prevents agents from stepping on each other during execution, (2) Superpowers' review skill checks for scope creep, (3) our integration merge phase (Point 3) catches file conflicts between branches.
**Status:** DECIDED — DEFERRED TO v2
**Decision:** Skip for v1. Do not build declared-vs-actual file diff validation. The problem is already covered by VK isolation + Superpowers review + integration merge conflict detection. If agents regularly go out of scope in practice, revisit and add as a lightweight check later.
**Rationale:** Three safety nets already exist. Adding a fourth is extra custom code to maintain for a problem that may not materialize. Quality v1 = minimal custom code, maximum leverage from existing tools.

---

## Point 6: Crash Recovery / Idempotent Execution + Provider Swap Handling
**Original problem:** Undefined behavior on crash. Worktrees in /tmp lost on reboot.
**REFRAMED after Point 0:** VK persists task state, worktrees are in `.git/worktrees`, Superpowers' state is in repo files. Our glue code is ~900 lines of mostly stateless orchestration. The real question expanded to include mid-task provider swaps.
**Status:** DECIDED
**Decision:**
- **Crash recovery:** Minimal. VK handles operational persistence (board, tasks, worktrees). Git handles code state. Integration phase can inspect the integration branch to determine merge progress on restart. No custom checkpoint system needed.
- **Provider Router state:** Small JSON file on disk. Records: provider cooldown timers (which providers are exhausted and when they reset), and a log of provider swap events (for the task master to review). In-memory state rebuilt from this file on restart.
- **Mid-task provider swap — graceful path (providers that warn, e.g., Anthropic):**
  1. Provider Router detects "approaching limit" warning.
  2. Injects wrap-up message: agent summarizes progress + remaining work.
  3. Swap to next priority provider.
  4. New agent receives: task description + handoff summary + worktree state on disk.
  5. Continues from where previous agent left off.
- **Mid-task provider swap — abrupt path (providers with no warning):**
  1. API call fails with quota error.
  2. No graceful summary possible.
  3. Swap to next priority provider.
  4. New agent receives: task description + conversation history + reads worktree state.
  5. Picks up by inferring progress from worktree.
  6. QA layer (Superpowers review + integration tests) catches any inconsistencies.
- **Task restart vs continue:** Continue mid-task by default (work is on disk in worktree). Restarting from scratch is overkill for a rare edge case. QA handles any rough edges from the handoff.
- **Back-to-action timers:** When preferred provider recovers, it becomes active for the NEXT task, not the current one. Never swap mid-task for a "better" provider — finish what you started.
- **NOTE FOR CODING AGENT:** Before implementing the Provider Router, research online the latest behavior of each supported provider (NVIDIA NIM, OpenAI, Anthropic, Ollama) regarding: quota warning signals, rate limit headers, error response formats, reset time indicators. Each provider may handle this differently — the Router must adapt per provider.
**Rationale:** Reactive, not proactive. The API tells us when we're out — we don't predict. Graceful handoff when possible (providers that warn), pragmatic fallback when not (abrupt cutoff + QA catches issues). Minimal persistence — one JSON file for cooldown timers and swap log. VK + git handle everything else.

---

## Point 7: Lower Temperature for Plan-Writing
**Original problem:** Temperature 0.7 for both brainstorming and JSON manifest generation.
**REFRAMED after Point 0:** Superpowers handles planning prompts, our Provider Router sets model config per role. Modern models are robust across temperature ranges — the impact is marginal in the middle (0.3-0.5), but matters at the extremes (brainstorming too low = flat, structured output too high = occasionally breaks).
**Status:** DECIDED
**Decision:** Configure temperature per role in `el-equipo-ai.yaml`. Not critical to obsess over, but worth setting sensible defaults:
```yaml
roles:
  planner_creative:    { temperature: 0.7 }  # brainstorming — explore ideas
  planner_structured:  { temperature: 0.2 }  # JSON manifest — be precise
  executor:            { temperature: 0.3 }  # code writing — mostly deterministic
  reviewer:            { temperature: 0.4 }  # review — think critically about edge cases
```
If models support JSON mode (forced valid JSON output), enable it for `planner_structured`. Coding agent should check each model's JSON mode support before implementing.
These are configurable defaults, not hard rules. Users can tune per project.
**Rationale:** Brainstorming needs creativity (0.7). Structured JSON output needs precision (0.2). Code and review sit in between. Modern models handle mid-range temperatures well, but the brainstorm-vs-JSON split genuinely matters.
**NOTE FOR v2:** Consider naming roles with personality/humor — e.g., adapting Graeber's "Bullshit Jobs" categories (taskmaster, box ticker, duct taper, goon, flunky) as role labels. Might make the config more memorable and fun, or might make it confusing — evaluate once the roles are battle-tested.

---

## Point 8: Cross-Model Diversity (Writer vs Reviewer/Tester)
**Original problem:** Both planner and reviewer use GLM-5. Same model reviewing its own patterns = no diversity.
**REFRAMED after Point 0:** Model assignment per role is purely a Provider Router config decision. Cross-model diversity is not a feature to build — it's a natural consequence of having separate roles with separate priority lists.
**Status:** DECIDED
**Decision:**
- Each role has its own ordered priority list of provider+model pairs in config.
- Roles: `planner_creative`, `planner_structured`, `executor`, `tester`, `reviewer` (expandable).
- Cross-model diversity happens naturally: user assigns Claude to `executor`, GPT to `tester` → complementary blind spots for free. User with one API key puts same model everywhere → also fine.
- No enforcement of diversity. No special logic. Just config.
- When all providers for a role are exhausted: notify user, wait until first provider recovers.
- **Responsibility separation:**
  - Superpowers says WHAT to do (methodology: TDD, brainstorm, review discipline)
  - VK dispatches tasks to agents (orchestration)
  - Provider Router decides WHICH BRAIN each agent uses (role → priority list → availability)
- Example config:
  ```yaml
  roles:
    planner_creative:
      - { provider: nvidia, model: "z-ai/glm5" }
      - { provider: anthropic, model: "claude-sonnet-4.6" }
    executor:
      - { provider: anthropic, model: "claude-sonnet-4.6" }
      - { provider: nvidia, model: "minimaxai/minimax-m2.1" }
    tester:
      - { provider: openai, model: "gpt-4o" }
      - { provider: anthropic, model: "claude-sonnet-4.6" }
    reviewer:
      - { provider: openai, model: "gpt-4o" }
      - { provider: nvidia, model: "z-ai/glm5" }
  ```
**Rationale:** The simplest design that achieves cross-model diversity without special logic. Roles are config, providers are config, fallback chains are config. The Provider Router just follows the priority list. Everything else is a user choice, not a system constraint.

---

## Point 9: Sandbox run_command
**Original problem:** LLM-driven shell with no restrictions = arbitrary code execution.
**REFRAMED after Point 0:** The entire El-equipo-AI system runs inside ONE container. That container IS the sandbox. Agents can do whatever they want inside it — if they trash the filesystem, restart the container. There is no "outside" from the agents' perspective.
**Status:** DECIDED
**Decision:** No agent-level isolation needed. The deployment container is the security boundary. No Docker-per-agent, no command denylist, no sandboxing logic in our glue code.
- The whole stack (VK + Superpowers + host agents + our glue code) runs in a single container.
- Agents work freely inside it. VK worktrees provide task-level separation within the container.
- Container definition (Dockerfile) is part of our glue — added to Point 0 as component #6.
- No dev/prod split for El-equipo-AI itself. It runs in its container, receives a task, delivers code.
**Rationale:** Container = sandbox. Everything inside is disposable and rebuildable. Agent-level isolation within the container is unnecessary complexity. The blast radius of any agent action is bounded by the container walls.

---

## Point 10: Tech Stack for Custom Code
**Original problem:** "Python or Rust" and "SQLite or JSON" left undecided.
**REFRAMED after Point 0:** ~900 lines of glue, not a framework.
**Status:** DECIDED
**Decision:**
- **Language:** Python 3.11+. OpenAI SDK is Python-native, MCP client libraries are best in Python, git operations via subprocess. For ~900 lines, performance is irrelevant — no case for Rust/Go.
- **State persistence:** Single JSON file. Stores provider cooldown timers + swap event log (per Point 6). SQLite is overkill. VK handles its own persistence, git handles code state.
- **Dependencies (minimal):** `openai` (provider API calls), `pyyaml` (config parsing). Possibly `requests` if MCP client needs it. Nothing else.
- **Framework:** None. No Flask, FastAPI, Click, Typer. Just Python modules + scripts.
- **Packaging:** Dockerfile (per Point 9).
**Rationale:** Simplest stack that works. Python is the path of least resistance for OpenAI-compatible API work. Minimal dependencies = minimal maintenance. No framework overhead for a project this small.

---

## Point 11: Executor-to-Planner Feedback Loop
**Original problem:** After 3 failed retries, task dies with no recovery path.
**REFRAMED after Point 0:** VK handles retries, Superpowers' debugging skill helps agents self-correct. Question is what happens after all retries are exhausted.
**Status:** DECIDED
**Decision:** Two-step escalation: one architect consultation, then human.
- **Step 1 — Architect consultation (automatic, one try).** After agent exhausts retries, send a READ-ONLY query to the planner/architect model with the failure context (task description, what was tried, error logs, agent's analysis from Point 4 graceful wrap-up). Ask: "Is this a simple fix (wrong approach, missing context) or a deeper scope problem (needs refactoring across tasks)?"
  - If architect says **simple fix:** create a new task in VK with the architect's revised instructions. Dispatch one agent. If THIS agent also fails → go to Step 2.
  - If architect says **scope problem:** go to Step 2 immediately.
- **Step 2 — Escalate to human.** Notify the user with full context: original task, failure logs, architect's analysis, what was attempted. Wait for human decision (re-scope, split, do manually, skip).
- **No infinite re-planning loops.** Maximum one automatic retry via architect. Second failure = human, always.
- **Human notification system (v1 + v2):**
  - v1: stdout/logs + VK dashboard (task marked failed with context visible on the board). Sufficient for active monitoring.
  - v2: Proper notification system for async operation (agents may work autonomously for hours/days while human does other things). Candidates: email, Slack webhook, push notification, SMS. **This needs its own design decision — noted as Point 14.**
**Rationale:** One architect consultation is cheap (single API call, read-only) and catches simple fixes without bothering the human. But models aren't yet strong enough to self-guide through complex failures — second failure means human judgment is needed. The notification system is critical for the autonomy vision but is a separate concern from the feedback loop logic.

---

## Point 12: Structured Logging
**Original problem:** No logging or audit trail for autonomous runs.
**REFRAMED after Point 0:** VK has its own dashboard (operational view: task status, diffs). Superpowers produces structured output (specs, plans, reviews). The gap is our glue code's infrastructure events — provider calls, swaps, integration merges, architect consultations. These are invisible without logging.
**Status:** DECIDED
**Decision:**
- **Format:** Append-only JSONL file (one JSON object per line). Easy to grep, parse, or pipe into any tool.
- **What gets logged:** Provider calls (role, provider, model, status), provider swaps (from, to, reason, reset time), stall detector events, architect consultations (Point 11), integration merge steps (branch, status, conflicts).
- **Size limiter:** Log rotation by size. When file exceeds a configurable max (default 10MB), rotate: rename current to `el-equipo-ai.log.1`, start fresh. Keep max 3 rotated files (configurable). Total max disk usage: ~40MB. Old logs are deleted automatically.
  ```yaml
  logging:
    file: "el-equipo-ai.log"
    max_size_mb: 10
    max_rotated_files: 3
  ```
- **Purpose:** Debug/insight. Not real-time monitoring (that's VK's job). Useful for: diagnosing slow tasks, tracking provider usage patterns, debugging glue code, understanding failure chains.
- **Implementation cost:** ~20 lines of code (log_event function + rotation logic). Minimal.
**Rationale:** Costs almost nothing to implement. Harmless if unused. Saves hours when debugging. Size limiter prevents unbounded growth during long autonomous runs (hours/days).

---

## Point 13: Dependency Update Handling (NEW)
**Problem:** Superpowers and Vibe Kanban are actively developed. Updates may introduce breaking changes to interfaces our glue code depends on (Superpowers' plan output format, VK's MCP task creation API). Updating on the working branch risks breaking the system mid-work.
**Status:** DECIDED (per Point 0)
**Decision:** All dependency updates happen in a DEDICATED BRANCH:
1. Create branch `updates/superpowers-vX.Y` or `updates/vibe-kanban-vX.Y`
2. Update the dependency version
3. Run full test suite (including integration tests)
4. If tests pass: merge to main
5. If tests fail: fix the glue code to adapt to new interfaces, re-test, then merge
Pin dependency versions in config/lockfile. Never auto-update.
6. **Release notes audit:** The update process MUST read the dependency's release notes / changelog and check whether new features overlap with our custom glue code. If Superpowers adds a feature that duplicates something we built (e.g., provider routing, integration testing), notify the user so we can evaluate replacing our custom code with the upstream feature. Goal: keep our custom code as small as possible over time.
**Rationale:** Treat dependency updates like any other code change — isolated, tested, reviewed before merging. This is standard practice but critical here because our glue code's interfaces depend on both tools' output formats. The release notes audit prevents our custom code from becoming redundant — if upstream adds what we built, we should delete our version and use theirs.

---

## Point 14: Human Notification System (NEW)
**Problem:** El-equipo-AI is designed for autonomous operation — agents may work for hours or days without human input. When the system needs human attention (persistent task failure, all providers exhausted, integration test failure, final approval), the human may not be watching stdout.
**Status:** DECIDED
**Decision:**
- **Two notification tiers:**
  - **Info:** Progress updates, non-blocking events ("task 3/10 done", "provider swapped"). No action needed.
  - **Action-required (human-in-the-loop):** System is BLOCKED waiting for human input ("task failed after architect consultation", "approve final merge?", "all providers exhausted").
- **v1 (simple, one-way):**
  - Info messages → stdout only.
  - Action-required messages → sent to ALL configured messaging channels (Telegram, Discord, Slack — via webhooks, can be multiple simultaneously). One-way: notification tells the human what happened + link to VK dashboard. Human goes to VK to inspect and act. System waits.
  - Meanwhile, other independent tasks that don't need human input continue running. Only the blocked task waits.
  - Config:
    ```yaml
    notifications:
      action_required:
        - type: webhook
          name: "my-telegram"
          url_env: "TELEGRAM_WEBHOOK_URL"
        - type: webhook
          name: "collaborator-discord"
          url_env: "DISCORD_WEBHOOK_URL"
    ```
- **v2 (two-way, multi-channel response):**
  - Interactive replies via messaging channel: simple commands (/retry, /skip, /approve, /abort) determined by event type (hardcoded mapping, no LLM needed).
  - Any-responder: multiple channels receive the notification, first reply from any channel wins.
  - "Handled" broadcast: once one person responds, all other channels get "resolved by [name] — action: retry".
  - Simultaneous response handling: first wins, second gets "already handled."
  - VK dashboard always remains as fallback for complex instructions that go beyond simple commands.
  - Reply options per event type:
    - Task failure: retry, skip, abort
    - Integration test failure: retry, abort, inspect
    - Spec approval: approve, reject
    - Provider exhaustion: wait (default), abort
    - Final merge: approve, reject
**Rationale:** v1 keeps it simple — webhooks are universal (Telegram, Discord, Slack all support them), one-way is trivial to implement (~30 lines), and the human acts via VK where full context is available. v2 adds convenience (reply from phone without opening VK) and team collaboration (any-responder), but the message bus pattern (notification IDs, response tracking, cross-channel broadcasts) is real complexity best deferred until v1 patterns are proven.

---

## Point 15: Host Agent — OpenCode (full migration from Claude Code)
**Problem:** The Dockerfile hardcoded `@anthropic-ai/claude-code` as the sole host agent CLI, creating a single-provider dependency at the execution layer — the layer that does ~90% of real work (editing files, running tests, navigating code). This directly contradicts the core design principle from Point 0: use whatever model/tool is available, swap via config.
**Status:** DECIDED
**Decision:**
- **Host agent:** OpenCode (https://opencode.ai). Installed in the container as the execution agent. Claude Code is removed from the default stack entirely.
- **Why OpenCode:**
  1. **75+ provider support** — OpenCode natively supports NVIDIA NIM, OpenAI, Anthropic, Ollama, and 70+ other providers via its own config. Matches our provider-agnostic philosophy.
  2. **Both key tools support it** — Superpowers works with OpenCode via hooks (auto-bootstrap on agent start). Vibe Kanban has a dedicated OpenCode integration documented at their docs site.
  3. **No single-vendor lock-in** — OpenCode starts with whatever provider you configure. A user with only an NVIDIA NIM key can run the full stack without needing an Anthropic key for the agent itself.
  4. **Go binary** — Single binary install, no npm dependency chain for the agent itself. Node.js is still needed for Vibe Kanban but is no longer required for the host agent.
- **Superpowers integration:** Superpowers is cloned and integrated via OpenCode hooks (the `hooks` field in OpenCode's config). The hooks auto-bootstrap Superpowers methodology on agent start. No plugin marketplace dependency.
- **Impact on Python code:** None. The Provider Router handles glue-layer API calls (planning, escalation). Host agent selection is orthogonal — it's a container-level decision, not a code-level one.
**Rationale:** The execution layer should be as provider-agnostic as the glue layer. Locking the host agent to a single vendor while preaching multi-provider everywhere else is inconsistent. OpenCode aligns with the architecture: configure your provider, start working.

---

## Point 16: Container Terminal — tmux split-pane workspace
**Problem:** The container needs a persistent, attachable terminal. Users need to: (1) talk to the AI agent conversationally, (2) run quick utility commands without spending tokens, (3) attach from any device, (4) detach without killing the container. OpenCode doesn't yet support zero-token custom slash commands (feature requests #7337, #5305 exist upstream), so we need a way to run `el-equipo-ai status` and similar utilities without going through the LLM.
**Status:** DECIDED
**Decision:**
- **Split-pane tmux layout:**
  - **Left pane (65%):** OpenCode agent session — conversational interface for brainstorming, planning, code review, and agent-driven execution.
  - **Right pane (35%):** zsh shell — for zero-token utility commands (`el-equipo-ai status`, `pytest`, `git log`, etc.).
  - **Bottom status bar:** Always-visible navigation hints: `Ctrl+b ← → switch panes | Ctrl+b d detach`.
  - **Pane title labels:** Each pane has a visible label at the top ("OpenCode Agent" / "Shell").
- **Attach:** `docker compose exec el-equipo-ai tmux attach` — works from any device.
- **Detach:** `Ctrl+b, d` — container keeps running.
- **Override CMD:** `docker compose run --rm el-equipo-ai bash` — bypasses tmux for scripted/CI use.
- **OpenCode config:** JSON format (`opencode.json`), auto-generated on first run if not present. Manual edits preserved across restarts.
- **Dependencies added:** `tmux`, `zsh` (~2MB combined, negligible image size impact).
- **Future:** When OpenCode adds native zero-token slash commands (upstream #7337/#5305), utility commands can migrate into the left pane and the split becomes optional. Until then, the right pane provides the escape hatch.
**Rationale:** The primary interaction model is conversational — the user talks to OpenCode, the agent uses el-equipo-ai modules as tools. But some operations (checking status, running tests, inspecting logs) should cost zero tokens and be deterministic. A tmux split gives both: agent conversation on the left, reliable shell on the right, always-visible hints so users don't have to memorize shortcuts.
