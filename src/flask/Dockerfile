FROM python:3.11-slim@sha256:82c07f2f6e35255b92eb16f38dbd22679d5e8fb523064138d7c6468e7bf0c15b AS base

ENV POETRY_VERSION=1.8.2
ENV POETRY_HOME="/opt/poetry"

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="$POETRY_HOME/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy only necessary files for installing deps
COPY pyproject.toml poetry.lock ./

# Install dependencies without dev tools
RUN poetry install --no-dev --no-interaction

# Copy actual app code
COPY . .

# Run app
CMD ["poetry", "run", "python", "-m", "app"]
