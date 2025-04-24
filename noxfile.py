##: name = noxfile.py
##: description = Nox sessions for testing, linting, CI, and documentation generation in LedgerBase. # noqa: E501
##: category = dev
##: usage = nox [-s <session_name>] [-- <args>] (Default: lint,  autoflake, mypy, tests) # noqa: E501
##: behavior = Defines reusable Nox sessions for CI workflows including security scans and local development checks. Relies on Poetry for Python tool versions. # noqa: E501
##: dependencies = nox, poetry, docker, git, npm, wget, ggshield, twine
##: tags = ci, automation, testing, docs, security, linting, fuzzing, secrets, packaging
##: author = Byron Williams
##: last_modified = 2025-04-20 # Updated date

# LedgerBase - Nox Configuration
# Organized for CI, security, linting, testing, and utility automation

import functools
import json
import os
import shlex
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import ParamSpec, TypeVar

import nox
import nox.command
from nox.sessions import Session

P = ParamSpec("P")
R = TypeVar("R")


# Set default sessions to run when 'nox' is invoked without arguments
nox.options.sessions = ["lint", "mypy", "tests"]

# ─────────────────────────────────────────────────────────────────────────────
# Table of Contents
# ─────────────────────────────────────────────────────────────────────────────
# 1. Global Config & Setup
# 2. Core Development Sessions
# 3. Linting & Formatting Sessions
# 4. Security & Compliance Sessions
# 5. Fuzzing Session
# 6. Documentation & Artifact Sessions
# 7. Utility Sessions
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# 1. Global Config & Setup
# ─────────────────────────────────────────────────────────────────────────────

PYTHON_VERSIONS: list[str] = ["3.11", "3.12"]
LATEST: str = "3.12"
PACKAGE_DIR: str = "src/ledgerbase"
EXCLUDE_PATHS: set[str] = {
    ".nox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    ".git",
    "migrations",
    "scripts",
}
LINT_TARGETS: list[str] = ["src", "tests", "noxfile.py"]
MIN_COVERAGE: int = 90

# --- Tool Version Pinning (Hybrid Approach) ---
# Keep versions only for tools NOT primarily managed by Poetry/Renovate in pyproject.toml # noqa: E501
# or where specific pinning independent of pyproject.toml is desired for Nox runs.
TOOL_VERSIONS: dict[str, str] = {
    "poetry": "1.8.3",  # Poetry itself
    "safety-sarif": "1.2.0",  # Keep if installed separately via pip? Or add to pyproject? # noqa: E501
    "cifuzz": "latest",  # Placeholder for external tool
    "snyk": "latest",  # NPM package
    "semgrep": "1.75.0",  # Keep if installing via pip in Nox, remove if using external CLI # noqa: E501
    "yamllint": "1.35.1",  # Python tool, could be moved to pyproject? Keep for now.
    "prettier": "latest",  # NPM package
    "markdownlint-cli": "latest",  # NPM package
    "requests": "2.31.0",  # Used in Aikido report, could be dev dep. Keep for now.
    "shellcheck": "latest",  # for shell scripts
    "hadolint": "latest",  # for Dockerfiles
    "jq": "latest",  # for JSON linting
    "vale": "latest",  # for prose linting
    "taplo": "0.12.3",  # for TOML linting
}

# --- Report Directories ---
REPORT_DIR: Path = Path("docs/reports")
SARIF_DIR: Path = REPORT_DIR / "sarif"
JSON_DIR: Path = REPORT_DIR / "json"
XML_DIR: Path = REPORT_DIR / "xml"
TXT_REPORT_DIR: Path = REPORT_DIR / "txt"

# -- Semgrep Shared list of registry bundles (community + p-packs your plan supports)
SHARED_BUNDLES = [
    "r/python.flask",  # community-only
    "p/cwe-top-25",
    "p/security-audit",
    "p/secure-defaults",
    "p/r2c-best-practices",
    "p/owasp-top-ten",
    "p/sql-injection",
    "p/command-injection",
    "p/xss",
    "p/github-actions",
    "p/semgrep-misconfigurations",
    "p/ci",
    "p/semgrep-rule-lints",
    "p/semgrep-rule-ci",
]


# --- Helper Functions ---
# (ensure_reports, require_tool, install_poetry_and_deps, discover_files,
# load_env_from_sops,
#  check_docker, get_repo_name, get_branch_name, get_poetry_dependencies
#  functions remain the same)
def ensure_reports(
    *dirs_to_ensure: Path,
) -> Callable[
    [Callable[[Session, P], R]],
    Callable[[Session, P], R],
]:
    """Ensure report directories exist before running a session function."""
    def decorator(func: Callable[[Session, P], R]) -> Callable[[Session, P], R]:
        @functools.wraps(func)
        def wrapper(session: Session, *args: P.args, **kwargs: P.kwargs) -> R:
            for report_dir in dirs_to_ensure:
                report_dir.mkdir(parents=True, exist_ok=True)
            return func(session, *args, **kwargs)
        return wrapper
    return decorator


def require_tool(session: Session, tool_name: str) -> None:
    """Check if an external tool exists in the system's PATH."""
    session.log(f"Checking for tool: {tool_name}")
    if not shutil.which(tool_name):
        session.error(
            f"External tool '{tool_name}' not found in PATH. Please install it.",
        )


def install_poetry_and_deps(
    session: Session,
    *,
    with_dev: bool = True,
    no_root: bool = True,
) -> None:
    """Install Poetry and project dependencies using pinned Poetry version.
    Installs Poetry {TOOL_VERSIONS['poetry']}. Args: session: The Nox session object.
    with_dev: Whether to include development dependencies. no_root: If True, do not
    install the project package itself, only its dependencies. If False, install the
    project package along with dependencies (needed for tests/tools importing project code).
    """  # noqa: E501
    session.install(f"poetry=={TOOL_VERSIONS['poetry']}")
    command = ["poetry", "install"]
    groups = ["dev"]
    if no_root:
        command.append("--no-root")
    if with_dev:
        for group in groups:
            command.extend(["--with", group])
    else:
        command.extend(["--only", "main"])
    session.run(*command, silent=True)


