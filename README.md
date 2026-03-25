# Lab 7 — Build a Client with an AI Coding Agent

[Sync your fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork#syncing-a-fork-branch-from-the-command-line) regularly — the lab gets updated.

## Product brief

> Build a Telegram bot that lets users interact with the LMS backend through chat. Users should be able to check system health, browse labs and scores, and ask questions in plain language. The bot should use an LLM to understand what the user wants and fetch the right data. Deploy it alongside the existing backend on the VM.

This is what a customer might tell you. Your job is to turn it into a working product using an AI coding agent (Qwen Code) as your development partner.

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  ┌──────────────┐     ┌──────────────────────────────────┐   │
│  │  Telegram    │────▶│  Your Bot                        │   │
│  │  User        │◀────│  (aiogram / python-telegram-bot) │   │
│  └──────────────┘     └──────┬───────────────────────────┘   │
│                              │                               │
│                              │ slash commands + plain text    │
│                              ├───────▶ /start, /help         │
│                              ├───────▶ /health, /labs        │
│                              ├───────▶ intent router ──▶ LLM │
│                              │                    │          │
│                              │                    ▼          │
│  ┌──────────────┐     ┌──────┴───────┐    tools/actions      │
│  │  Docker      │     │  LMS Backend │◀───── GET /items      │
│  │  Compose     │     │  (FastAPI)   │◀───── GET /analytics  │
│  │              │     │  + PostgreSQL│◀───── POST /sync      │
│  └──────────────┘     └──────────────┘                       │
└──────────────────────────────────────────────────────────────┘
```

## Requirements

### P0 — Must have

1. Testable handler architecture — handlers work without Telegram
2. CLI test mode: `cd bot && uv run bot.py --test "/command"` prints response to stdout
3. `/start` — welcome message
4. `/help` — lists all available commands
5. `/health` — calls backend, reports up/down status
6. `/labs` — lists available labs
7. `/scores <lab>` — per-task pass rates
8. Error handling — backend down produces a friendly message, not a crash

### P1 — Should have

1. Natural language intent routing — plain text interpreted by LLM
2. All 9 backend endpoints wrapped as LLM tools
3. Inline keyboard buttons for common actions
4. Multi-step reasoning (LLM chains multiple API calls)

### P2 — Nice to have

1. Rich formatting (tables, charts as images)
2. Response caching
3. Conversation context (multi-turn)

### P3 — Deployment

1. Bot containerized with Dockerfile
2. Added as service in `docker-compose.yml`
3. Deployed and running on VM
4. README documents deployment

## Learning advice

Notice the progression above: **product brief** (vague customer ask) → **prioritized requirements** (structured) → **task specifications** (precise deliverables + acceptance criteria). This is how engineering work flows.

You are not following step-by-step instructions — you are building a product with an AI coding agent. The learning comes from planning, building, testing, and debugging iteratively.

## Learning outcomes

By the end of this lab, you should be able to say:

1. I turned a vague product brief into a working Telegram bot.
2. I can ask it questions in plain language and it fetches the right data.
3. I used an AI coding agent to plan and build the whole thing.

## Tasks

### Prerequisites

1. Complete the [lab setup](./lab/setup/setup-simple.md#lab-setup)

> **Note**: First time in this course? Do the [full setup](./lab/setup/setup-full.md#lab-setup) instead.

### Required

1. [Plan and Scaffold](./lab/tasks/required/task-1.md) — P0: project structure + `--test` mode
2. [Backend Integration](./lab/tasks/required/task-2.md) — P0: slash commands + real data
3. [Intent-Based Natural Language Routing](./lab/tasks/required/task-3.md) — P1: LLM tool use
4. [Containerize and Document](./lab/tasks/required/task-4.md) — P3: containerize + deploy

## Deploy

This section explains how to deploy the bot to your VM using Docker Compose.

### Prerequisites

- VM with Docker and Docker Compose installed
- Backend already running on the VM (Lab 6 setup)
- Telegram bot token from [@BotFather](https://t.me/BotFather)
- LLM API credentials (if using natural language routing)

### Environment variables

Create `.env.docker.secret` in the project root with the following:

```bash
# Telegram Bot
BOT_TOKEN=your_bot_token_here

# LMS Backend API
LMS_API_KEY=your_lms_api_key_here

# LLM API (optional - for natural language routing)
LLM_API_KEY=your_llm_api_key_here
LLM_API_BASE_URL=http://host.docker.internal:42005
LLM_API_MODEL=qwen-2.5-72b

# Other required vars (from Lab 6 setup)
REGISTRY_PREFIX=harbor.pg.innopolis.university/docker-hub-cache/
BACKEND_NAME="Learning Management Service"
BACKEND_DEBUG=false
BACKEND_CONTAINER_ADDRESS=0.0.0.0
BACKEND_CONTAINER_PORT=8000
BACKEND_HOST_ADDRESS=127.0.0.1
BACKEND_HOST_PORT=42002
BACKEND_ENABLE_INTERACTIONS=true
BACKEND_ENABLE_LEARNERS=true
LMS_API_HOST_ADDRESS=0.0.0.0
LMS_API_HOST_PORT=80
CADDY_CONTAINER_PORT=80
POSTGRES_DB=db-lab-7
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST_ADDRESS=127.0.0.1
POSTGRES_HOST_PORT=42004
PGADMIN_EMAIL=admin@example.com
PGADMIN_PASSWORD=admin
PGADMIN_HOST_ADDRESS=127.0.0.1
PGADMIN_HOST_PORT=42003
```

> **Note**: `LLM_API_BASE_URL` uses `host.docker.internal` to reach the LLM proxy running on the host machine.

### Deploy commands

1. **Stop the old bot** (if running with nohup):
   ```bash
   cd ~/se-toolkit-lab-7
   pkill -f "bot.py" 2>/dev/null || true
   ```

2. **Start all services**:
   ```bash
   docker compose --env-file .env.docker.secret up --build -d
   ```

3. **Verify services are running**:
   ```bash
   docker compose --env-file .env.docker.secret ps
   ```

   You should see:
   - `backend` - healthy
   - `postgres` - healthy
   - `pgadmin` - running
   - `caddy` - running
   - `bot` - running

### Verify deployment

1. **Check bot logs**:
   ```bash
   docker compose --env-file .env.docker.secret logs bot --tail 20
   ```

   Look for:
   - "Bot is starting..." — bot started successfully
   - "HTTP Request: POST .../getUpdates" — bot is polling Telegram

2. **Test in Telegram**:
   - Send `/start` — should receive welcome message
   - Send `/health` — should see backend status
   - Send "what labs are available?" — should list labs (LLM-powered)

3. **Check backend connectivity**:
   ```bash
   curl -sf http://localhost:42002/items/ -H "Authorization: Bearer YOUR_LMS_API_KEY" | head -c 200
   ```

### Troubleshooting

| Symptom | Solution |
|---------|----------|
| Bot container restarting | Check logs: `docker compose logs bot`. Usually missing env var or import error. |
| `/health` fails | `LMS_API_BASE_URL` must be `http://backend:8000` (not localhost). |
| LLM queries fail | `LLM_API_BASE_URL` must use `host.docker.internal`. |
| Build fails at `uv sync --frozen` | Ensure `bot/uv.lock` exists and is copied in Dockerfile. |

### Stop services

```bash
docker compose --env-file .env.docker.secret down
```

> **Note**: This stops all services but preserves data (PostgreSQL data is in a named volume).
