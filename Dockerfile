# syntax=docker/dockerfile:1.4
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_HOME="/opt/poetry"

# Add Poetry to path for all layers
ENV PATH="${POETRY_HOME}/bin:$PATH"

WORKDIR /app

# Install Poetry and dependencies
RUN apt-get update && \
    apt-get install -y curl build-essential && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    export PATH="${POETRY_HOME}/bin:$PATH" && \
    poetry --version

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root


COPY . .

# Create a non-root user for security best practices
# Using a non-root user helps limit the potential impact of container vulnerabilities
RUN groupadd -r appuser && useradd --no-log-init -r -s /bin/bash -g appuser appuser

# Set proper ownership and switch to non-root user
RUN chown -R appuser:appuser /app
USER appuser

CMD ["poetry", "run", "flask", "run", "--host=0.0.0.0"]