def discover_files(
    root: str,
    extensions: list[str],
    exclude_dirs: set[str],
) -> list[str]:
    """Discover files with given extensions, excluding certain directories."""
    return [
        str(Path(dirpath) / file)
        for dirpath, _, filenames in os.walk(root)
        if not any(excluded in Path(dirpath).parts for excluded in exclude_dirs)
        for file in filenames
        if any(file.endswith(ext) for ext in extensions)
    ]


def load_env_from_sops(
    session: Session,
    path: str = "ledgerbase_secure_env/.env.dev",
) -> None:
    """Load environment variables from decrypted .env file (if exists).
    Check SNYK_TOKEN, AIKIDO_API_TOKEN.
    """
    env_path = Path(path)
    if not env_path.exists():
        session.warn(f"⚠️ Env file not found at {path}, skipping SOPS load.")
        return
    try:
        with env_path.open() as f:
            for line_content in f:
                stripped_line = line_content.strip()
                if (
                    stripped_line
                    and not stripped_line.startswith("#")
                    and "=" in stripped_line
                ):
                    key, val = stripped_line.split("=", 1)
                    session.env[key.strip()] = val.strip().strip('"').strip("'")
        session.log(f"Loaded environment variables from {path}")
    except OSError as e:
        session.warn(f"Failed to load environment variables from {path}: {e}")


def check_docker(session: Session) -> None:
    """Ensure Docker CLI is installed and the Docker daemon is running."""
    require_tool(session, "docker")
    try:
        session.run("docker", "version", external=True, silent=True)
        session.run("docker", "info", external=True, silent=True)
        session.log("Docker check passed.")
    except (subprocess.CalledProcessError, nox.command.CommandFailed) as e:
        session.error(
            f"Docker check failed: {e}\nDocker might not be installed, the daemon "
            f"isn't running, or the user lacks permissions.\nPlease install Docker "
            f"(https://docs.docker.com/get-docker/) and ensure the Docker daemon is "
            f"running before retrying.",
        )


def get_repo_name() -> str:
    """Get repository name from GITHUB_REPOSITORY or current directory."""
    repo = os.environ.get("GITHUB_REPOSITORY")
    return repo.split("/", 1)[1] if repo and "/" in repo else Path.cwd().name


def get_branch_name() -> str:
    """Get branch name from GITHUB_REF_NAME or local git command."""
    branch = os.environ.get("GITHUB_REF_NAME")
    if branch:
        return branch
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            text=True,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown-branch"


def get_poetry_dependencies(session: Session, *, include_dev: bool = True) -> list[str]:
    """Export dependencies from Poetry and return a list of package names."""
    req_file = Path(session.create_tmp()) / "poetry_deps.txt"
    export_cmd = [
        "poetry",  # nosec: B607 - Using Poetry from PATH is safe as it's a trusted tool
        "export",
        "--format=requirements.txt",
        f"--output={req_file}",
        "--without-hashes",  # nosec: B603 - All arguments are hardcoded or generated safely
    ]
    if include_dev:
        export_cmd.append("--with=dev")
    else:
        export_cmd.append("--only=main")
    # Try running poetry from session env first, fallback to external
    try:
        session.run(*export_cmd, external=False, silent=True)
    except nox.command.CommandFailed:
        session.log("Session poetry failed, trying external poetry...")
        session.run(*export_cmd, external=True, silent=True)
    packages = []
    if req_file.exists():
        with req_file.open() as f:
            for line_content in f:
                stripped_line = line_content.strip()
                if stripped_line and not stripped_line.startswith("#"):
                    pkg_name = (
                        stripped_line.split("==")[0]
                        .split(">=")[0]
                        .split("<=")[0]
                        .split("<")[0]
                        .split(">")[0]
                        .split("~=")[0]
                    )
                    packages.append(pkg_name.strip())
    return packages


AIKIDO_IMAGE = "aikidosecurity/local-scanner:latest"
TOKEN_ENV = "AIKIDO_API_TOKEN"


# ─────────────────────────────────────────────────────────────────────────────
# 2. Core Development Sessions
# ─────────────────────────────────────────────────────────────────────────────
@nox.session(python=PYTHON_VERSIONS, tags=["ci", "core"])
def tests(session: Session) -> None:
    """Run the test suite using pytest. Installs project and dev dependencies.
    Requires project code (`no_root=False`).
    """
    install_poetry_and_deps(session, with_dev=True, no_root=False)
    session.run("pytest", *session.posargs)


@nox.session(python=LATEST, tags=["ci", "core"])
@ensure_reports(XML_DIR)
def coverage(session: Session) -> None:
    """Run pytest with coverage and enforce minimum coverage level. Requires
    project code (`no_root=False`).
    """
    install_poetry_and_deps(session, with_dev=True, no_root=False)
    report_path = XML_DIR / "coverage.xml"
    session.run(
        "pytest",
        f"--cov={PACKAGE_DIR}",
        f"--cov-report=xml:{report_path}",
        "--cov-report=term",
        f"--cov-fail-under={MIN_COVERAGE}",
        "tests/",
        *session.posargs,
    )
    session.log(f"Coverage XML report generated at {report_path}")


@nox.session(python=LATEST, tags=["ci", "core"], reuse_venv=True)
def pre_commit(session: Session) -> None:
    """Run all pre-commit hooks on all files. Uses the pre-commit framework's installed
    hooks and environments.
    """
    session.install("pre-commit")
    session.run("pre-commit", "run", "--all-files", *session.posargs)


