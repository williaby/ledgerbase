# LedgerBase

LedgerBase is a personal financial management system tailored for families who want detailed insight into budgeting, debt tracking, savings behavior, and expense attribution — all managed via a structured ETL pipeline and a clean interface.

## Key Features

- Bank data ingestion via Plaid or CSV
- Vendor dictionary + regex mapping
- 2-level budget categorization + historical tracking
- Unmatched vendor review queue with ML suggestions
- Tagging by person, savings model, and business reimbursement
- CLI tools, audit trail, and reporting views
- Fully Dockerized for Unraid or local development

## Stack

- Python 3.11
- Flask + SQLAlchemy
- PostgreSQL
- Docker + Docker Compose
- Jinja2 Templates + HTMX (planned)
- Optional: Jupyter, Alembic, GitHub Actions, ML integration

## Getting Started

See [docs/setup-instructions.md](docs/setup-instructions.md)

## Status

[![Dev Checks](https://github.com/williaby/ledgerbase/actions/workflows/dev-checks.yml/badge.svg)](https://github.com/williaby/ledgerbase/actions/workflows/dev-checks.yml)
[![Weekly Audit](https://github.com/williaby/ledgerbase/actions/workflows/security-deps-audit.yml/badge.svg)](https://github.com/williaby/ledgerbase/actions/workflows/security-deps-audit.yml)
[![codecov](https://codecov.io/gh/williaby/ledgerbase/branch/main/graph/badge.svg?token=NH77ZXWUJQ)](https://codecov.io/gh/williaby/ledgerbase)
