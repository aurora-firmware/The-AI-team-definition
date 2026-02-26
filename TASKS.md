# El-equipo-AI — Implementation Task Breakdown

Every task is designed to be:
- **Atomic:** One clear outcome per task.
- **One-shottable:** Small enough that an agent can complete it in one pass.
- **Verifiable:** Each task has a test or check that proves it works.
- **Parallelizable:** Tasks in the same group have no file overlap and can run simultaneously.

Dependencies between groups are explicit. Tasks within a group are independent.

-----

## Project Structure

```
el-equipo-ai/
├── el_equipo_ai/
│   ├── __init__.py
│   ├── config.py              # Config loader
│   ├── provider_router.py     # Provider selection + API calls
│   ├── quota_manager.py       # Cooldown timers, swap logic, state persistence
│   ├── stall_detector.py      # Pattern tracking, wrap-up injection
│   ├── manifest_bridge.py     # Superpowers plan → VK tasks
│   ├── integration.py         # Merge orchestration, test, bisect
│   ├── escalation.py          # Architect consultation + human escalation
│   ├── notifier.py            # Webhook sender
│   ├── logger.py              # JSONL logger with rotation
│   └── models.py              # Shared data classes / types
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_provider_router.py
│   ├── test_quota_manager.py
│   ├── test_stall_detector.py
│   ├── test_manifest_bridge.py
│   ├── test_integration.py
│   ├── test_escalation.py
│   ├── test_notifier.py
│   ├── test_logger.py
│   └── conftest.py            # Shared fixtures
├── el-equipo-ai.yaml          # Example config
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt
├── pyproject.toml
└── README.md
```

-----

## GROUP 0: Scaffolding (must complete first)

All subsequent groups depend on this.

### T0.1 — Project skeleton + packaging

**Files:** `pyproject.toml`, `requirements.txt`, `el_equipo_ai/__init__.py`, `tests/__init__.py`, `tests/conftest.py`
**Description:** Create the project with pyproject.toml (name: el-equipo-ai, python >=3.11). requirements.txt with: `openai>=1.0`, `pyyaml>=6.0`, `requests>=2.28`. Empty __init__.py files. conftest.py with basic pytest config and a fixture that provides a path to a sample config file.
**Verification:** `pip install -e .` succeeds. `pytest --co` discovers the test directory.

### T0.2 — Shared data models

**Files:** `el_equipo_ai/models.py`
**Description:** Define dataclasses used across all modules:
- `ProviderConfig(name, base_url, api_key_env)`
- `RoleConfig(name, temperature, json_mode, models: list[ModelOption])`
- `ModelOption(provider, model)`
- `StallConfig(repeat_threshold, grace_calls_after_signal, hard_timeout_minutes, grace_timeout_minutes)`
- `NotificationChannel(type, name, url_env)`
- `LogConfig(file, max_size_mb, max_rotated_files)`
- `ProjectConfig(test_command, setup_script)`
- `AppConfig` (top-level, contains all the above)
- `TaskFailureReport(task_id, attempts, what_tried, what_failed, agent_analysis)`
- `ProviderStatus` enum: `AVAILABLE`, `COOLDOWN`, `EXHAUSTED`
- `ProviderState(name, status, reset_at: datetime | None)`
- `LogEvent(ts, type, **data)` — flexible event structure
**Verification:** `python -c "from el_equipo_ai.models import AppConfig"` succeeds. All dataclasses can be instantiated with sample data.

### T0.3 — Example config file

**Files:** `el-equipo-ai.yaml`
**Description:** Create the full example config file matching the schema in spec Section 10.1. Use placeholder env var names. Include comments explaining each section. This is both documentation and the test fixture.
**Verification:** File is valid YAML (parseable by `python -c "import yaml; yaml.safe_load(open('el-equipo-ai.yaml'))"`).

-----

## GROUP 1: Config + Logger (foundation utilities)

Depends on: GROUP 0.
All tasks in this group are independent of each other.

### T1.1 — Config loader