@nox.session(python=LATEST, tags=["ci", "core"], reuse_venv=True)
def check_lockfile(session: Session) -> None:
    """Verify that poetry.lock is consistent with pyproject.toml."""
    # Installs the specific poetry version used for checking
    session.install(f"poetry=={TOOL_VERSIONS['poetry']}")
    # Use the new recommended check command
    session.run("poetry", "check", "--lock")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Linting & Formatting Sessions
# ─────────────────────────────────────────────────────────────────────────────
@nox.session(python=PYTHON_VERSIONS, tags=["ci", "core", "linting"], reuse_venv=True)
def lint(session: Session) -> None:
    """Run Ruff linter (uses pyproject.toml, assumes 'I' ignored). Relies on ruff being installed via Poetry dev deps."""  # noqa: E501
    # Install project & dev deps, including ruff. Need full env (no_root=False) for entry points. # noqa: E501
    install_poetry_and_deps(session, with_dev=True, no_root=False)
    session.log("Running Ruff checks ")
    try:
        session.run("ruff", "check", *LINT_TARGETS, *session.posargs)
    except nox.command.CommandFailed:
        session.error("Ruff linting failed. Run 'nox -s ruff_fix' to apply auto-fixes.")


@nox.session(python=LATEST, tags=["core", "linting", "format"], reuse_venv=True)
def ruff_fix(session: Session) -> None:
    """Auto-fix Ruff lint issues  & format code with Ruff. Relies on ruff being installed via Poetry dev deps."""  # noqa: E501
    install_poetry_and_deps(session, with_dev=True, no_root=False)
    targets = LINT_TARGETS + session.posargs
    session.log("Running Ruff auto-fix ...")
    session.run("ruff", "check", *targets, "--fix", "--exit-zero")
    session.log("Running Ruff formatter...")
    session.run("ruff", "format", *targets)


@nox.session(python=PYTHON_VERSIONS, tags=["ci", "core", "linting"], reuse_venv=True)
def mypy(session: Session) -> None:
    """Perform static type checking using Mypy (uses pyproject.toml). Needs project
    installed. Relies on mypy being installed via Poetry dev deps.
    """
    install_poetry_and_deps(session, with_dev=True, no_root=False)
    session.run("mypy", *session.posargs if session.posargs else [PACKAGE_DIR])


@nox.session(python=LATEST, tags=["ci", "docs", "linting"], reuse_venv=True)
def lint_rst(session: Session) -> None:
    """Lint reStructuredText files using sphinx-lint. Needs project installed. Relies
    on sphinx-lint being installed via Poetry dev deps.
    """
    install_poetry_and_deps(session, with_dev=True, no_root=False)
    rst_dirs_or_files = ["docs/source"]
    session.log("🔍 Running sphinx-lint on RST files...")
    try:
        session.run("sphinx-lint", *rst_dirs_or_files, *session.posargs)
    except nox.command.CommandFailed as e:
        session.warn(f"sphinx-lint found issues: {e}")


@nox.session(python=LATEST, tags=["ci", "linting"], reuse_venv=True)
def vulture(session: Session) -> None:
    """Scan for unused code using vulture.
    - Skips noxfile.py (dynamic usage).
    - Uses whitelist + higher confidence to reduce false positives.
    """
    install_poetry_and_deps(session, with_dev=True, no_root=False)

    scan_paths = [
        p for p in LINT_TARGETS if not p.endswith("noxfile.py")
    ] + session.posargs
    if not scan_paths:
        session.error("No valid paths to scan.")

    whitelist = Path("vulture_whitelist.py")
    if whitelist.exists():
        scan_paths.insert(0, str(whitelist))
        session.log(f"🛡️ Using whitelist: {whitelist}")

    session.log("🔍 Running vulture (min-confidence=90)...")
    try:
        session.run("vulture", *scan_paths, "--min-confidence", "90")
    except nox.command.CommandFailed:
        session.warn("Vulture found potential dead code.")


# ─────────────────────────────────────────────────────────────────────────────
# Additional Linting Sessions
# ─────────────────────────────────────────────────────────────────────────────


@nox.session(python=False, tags=["ci", "linting"])
def shellcheck(session: Session) -> None:
    """Lint all shell scripts in /scripts with ShellCheck."""
    require_tool(session, "shellcheck")
    scripts = discover_files("scripts", [".sh"], EXCLUDE_PATHS)
    if not scripts:
        session.log("No shell scripts found to lint.")
        return
    session.log("🔍 Running ShellCheck…")
    session.run("shellcheck", *scripts, external=True)


@nox.session(python=False, tags=["ci", "linting", "docker"])
def hadolint(session: Session) -> None:
    """Lint Dockerfiles using Hadolint."""
    require_tool(session, "hadolint")
    dockerfiles = [str(p) for p in Path().glob("Dockerfile*")]
    if not dockerfiles:
        session.log("No Dockerfiles found to lint.")
        return
    session.log("🔍 Running Hadolint…")
    session.run("hadolint", *dockerfiles, "-c", ".hadolint.yaml", external=True)


@nox.session(python=LATEST, tags=["ci", "linting"])
def sqlfluff(session: Session) -> None:
    """Lint SQL files (e.g. in migrations) with SQLFluff."""
    # install into venv so we can pin a version if desired
    session.install("sqlfluff")
    sqls = discover_files("migrations", [".sql"], EXCLUDE_PATHS)
    if not sqls:
        session.log("No SQL files found to lint.")
        return
    session.log("🔍 Running SQLFluff lint…")
    # you can set dialect via CLI (--dialect postgres/mysql/etc)
    session.run("sqlfluff", "lint", *sqls)


