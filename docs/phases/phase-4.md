# Phase 4 – Unmatched Vendor Queue and Review Dashboard

**Goal**: Improve vendor assignment efficiency by centralizing unmatched transaction management and enabling pattern-based updates via a review interface.

---

## Milestone Tasks

| Task ID | Description                                                          | Status   |
|---------|----------------------------------------------------------------------|----------|
| #25     | Build unmatched vendor queue backend logic                           | [ ]      |
| #26     | Create `/review/unmatched` Flask route and template                  | [ ]      |
| #27     | Add review UI: vendor, category suggestions, and manual entry        | [ ]      |
| #28     | Create approval flow to update vendor_patterns table                 | [ ]      |
| #29     | Reprocess affected transactions on pattern approval                  | [ ]      |
| #30     | Add auto-suggestion engine for vendor matching (future ML hook)      | [ ]      |
| #31     | Track review history and approvals for audit trail                   | [ ]      |
| #32     | Write user guide: how to review and classify unmatched vendors       | [ ]      |

---

## Notes

- Suggestions may include fuzzy or keyword-based matching
- Reviewer actions should propagate only to unedited transactions
- Each approval should auto-trigger normalization with updated pattern
- Future ML module can extend the suggestion engine

---

## Directory Integration
