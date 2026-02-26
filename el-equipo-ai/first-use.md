# El-equipo-AI — First Use Guide

This guide walks you from zero to a running system. Follow the sections in order.

---

## 1. Prerequisites

You need the following installed on your host machine before anything else.

| Tool | Version | Why |
|---|---|---|
| Docker | 24+ | The recommended way to run the full stack |
| Docker Compose | v2 (bundled with Docker Desktop) | Orchestrates the container |
| Git | Any | To clone this repo and work with project branches |
| An API key | At least one (see below) | The agents need a brain |

You do **not** need Python, Node.js, or any other runtime on your host — they all live inside the container.

### Getting API keys

You need at least one key. You can start with just one and add others later.

| Provider | Where to get a key | Free tier |
|---|---|---|
| **NVIDIA NIM** (recommended start) | https://build.nvidia.com/settings/api-keys | ~5000 credits, 40 req/min |
| **Anthropic** | https://console.anthropic.com/settings/keys | Pay-as-you-go |
| **OpenAI** | https://platform.openai.com/api-keys | Pay-as-you-go |
| **Ollama** (local) | No key needed — install Ollama on host | Free, needs GPU |

---

## 2. Installation

### Step 1 — Clone the repository

```bash
git clone https://github.com/Aurora-Firmware/The-AI-team-definition.git
cd The-AI-team-definition/el-equipo-ai
```

### Step 2 — Create your environment file

Copy the example and fill in your keys. **Never commit this file.**

```bash
cp .env.example .env   # if it doesn't exist yet, create it manually (see below)
```

Create `.env` with the keys you have. Leave the others empty — the system will skip providers with no key.

```bash
# .env — your API keys (git-ignored)

# At least one of these is required:
NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx

# Optional — for notifications when agents need human input:
TELEGRAM_WEBHOOK_URL=https://api.telegram.org/bot<TOKEN>/sendMessage?chat_id=<CHAT_ID>
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/<ID>/<TOKEN>
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/<T>/<B>/<X>
```

> **Telegram setup tip:** Create a bot via @BotFather, get the token, send a message to the bot, then call `https://api.telegram.org/bot<TOKEN>/getUpdates` to find your `chat_id`. The webhook URL is `https://api.telegram.org/bot<TOKEN>/sendMessage?chat_id=<CHAT_ID>`.

### Step 3 — Create the projects directory

This is where agent-modified code will live inside the container.

```bash
mkdir -p projects
```

Mount any project repo you want agents to work on here:

```bash
# Option A: clone inside projects/
git clone https://github.com/your-org/your-project.git projects/your-project

# Option B: symlink an existing repo
ln -s /path/to/your-local-repo projects/your-project
```

### Step 4 — Build the container

The first build takes a few minutes — it installs Python, Node.js, Vibe Kanban, Claude Code, Superpowers, and the El-equipo-AI package.

```bash
docker compose build
```

Expected output ends with something like:
```
 => exporting to image
 => => naming to docker.io/library/el-equipo-ai:latest
```

---

## 3. Configuration

The config file `el-equipo-ai.yaml` controls everything: which models to use, in what order, with what temperature, and how the system behaves.

### Option A — Use the defaults (quickest start)

The bundled `el-equipo-ai.yaml` already has sensible defaults. You only need to set your API keys in `.env` (done above). The config reads them automatically via the `api_key_env` fields.

### Option B — Customise for your setup

Edit `el-equipo-ai.yaml`. The most important things to adjust:

**1. Provider order — who goes first?**

In each role's `models` list, the first entry is the preferred provider. Put your cheapest or most available provider first.

```yaml
roles:
  executor:
    temperature: 0.3
    models:
      - { provider: nvidia, model: "minimaxai/minimax-m2.1" }   # primary
      - { provider: anthropic, model: "claude-sonnet-4-6" }     # fallback
```

**2. Remove providers you don't have keys for**

If you only have an NVIDIA key, remove the `anthropic` and `openai` entries from `providers:` and from each role's `models:` list. The system will only try providers that are listed.

**3. Set your project's test command**

```yaml
project:
  test_command: "pytest"          # Python
  # test_command: "npm test"      # Node.js
  # test_command: "cargo test"    # Rust
  setup_script: "pip install -e ." # runs in each worktree before agents start
```

**4. Adjust timeouts if needed**

The defaults are conservative. For faster feedback during testing:

```yaml
stall_detection:
  repeat_threshold: 3        # calls before a loop is flagged
  hard_timeout_minutes: 30   # max time per task
  grace_timeout_minutes: 2   # extra time to wrap up after timeout
```

---

## 4. Verify the installation

### Start the container

```bash
docker compose up -d
```

### Check it's running

```bash
docker compose ps
```

Expected:
```
NAME            IMAGE               STATUS    PORTS
el-equipo-ai    el-equipo-ai:latest running   0.0.0.0:3000->3000/tcp
```

### Test the CLI

```bash
docker compose exec el-equipo-ai el-equipo-ai --help
```

Expected output:
```
usage: el-equipo-ai [-h] [--config CONFIG] {plan,execute,integrate,status} ...

El-equipo-AI — autonomous coding orchestrator

positional arguments:
  {plan,execute,integrate,status}
    plan        Generate a task plan from a feature description
    execute     Bridge a plan file into Vibe Kanban tasks
    integrate   Run integration test phase
    status      Show provider and task status
```