@nox.session(python=False, tags=["ci", "linting"])
def jsonlint(session: Session) -> None:
    """Validate all JSON files with jq."""
    require_tool(session, "jq")
    jsons = discover_files(".", [".json"], EXCLUDE_PATHS)
    if not jsons:
        session.log("No JSON files found to lint.")
        return
    session.log("🔍 Running jq --exit-status…")
    for f in jsons:
        session.run("jq", "--exit-status", ".", f, external=True)


@nox.session(python=False, tags=["ci", "linting"])
@ensure_reports(TXT_REPORT_DIR)  # Ensure the specific txt report directory exists
def prose(session: Session) -> None:
    """Lint documentation prose with Vale.
    Outputs report to docs/reports/txt/vale_report.txt and forces exit code 0.
    """
    require_tool(session, "vale")

    # Define the output report path within the new directory
    report_path = TXT_REPORT_DIR / "vale_report.txt"

    # Discover files (using the existing discover_files function and EXCLUDE_PATHS)
    # Ensure 'discover_files' and 'EXCLUDE_PATHS' are defined in your noxfile
    docs_to_check = discover_files("docs", [".md", ".rst"], EXCLUDE_PATHS)
    if not docs_to_check:
        session.log("No docs found to lint.")
        return

    session.log(f"🔍 Running Vale prose linter, outputting report to {report_path}...")

    # Run Vale with --no-exit and --output flags pointing to the new location
    # Use success_codes=[0] because --no-exit forces Vale to always return 0.
    session.run(
        "vale",
        "--no-exit",  # Force exit code 0
        f"--output={report_path}",  # Specify output file
        *docs_to_check,  # Pass the discovered document paths
        external=True,
        success_codes=[0],  # Explicitly define success code for nox
    )
    session.log(f"Vale report generated at {report_path}")
    session.log("Note: Vale session forced to succeed. Check report file for issues.")


@nox.session(python=LATEST, tags=["ci", "linting"], reuse_venv=True)
def lint_other(session: Session) -> None:
    """Run linting/formatting on YAML, Markdown, and check for typos. Uses external npm
    tools and Python tools installed via Poetry dev deps.
    """
    install_poetry_and_deps(
        session,
        with_dev=True,
        no_root=False,
    )  # Install python deps like codespell
    session.install(
        f"yamllint=={TOOL_VERSIONS['yamllint']}",
    )  # Keep yamllint install for now unless moved to pyproject
    require_tool(session, "npm")
    session.run(
        "npm",
        "install",
        "-g",
        f"prettier@{TOOL_VERSIONS['prettier']}",
        f"markdownlint-cli@{TOOL_VERSIONS['markdownlint-cli']}",
        external=True,
        silent=True,
    )
    yaml_files = discover_files(".", [".yaml", ".yml"], EXCLUDE_PATHS)
    if yaml_files:
        session.log("🔍 Running Prettier (format) + Yamllint on YAML files...")
        require_tool(session, "prettier")
        session.run("prettier", "--write", *yaml_files, external=True)
        session.run(
            "yamllint",
            "-f",
            "parsable",
            *yaml_files,
        )  # Runs installed yamllint
    else:
        session.log("No YAML files found.")
    md_files = discover_files(".", [".md"], EXCLUDE_PATHS)
    if md_files:
        session.log("🔍 Running Prettier (format) + Markdownlint...")
        require_tool(session, "prettier")
        require_tool(session, "markdownlint")
        session.run("prettier", "--write", *md_files, external=True)
        session.run("markdownlint", "--fix", *md_files, external=True)
    else:
        session.log("No Markdown files found.")
    session.log("🔍 Running codespell for typos...")
    codespell_targets = [
        "src",
        "docs",
        "tests",
        ".",
        "README.md",
        "CONTRIBUTING.md",
        "noxfile.py",
    ]
    existing_targets = [t for t in codespell_targets if Path(t).exists()]
    if existing_targets:
        session.run(
            "codespell",
            *existing_targets,
        )  # Runs codespell installed via poetry
    else:
        session.log("No targets found for codespell.")


@nox.session(python=False, tags=["ci", "linting"])
def taplo(session: Session) -> None:
    """Lint & format all TOML files with Taplo."""
    require_tool(session, "taplo")
    toml_files = discover_files(".", [".toml"], EXCLUDE_PATHS)
    if not toml_files:
        session.log("No TOML files found to lint/format.")
        return

    session.log("🔍 Checking TOML syntax & style…")
    session.run("taplo", "check", *toml_files, external=True)

    session.log("🔧 Formatting TOML files in-place…")
    session.run("taplo", "format", "--write", *toml_files, external=True)


@nox.session(python=PYTHON_VERSIONS, tags=["ci", "linting"])
def lint_all(session: Session) -> None:
    """Composite lint session: runs all code, style, shell, Docker, SQL,
    JSON and prose linters in one go.
    """
    # Order matters: cleanup → import ordering → style → docs → scripts
    for name in [
        "lint",  # Ruff checks
        "lint_other",  # Prettier → Yamllint/Markdownlint → codespell
        "lint_rst",
        "shellcheck",
        "hadolint",
        "sqlfluff",
        "jsonlint",
        "taplo",
        "prose",
    ]:
        session.log(f"▶️  Running {name}…")
        # invoke each session in turn
        session.run("nox", "-s", name, external=True)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Security & Compliance Sessions
