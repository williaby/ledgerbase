##: name = vulture_whitelist.py
##: description = Whitelist for Vulture to suppress false positives for unused code
##: category = maintainability
##: usage = Used automatically by Vulture during static analysis
##: behavior = Prevents Vulture from flagging intentionally unused code
##: inputs = none
##: outputs = none
##: dependencies = Vulture
##: author = LedgerBase Team
##: last_modified = 2023-11-15
##: changelog = Initial version

"""Vulture whitelist for suppressing false positives.

This module defines a list of symbols that are used dynamically or as entry points
in the codebase but might be flagged as unused by static analysis tools like Vulture.
By including these symbols in this whitelist, we prevent false positive reports
during code quality checks.
"""

_ = [
    # ─── Nox Session Entry Points ─────────────────────────────────────────────
    "tests",
    "coverage",
    "pre_commit",
    "check_lockfile",
    "lint",
    "ruff_fix",
    "isort",
    "autoflake",
    "mypy",
    "lint_rst",
    "vulture",
    "lint_other",

    # ─── Security & Compliance ────────────────────────────────────────────────
    "bandit_scan",
    "safety",
    "trivy",
    "sbom_validate",
    "license_report",
    "snyk_code",
    "snyk_oss",
    "snyk_container",
    "trufflehog",
    "ggshield",
    "semgrep_ci",
    "semgrep_full",
    "aikido_weekly_scan",
    "aikido_pr_scan",
    "aikido_usage_report",

    # ─── Dev & Utility Sessions ───────────────────────────────────────────────
    "fuzz",
    "build_docs",
    "gen_script_docs",
    "gen_master_index",
    "docker_build",
    "package_check",
    "list_security_sessions",

    # ─── Helpers Invoked Indirectly ───────────────────────────────────────────
    "load_env_from_sops",
    "check_docker",
    "get_repo_name",
    "get_branch_name",
    "get_poetry_dependencies",
    "discover_files",
    "install_poetry_and_deps",
    "require_tool",
    "ensure_reports",
]
