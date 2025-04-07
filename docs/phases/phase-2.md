# Phase 2 – Vendor Dictionary + Manual Categorization

**Goal**: Implement the vendor classification system, unmatched vendor queue, and manual categorization tools for enhanced data accuracy.

---

## Milestone Tasks

| Task ID | Description                                                    | Status   |
|---------|----------------------------------------------------------------|----------|
| #9      | Create `vendors` and `vendor_patterns` tables                  | [ ]      |
| #10     | Implement regex-based vendor matching in the ETL pipeline      | [ ]      |
| #11     | Build unmatched vendor queue UI in Flask                       | [ ]      |
| #12     | Allow vendor approval and auto-update to dictionary            | [ ]      |
| #13     | Add category-level editing and override capability             | [ ]      |
| #14     | Log vendor version history and pattern changes                 | [ ]      |
| #15     | Add label and comment fields to transactions_normalized        | [ ]      |
| #16     | Add filters in UI: unmatched, vendor, category, label, person  | [ ]      |

---

## Notes

- Regex rules may be tied to institutions if vendor format varies
- Each approved vendor match must automatically reprocess relevant transactions
- UI will support inline editing of labels, categories, and vendor associations
- Pattern updates should maintain an audit trail (future-proofing for ML support)

---

## Directory Integration