**Files:** `el_equipo_ai/config.py`, `tests/test_config.py`
**Description:** Write `load_config(path: str) -> AppConfig` that:
- Reads YAML file
- Validates required fields exist (providers, roles, stall_detection, logging)
- Resolves `api_key_env` to actual env var values (using `os.environ.get`)
- Returns a populated `AppConfig` dataclass
- Raises clear error messages on missing fields or bad types
**Tests:**
- Loading the example config succeeds and returns correct types
- Missing required field raises `ValueError` with field name
- Missing env var for api_key_env sets key to `None` (not crash)
**Verification:** `pytest tests/test_config.py` all pass.

### T1.2 — JSONL logger with rotation

**Files:** `el_equipo_ai/logger.py`, `tests/test_logger.py`
**Description:** Write a `Logger` class:
- `__init__(self, config: LogConfig)` — opens log file in append mode
- `log(self, event_type: str, **data)` — writes one JSONL line: `{"ts": iso8601_now, "type": event_type, ...data}`
- Before each write, check file size. If >= `max_size_mb`, rotate: rename current to `.1`, shift `.1` to `.2`, etc. Delete files beyond `max_rotated_files`.
- Thread-safe (use a lock — multiple agents may log concurrently).
**Tests:**
- Writing an event produces valid JSONL line with timestamp
- Rotation triggers at size limit
- Old files beyond max count are deleted
- Concurrent writes don't corrupt the file
**Verification:** `pytest tests/test_logger.py` all pass.

### T1.3 — Webhook notifier

**Files:** `el_equipo_ai/notifier.py`, `tests/test_notifier.py`
**Description:** Write a `Notifier` class:
- `__init__(self, channels: list[NotificationChannel], logger: Logger)`
- `info(self, message: str)` — prints to stdout. Logs event type `notification_info`.
- `action_required(self, title: str, body: str, vk_link: str | None)` — sends POST to ALL configured webhook URLs with JSON payload: `{"text": formatted_message}`. Logs event type `notification_action_required`. Does NOT block on failure — if a webhook fails, log the error and continue to next channel.
- Payload format: `"[ACTION REQUIRED] {title}\n{body}\nInspect: {vk_link}"`
**Tests:**
- `info()` prints to stdout (capture with capsys)
- `action_required()` sends POST to all channels (mock requests.post)
- Failed webhook is logged but doesn't raise
- Missing url_env (None) skips that channel gracefully
**Verification:** `pytest tests/test_notifier.py` all pass.

-----

## GROUP 2: Provider Router (core brain selection)

Depends on: GROUP 1 (needs config + logger).
All tasks in this group are independent of each other.

### T2.1 — Provider Router: role-based model selection

**Files:** `el_equipo_ai/provider_router.py` (partial — selection logic), `tests/test_provider_router.py` (partial)
**Description:** Write the model selection part of `ProviderRouter`:
- `__init__(self, config: AppConfig, logger: Logger)`
- `get_provider_for_role(self, role_name: str) -> tuple[ProviderConfig, str]` — returns (provider, model_id) for the highest-priority AVAILABLE provider in that role's list. If none available, returns `None`.
- Maintains internal `dict[str, ProviderState]` for each provider.
- `mark_cooldown(self, provider_name: str, reset_at: datetime)` — sets provider to COOLDOWN.
- `check_cooldowns(self)` — checks all cooldown timers, marks providers as AVAILABLE if reset_at has passed.
**Tests:**
- Returns first provider when all available
- Skips provider in cooldown, returns second
- Returns None when all providers exhausted
- Provider returns to AVAILABLE after cooldown expires
**Verification:** `pytest tests/test_provider_router.py` all pass.

### T2.2 — Provider Router: API call wrapper

**Files:** `el_equipo_ai/provider_router.py` (partial — API calling), `tests/test_provider_router.py` (partial)
**Description:** Add the API calling method to `ProviderRouter`:
- `call(self, role_name: str, messages: list[dict], tools: list[dict] | None = None) -> dict` — gets provider for role, creates OpenAI client with that provider's base_url and api_key, calls `client.chat.completions.create(model=..., messages=..., temperature=role.temperature, tools=...)`.
- On success: logs `provider_call` event, returns response.
- On 429 (rate limit): check `Retry-After` header, wait and retry once. If still 429, raise.
- On quota error (402/429 with quota message): call `mark_cooldown`, retry with next provider via `get_provider_for_role`. If no providers left, raise `AllProvidersExhausted`.
- If role has `json_mode: true` and model supports it, add `response_format={"type": "json_object"}`.
**Tests:**
- Successful call returns response and logs event (mock openai client)
- 429 with Retry-After waits and retries (mock)
- Quota error triggers fallback to next provider (mock)
- AllProvidersExhausted raised when none left
**Verification:** `pytest tests/test_provider_router.py` all pass.

