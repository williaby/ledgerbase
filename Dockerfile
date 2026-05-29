# syntax=docker/dockerfile:1.4
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install uv (static binary from the official image)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies first for better layer caching (no dev tools, no project)
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

COPY . .

# Put the project virtualenv on PATH for all later layers
ENV PATH="/app/.venv/bin:$PATH"

# Create a non-root user for security best practices
# Using a non-root user helps limit the potential impact of container vulnerabilities
RUN groupadd -r appuser && useradd --no-log-init -r -s /bin/bash -g appuser appuser

# Set proper ownership and switch to non-root user
RUN chown -R appuser:appuser /app
USER appuser

CMD ["uv", "run", "--no-sync", "flask", "run", "--host=0.0.0.0"]
