# Bot Development Plan

## Overview

This document outlines the development plan for the LMS Telegram Bot that integrates with the learning management system backend. The bot provides students with a conversational interface to access their grades, lab information, and other LMS features.

## Architecture

### Testable Handler Architecture (P0.1)

The bot follows a clean architecture pattern where handlers are completely separated from the Telegram transport layer. Each handler is an async function that:
- Takes input parameters (command arguments, user context)
- Returns a text response
- Has no dependency on Telegram's aiogram library

This architecture enables:
- Unit testing without Telegram connection
- The `--test` CLI mode for offline verification
- Easy migration to other messaging platforms

### Directory Structure

```
bot/
├── bot.py              # Entry point with --test mode and Telegram polling
├── config.py           # Environment variable loading with pydantic-settings
├── handlers/           # Command handlers (no Telegram dependency)
│   ├── __init__.py
│   ├── start.py        # /start command handler
│   ├── help.py         # /help command handler
│   ├── health.py       # /health command handler
│   └── labs.py         # /labs command handler
├── services/           # External API clients
│   ├── __init__.py
│   ├── lms_client.py   # LMS backend API client
│   └── llm_client.py   # LLM API client for intent routing
├── pyproject.toml      # Bot dependencies
└── PLAN.md             # This file
```

## Task Breakdown

### Task 1: Scaffold (Completed)

- [x] Create `bot/pyproject.toml` with dependencies
- [x] Create `bot/config.py` for configuration management
- [x] Create `bot/handlers/` directory with basic handlers
- [x] Create `bot/services/` directory for API clients
- [x] Create `bot/bot.py` with `--test` mode support
- [x] Create `.env.bot.example` with placeholder values
- [x] Deploy and verify in Telegram

### Task 2: Backend Integration (Completed)

- [x] Implement full LMS API client with all endpoints
- [x] Add error handling with user-friendly messages (includes actual error details)
- [x] Implement `/health` command with actual backend status check
- [x] Implement `/labs` command fetching real data from `/items/` endpoint
- [x] Implement `/scores <lab_id>` command fetching from `/analytics/pass-rates`
- [x] Proper authentication with LMS API via Bearer token
- [x] Handle edge cases: missing arguments, non-existent labs, backend down

**LMS Client Endpoints:**
- `GET /items/` — list all labs and tasks (for `/health` and `/labs`)
- `GET /analytics/pass-rates?lab=lab-04` — per-task pass rates (for `/scores`)

**Error Handling:**
- Connection refused: shows "connection refused (URL). Check that the services are running."
- HTTP errors: shows "HTTP 502 Bad Gateway. The backend service may be down."
- Empty data: shows "No data available for lab-04. Check that the lab exists and ETL sync has been run."

### Task 3: Intent Routing with LLM

- [ ] Integrate LLM API for natural language understanding
- [ ] Implement intent classification for user messages
- [ ] Support natural language queries like "what labs are available"
- [ ] Add context-aware responses based on user history

### Task 4: Deployment and Monitoring

- [ ] Add Docker configuration for the bot
- [ ] Integrate with docker-compose.yml
- [ ] Add health check endpoint for monitoring
- [ ] Implement logging with structured format
- [ ] Add metrics collection (requests, errors, response time)
- [ ] Set up graceful shutdown handling

## Configuration

### Environment Variables

The bot uses the following environment variables (loaded from `.env.bot.secret`):

| Variable | Description | Required |
|----------|-------------|----------|
| `BOT_TOKEN` | Telegram bot authentication token | Yes (Telegram mode) |
| `LMS_API_BASE_URL` | Base URL of the LMS backend API | Yes |
| `LMS_API_KEY` | API key for LMS authentication | Yes |
| `LLM_API_KEY` | API key for LLM intent detection | No (fallback available) |

### Test Mode

Test mode allows offline verification without Telegram:

```bash
cd bot
uv sync
uv run bot.py --test "/start"
uv run bot.py --test "/help"
uv run bot.py --test "/health"
uv run bot.py --test "/labs"
uv run bot.py --test "/scores lab-04"
```

## Deployment

### Local Development

1. Copy `.env.bot.example` to `.env.bot.secret`
2. Fill in real values
3. Run `uv sync`
4. Run `uv run bot.py` for Telegram mode
5. Run `uv run bot.py --test "/start"` for test mode

### Production (VM)

1. Ensure `.env.bot.secret` exists with real values
2. Pull latest changes: `git pull`
3. Sync dependencies: `cd bot && uv sync`
4. Start bot: `nohup uv run bot.py > bot.log 2>&1 &`
5. Check logs: `tail -f bot.log`

## Testing Strategy

1. **Unit Tests**: Test handlers in isolation (no Telegram, no API)
2. **Integration Tests**: Test LMS client with mocked API
3. **E2E Tests**: Test full bot flow with Telegram Test API
4. **Manual Tests**: Use `--test` mode for quick verification

## Future Improvements

- Inline keyboard support for lab selection
- User authentication flow
- Push notifications for grade updates
- Multi-language support (Russian/English)
- Conversation state management for multi-turn dialogs