### T2.3 — Quota state persistence

**Files:** `el_equipo_ai/quota_manager.py`, `tests/test_quota_manager.py`
**Description:** Write `QuotaManager`:
- `__init__(self, state_file: str, logger: Logger)` — loads state from JSON file if it exists.
- `save(self)` — writes current provider states to JSON file (provider name, status, reset_at as ISO8601).
- `load(self)` — reads JSON file, returns `dict[str, ProviderState]`. If file doesn't exist, returns empty dict.
- `log_swap_event(self, from_provider: str, to_provider: str, reason: str, reset_at: datetime | None)` — appends to swap log in the JSON file.
- JSON file structure: `{"provider_states": {...}, "swap_log": [...]}`
**Tests:**
- Save and load round-trips correctly
- Missing file returns empty state
- Swap events accumulate in the log
- ISO8601 datetime serialization/deserialization works
**Verification:** `pytest tests/test_quota_manager.py` all pass.

-----

## GROUP 3: Stall Detection (agent monitoring)

Depends on: GROUP 2 (needs provider router to inject messages).
All tasks in this group are independent of each other.

### T3.1 — Stall detector: pattern tracker

**Files:** `el_equipo_ai/stall_detector.py` (partial — detection), `tests/test_stall_detector.py` (partial)
**Description:** Write `StallDetector`:
- `__init__(self, config: StallConfig, logger: Logger)`
- `record_tool_call(self, task_id: str, tool_name: str, tool_input: str, tool_output: str)` — adds to per-task sliding window.
- `check_stall(self, task_id: str) -> str | None` — analyzes the window, returns stall pattern type or None:
  - `"command_loop"`: same `run_command` input AND output repeated >= threshold times
  - `"read_loop"`: same `read_file` path repeated >= threshold times with no `edit_file` in between
  - `"edit_revert_cycle"`: alternating edit/run_command with same failing output >= threshold times
  - `None`: no stall detected
- Sliding window size: `threshold * 3` (enough history to detect patterns).
**Tests:**
- No stall on varied tool calls → returns None
- Command loop detected after N identical run_command calls
- Read loop detected after N reads without edits
- Edit-revert cycle detected
- Different tasks tracked independently
**Verification:** `pytest tests/test_stall_detector.py` all pass.

### T3.2 — Stall detector: wrap-up signal + hard timeout

**Files:** `el_equipo_ai/stall_detector.py` (partial — intervention), `tests/test_stall_detector.py` (partial)
**Description:** Add intervention logic:
- `get_wrap_up_message(self, pattern: str, task_id: str) -> str` — returns the wrap-up prompt tailored to the pattern type. Core message: "You have attempted the same approach multiple times without progress. Stop trying. Summarize: (1) what you tried, (2) what's failing, (3) root cause guess. Call task_complete(failed)."
- `start_task_timer(self, task_id: str)` — records task start time.
- `is_hard_timeout(self, task_id: str) -> bool` — checks if wall-clock time exceeds `hard_timeout_minutes`.
- `get_grace_state(self, task_id: str) -> dict` — returns `{"signaled": bool, "calls_since_signal": int}`. After signal, increments on each `record_tool_call`. If `calls_since_signal >= grace_calls_after_signal`, returns `{"force_kill": True}`.
- `is_grace_timeout(self, task_id: str) -> bool` — if hard timeout fired and grace signal was sent, checks if `grace_timeout_minutes` has also passed.
**Tests:**
- Wrap-up message contains required instructions
- Hard timeout detection based on elapsed time
- Grace call counter increments correctly
- Force kill triggered after grace calls exceeded
- Grace timeout after hard timeout
**Verification:** `pytest tests/test_stall_detector.py` all pass.

-----

## GROUP 4: Task Manifest Bridge + Escalation (VK interaction)

