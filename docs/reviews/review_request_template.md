# LedgerBase – Issue Review Request

Thank you for helping review this issue implementation. This project has internal logic and specific data pipelines, so this template provides everything needed to assess a proposed change.

---

## Project Overview

**LedgerBase** is a self-hosted financial management and budgeting system for a family of six. It ingests bank and credit card transactions, categorizes expenses using a custom vendor dictionary, and tracks budgets, savings goals, debt payments, and individual expenses by person.

**Key Features**:

- Transaction import from Plaid or CSV
- Vendor pattern matching via regex
- 2-level budget categories + rollover savings logic
- Unmatched vendor queue with ML suggestions
- Person tagging (Byron, Veronica, Ariannah, etc.)
- Expense classification + business reimbursement tracking
- Docker-based deployment for Unraid
- Admin CLI and role-based review dashboard

---

## Issue Under Review

### Issue #[INSERT_ISSUE_NUMBER] – [INSERT_ISSUE_TITLE]

[Paste full issue markdown here]

---

## Review Expectations

Please evaluate the proposed code or solution using the following checklist:

- [ ] Does it **fully address the described issue**?
- [ ] Is the **logic accurate** (e.g., categorization, database design, budget math)?
- [ ] Is it **functional and testable** within the LedgerBase architecture (Flask + Postgres)?
- [ ] Are **edge cases considered** (e.g., new vendors, malformed data)?
- [ ] Does it respect the overall structure of the project and integrate cleanly?

---

## Optional Guidance for LLM Reviewers

If using an AI reviewer (e.g., ChatGPT or Copilot), consider asking:

- “Does the proposed function align with the described feature?”
- “What potential bugs or edge cases should be addressed?”
- “How could this code be made more testable or modular?”
- “Does this follow Flask and SQLAlchemy best practices?”

---

## Review Artifacts

- [ ] Link to relevant code snippet / PR / branch: `[insert GitHub link here]`
- [ ] Screenshots or logs (if applicable)
- [ ] Sample inputs/outputs (if data logic is involved)

---

Once you’ve reviewed the submission, you may:

- Approve the change
- Suggest improvements
- Flag blockers or concerns

Thank you for supporting quality in LedgerBase.
