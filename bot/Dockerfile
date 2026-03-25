# Bot Dockerfile
# Uses uv for dependency management (no requirements.txt)

ARG REGISTRY_PREFIX=harbor.pg.innopolis.university/docker-hub-cache/
FROM ${REGISTRY_PREFIX}python:3.14.2-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv==0.6.15

# Copy bot project files
COPY bot/pyproject.toml ./
COPY bot/uv.lock ./

# Sync dependencies using uv
RUN uv sync --frozen

# Copy bot source code
COPY bot/ ./

# Default command
CMD ["uv", "run", "bot.py"]
