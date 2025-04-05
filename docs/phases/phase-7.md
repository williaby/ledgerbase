# Phase 7 – Admin Tools, Importers, and CLI Utilities

**Goal**: Add automation and convenience for managing vendors, accounts, and data ingestion. Extend the system with command-line and file-based workflows for faster interaction and debugging.

---

## Milestone Tasks

| Task ID | Description                                                             | Status   |
|---------|-------------------------------------------------------------------------|----------|
| #49     | Build CLI for importing transaction CSVs by account                     | [ ]      |
| #50     | Auto-detect institution format and normalize into central table         | [ ]      |
| #51     | Add CLI for managing vendor patterns (add, list, update, delete)        | [ ]      |
| #52     | Create admin route for reprocessing transactions by pattern or vendor   | [ ]      |
| #53     | Add debug tool to preview regex matches before applying to data         | [ ]      |
| #54     | Log all CLI actions to admin audit trail                                | [ ]      |
| #55     | Create import status table and file upload tracker                      | [ ]      |
| #56     | Document CLI usage and admin workflows                                  | [ ]      |

---

## Notes

- Tools should log actions with timestamps and user ID (if known)
- CLI tools must use shared internal modules from ETL/utility layer
- Pattern match preview enables safer edits to vendor definitions
- Reprocessing options help support backfills and corrections over time

---

## Directory Integration