### Check provider status

```bash
docker compose exec el-equipo-ai el-equipo-ai --config /app/el-equipo-ai.yaml status
```

Expected output shows all configured providers as `available`:
```
=== Provider Status ===
  nvidia: available
  anthropic: available
  openai: available
=== Swap Log (0 events) ===
```

If a provider shows `exhausted` immediately, the API key for it is likely invalid. Double-check your `.env`.

### Run the test suite

Verifies all internal components work correctly:

```bash
docker compose exec el-equipo-ai pytest /app/tests/ -v
```

All tests should pass. The tests use mocked external APIs so no real API calls are made.

### Open Vibe Kanban

Open http://localhost:3000 in your browser. You should see the Vibe Kanban task board UI. This is where agents' work appears in real time.

---

## 5. First run

Once everything checks out, here is a minimal end-to-end flow.

### Step 1 — Describe a feature

```bash
docker compose exec el-equipo-ai \
  el-equipo-ai --config /app/el-equipo-ai.yaml plan \
  "Add a health-check endpoint /health to the API that returns {status: ok, version: ...}"
```

This makes two API calls:
1. Creative brainstorm (`planner_creative` role)
2. Structured task breakdown (`planner_structured` role)

The output is a markdown task plan. Save it:

```bash
docker compose exec el-equipo-ai \
  el-equipo-ai --config /app/el-equipo-ai.yaml plan \
  "Add a health-check endpoint /health" > my-plan.txt
```

Review `my-plan.txt`. If it looks good, continue.

### Step 2 — Push the plan into Vibe Kanban

```bash
# Copy the plan into the container first
docker cp my-plan.txt el-equipo-ai:/tmp/my-plan.txt

# Bridge it to VK tasks
docker compose exec el-equipo-ai \
  el-equipo-ai --config /app/el-equipo-ai.yaml execute /tmp/my-plan.txt
```

Refresh http://localhost:3000 — you should see the tasks appear on the board.

### Step 3 — Let Vibe Kanban run the agents

In the Vibe Kanban UI, start execution. Agents will pick up tasks, work in parallel git worktrees, and submit diffs for review.

When a task needs human input (stall, escalation, or final approval), you'll receive a notification on the channels you configured and see `[ACTION REQUIRED]` in the container logs:

```bash
docker compose logs -f el-equipo-ai
```

### Step 4 — Integration phase

After all tasks are reviewed and approved in VK, run the integration phase:

```bash
docker compose exec el-equipo-ai \
  el-equipo-ai --config /app/el-equipo-ai.yaml integrate \
  feat/task-1 feat/task-2 feat/task-3
```

Pass the branch names in dependency order. The system will merge them, run your test suite, and notify you when ready for final approval.

---

## 6. Common issues

**Container won't start**
```bash
docker compose logs el-equipo-ai
```
Most likely cause: port 3000 is already in use. Change the port mapping in `docker-compose.yaml`: `"3001:3000"`.

**API key not picked up**
```bash
docker compose exec el-equipo-ai env | grep API_KEY
```
If the key is empty, check your `.env` file is in the same directory as `docker-compose.yaml` and has no trailing spaces.

**Provider immediately shows as exhausted**
The API key is invalid or the account has no credits. Log into the provider's dashboard and verify.

**Vibe Kanban not reachable at localhost:3000**
The VK process inside the container may still be starting up. Wait 10–15 seconds and refresh. Check with:
```bash
docker compose exec el-equipo-ai curl -s http://localhost:3000/health
```

**`plan` command returns garbled output**
The model returned non-plan text. This can happen with temperature 0.7 on less capable models. Try switching `planner_creative` to a stronger model in config.

**Tests fail after `pytest /app/tests/`**
Check which test failed. Tests that hit real git operations (in `test_integration.py`) need git configured. Run:
```bash
docker compose exec el-equipo-ai git config --global user.email "agent@el-equipo-ai"
docker compose exec el-equipo-ai git config --global user.name "El Equipo AI"
```

---

## 7. Updating

To update El-equipo-AI itself:

```bash
git pull
docker compose build --no-cache
docker compose up -d
```

To update Vibe Kanban or Superpowers (pinned in the Dockerfile), follow the dependency update process described in the spec: create a branch, update the pin, rebuild, run tests, then merge.

---

## 8. Local development (without Docker)

If you want to run or develop without Docker:

```bash
cd el-equipo-ai

# Python 3.11+ required
python3 -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"

# Set env vars manually
export NVIDIA_API_KEY=nvapi-xxx
export ANTHROPIC_API_KEY=sk-ant-xxx

# Run tests
pytest tests/ -v

# Run CLI
el-equipo-ai --config el-equipo-ai.yaml status
```

Note: In local dev mode, Vibe Kanban runs separately. Start it with:
```bash
npx vibe-kanban
```

---

## Quick reference

```bash
# Start
docker compose up -d

# Check status
docker compose exec el-equipo-ai el-equipo-ai --config /app/el-equipo-ai.yaml status

# Plan a feature
docker compose exec el-equipo-ai el-equipo-ai --config /app/el-equipo-ai.yaml plan "your feature"

# Watch logs
docker compose logs -f el-equipo-ai

# Run tests
docker compose exec el-equipo-ai pytest /app/tests/ -v

# Stop
docker compose down
```
