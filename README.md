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

## CI / DevOps Status

| Workflow           | Status |
|--------------------|--------|
| Lint & Format      | ![Lint](https://github.com/williaby/ledgerbase/actions/workflows/dev-checks.yml/badge.svg?branch=main) |
| Unit Tests         | ![Tests](https://github.com/williaby/ledgerbase/actions/workflows/dev-checks.yml/badge.svg?branch=main) |
| Type Check (mypy)  | ![Mypy](https://github.com/williaby/ledgerbase/actions/workflows/dev-checks.yml/badge.svg?branch=main) |
| Pre-commit Hooks   | ![Pre-commit](https://github.com/williaby/ledgerbase/actions/workflows/pre-commit.yml/badge.svg?branch=main) |
| Security - Bandit  | ![Bandit](https://github.com/williaby/ledgerbase/actions/workflows/security-bandit.yml/badge.svg?branch=main) |
| Security - Safety  | ![Safety](https://github.com/williaby/ledgerbase/actions/workflows/security-safety.yml/badge.svg?branch=main) |
| Security - Trivy   | ![Trivy](https://github.com/williaby/ledgerbase/actions/workflows/security-trivy.yml/badge.svg?branch=main) |
| Security - Secrets | ![Secrets](https://github.com/williaby/ledgerbase/actions/workflows/security-secrets.yml/badge.svg?branch=main) |
| pip-audit & License| ![pip-audit](https://github.com/williaby/ledgerbase/actions/workflows/security-pip-audit.yml/badge.svg?branch=main) |
| SBOM Scan          | ![SBOM](https://github.com/williaby/ledgerbase/actions/workflows/sbom.yml/badge.svg?branch=main) |
| License Scan       | ![License](https://github.com/williaby/ledgerbase/actions/workflows/license-scan.yml/badge.svg?branch=main) |
| Status Summary     | ![Summary](https://github.com/williaby/ledgerbase/actions/workflows/status-summary.yml/badge.svg?branch=main) |
