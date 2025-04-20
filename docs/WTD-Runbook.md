# name = WTD-Runbook.md
# description = Documentation for the What The Diff PR summary feature in the ledgerbase project
# category = docs
# usage = Reference for developers to understand how the What The Diff PR summary feature works
# behavior = Explains the trigger conditions, diff filtering, and summary generation process
# inputs = none
# outputs = none
# dependencies = What-The-Diff CLI, GitHub token
# author = LedgerBase Team
# last_modified = 2023-11-15
# changelog = Initial version

# What The Diff PR Summaries Run‑Book

## 📖 Overview

Every pull request in **ledgerbase** now gets an AI‑generated summary via What The Diff. Summaries land as a single comment at the top of the PR, giving reviewers a quick overview of what's changed and why.

## 🛠️ How It Works

1. **Trigger**
    - Fires on PR open, reopen, or new commits.
    - Skips any PR authored by a bot (login ends with `[bot]`).
2. **Diff Filtering**

    - We ignore changes in `dist/`, `build/`, `vendor/`, lockfiles, and image assets to conserve token usage.
    - Additional exclusions managed via [`.gitattributes`](#diff-exclusions).

3. **Summary Generation**
    - Uses the official What The Diff CLI.
    - Posts one standalone comment per PR.

## ⚙️ Diff Exclusions (`.gitattributes`)

```gitattributes
dist/**           linguist-generated=true
build/**          linguist-generated=true
vendor/**         linguist-vendored=true
*.lock            linguist-vendored=true
*.png             linguist-generated=true
*.jpg             linguist-generated=true
```
