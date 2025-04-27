---
title: "Enhanced File Annotation & Docstring Specification"
name: "annotation_spec.md"
description: >
  Defines the required structure for metadata front‑matter and docstrings across all project files.
category: docs
usage: "Reference for all project contributors when creating or modifying files"
behavior: "Defines standards for file documentation"
inputs: none
outputs: none
dependencies: none
author: "Byron Williams"
version: "2.0"
last_modified: "2023-11-15"
changelog: "Converted spec to YAML front-matter format and updated examples"
tags: [docs, specification]
---

## Enhanced File Annotation & Docstring Specification

## Purpose

This specification defines a unified approach to file metadata and docstrings, using YAML front‑matter across all text‑based source files (`.md`, `.py`, `.sh`, `.yml`, `.toml`). It improves clarity, onboarding, and automation compatibility.

## Part 1: YAML Front‑Matter Metadata (Mandatory)

All files **MUST** begin with a YAML block enclosed by `---` on the first lines. This block declares metadata consumed by documentation and validation tools.
Python files **MUST** have the front-matter embedded in the module docstring.

### 1.1 Required Fields

| Field          | Required | Description                                              | Example                                               |
|----------------|----------|----------------------------------------------------------|-------------------------------------------------------|
| name           | ✅ Yes   | File name or logical identifier.                         | name: "run_semgrep_modular.py"                        |
| description    | ✅ Yes   | Summary of the file's primary purpose and functionality. | description: "Parallelized modular Semgrep runner"    |
| category       | ✅ Yes   | Grouping keyword (e.g., security, performance).          | category: security                                    |
| usage          | ✅ Yes   | Usage instructions.                                      | usage: "python run_script.py [--verbose]"             |
| behavior       | ✅ Yes   | High-level behavior or side effects.                     | behavior: "Emits SARIF reports"                       |
| inputs         | ✅ Yes   | Key input files, env vars, or params.                    | inputs: "source code folders"                         |
| outputs        | ✅ Yes   | Key outputs or side effects.                             | outputs: "sarif/*.sarif"                              |
| dependencies   | ✅ Yes   | External libraries or tools.                             | dependencies: "Semgrep CLI"                           |
| author         | ✅ Yes   | Primary maintainer.                                      | author: "Your Name"                                   |
| last_modified  | ✅ Yes   | Last modification date (YYYY-MM-DD).                     | last_modified: "2023-11-15"                           |
| tags           | ⬜ Optional | Keywords for grouping/searching.                      | tags: [security, automation]                          |
| changelog      | ✅ Yes   | Historical context or versioning notes.                  | changelog: "Initial version, Added new validation"    |

> **Note:** Use `none` where a value does not apply to preserve structure and enable tooling.
> **Note:** If inputs includes "secrets:" then make sure to include "# pragma: allowlist secret" to avoid false positives
>
### 1.2 Example for Markdown (`.md`)

```md
---
# Front‑Matter for Markdown Page

title: "Project Overview"
name: "overview.md"
description: "Introduction to the LedgerBase project."
category: docs
usage: "Reference documentation for project overview"
behavior: "Provides high-level project information"
inputs: none
outputs: none
dependencies: none
author: "Byron Williams"
last_modified: "2023-11-15"
changelog: "Added front-matter migration guide"
tags: [docs, introduction]
---

# Project Overview
…
```

### 1.3 Example for Python (`.py`)

```python
#!/usr/bin/env python
"""
---
title: "Data Export Script"
name: "export_data.py"
description: "Exports ledger transactions to CSV."
category: script
usage: "python export_data.py [--format=csv]"
behavior: "Reads from database and writes to file system"
inputs: "Database connection parameters"
outputs: "CSV files in the output directory"
dependencies: "pandas, csv"
author: "Byron Williams"
last_modified: "2023-11-15"
changelog: "Initial migration to front-matter format"
tags: [export, data]
---

Core functionality for exporting transactions.
"""
import csv
…
```

## Part 2: Docstring Requirements (Python Only)

Follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) for all Python docstrings:

1. **Module docstring** immediately after front‑matter (or imports).
2. **Class docstrings** listing purpose and attributes.
3. **Function docstrings** with Args, Returns, Raises sections.

## Part 3: Validation & Automation

1. **Migration Script** (`tools/convert_headers.py`) to bulk‑convert old headers to front‑matter.
2. **Validation Hook** (`tools/check_front_matter.py`) integrated in pre‑commit:
   - Verifies presence and format of required fields.
   - Blocks commits on errors.

## FAQ & Pitfalls

- **Q:** Is front‑matter only for Markdown?
  **A:** No — it applies to any text file (`.py`, `.md`, `.sh`, `.yml`, `.toml`) that begins with a `---` block.

- **Q:** How to exempt binary or non‑text files?
  **A:** Only apply validation to supported extensions via pre‑commit patterns.

---

End of specification.
