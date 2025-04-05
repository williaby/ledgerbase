# LedgerBase Setup Instructions

These instructions ensure a smooth development start for LedgerBase. Complete before working on Issue #1.

---

## 1. Git Repository Initialization

- [ ] Clone repository using SSH:
  ```bash
  git clone git@github.com:williaby/ledgerbase.git
  ```

- [ ] Directory structure:
  ```
  ledgerbase/
  ├── docker/
  ├── app/               # Flask app
  ├── etl/               # ETL processors by institution
  ├── cli/               # Admin + setup CLI
  ├── notebooks/         # Jupyter notebooks
  ├── migrations/        # Alembic migrations
  ├── tests/
  ├── docs/
  ├── .env.example
  ├── docker-compose.yml
  ├── requirements.txt
  └── README.md
  ```

---

## 2. Environment Configuration

- [ ] Create `.env.example` file:
  ```dotenv
  FLASK_ENV=development
  POSTGRES_DB=ledgerbase
  POSTGRES_USER=ledger
  POSTGRES_PASSWORD=supersecure
  PLAID_CLIENT_ID=your_id_here
  PLAID_SECRET=your_sandbox_secret
  ```

- [ ] Do NOT commit your `.env`. Add to `.gitignore`.

---

## 3. Local Dev Tools

Install:
- Docker & Docker Compose
- Python 3.11+
- [ ] Pre-commit:  
  ```bash
  pip install pre-commit
  ```

---

## 4. Python Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 5. Pre-Commit Hook Setup (optional)

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
  - repo: https://github.com/pre-commit/mirrors-flake8
    rev: v4.0.1
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/mirrors-isort
    rev: v5.10.1
    hooks:
      - id: isort
```

Then:
```bash
pre-commit install
```

---

## 6. Git Ignore File

Recommended `.gitignore`:
```
.venv/
.env
__pycache__/
*.pyc
*.sqlite
migrations/
```

---

## 7. GitHub Repository Configuration

- Protect `main` branch
- Use `dev` for new feature development
- Enable Pull Requests even for solo projects for clarity
- Create Milestones for each Phase

---

## 8. First Commit

After confirming setup:
```bash
git add .
git commit -m "Initialize LedgerBase project structure and setup files"
git push origin main
```

You're now ready to begin **Issue #1**.