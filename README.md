# LedgerBase

![Lint](https://github.com/williaby/ledgerbase/actions/workflows/dev-checks.yml/badge.svg)
![Security Audit](https://github.com/williaby/ledgerbase/actions/workflows/security-deps-audit.yml/badge.svg)
![Trivy Scan](https://github.com/williaby/ledgerbase/actions/workflows/security-trivy.yml/badge.svg)
![Snyk Scan](https://github.com/williaby/ledgerbase/actions/workflows/security-snyk.yml/badge.svg)

LedgerBase is a modular financial transaction classification and budgeting platform
designed for centralized, transparent, and analyzable financial recordkeeping. Built
with modern Python practices and cloud-native tools, it supports multi-account imports,
vendor classification, budget tracking, and reconciliation with actual savings.

---

## 🧩 Stack

- **Python 3.12+**
- **Poetry** – Dependency management
- **Flask** – Backend API framework
- **PostgreSQL** – Primary data store
- **Docker Compose** – Container orchestration
- **GitHub Actions** – CI/CD
- **Bandit**, **Flake8**, **Mypy**, **Black**, **Isort** – Code quality and security
  checks

---

## 📦 Features

- ETL pipeline for importing and normalizing transactions
- Vendor dictionary with regex-based classification
- Budgeting system with historical and savings-based models
- Person-level tagging for family member analysis
- Reimbursement and savings account reconciliation
- Modular service structure for maintainability

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Poetry (`pip install poetry`)

### Clone the repository

```bash
git clone https://github.com/williaby/ledgerbase.git
cd ledgerbase
```

### Install dependencies

```bash
poetry install
```

### Run locally

```bash
poetry run flask run
```

For detailed setup and architecture,
see [docs/setup-instructions.md](docs/setup-instructions.md).

---

## 🧪 Testing and Linting

```bash
poetry run pytest
poetry run flake8
poetry run bandit -r src
poetry run mypy src
```

Or run everything with:

```bash
pre-commit run --all-files
```

> Note: Ensure `pre-commit` is installed and initialized:
> ```bash
> poetry run pre-commit install
> ```

---

## 🔐 Security

The project integrates static security analysis via:

- `Bandit` – Python vulnerability scanning
- `Trivy` – Docker image scanning
- `Snyk` – Dependency vulnerability scanning
- `detect-secrets` – Secret leak prevention

---

## 🛠️ Development

The codebase uses a modular layout under `src/ledgerbase/`. Each service (e.g.,
`plaid_service`, `etl`, `security`) follows single responsibility principles.

### Docker Compose

```bash
docker-compose up --build
```

Use the included `Dockerfile` in `src/flask/` for Flask containerization.

---

## 🧬 Contributing

We welcome contributions and suggestions! To get started:

1. Fork the repo
2. Create your branch: `git checkout -b feature/xyz`
3. Commit your changes: `git commit -am 'Add xyz'`
4. Push to the branch: `git push origin feature/xyz`
5. Create a pull request

Please ensure you run the full pre-commit suite and tests before submitting PRs.

---

## 🪪 License

MIT License. See [`LICENSE`](LICENSE) for details.

---

## 👤 Maintainer

**Byron Williams**
CPA
[GitHub: @williaby](https://github.com/williaby)
