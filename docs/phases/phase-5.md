# Phase 5 – Business Expenses + Savings Logic

**Goal**: Extend transaction tagging for business reimbursements and build support for savings-based budget categories with rollover balances and actual reconciliation.

---

## Milestone Tasks

| Task ID | Description                                                            | Status   |
|---------|------------------------------------------------------------------------|----------|
| #33     | Add business expense tagging to transactions_normalized                | [ ]      |
| #34     | Build UI for tagging personal expenses as reimbursable                 | [ ]      |
| #35     | Generate monthly reimbursement report by vendor and person             | [ ]      |
| #36     | Create savings-based budget system with rollover allocation            | [ ]      |
| #37     | Add savings_accounts table and reconciliation logic                    | [ ]      |
| #38     | Link savings-based categories to current account balances              | [ ]      |
| #39     | Visualize budgeted vs. actual savings allocations over time            | [ ]      |
| #40     | Document logic: business reimbursements + savings reconciliation       | [ ]      |

---

## Notes

- Savings-based budgets accumulate unused amounts instead of resetting
- Business expenses are tagged and exported per user for reimbursement
- Reimbursement reports should include vendor, total, transaction count, and date range
- Savings logic must validate that account balances support cumulative allocations

---

## Directory Integration