Depends on: GROUP 2 (needs provider router for escalation API calls).
All tasks in this group are independent of each other.

### T4.1 — VK MCP client wrapper

**Files:** `el_equipo_ai/manifest_bridge.py` (partial — MCP client), `tests/test_manifest_bridge.py` (partial)
**Description:** Write a thin MCP client for VK:
- `VKClient.__init__(self, vk_url: str, logger: Logger)` — stores VK base URL.
- `create_task(self, title: str, description: str, dependencies: list[str] | None, role: str, verification_command: str | None) -> str` — calls VK MCP `create_task` endpoint. Returns task ID. Logs `vk_task_created` event.
- `get_task_status(self, task_id: str) -> str` — calls VK MCP to get task status (todo, in_progress, done, failed).
- `list_tasks(self, project_id: str) -> list[dict]` — lists all tasks for a project.
**NOTE FOR CODING AGENT:** Research the actual VK MCP server API (tool names, parameter format) before implementing. Check https://vibekanban.com/docs/integrations/vibe-kanban-mcp-server for the latest interface.
**Tests:**
- create_task sends correct payload (mock HTTP)
- Response parsed to task ID
- get_task_status returns correct status
- Network error logged but raises
**Verification:** `pytest tests/test_manifest_bridge.py` all pass.

### T4.2 — Plan parser + task creation

**Files:** `el_equipo_ai/manifest_bridge.py` (partial — parser), `tests/test_manifest_bridge.py` (partial)
**Description:** Write the plan-to-tasks translation:
- `parse_superpowers_plan(plan_text: str) -> list[TaskSpec]` — parses Superpowers' plan output (markdown with structured task sections) into a list of `TaskSpec(title, description, dependencies, role, verification_command, files_modify, files_create)`.
- `bridge_plan_to_vk(plan_text: str, vk_client: VKClient) -> list[str]` — parses plan, creates each task in VK via MCP, preserves dependency chain by mapping local IDs to VK task IDs. Returns list of created VK task IDs.
**NOTE FOR CODING AGENT:** Research Superpowers' actual plan output format (from the `writing-plans` skill SKILL.md) before implementing the parser. The format may use markdown headers, bullet points, or structured sections. The parser must handle the actual format, not a guessed one.
**Tests:**
- Parser extracts tasks from sample plan markdown
- Dependencies mapped correctly when bridging to VK
- Empty plan produces empty task list
- Malformed plan raises clear error
**Verification:** `pytest tests/test_manifest_bridge.py` all pass.

### T4.3 — Escalation: architect consultation

**Files:** `el_equipo_ai/escalation.py` (partial — architect), `tests/test_escalation.py` (partial)
**Description:** Write architect consultation:
- `consult_architect(failure_report: TaskFailureReport, provider_router: ProviderRouter, logger: Logger) -> ArchitectVerdict` — sends a read-only query to the `planner_creative` role model. Prompt: "A task failed after multiple attempts. Based on this failure context, is this (A) a simple fix — provide revised instructions, or (B) a scope problem requiring human re-planning? Respond with JSON: {verdict: 'simple_fix'|'scope_problem', revised_instructions: string|null, analysis: string}."
- Returns `ArchitectVerdict(verdict, revised_instructions, analysis)`.
- Logs `architect_consult` event.
**Tests:**
- Simple fix verdict parsed correctly (mock API response)
- Scope problem verdict parsed correctly
- API failure raises and logs
- Malformed response defaults to scope_problem (safe fallback)
**Verification:** `pytest tests/test_escalation.py` all pass.

### T4.4 — Escalation: full pipeline

**Files:** `el_equipo_ai/escalation.py` (partial — pipeline), `tests/test_escalation.py` (partial)
**Description:** Write the full escalation flow:
- `handle_task_failure(failure_report: TaskFailureReport, provider_router: ProviderRouter, vk_client: VKClient, notifier: Notifier, logger: Logger) -> EscalationResult`:
  1. Call `consult_architect`.
  2. If `simple_fix`: create new task in VK with revised instructions. Return `EscalationResult(action="retried", new_task_id=...)`.
  3. If `scope_problem`: call `notifier.action_required` with full context. Return `EscalationResult(action="escalated_to_human", ...)`.
  4. If this is the SECOND failure for the same original task (check via `failure_report.attempts`): skip architect, go directly to human. Return `EscalationResult(action="escalated_to_human", ...)`.
