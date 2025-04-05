
# LedgerBase Project – Milestone Checklist

A full cross-phase implementation roadmap to monitor task progress.
Each item corresponds to a GitHub issue. Replace `#X` with actual issue numbers when created.

---

## Phase 1 – Core Infrastructure & Plaid ETL
- [ ] #1 Initialize Docker Compose for PostgreSQL + Flask
- [ ] #2 Define and Apply Initial Database Schema
- [ ] #3 Implement Plaid API Integration for Wells Fargo
- [ ] #4 Normalize Plaid Transactions to Internal Schema
- [ ] #5 Store Access Tokens and Link Accounts
- [ ] #6 Build Command-Line ETL Script
- [ ] #7 Test Plaid to DB Workflow End-to-End
- [ ] #8 Add Documentation for Setup + Plaid Integration

- [ ] #74 **(Phase 1)** See issue details.
## Phase 2 – Vendor Dictionary + Manual Categorization
- [ ] #9 Create `vendors` and `vendor_patterns` tables
- [ ] #10 Implement regex-based vendor matching
- [ ] #11 Build unmatched vendor queue UI
- [ ] #12 Allow vendor approval and auto-update to dictionary
- [ ] #13 Add category-level editing and override capability
- [ ] #14 Log vendor version history and pattern changes
- [ ] #15 Add label and comment fields
- [ ] #16 Add filters in UI: unmatched, vendor, label, person

- [ ] #65 **(Phase 2)** See issue details.
- [ ] #70 **(Phase 2)** See issue details.
## Phase 3 – Budgeting System Core
- [ ] #17 Create `budget_entries` schema
- [ ] #18 Build budget entry UI
- [ ] #19 Implement budget rollover and cloning logic
- [ ] #20 Compare actuals vs. budgets
- [ ] #21 Support versioning and override tracking
- [ ] #22 Add savings health and deviation reporting
- [ ] #23 Create person-aware budget views
- [ ] #24 Document budgeting model and assumptions

- [ ] #66 **(Phase 3)** See issue details.
- [ ] #72 **(Phase 3)** See issue details.
## Phase 4 – Unmatched Vendor Queue and Review Dashboard
- [ ] #25 Build unmatched vendor queue backend
- [ ] #26 Create Flask route for review interface
- [ ] #27 Add review UI for vendor and category suggestions
- [ ] #28 Create approval flow for vendor_patterns
- [ ] #29 Reprocess affected transactions
- [ ] #30 Auto-suggestion engine for vendor matching (future ML)
- [ ] #31 Track review history and audit log
- [ ] #32 Document vendor review and approval process

- [ ] #67 **(Phase 4)** See issue details.
- [ ] #71 **(Phase 4)** See issue details.
## Phase 5 – Business Expenses + Savings Logic
- [ ] #33 Add business expense tagging
- [ ] #34 Build UI for tagging reimbursable items
- [ ] #35 Generate reimbursement report
- [ ] #36 Create savings-based budget system
- [ ] #37 Add savings account tracking
- [ ] #38 Reconcile savings categories to account balances
- [ ] #39 Visualize budgeted vs. actual savings
- [ ] #40 Document business + savings tagging logic

## Phase 6 – Reporting & Person-Level Insights
- [ ] #41 Monthly budget vs. actual report
- [ ] #42 Add filters: category, label, person, type
- [ ] #43 Savings accumulation report
- [ ] #44 Per-person expense summary
- [ ] #45 Transaction drill-down from reports
- [ ] #46 Export reports to CSV/HTML
- [ ] #47 Schedule recurring monthly reports
- [ ] #48 Document all standard reports

- [ ] #69 **(Phase 6)** See issue details.
- [ ] #73 **(Phase 6)** See issue details.
## Phase 7 – Admin Tools, Importers, and CLI Utilities
- [ ] #49 CLI: CSV import by account
- [ ] #50 Auto-detect institution format
- [ ] #51 CLI: Vendor pattern manager
- [ ] #52 Admin reprocessing UI
- [ ] #53 Regex match debugger
- [ ] #54 CLI action audit logging
- [ ] #55 File import + upload status tracker
- [ ] #56 Document CLI utilities and admin workflows

## Phase 8 – Final UI Polish, Deployment, and Automation
- [ ] #57 Refactor and style UI templates
- [ ] #58 Create dashboard: budget + alerts
- [ ] #59 Docker production environment setup
- [ ] #60 Configure automated Plaid sync job
- [ ] #61 Deploy Cloudflare remote tunnel
- [ ] #62 Admin toggle UI for system config
- [ ] #63 End-to-end QA workflow validation
- [ ] #64 Deployment + operations manual
- [ ] #68 **(Phase 8)** See issue details.