# ─────────────────────────────────────────────────────────────────────────────
@nox.session(python=LATEST, tags=["ci", "security"], reuse_venv=True)
@ensure_reports(SARIF_DIR)  # Only need SARIF_DIR now
def bandit_scan(session: Session) -> None:
    """Run Bandit SAST scanner.
    Relies on bandit and bandit-sarif-formatter installed via Poetry dev deps.
    Generates a SARIF report.
    """
    # Install bandit & bandit-sarif-formatter via dev dependencies
    install_poetry_and_deps(session, with_dev=True, no_root=False)

    # Define the SARIF report path
    sarif_path = SARIF_DIR / "bandit.sarif"

    # Run bandit, outputting directly to SARIF format
    # The bandit-sarif-formatter package enables the 'sarif' format option
    session.run(
        "bandit",
        "-r",  # Recursive scan
        PACKAGE_DIR,  # Target directory
        "-f",  # Format flag
        "sarif",  # Specify SARIF format
        "-o",  # Output flag
        str(sarif_path),  # Output path
        *session.posargs,  # Pass any additional arguments
    )
    session.log(f"Bandit SARIF report generated at {sarif_path}")


@nox.session(python=LATEST, tags=["ci", "security"], reuse_venv=True)
@ensure_reports(JSON_DIR)  # Revert to ensuring JSON_DIR
def safety(session: Session) -> None:
    """Scan dependencies for vulnerabilities using Safety.
    Relies on safety installed via Poetry dev deps. Generates a JSON report.
    """
    install_poetry_and_deps(session, with_dev=True, no_root=False)

    # Define the JSON report path
    json_path = JSON_DIR / "safety_output.json"  # Use JSON path again
    requirements_path = Path(session.create_tmp()) / "requirements.txt"

    session.run(
        "poetry",
        "export",
        "--format=requirements.txt",
        f"--output={requirements_path}",
        "--with=dev",
        "--without-hashes",
        external=False,
    )

    try:
        # Specify JSON format AND use --save-json for the output file
        session.run(
            "safety",
            "check",
            f"--file={requirements_path}",
            "--output",
            "json",  # Select JSON format type
            "--save-json",
            str(json_path),  # Specify the output file path
            # '--full-report', # Add back if desired and compatible
            *session.posargs,
        )
        session.log(f"Safety JSON report generated at {json_path}")
    except nox.command.CommandFailed as e:
        session.warn(f"Safety check failed: {e}")


@nox.session(reuse_venv=True, tags=["ci", "security", "docker"])
@ensure_reports(JSON_DIR, SARIF_DIR)
def trivy(session: Session) -> None:
    """Run Trivy vulnerability scanner on Docker image. Requires external Docker & Trivy CLI tools."""  # noqa: E501
    check_docker(session)
    require_tool(session, "trivy")
    image_tag = session.posargs[0] if session.posargs else f"{get_repo_name()}:latest"
    sarif_path = SARIF_DIR / "trivy-results.sarif"
    json_path = JSON_DIR / "trivy-results.json"
    session.log(f"Building Docker image: {image_tag}")
    session.run("docker", "build", "-t", image_tag, ".", external=True)
    session.log(f"Scanning image {image_tag} with Trivy...")
    session.run(
        "trivy",
        "image",
        "--format",
        "sarif",
        "--output",
        str(sarif_path),
        "--exit-code",
        "0",
        "--ignore-unfixed",
        "--severity",
        "HIGH,CRITICAL",
        image_tag,
        external=True,
    )
    session.log(f"Trivy SARIF report generated at {sarif_path}")
    session.run(
        "trivy",
        "image",
        "--format",
        "json",
        "--output",
        str(json_path),
        "--exit-code",
        "0",
        "--ignore-unfixed",
        "--severity",
        "HIGH,CRITICAL",
        image_tag,
        external=True,
    )
    session.log(f"Trivy JSON report generated at {json_path}")


@nox.session(python=False, tags=["ci", "security"])
def sbom_validate(session: Session) -> None:
    """Generate SBOM (CycloneDX format) with Trivy and validate it. Requires external
    Docker, Trivy, and Wget tools.
    """
    check_docker(session)
    require_tool(session, "trivy")
    require_tool(session, "wget")
    image_tag = f"{get_repo_name()}:sbom-build"
    output_dir = Path("docs/generated/sbom")
    output_dir.mkdir(parents=True, exist_ok=True)
    sbom_path = output_dir / "sbom.cdx.json"
    session.log(f"Building Docker image for SBOM generation: {image_tag}")
    session.run("docker", "build", "-t", image_tag, ".", external=True)
    session.log(f"Generating SBOM for {image_tag}...")
    session.run(
        "trivy",
        "image",
        image_tag,
        "--format",
        "cyclonedx",
        "--output",
        str(sbom_path),
        external=True,
    )
    session.log(f"SBOM generated at {sbom_path}")
    cyclonedx_cli_path = Path("./cyclonedx")
    if not cyclonedx_cli_path.exists():
        session.log("Downloading CycloneDX CLI...")
        session.run(
            "wget",
            "-q",
            "https://github.com/CycloneDX/cyclonedx-cli/releases/latest/download/cyclonedx-linux-x64",
            "-O",
            str(cyclonedx_cli_path),
            external=True,
        )
        session.run("chmod", "+x", str(cyclonedx_cli_path), external=True)
    session.log(f"Validating SBOM file: {sbom_path}")
    session.run(
        str(cyclonedx_cli_path),
        "validate",
        "--input-file",
        str(sbom_path),
        "--input-format",
        "json",
        external=True,
    )
    session.log("SBOM validation complete.")


