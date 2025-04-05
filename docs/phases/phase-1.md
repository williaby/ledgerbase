# Phase 1 – Core Infrastructure & Plaid ETL

**Goal**: Establish the foundational architecture and enable automated transaction ingestion using the Plaid API.

---

## Milestone Tasks

| Task ID | Description                                          | Status   |
|---------|------------------------------------------------------|----------|
| #1      | Initialize Docker Compose for PostgreSQL + Flask     | [ ]      |
| #2      | Define and Apply Initial Database Schema             | [ ]      |
| #3      | Implement Plaid API Integration for Wells Fargo      | [ ]      |
| #4      | Normalize Plaid Transactions to Internal Schema      | [ ]      |
| #5      | Store Access Tokens and Link Accounts                | [ ]      |
| #6      | Build Command-Line ETL Script                        | [ ]      |
| #7      | Test Plaid to DB Workflow End-to-End                 | [ ]      |
| #8      | Add Documentation for Setup + Plaid Integration      | [ ]      |

---

## Notes

- This milestone focuses on automation and core ingestion pipelines.
- All services are expected to be containerized and managed via Docker Compose.
- Flask is stubbed in this phase and will be expanded in Phase 2.
- Schema and token management must follow `.env`-driven configuration with no sensitive values committed.

---

## Directory Integration