- `EscalationResult(action, new_task_id, analysis)`
**Tests:**
- First failure → architect → simple fix → new VK task created
- First failure → architect → scope problem → human notified
- Second failure → skips architect → human notified directly
- Notifier called with correct context on escalation
**Verification:** `pytest tests/test_escalation.py` all pass.

-----

## GROUP 5: Integration Test Phase (merge orchestration)

Depends on: GROUP 4 (needs VK client for conflict fix tasks).
All tasks in this group are SEQUENTIAL (each builds on the previous).

### T5.1 — Git operations helper

**Files:** `el_equipo_ai/integration.py` (partial — git ops), `tests/test_integration.py` (partial)
**Description:** Write low-level git helpers using subprocess:
- `create_branch(branch_name: str, from_ref: str = "main") -> bool` — `git checkout -b {branch_name} {from_ref}`.
- `merge_branch(source_branch: str) -> MergeResult` — `git merge --no-ff {source_branch}`. Returns `MergeResult(success: bool, conflict_files: list[str], output: str)`. On conflict: parses git output for conflicting file names.
- `run_tests(test_command: str) -> TestResult` — runs command via subprocess. Returns `TestResult(passed: bool, output: str, exit_code: int)`.
- `abort_merge() -> None` — `git merge --abort`.
- `get_current_branch() -> str` — `git branch --show-current`.
- `get_merge_log(branch: str) -> list[str]` — returns list of branches already merged into the given branch (for crash recovery).
All commands run via `subprocess.run` with `capture_output=True, text=True`.
**Tests:**
- create_branch succeeds in a test git repo (use tmp_path fixture)
- merge_branch detects conflicts correctly
- run_tests captures pass/fail
- abort_merge cleans up
**Verification:** `pytest tests/test_integration.py` all pass (uses temporary git repos).

### T5.2 — Sequential merge in dependency order

**Files:** `el_equipo_ai/integration.py` (partial — merge loop), `tests/test_integration.py` (partial)
**Description:** Write the merge orchestration:
- `merge_all_branches(branches_in_order: list[str], integration_branch: str, logger: Logger) -> MergeAllResult`:
  1. Create integration branch from main.
  2. For each branch in dependency order: merge into integration branch.
  3. If conflict: abort merge, return `MergeAllResult(success=False, failed_at=branch, conflict_files=[...])`.
  4. If all merge: return `MergeAllResult(success=True, ...)`.
- On restart (crash recovery): call `get_merge_log` on integration branch to determine which branches are already merged. Skip those. Resume from next.
**Tests:**
- All branches merge cleanly → success
- Conflict on branch 3 → returns failure with correct branch name and files
- Already-merged branches detected and skipped on restart
**Verification:** `pytest tests/test_integration.py` all pass.

### T5.3 — Bisect on test failure

**Files:** `el_equipo_ai/integration.py` (partial — bisect), `tests/test_integration.py` (partial)
**Description:** Write bisect logic:
- `bisect_failure(branches: list[str], test_command: str, logger: Logger) -> str`:
  1. Full merge succeeded but tests failed. Which branch introduced the failure?
  2. Binary search: merge first half of branches → test. If pass, problem is in second half. If fail, problem is in first half. Recurse.
  3. Returns the branch name that introduced the test failure.
  4. Logs each bisect step.
- Uses `merge_all_branches` + `run_tests` internally.
**Tests:**
- Correctly identifies the failing branch (mock test results for specific branch combos)
- Log entries for each bisect step
- Works with 1 branch (trivial case)
- Works with 10 branches (bisect should need max 4 steps)
**Verification:** `pytest tests/test_integration.py` all pass.

### T5.4 — Conflict escalation to VK

**Files:** `el_equipo_ai/integration.py` (partial — conflict handling), `tests/test_integration.py` (partial)
**Description:** Write conflict resolution flow:
- `handle_merge_conflict(failed_branch: str, conflict_files: list[str], conflict_diff: str, vk_client: VKClient, logger: Logger) -> str`:
  1. Creates a new fix task in VK via MCP: title "Resolve merge conflict: {failed_branch}", description includes conflict diff and list of conflicting files.
  2. Logs `integration_conflict` event.
  3. Returns the new VK task ID.
