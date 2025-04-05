up:
	docker compose up --build -d

down:
	docker compose down

restart:
	docker compose down && docker compose up --build -d

logs:
	docker compose logs -f

bash:
	docker compose exec web bash

psql:
	docker compose exec db psql -U $$POSTGRES_USER -d $$POSTGRES_DB

init-db:
	psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -h localhost -f schema/init.sql

load-plaid-env:
	@echo "PLAID_CLIENT_ID=$$(grep PLAID_CLIENT_ID .env.plaid | cut -d '=' -f2)"
	@echo "PLAID_SECRET=$$(grep PLAID_SECRET .env.plaid | cut -d '=' -f2)"
	@echo "PLAID_ENV=$$(grep PLAID_ENV .env.plaid | cut -d '=' -f2)"
