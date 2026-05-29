# Declare phony targets so Make treats these names as actions, not files
.PHONY: up down restart logs dev-setup lint format test encrypt-sa decrypt-sa clean-sa

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

# Development Setup
dev-setup:
	@echo "🔧 Installing dependencies and loading environment..."
	make decrypt-sa
	# Add other local setup commands here, e.g., uv sync, pre-commit install

# Code Quality Targets
lint:
	@echo "🔍 Running linters..."
	# e.g., nox -s lint

format:
	@echo "🎨 Formatting code..."
	# e.g., nox -s format

test:
	@echo "🧪 Running tests..."
	# e.g., nox -s tests

# Service Account Encryption Management
encrypt-sa:
	@echo "🔒 Encrypting service-account.json…"
	sops -i --encrypt ledgerbase_secure_env/service-account.json

decrypt-sa:
	@echo "🔓 Decrypting service-account.json in place…"
	sops -d --output ledgerbase_secure_env/service-account.json \
		ledgerbase_secure_env/service-account.json

clean-sa:
	@echo "❗️ service-account.json is decrypted. Run 'make encrypt-sa' to re-encrypt."