@nox.session(python=LATEST, tags=["ci", "security"], reuse_venv=True)
@ensure_reports(JSON_DIR)
def license_report(session: Session) -> None:
    """Generate dependency license report using pip-licenses. Relies on pip-licenses
    installed via Poetry dev deps. Uses explicit dependency list.
    """
    install_poetry_and_deps(
        session,
        with_dev=True,
        no_root=False,
    )  # Install pip-licenses & poetry
    json_path = JSON_DIR / "license-report.json"
    disallowed_path = JSON_DIR / "disallowed-licenses.txt"
    dependencies_to_check = get_poetry_dependencies(session, include_dev=True)
    if not dependencies_to_check:
        session.error("Could not retrieve dependency list from Poetry.")
    session.run(
        "pip-licenses",
        "--format=json",
        f"--output-file={json_path}",
        "--with-authors",
        "--with-urls",
        "--packages",
        *dependencies_to_check,
        *session.posargs,
    )
    if not json_path.exists():
        session.error(f"License report file not found at {json_path}.")
        return
    session.log(f"License report generated at {json_path}")
    try:
        with json_path.open() as f:
            licenses = json.load(f)
    except json.JSONDecodeError:
        session.error(f"Failed to parse license report JSON file: {json_path}")
        return
    allowed_licenses = {"MIT", "BSD", "Apache-2.0", "ISC", "Python-2.0"}
    disallowed = [
        (f"{pkg.get('Name', 'Unknown')} ({pkg.get('Version', 'N/A')}) - "
         f"License: {pkg.get('License', 'Unknown')}")
        for pkg in licenses
        if pkg.get("License", "UNKNOWN") not in allowed_licenses
    ]
    if disallowed:
        session.warn(
            f"Found {len(disallowed)} packages with disallowed or unknown licenses:",
        )
        with disallowed_path.open("w") as out:
            for item in disallowed:
                session.log(f"  - {item}")
                out.write(f"{item}\n")
        session.log(f"List saved to {disallowed_path}")
    else:
        session.log("All dependency licenses are compliant with the allowed list.")
        if disallowed_path.exists():
            disallowed_path.unlink()


