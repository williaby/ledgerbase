FROM python:3.11-slim@sha256:82c07f2f6e35255b92eb16f38dbd22679d5e8fb523064138d7c6468e7bf0c15b AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install uv (static binary from the official image)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Create non-root user 'appuser'
RUN addgroup --system appuser && adduser --system --ingroup appuser appuser

# Copy only necessary files for installing deps
COPY pyproject.toml uv.lock ./

# Install dependencies without dev tools
RUN uv sync --frozen --no-dev --no-install-project

# Put the project virtualenv on PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copy actual app code and change ownership
COPY . .
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Run app
CMD ["uv", "run", "--no-sync", "python", "-m", "app"]