- `integration_pipeline(branches_in_order: list[str], test_command: str, vk_client: VKClient, notifier: Notifier, logger: Logger) -> IntegrationResult`:
  1. Call `merge_all_branches`. If conflict → `handle_merge_conflict`, return `IntegrationResult(status="conflict_escalated", ...)`.
  2. If all merged → `run_tests`. If pass → return `IntegrationResult(status="passed", ...)`.
  3. If tests fail → `bisect_failure` → return `IntegrationResult(status="test_failed", failing_branch=..., ...)`.
  4. On pass: call `notifier.action_required("Integration tests passed — approve final merge?", ...)`.
**Tests:**
- Clean merge + tests pass → "passed" + notifier called for approval
- Merge conflict → fix task created in VK
- Tests fail → bisect identifies failing branch
**Verification:** `pytest tests/test_integration.py` all pass.

-----

## GROUP 6: Container (packaging)

Depends on: GROUP 0 (needs project structure).
Independent of all other groups — can run in parallel with GROUPS 1-5.

### T6.1 — Dockerfile

**Files:** `Dockerfile`
**Description:** Write a Dockerfile that installs:
- Python 3.11+, Node.js (for VK), git
- Vibe Kanban (via npm: `npx vibe-kanban`)
- El-equipo-AI Python package (pip install from local)
- Superpowers plugin for Claude Code
- Any configured host agent CLIs (Claude Code, OpenCode, etc.)
**NOTE FOR CODING AGENT:** Research the latest installation methods for Vibe Kanban and Superpowers before writing. Check `npx vibe-kanban` and Superpowers marketplace install commands. Pin versions.
**Verification:** `docker build -t el-equipo-ai .` succeeds.

### T6.2 — docker-compose.yaml

