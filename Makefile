# Active Environment File (defaults to dev)
ENV_FILE ?= .env.dev

# Docker Compose Lifecycle
up:
	docker compose --env-file $(ENV_FILE) up --build -d

down:
	docker compose --env-file $(ENV_FILE) down

restart:
	docker compose --env-file $(ENV_FILE) down
	docker compose --env-file $(ENV_FILE) up --build -d

logs:
	docker compose --env-file $(ENV_FILE) logs -f

bash:
	docker compose --env-file $(ENV_FILE) exec web bash

# Run psql against external PostgreSQL instance
psql:
	psql -h $$(grep POSTGRES_HOST $(ENV_FILE) | cut -d '=' -f2) \
	     -p $$(grep POSTGRES_PORT $(ENV_FILE) | cut -d '=' -f2) \
	     -U $$(grep POSTGRES_USER $(ENV_FILE) | cut -d '=' -f2) \
	     -d $$(grep POSTGRES_DB $(ENV_FILE) | cut -d '=' -f2)

# Initialize the DB with schema (from host machine)
init-db:
	psql -h $$(grep POSTGRES_HOST $(ENV_FILE) | cut -d '=' -f2) \
	     -p $$(grep POSTGRES_PORT $(ENV_FILE) | cut -d '=' -f2) \
	     -U $$(grep POSTGRES_USER $(ENV_FILE) | cut -d '=' -f2) \
	     -d $$(grep POSTGRES_DB $(ENV_FILE) | cut -d '=' -f2) \
	     -f schema/init.sql

# Output Plaid Environment Settings
load-plaid-env:
	@grep PLAID_ .env.plaid

# Dependency Management
deps:
	pip-compile requirements.in --strip-extras
	pip install -r requirements.txt



upgrade:
	pip-compile --upgrade requirements.in

audit:
	pip install --quiet safety
	safety check -r requirements.txt

# Development Setup
dev-setup:
	pip install --upgrade pip
	pip install -r requirements-dev.txt

# Code Quality
lint:
	flake8 ledgerbase

format:
	black ledgerbase

test:
	pytest --cov=ledgerbase
