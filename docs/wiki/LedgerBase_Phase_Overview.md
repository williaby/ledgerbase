# LedgerBase – Phase Overview

This file outlines the 8 core development phases of the LedgerBase project, grouped by functionality and execution priority.

## Phase 1 – Core Infrastructure & Plaid ETL
Build Docker environment, initialize database and Flask app, integrate Plaid API, and prepare dev/test scaffolding.

## Phase 2 – Vendor Dictionary + Manual Categorization
Design the vendor identification system using regex and define UI for categorization and debt linking.

## Phase 3 – Budgeting System Core
Implement 2-level budget categories, rollover budgets, and per-month history tracking.

## Phase 4 – Unmatched Vendor Queue and Review Dashboard
Build queue interface to match new vendors, with suggestion engine and audit logging.

## Phase 5 – Business Expenses + Savings Logic
Add tagging for reimbursable business expenses, saving-based budgeting, and validation of actual savings balances.

## Phase 6 – Reporting & Person-Level Insights
Develop UI for monthly reports, variance tracking, and breakdowns by family member or tag.

## Phase 7 – Admin Tools, Importers, and CLI Utilities
Create CLI tools for imports and reviews, auto-table generation, and ETL modularization.

## Phase 8 – Final UI Polish, Deployment, and Automation
Role-based access, deployment pipeline, health checks, alerts, and post-MVP integrations.
