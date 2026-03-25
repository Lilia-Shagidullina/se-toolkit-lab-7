# Bot Dockerfile
# Uses uv for dependency management (no requirements.txt)

ARG REGISTRY_PREFIX=harbor.pg.innopolis.university/docker-hub-cache/
FROM ${REGISTRY_PREFIX}python:3.14.2-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv==0.6.15

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
CMD ["uv", "run", "bot.py"]
