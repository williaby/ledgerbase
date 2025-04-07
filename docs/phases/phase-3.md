# Phase 3 – Budgeting System Core

**Goal**: Build the core logic and UI for budget planning, comparison, and versioned budget tracking by category and month.

---

## Milestone Tasks

| Task ID | Description                                                        | Status   |
|---------|--------------------------------------------------------------------|----------|
| #17     | Create `budget_entries` schema for monthly category budgeting      | [ ]      |
| #18     | Build budget entry UI per month and category level 1/2             | [ ]      |
| #19     | Implement budget rollover logic and monthly cloning                | [ ]      |
| #20     | Compare monthly actuals vs. budgeted values                        | [ ]      |
| #21     | Support budget version history and manual override tracking        | [ ]      |
| #22     | Add budget health and savings deviation reporting                  | [ ]      |
| #23     | Create person-aware budget views (aggregated + filtered)           | [ ]      |
| #24     | Write documentation for budgeting model and assumptions            | [ ]      |

---

## Notes

- Budgets should clone automatically month-to-month unless manually changed
- Each entry includes `category_level1`, `category_level2`, `amount`, and `rollover` flag
- Transaction filtering for comparison must exclude transfers and income
- Person tagging helps explain outliers or special expenses within family categories

---

## Directory Integration
