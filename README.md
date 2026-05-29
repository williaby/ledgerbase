
# LedgerBase

LedgerBase is a modular financial transaction classification and budgeting platform
designed for centralized, transparent, and analyzable financial recordkeeping. Built
with modern Python practices and cloud-native tools, it supports multi-account imports,
vendor classification, budget tracking, and reconciliation with actual savings.

## 🛡️ Security Workflow Status

| Workflow          | Status |
|-------------------|--------|
| Bandit            | ![Bandit](https://github.com/williaby/ledgerbase/actions/workflows/security-bandit.yml/badge.svg?branch=main) |
| pip-audit         | ![pip-audit](https://github.com/williaby/ledgerbase/actions/workflows/security-pip-audit.yml/badge.svg?branch=main) |
| Semgrep           | ![Semgrep](https://github.com/williaby/ledgerbase/actions/workflows/security-semgrep.yml/badge.svg?branch=main) |
| Snyk              | ![Snyk](https://github.com/williaby/ledgerbase/actions/workflows/security-snyk.yml/badge.svg?branch=main) |
| Trivy             | ![Trivy](https://github.com/williaby/ledgerbase/actions/workflows/security-trivy.yml/badge.svg?branch=main) |
| Safety            | ![Safety](https://github.com/williaby/ledgerbase/actions/workflows/safety.yml/badge.svg?branch=main) |

**Repository Scorecard:**
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/williaby/ledgerbase/badge)](https://securityscorecards.dev/viewer/?uri=github.com/williaby/ledgerbase)

---

## 🧩 Stack

- **Python 3.12+**
- **uv** – Dependency management
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
- uv (`pipx install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Clone the repository

```bash
git clone https://github.com/williaby/ledgerbase.git
cd ledgerbase
```

### Install dependencies

```bash
uv sync
```

### Run locally

```bash
uv run flask run
```

For detailed setup and architecture,
see [docs/setup-instructions.md](docs/setup-instructions.md).

---

## 🧪 Testing and Linting

```bash
uv run pytest
uv run ruff check src
uv run bandit -r src
uv run mypy src
```

Or run everything with:

```bash
pre-commit run --all-files
```

> Note: Ensure `pre-commit` is installed and initialized:
>
> ```bash
> uv run pre-commit install
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