@nox.session(name="snyk_code")
def snyk_code(session: nox.Session) -> None:
    """Run Snyk Code scan and save results as SARIF, fail only for
    high/critical issues.
    """
    sarif_path = Path("docs/reports/sarif/snyk-code.sarif")
    session.log("📦 Installing/Updating Snyk CLI...")
    session.run("npm", "install", "-g", "snyk@latest", external=True)

    session.log("🔐 Authenticating Snyk CLI...")
    session.run("snyk", "auth", os.environ["SNYK_TOKEN"], external=True)

    session.log("🧪 Running Snyk Code scan...")
    result = subprocess.run(
        ["snyk", "code", "test", "--sarif"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        text=True,
    )

    # Write stdout to SARIF file
    sarif_path.parent.mkdir(parents=True, exist_ok=True)
    sarif_path.write_text(result.stdout, encoding="utf-8")

    session.log(f"✔️ Snyk SARIF saved: {sarif_path}")

    # Check severity
    if (
        '"level": "error"' in result.stdout
        or '"level": "high"' in result.stdout
        or '"level": "critical"' in result.stdout
    ):
        session.error("❌ High or critical issues detected in Snyk Code scan.")
    else:
        session.log("✅ Only low/medium/warning level issues found.")


@nox.session(python=LATEST, tags=["ci", "security"], reuse_venv=True)
@ensure_reports(SARIF_DIR)
def snyk_oss(session: nox.Session) -> None:
    """Run Snyk Open Source (SCA) scan and save results as SARIF, fail only for
    high/critical issues.
    """
    token = os.environ.get("SNYK_TOKEN")
    if not token:
        session.error("Missing required SNYK_TOKEN environment variable.")

    # Install dependencies so Snyk can scan them
    install_poetry_and_deps(session, with_dev=True, no_root=False)

    sarif_path = SARIF_DIR / "snyk-oss.sarif"

    session.log("📦 Installing/Updating Snyk CLI...")
    session.run("npm", "install", "-g", f"snyk@{TOOL_VERSIONS['snyk']}", external=True)

    session.log("🔐 Authenticating Snyk CLI...")
    session.run("snyk", "auth", token, external=True)

    session.log("🧪 Running Snyk OSS scan...")
    result = subprocess.run(
        ["snyk", "test", "--sarif"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        text=True,
    )

    # Write stdout (SARIF) to file
    sarif_path.parent.mkdir(parents=True, exist_ok=True)
    sarif_path.write_text(result.stdout, encoding="utf-8")
    session.log(f"✔️ Snyk SARIF saved: {sarif_path}")

    # Fail only on high/critical
    if '"level": "high"' in result.stdout or '"level": "critical"' in result.stdout:
        session.error("❌ High or critical issues detected in Snyk OSS scan.")
    else:
        session.log("✅ Only low/medium/warning level issues found.")


@nox.session(reuse_venv=True, tags=["ci", "security", "docker"])
@ensure_reports(SARIF_DIR)
def snyk_container(session: nox.Session) -> None:
    """Run Snyk Container scan and save results as SARIF, fail only for
    high/critical issues.
    """
    token = os.environ.get("SNYK_TOKEN")
    if not token:
        session.error("Missing required SNYK_TOKEN environment variable.")

    image_tag = session.posargs[0] if session.posargs else f"{get_repo_name()}:latest"
    sarif_path = SARIF_DIR / "snyk-container.sarif"

    session.log(f"📦 Building Docker image: {image_tag}")
    session.run("docker", "build", "-t", image_tag, ".", external=True)

    session.log("📦 Installing/Updating Snyk CLI...")
    session.run("npm", "install", "-g", f"snyk@{TOOL_VERSIONS['snyk']}", external=True)

    session.log("🔐 Authenticating Snyk CLI...")
    session.run("snyk", "auth", token, external=True)

    session.log(f"🧪 Running Snyk Container scan on {image_tag}...")
    subprocess.run(
        [
            "snyk",
            "container",
            "test",
            image_tag,
            "--file=Dockerfile",
            f"--sarif-file-output={sarif_path}",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        text=True,
    )

    session.log(f"✔️ Snyk SARIF saved: {sarif_path}")
    sarif_contents = sarif_path.read_text(encoding="utf-8")

    # Fail only on high/critical
    if '"level": "high"' in sarif_contents or '"level": "critical"' in sarif_contents:
        session.error("❌ High or critical issues detected in Snyk Container scan.")
    else:
        session.log("✅ Only low/medium/warning level issues found.")


@nox.session(python=False, tags=["ci", "security", "secrets"])
def ggshield(session: Session) -> None:
    """Scan for secrets using GitGuardian ggshield. Requires external ggshield CLI and
    GITGUARDIAN_API_KEY env var.
    """
    require_tool(session, "ggshield")
    api_key = os.environ.get("GITGUARDIAN_API_KEY")
    if not api_key:
        session.warn(
            "GITGUARDIAN_API_KEY environment variable not set. Scan may fail or"
            " be limited.",
        )
    scan_cmd = ["ggshield"] + (session.posargs if session.posargs else ["scan", "ci"])
    session.log("Running GitGuardian ggshield scan...")
    try:
        session.run(*scan_cmd, external=True)
        session.log("ggshield scan passed.")
    except nox.command.CommandFailed as e:
        session.error(f"ggshield scan failed: {e}. Check output and API key.")


@nox.session(python=LATEST, reuse_venv=True, tags=["ci", "security"])
@ensure_reports(SARIF_DIR)
def semgrep_ci(session: Session) -> None:
    """Run Semgrep SAST scan in 'ci' mode (diff-aware). Requires external Semgrep CLI.
    Uploads results if SEMGREP_APP_TOKEN set.
    """
    sarif_path = SARIF_DIR / "semgrep-ci.sarif"
    _run_semgrep(session, mode="ci", sarif_path=sarif_path)


@nox.session(python=LATEST, reuse_venv=True, tags=["ci", "security"])
@ensure_reports(SARIF_DIR)
def semgrep_full(session: Session) -> None:
    """Run a full Semgrep SAST repository scan. Requires external Semgrep CLI."""
    sarif_path = SARIF_DIR / "semgrep_full.sarif"
    _run_semgrep(session, mode="scan", sarif_path=sarif_path)


def _run_semgrep(session: Session, mode: str, sarif_path: Path) -> None:
    """Install Semgrep into the venv, then run with server-side bundles +
    custom rules.
    """
    # 1) ensure the Python package is present
    session.install("--upgrade-strategy", "eager", "semgrep==1.119.0")

    # 2) build the CLI args
    args: list[str] = [
        mode,
        "--jobs",
        "4",
        "--sarif",  # shorthand for --format=sarif
        "--output",
        str(sarif_path),
    ]
    # 3) add one --config per registry bundle
    for bundle in SHARED_BUNDLES:
        args += ["--config", bundle]

    # 4) still load your custom rules on top
    args += ["--config", "custom-rules.yml"]

    # 5) if doing a full scan, target the repo root
    if mode == "scan":
        args.append(".")

    # 6) run
    session.log(f"▶️  semgrep {' '.join(args)}")
    session.run("semgrep", *args)  # runs in the venv you just installed into
    session.log(f"✅ Semgrep SARIF report saved to {sarif_path}")


# ─────────────────────────────────────────────────────────────────────────────
# 5. Fuzzing Session
# ─────────────────────────────────────────────────────────────────────────────
@nox.session(python=LATEST, tags=["security", "fuzzing"], reuse_venv=True)
def fuzz(session: Session) -> None:
    """Build and run fuzzers locally using CIFuzz (requires external setup). Assumes
    CIFuzz CLI is installed and configured externally.
    """
    session.log("Attempting to build and run fuzzers locally with CIFuzz...")
    session.log("Ensure CIFuzz environment is set up (e.g., Docker, prerequisites).")
    require_tool(session, "cifuzz")
    session.log("Building fuzzers...")
    session.run("cifuzz", "build", *session.posargs, external=True)
    session.log("Running fuzzers (example: requires specifying target(s))...")
    session.warn("Fuzz session requires specifying target(s) via positional args.")
    session.warn("Example: nox -s fuzz -- <fuzzer_name> -- <libfuzzer_args>")


# ─────────────────────────────────────────────────────────────────────────────
# 6. Documentation & Artifact Sessions
# ─────────────────────────────────────────────────────────────────────────────
@nox.session(python=LATEST, tags=["ci", "docs"])
def build_docs(session: Session) -> None:
    """Build HTML & PDF docs using Sphinx. Installs project & dev dependencies.
    Uses '-- --strict' for warnings-as-errors. Requires external 'make' and LaTeX tools.
    """
    strict_mode = "--strict" in session.posargs
    install_poetry_and_deps(
        session,
        with_dev=True,
        no_root=False,
    )  # Needs Sphinx & project
    common_args = ["-a", "-j", "auto"]
    require_tool(session, "make")
    if strict_mode:
        session.log("Building docs strict...")
        common_args.extend(["-W", "--keep-going"])
    else:
        session.log("Building docs...")
        common_args.append("-n")
    html_build_dir = Path("docs/build/html")
    session.run(
        "sphinx-build",
        "-b",
        "html",
        *common_args,
        "docs/source",
        str(html_build_dir),
    )
    session.log(f"HTML documentation built at {html_build_dir}")
    latex_build_dir = Path("docs/build/latex")
    try:
        session.run(
            "sphinx-build",
            "-b",
            "latex",
            *common_args,
            "docs/source",
            str(latex_build_dir),
        )
        session.log(f"LaTeX files built at {latex_build_dir}. Running make...")
        session.run("make", "-C", str(latex_build_dir), "all-pdf", external=True)
        session.log(f"PDF documentation built in {latex_build_dir}")
    except nox.command.CommandFailed as e:
        session.warn(f"PDF build failed: {e}. Ensure LaTeX & make installed.")


@nox.session(python=LATEST, tags=["ci", "docs", "util"], reuse_venv=True)
def gen_script_docs(session: Session) -> None:
    """Generate markdown documentation from shell script headers via script."""
    script_path = Path("scripts/generate_script_docs.py")
    if script_path.exists():
        session.log(f"Running script: {script_path}")
        session.run("python", str(script_path), *session.posargs)
    else:
        session.warn(f"Script not found: {script_path}, skipping.")


@nox.session(python=LATEST, tags=["ci", "docs", "util"], reuse_venv=True)
def gen_master_index(session: Session) -> None:
    """Generate the top-level documentation index file via script."""
    script_path = Path("scripts/generate_master_index.py")
    if script_path.exists():
        session.log(f"Running script: {script_path}")
        session.run("python", str(script_path), *session.posargs)
    else:
        session.warn(f"Script not found: {script_path}, skipping.")


@nox.session(python=False, tags=["ci", "docker"])
def docker_build(session: Session) -> None:
    """Build the development Docker image (e.g., 'ledgerbase:dev'). Requires external
    Docker tool. Specify tag/dockerfile via posargs.
    """
    check_docker(session)
    image_tag = session.posargs[0] if session.posargs else f"{get_repo_name()}:dev"
    dockerfile = session.posargs[1] if len(session.posargs) > 1 else "Dockerfile"
    session.log(f"Building Docker image '{image_tag}' from '{dockerfile}'...")
    session.run(
        "docker",
        "build",
        "-f",
        dockerfile,
        "-t",
        image_tag,
        ".",
        *session.posargs[2:],
        external=True,
    )
    session.log(f"Docker image built: {image_tag}")


@nox.session(python=LATEST, tags=["ci", "packaging"], reuse_venv=True)
def package_check(session: Session) -> None:
    """Build the sdist and wheel, then check them using twine. Relies on twine
    installed via Poetry dev deps. Ensures package artifacts are valid.
    """
    install_poetry_and_deps(
        session,
        with_dev=True,
        no_root=False,
    )  # Install twine & poetry
    # session.install(f"twine=={TOOL_VERSIONS['twine']}") # Removed # noqa: ERA001
    dist_dir = Path("dist")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    session.log("Building sdist and wheel...")
    session.run("poetry", "build", external=False)
    session.log("Checking built artifacts with twine...")
    session.run("twine", "check", "dist/*")
    session.log("Twine check passed.")


# ─────────────────────────────────────────────────────────────────────────────
# 7. Utility Sessions
# ─────────────────────────────────────────────────────────────────────────────
@nox.session(python=False, tags=["util"])
def list_security_sessions(session: Session) -> None:
    """Output a JSON list of sessions tagged 'security' for CI matrix generation.
    Runs 'nox -l --json' and filters the output. Requires 'nox' in PATH.
    """
    try:
        nox_path = shutil.which("nox")
        if not nox_path:
            session.error("Could not find 'nox' executable in PATH.")
        list_output = (subprocess.check_output
                       ([nox_path, "-l", "--json"], text=True))  # nosec: B603, B607 - nox_path is validated above
        all_sessions = json.loads(list_output)
        security_sessions: list[str] = [
            s["session"] for s in all_sessions if "security" in s.get("tags", [])
        ]
        print(json.dumps(security_sessions))  # ONLY print JSON list
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        json.JSONDecodeError,
    ) as e:
        session.error(
            f"Could not dynamically list sessions: {e}. Check nox installation and "
            f"permissions.",
        )


@nox.session(python=LATEST, tags=["util"], reuse_venv=True)
@ensure_reports(TXT_REPORT_DIR) # Use your existing helper
def pre_commit_log(session: Session) -> None:
    """Run all pre-commit hooks verbosely and log to docs/reports/txt/pre-commit.log
    using shell redirection.
    """
    log_path = TXT_REPORT_DIR / "pre-commit.log"

    # IMPORTANT: Determine the correct command to run pre-commit.
    # Since your hooks use 'poetry run ...', pre-commit likely needs to be
    # invoked in a way that respects the poetry environment.
    # Using 'poetry run pre-commit ...' is the safest bet.
    pre_commit_base_command = "poetry run pre-commit"

    # Construct the full command with arguments
    full_command = f"{pre_commit_base_command} run --all-files --verbose"

    # Construct the shell command with redirection. shlex.quote handles
    # spaces/special chars. This redirects stdout (>) to the log file and
    # stderr (2>&1) to the same place as stdout.
    shell_command = f"{full_command} > {shlex.quote(str(log_path))} 2>&1"

    session.log(f"Running pre-commit via shell and logging to {log_path}")
    session.log(f"Executing: bash -c '{shell_command}'")

    # We run 'bash -c' as the external command
    try:
        session.run("bash", "-c", shell_command, external=True)
        # Check if the log file was created and has content, log success
        if log_path.exists() and log_path.stat().st_size > 0:
             session.log(f"Pre-commit log generated successfully at {log_path}")
        elif log_path.exists():
             session.log(f"Pre-commit ran, but log file at {log_path} is empty.")
        else:
             session.warn(f"Pre-commit ran, but log file {log_path} was not created.")

    except nox.command.CommandFailed as e:
        # The exception 'e' itself contains the exit code info in its string
        # representation. So, just use 'e' directly in the f-string.
        session.error(
            f"Pre-commit run failed. Check log at {log_path} for details. Error: {e}")


    except (OSError, RuntimeError) as e:

        session.error(
            f"An unexpected error occurred during pre_commit_log session: {e}")