**Files:** `docker-compose.yaml`
**Description:** Write compose file:
- Service `el-equipo-ai`: builds from Dockerfile, mounts `./projects:/workspace` for project repos, passes env vars for API keys (`NVIDIA_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `TELEGRAM_WEBHOOK_URL`, etc.), exposes VK port (3000).
- Volume for persistent data (logs, quota state JSON).
**Verification:** `docker compose config` validates successfully.

-----

## GROUP 7: End-to-end wiring + tests

Depends on: ALL previous groups.

### T7.1 — Main entrypoint

**Files:** `el_equipo_ai/__init__.py` (update), `el_equipo_ai/main.py`
**Description:** Write the main orchestration script that wires everything together:
- Load config
- Initialize: Logger, QuotaManager, ProviderRouter, StallDetector, VKClient, Notifier
- Expose top-level functions that the workflow calls:
  - `plan(feature_description: str)` — uses provider_router to call planner_creative, then planner_structured
  - `execute(plan_text: str)` — uses manifest_bridge to create VK tasks, then monitors VK task statuses, runs stall detection on active tasks
  - `integrate()` — runs integration pipeline
  - `status()` — prints current state (provider statuses, task statuses, etc.)
**Verification:** `python -m el_equipo_ai.main --help` runs without error (if using argparse) or module imports cleanly.

### T7.2 — End-to-end integration test

**Files:** `tests/test_e2e.py`
**Description:** Write an end-to-end test that mocks external services (VK MCP, model API) and verifies the full pipeline:
1. Load test config
2. Call plan() with a sample feature description → mock planner returns a plan
3. Call execute() → mock bridge creates VK tasks → mock VK reports tasks completing
4. Call integrate() → mock git merges succeed → mock tests pass
5. Verify: notifier called for final approval, logger has full event trail, no errors
**Tests:**
- Happy path: full pipeline completes
- Provider fallback: primary provider fails, secondary succeeds
- Stall detection: mock agent stalls, wrap-up signal injected
- Escalation: mock task fails, architect consulted, human notified
**Verification:** `pytest tests/test_e2e.py` all pass.

-----

## Parallelism Map

```
GROUP 0 (scaffolding)
  ├── T0.1, T0.2, T0.3 — can run in parallel
  │
  ▼
GROUP 1 (config + logger + notifier)  ←──────── GROUP 6 (container)
  ├── T1.1, T1.2, T1.3 — in parallel            ├── T6.1, T6.2 — in parallel
  │                                               │ (independent of code groups)
  ▼                                               │
GROUP 2 (provider router)                         │
  ├── T2.1, T2.2, T2.3 — in parallel             │
  │                                               │
  ▼                                               │
GROUP 3 (stall detection)                         │
  ├── T3.1, T3.2 — in parallel                   │
  │                                               │
  ▼                                               │
GROUP 4 (bridge + escalation)                     │
  ├── T4.1, T4.2, T4.3, T4.4 — in parallel      │
  │                                               │
  ▼                                               │
GROUP 5 (integration)                             │
  ├── T5.1 → T5.2 → T5.3 → T5.4 — SEQUENTIAL   │
  │                                               │
  ▼                                               ▼
GROUP 7 (wiring + e2e) ◄─────────────────────────┘
  ├── T7.1 → T7.2 — SEQUENTIAL
```

**Maximum parallelism per group:**
- G0: 3 agents
- G1: 3 agents  |  G6: 2 agents  (G1 and G6 run in parallel = 5 agents)
- G2: 3 agents
- G3: 2 agents
- G4: 4 agents
- G5: 1 agent (sequential)
- G7: 1 agent (sequential)

**Total tasks: 24**
**Critical path (longest sequential chain):** G0 → G1 → G2 → G3 → G4 → G5 → G7 = 7 sequential group-waits.

-----

## Task Summary Table

| ID | Task | Group | Files | Parallel with |
|---|---|---|---|---|
| T0.1 | Project skeleton + packaging | 0 | pyproject.toml, requirements.txt, __init__.py | T0.2, T0.3 |
| T0.2 | Shared data models | 0 | models.py | T0.1, T0.3 |
| T0.3 | Example config file | 0 | el-equipo-ai.yaml | T0.1, T0.2 |
| T1.1 | Config loader | 1 | config.py, test_config.py | T1.2, T1.3, T6.x |
| T1.2 | JSONL logger with rotation | 1 | logger.py, test_logger.py | T1.1, T1.3, T6.x |
| T1.3 | Webhook notifier | 1 | notifier.py, test_notifier.py | T1.1, T1.2, T6.x |
| T2.1 | Provider Router: selection | 2 | provider_router.py, test_provider_router.py | T2.2, T2.3 |
| T2.2 | Provider Router: API calls | 2 | provider_router.py, test_provider_router.py | T2.1, T2.3 |
| T2.3 | Quota state persistence | 2 | quota_manager.py, test_quota_manager.py | T2.1, T2.2 |
| T3.1 | Stall detector: patterns | 3 | stall_detector.py, test_stall_detector.py | T3.2 |
| T3.2 | Stall detector: intervention | 3 | stall_detector.py, test_stall_detector.py | T3.1 |
| T4.1 | VK MCP client wrapper | 4 | manifest_bridge.py, test_manifest_bridge.py | T4.2, T4.3, T4.4 |
| T4.2 | Plan parser + task creation | 4 | manifest_bridge.py, test_manifest_bridge.py | T4.1, T4.3, T4.4 |
| T4.3 | Escalation: architect consult | 4 | escalation.py, test_escalation.py | T4.1, T4.2, T4.4 |
| T4.4 | Escalation: full pipeline | 4 | escalation.py, test_escalation.py | T4.1, T4.2, T4.3 |
| T5.1 | Git operations helper | 5 | integration.py, test_integration.py | (none — sequential) |
| T5.2 | Sequential merge | 5 | integration.py, test_integration.py | (none) |
| T5.3 | Bisect on failure | 5 | integration.py, test_integration.py | (none) |
| T5.4 | Conflict escalation to VK | 5 | integration.py, test_integration.py | (none) |
| T6.1 | Dockerfile | 6 | Dockerfile | T6.2, all of G1-G5 |
| T6.2 | docker-compose.yaml | 6 | docker-compose.yaml | T6.1, all of G1-G5 |
| T7.1 | Main entrypoint | 7 | main.py | (none) |
| T7.2 | End-to-end test | 7 | test_e2e.py | (none) |
