# Enhanced File Annotation & Docstring Specification v3

## Introduction

Consistent, clear documentation significantly enhances maintainability, collaboration,
onboarding, and automation capabilities. This guide defines mandatory requirements for
file headers and docstrings, along with recommended best practices and automation tools
to support compliance.

---

## Part 1: File Header Metadata (Mandatory)

Each source file (.py, .sh, .yml, .toml, etc.) **MUST** begin with structured metadata headers.

### 1.1 Supported Header Styles

| File Extension | Header Syntax | Example Prefix |
|----------------|---------------|----------------|
| .py            | ##:           | ##: name = example_script.py |
| .sh            | ##:           | ##: name = deploy.sh |
| .yml, .yaml    | #             | # name = config.yml |
| .toml          | #             | # name = pyproject.toml |

### 1.2 Metadata Fields (All Required)

All fields listed below are **mandatory**. If a field does not apply, use `none`
explicitly to preserve structure and enable tooling.

| Field          | Required | Description                                              | Example                                               |
|----------------|----------|----------------------------------------------------------|-------------------------------------------------------|
| name           | ✅ Yes   | File name or logical identifier.                         | ##: name = run_semgrep_modular.py                     |
| description    | ✅ Yes   | Summary of the file's primary purpose and functionality. | ##: description = Parallelized modular Semgrep runner |
| category       | ✅ Yes   | Grouping keyword (security, correctness, best-practice, performance, maintainability, or portability.).   | ##: category = security                               |
| usage          | ✅ Yes   | Usage instructions for scripts or CLIs.                  | ##: usage = python run_script.py [--verbose]          |
| behavior       | ✅ Yes   | High-level behavior or side effects.                     | ##: behavior = Emits SARIF reports                    |
| inputs         | ✅ Yes   | Key input files, env vars, or params.                    | ##: inputs = source code folders                      |
| outputs        | ✅ Yes   | Key outputs or side effects.                             | ##: outputs = sarif/*.sarif                           |
| dependencies   | ✅ Yes   | External libraries or tools.                             | ##: dependencies = Semgrep CLI                        |
| author         | ✅ Yes   | Primary maintainer.                                      | ##: author = Your Name                                |
| last_modified  | ✅ Yes   | Last modification date (YYYY-MM-DD).                     | ##: last_modified = {% now 'utc', '%Y-%m-%d' %}       |
| tags           | ⬜ Optional   | Keywords for grouping/searching.                         | ##: tags = security, automation                       |
| changelog      | ✅ Yes   | Historical context or versioning notes.                  | ##: changelog = Initial version, Added new validation |

> **Note:** All metadata fields are required. Use `none` if a specific field does not apply.
> This ensures uniformity and supports automation and documentation tooling.

### 1.3 Linting Compatibility

For Python files, append `# noqa: E265` to each metadata line to ensure Flake8/Ruff compatibility:

```python
##: name = example.py  # noqa: E265
```

### 1.4 Updating Guidelines

Metadata **MUST** be updated when significant file changes occur, including refactoring or interface updates.

---

## Part 2: Docstring Requirements (Mandatory)

All Python files (.py) **MUST** follow Google Python Style Guide for docstrings.

### 2.1 Module-Level Docstrings

Place immediately after file header metadata or imports.

```python
"""Module summary.

Detailed explanation of features, components, and usage.

Examples:
    >>> example_function()
    'Example Output'
"""
```

### 2.2 Class-Level Docstrings

```python
class ExampleClass:
    """Represents an example concept.

    Detailed description of responsibilities, behaviors, and use cases.

    Attributes:
        attr1 (str): Description.
        attr2 (int): Description.
    """
```

### 2.3 Function and Method Docstrings

```python
def example_function(param1, param2=0):
    """Calculate and return the result.

    Args:
        param1 (str): Description.
        param2 (int, optional): Description. Defaults to 0.

    Returns:
        bool: True if successful.

    Raises:
        ValueError: If `param1` is invalid.
    """
```

### 2.4 Documenting Exceptions and Edge Cases

Explicitly document any edge cases, boundary conditions, and conditional exceptions clearly.

---

## Part 3: Automation & Best Practices

### 3.1 Automated Validation Tools

Compliance enforced through pre-commit checks:

- Ruff, Black, Semgrep, Bandit, MyPy, markdownlint, doc8, detect-secrets, gitleaks, shellcheck
- Custom scripts for header metadata and docstring compliance.

### 3.2 Recommended Tagging Standards

Use standardized tags: security, refactor, deprecated, optimization, compliance.

---

## Part 4: FAQ & Common Pitfalls

- **When to document private methods?** Document if logic is complex or non-obvious.
- **Detail level for optional fields?** All fields are now required. Use `none` explicitly when a field doesn’t apply.
- **Handling internal vs public APIs?** Clearly differentiate expectations; internal APIs still need clarity for maintainability.

---

## Conclusion

Adherence to these guidelines ensures robust documentation, simplifies maintenance, and supports seamless collaboration.
