# Bot Dockerfile
# Uses uv for dependency management (no requirements.txt)

ARG REGISTRY_PREFIX=harbor.pg.innopolis.university/docker-hub-cache/
FROM ${REGISTRY_PREFIX}astral/uv:python3.14-bookworm-slim

WORKDIR /app

# Copy root project files for uv workspace
COPY pyproject.toml ./
COPY uv.lock ./

# Copy bot project files
COPY bot/pyproject.toml ./bot/
COPY bot/uv.lock ./bot/

# Sync dependencies using uv
RUN uv sync --frozen

# Copy bot source code
COPY bot/ ./bot/

# Default command
CMD ["uv", "run", "bot/bot.py"]
