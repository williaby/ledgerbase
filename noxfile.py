##: name = noxfile.py
##: description = Nox sessions for testing, linting, CI, and documentation generation in LedgerBase. # noqa: E501
##: category = dev
##: usage = nox -s <session_name> (e.g., nox -s tests)
##: behavior = Defines reusable Nox sessions for CI workflows such as linting, testing, doc building, and security scans. # noqa: E501
##: dependencies = nox, poetry
##: tags = ci, automation, testing, docs, security
##: author = Byron Williams
##: last_modified = 2025-04-12

# LedgerBase - Nox Configuration
# Organized for CI, security, linting, testing, and utility automation
# ─────────────────────────────────────────────────────────────────────────────
# Table of Contents
# ─────────────────────────────────────────────────────────────────────────────
# 1. Global Config
# 2. Core Dev Sessions (Tests, Lint, Pre-commit)       [tags: ci, core]
# 3. Security and Compliance                           [tags: ci, security]
# 4. Docker & Artifacts                                [tags: ci, docker, docs]
# 5. Extended Linting (YAML, Markdown, Mixed)          [tags: ci, extended-linting]
# 6. Session Discovery Utilities                       [tags: ci, util]

# ─────────────────────────────────────────────────────────────────────────────
# 1. Global Config
# ─────────────────────────────────────────────────────────────────────────────

import json
import os
from pathlib import Path

import nox
from nox.sessions import Session

PYTHON_VERSIONS = ["3.9", "3.10", "3.11"]
LATEST = "3.11"
PACKAGE_DIR = "src/ledgerbase"
EXCLUDE_PATHS = {
    ".nox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    ".git",
    "migrations",
    "tests",
    "scripts",
}
LINT_TARGETS = ["src", "tests", "noxfile.py"]


def install_poetry_and_deps(
    session: Session,
    *,
    with_dev: bool = True,
    no_root: bool = True,
) -> None:
    """Install Poetry and project dependencies."""
    session.install("poetry")
    command = ["poetry", "install"]
    if no_root:
        command.append("--no-root")
    command.extend(["--with", "dev"] if with_dev else ["--only", "main"])
    session.run(*command)


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
    """Load environment variables from decrypted .env.dev."""
    if not Path(path).exists():
        session.warn(f"⚠️ Env file not found at {path}")
        return
    with Path(path).open() as f:
        for line in f:
            if "=" in line and not line.strip().startswith("#"):
                key, val = line.strip().split("=", 1)
                session.env[key] = val.strip().strip('"')


# ─────────────────────────────────────────────────────────────────────────────
# 2. Core Dev Sessions (Tests, Lint, Pre-commit)
# ─────────────────────────────────────────────────────────────────────────────


@nox.session(name="tests", python=PYTHON_VERSIONS, tags=["ci", "core"])
def tests(session: Session) -> None:
    """Run unit tests with pytest."""
    install_poetry_and_deps(session)
    session.run("pytest")


@nox.session(name="lint", python=PYTHON_VERSIONS, tags=["ci", "core"])
def lint(session: Session) -> None:
    """Run consolidated linters using Ruff (replaces flake8/isort)."""
    session.install("ruff")
    session.run("ruff", "check", *LINT_TARGETS)


@nox.session(
    name="ruff_fix",
    python=PYTHON_VERSIONS,
    tags=["ci", "core", "extended-linting"],
)
def ruff_fix(session: Session) -> None:
    """Run Ruff linter with auto-fix enabled."""
    session.install("ruff")
    session.run("ruff", ".", "--fix")


@nox.session(name="pre-commit", python=PYTHON_VERSIONS, tags=["ci", "core"])
def pre_commit(session: Session) -> None:
    """Run all pre-commit hooks."""
    install_poetry_and_deps(session)
    session.run("pre-commit", "run", "--all-files")


@nox.session(name="black", python=PYTHON_VERSIONS, tags=["ci", "core"])
def black_check(session: Session) -> None:
    """Check formatting using Black."""
    install_poetry_and_deps(session)
    session.install("black")
    session.run("black", "--check", PACKAGE_DIR)


@nox.session(name="mypy", python=PYTHON_VERSIONS, tags=["ci", "core"])
def mypy_check(session: Session) -> None:
    """Run Mypy for static type checking."""
    install_poetry_and_deps(session)
    session.install("mypy")
    session.run("mypy", PACKAGE_DIR)


@nox.session(name="check-lockfile", python=False, tags=["ci", "core"])
def check_lockfile(session: Session) -> None:
    """Ensure poetry.lock is up to date."""
    session.install("poetry")
    session.run("poetry", "lock", "--check")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Security and Compliance
# ─────────────────────────────────────────────────────────────────────────────


@nox.session(name="bandit", python=LATEST, tags=["ci", "security"])
def bandit_scan(session: Session) -> None:
    """Run Bandit security scanner and convert output to SARIF."""
    install_poetry_and_deps(session)
    session.install("bandit", "bandit2sarif")
    session.run(
        "bandit",
        "-r",
        PACKAGE_DIR,
        "-f",
        "json",
        "-o",
        "bandit-report.json",
    )
    session.run("bandit2sarif", "bandit-report.json", "--output", "bandit-report.sarif")


@nox.session(name="safety", python="3.12", tags=["ci", "security"])
def safety(session: Session) -> None:
    """Run Safety vulnerability scanner and convert to SARIF."""
    session.install("safety", "safety-sarif", "jq")
    session.run(
        "safety",
        "check",
        "--full-report",
        "--json",
        "-o",
        "safety_output.json",
    )
    session.run("safety-sarif", "safety_output.json", "-o", "safety.sarif")


@nox.session(name="trivy", reuse_venv=True, tags=["ci", "security", "docker"])
def trivy(session: Session) -> None:
    """Run Trivy vulnerability scanner for Docker image in SARIF and JSON formats."""
    image_tag = session.posargs[0] if session.posargs else "ledgerbase:latest"
    sarif_output = "trivy-results.sarif"
    json_output = "trivy-results.json"
    session.run("docker", "build", "-t", image_tag, ".", external=True)
    session.run(
        "trivy",
        "image",
        "--format",
        "sarif",
        "--output",
        sarif_output,
        "--exit-code",
        "0",
        "--ignore-unfixed",
        "--severity",
        "HIGH,CRITICAL",
        image_tag,
        external=True,
    )
    session.run(
        "trivy",
        "image",
        "--format",
        "json",
        "--output",
        json_output,
        "--ignore-unfixed",
        "--severity",
        "HIGH,CRITICAL",
        image_tag,
        external=True,
    )


@nox.session(name="sbom_validate", python=False, tags=["ci", "security"])
def sbom_validate(session: Session) -> None:
    """Build SBOM with Trivy and validate with CycloneDX CLI."""
    image_tag = "ledgerbase:local"
    output_dir = Path("docs/generated/sbom")
    output_dir.mkdir(parents=True, exist_ok=True)
    sbom_path = output_dir / "sbom.cdx.json"
    session.run("docker", "build", "-t", image_tag, ".", external=True)
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
    session.run(
        "wget",
        "-q",
        "https://github.com/CycloneDX/cyclonedx-cli/releases/download/v0.24.0/cyclonedx-linux-x64",
        "-O",
        "cyclonedx",
        external=True,
    )
    session.run("chmod", "+x", "cyclonedx", external=True)
    session.run(
        "./cyclonedx",
        "validate",
        "--input-file",
        str(sbom_path),
        external=True,
    )


@nox.session(name="license_report", python=LATEST, tags=["ci", "security"])
def license_report(session: Session) -> None:
    """Generate license report and identify disallowed licenses."""
    session.install("pip-licenses")
    session.run(
        "pip-licenses",
        "--format=json",
        "--output-file=license-report.json",
        "--with-authors",
        "--with-urls",
    )
    license_file = Path("license-report.json")
    if not license_file.exists():
        session.error(
            "License report file not found. Ensure pip-licenses ran successfully.",
        )

    with license_file.open() as f:
        licenses = json.load(f)

    allowed = {"MIT", "BSD", "Apache-2.0", "ISC"}
    disallowed = [
        f"{pkg['Name']} ({pkg['License']})"
        for pkg in licenses
        if pkg.get("License") not in allowed
    ]

    if disallowed:
        disallowed_file = Path("disallowed.txt")
        with disallowed_file.open("w") as out:
            out.write("\n".join(disallowed))
        session.log(
            f"Found {len(disallowed)} disallowed licenses. See {disallowed_file}.",
        )
    else:
        session.log("No disallowed licenses found.")


@nox.session(name="snyk_code", tags=["ci", "security"])
def snyk_code(session: Session) -> None:
    """Run Snyk Code analysis and output SARIF."""
    token = os.environ.get("SNYK_TOKEN")
    if not token:
        session.error("Missing required SNYK_TOKEN environment variable.")
    # Install & authenticate
    session.run("npm", "install", "-g", "snyk", external=True)
    session.run("snyk", "auth", token, external=True)
    # Execute Code scan → SARIF
    session.run(
        "snyk",
        "code",
        "test",
        "--sarif",
        "--output",
        "snyk-code.sarif",
        external=True,
    )


@nox.session(name="snyk_oss", tags=["ci", "security"])
def snyk_oss(session: Session) -> None:
    """Run Snyk Open Source (SCA) scan and export JSON."""
    token = os.environ.get("SNYK_TOKEN")
    if not token:
        session.error("Missing required SNYK_TOKEN environment variable.")
    # Ensure your project deps are installed
    install_poetry_and_deps(session)
    # Install & authenticate
    session.run("npm", "install", "-g", "snyk", external=True)
    session.run("snyk", "auth", token, external=True)
    # Execute OSS scan → JSON
    session.run(
        "snyk",
        "test",
        "--all-projects",
        "--detection-depth=3",
        "--json-file-output",
        "snyk-oss.json",
        external=True,
    )


@nox.session(name="snyk_iac", tags=["ci", "security"])
def snyk_iac(session: Session) -> None:
    """Run Snyk Infrastructure-as-Code scan and output SARIF."""
    token = os.environ.get("SNYK_TOKEN")
    if not token:
        session.error("Missing required SNYK_TOKEN environment variable.")
    session.run("npm", "install", "-g", "snyk", external=True)
    session.run("snyk", "auth", token, external=True)
    # Execute IaC scan → SARIF
    session.run(
        "snyk",
        "iac",
        "test",
        "--sarif",
        "--output",
        "snyk-iac.sarif",
        external=True,
    )


@nox.session(name="snyk_container", tags=["ci", "security", "docker"])
def snyk_container(session: Session) -> None:
    """Run Snyk Container test and output JSON & SARIF."""
    token = os.environ.get("SNYK_TOKEN")
    if not token:
        session.error("Missing required SNYK_TOKEN environment variable.")
    # Build the Docker image
    session.run("docker", "build", "-t", "ledgerbase:latest", ".", external=True)
    # Install & authenticate
    session.run("npm", "install", "-g", "snyk", external=True)
    session.run("snyk", "auth", token, external=True)
    # Execute container test → JSON + SARIF
    session.run(
        "snyk",
        "container",
        "test",
        "ledgerbase:latest",
        "--file=Dockerfile",
        "--json-file-output",
        "snyk-container.json",
        "--sarif-file-output",
        "snyk-container.sarif",
        external=True,
    )


@nox.session(name="coverage", python=["3.9", "3.10", "3.11"])
def coverage(session: Session) -> None:
    """Run coverage report session."""
    # Install everything, including pytest-cov
    session.run("poetry", "install", "--with", "dev", external=True)
    # Run pytest with XML output
    session.run(
        "pytest",
        "--cov=src/ledgerbase",
        "--cov-report=xml",
        "--cov-report=term",
        "tests/",
    )


# Path to your Aikido CLI executable
AIKIDO_CLI = "aikido"

# Shared ignore file
IGNORE_FILE = ".semgrepignore"


@nox.session(name="aikido-pr-scan", reuse_venv=True)
def aikido_pr_scan(session: Session) -> None:
    """Run Aikido on changed files in a PR, using all scanners but limited to diffs."""
    # Install Aikido CLI if needed
    session.install("aikido-security-cli")
    # Get diff list from env (GitHub Actions will supply CHANGED_FILES)
    changed = session.env.get("CHANGED_FILES", "")
    if not changed:
        session.error("No CHANGED_FILES provided to aikido-pr-scan")
    session.run(
        AIKIDO_CLI,
        "scan",
        "--diff",
        "--paths",
        changed,
        "--ignore-path",
        IGNORE_FILE,
        "--all",  # run SAST, SCA, secrets, container, etc.
        external=True,
    )


@nox.session(name="aikido-weekly-scan", reuse_venv=True)
def aikido_weekly_scan(session: Session) -> None:
    """Weekly full-repo scan (excluding ignored patterns)."""
    session.install("aikido-security-cli")
    session.run(
        AIKIDO_CLI,
        "scan",
        "--all",
        "--ignore-path",
        IGNORE_FILE,
        external=True,
    )


@nox.session(name="aikido-usage-report", reuse_venv=True)
def aikido_usage_report(session: Session) -> None:
    """Query Aikido API for current free-plan usage and print as JSON."""
    session.install("requests")
    # Replace with your actual API token env var
    token = session.env.get("AIKIDO_API_TOKEN", "")
    if not token:
        session.error("Set AIKIDO_API_TOKEN in environment for usage report")
    session.run(
        "python",
        "- <<CODE",
        f"""
import os, requests, json
h = {{'Authorization': f'Bearer {token}'}}
r = requests.get('https://api.aikidosecurity.com/v1/usage', headers=h)
data = r.json()
print(json.dumps(data, indent=2))
""",
        external=False,
    )


###############################################################################
# Semgrep security scans (PR diffs + full-repo)
###############################################################################

# 1. Shared list of bundles (community + Pro bundles your free plan supports)
SHARED_BUNDLES = [
    # Community-only
    "r/python.flask",
    # Pro bundles (confirmed available)
    "p/bandit",
    "p/cwe-top-25",
    "p/security-audit",
    "p/secure-defaults",
    "p/r2c-best-practices",
    "p/owasp-top-ten",
    "p/sql-injection",
    "p/command-injection",
    "p/xss",
    "p/secrets",
    "p/gitleaks",
    "p/github-actions",
    "p/semgrep-misconfigurations",
    "p/ci",
    "p/semgrep-rule-lints",
    "p/semgrep-rule-ci",  # Trailing comma for COM812
]


def _run_semgrep(session: Session, mode: str, sarif_name: str) -> None:
    """Install Semgrep and run CI or full-scan mode.
    Uses server-side rules for all targets.
    """
    session.install("--upgrade-strategy", "eager", "semgrep==1.119.0")
    args = [
        mode,
        "--jobs",
        "4",
        "--sarif-output",
        sarif_name,  # Trailing comma for COM812
    ]
    if mode == "scan":
        args.append(".")
    session.run("semgrep", *args)


@nox.session(name="semgrep_ci", python="3.11", reuse_venv=True, tags=["ci", "security"])
def semgrep_ci(session: Session) -> None:
    """Run Semgrep in 'ci' mode (diff-only) and auto-upload to the Semgrep App
    when SEMGREP_APP_TOKEN/SEMGREP_DEPLOYMENT_ID are set.
    """
    _run_semgrep(session, mode="ci", sarif_name="semgrep-ci.sarif")


@nox.session(
    name="semgrep_full",
    python="3.11",
    reuse_venv=True,
    tags=["ci", "security"],
)
def semgrep_full(session: Session) -> None:
    """Run a full-repo scan so you can catch everything on your weekly schedule."""
    _run_semgrep(session, mode="scan", sarif_name="semgrep_full.sarif")


# ─────────────────────────────────────────────────────────────────────────────
# 4. Docker & Artifacts
# ─────────────────────────────────────────────────────────────────────────────


@nox.session(name="docker_build", python=False, tags=["ci", "docker"])
def docker_build(session: Session) -> None:
    """Build development Docker image."""
    session.run("docker", "build", "-f", "Dockerfile", "-t", "ledgerbase:dev", ".")


@nox.session(name="gen_script_docs", tags=["ci", "docs"])
def gen_script_docs(session: Session) -> None:
    """Generate markdown documentation for all project shell scripts."""
    session.run("python", "scripts/generate_script_docs.py")


@nox.session(name="build_docs", python=LATEST, tags=["ci", "docs"])
def build_docs(session: Session) -> None:
    """Build HTML & PDF documentation with strict warnings-as-errors."""
    # install EVERYTHING in dev (including Sphinx + extensions)
    install_poetry_and_deps(session, with_dev=True, no_root=False)

    # 1) HTML build
    session.run(
        "sphinx-build",
        "-b",
        "html",
        "-W",  # treat warnings as errors
        "docs/source",
        "docs/build/html",
    )

    # 2) PDF build
    session.run(
        "sphinx-build",
        "-b",
        "latex",
        "docs/source",
        "docs/build/latex",
    )
    session.run(
        "make",
        "-C",
        "docs/build/latex",
        "all-pdf",
    )


@nox.session(name="build_docs_strict", python=LATEST, tags=["ci", "docs"])
def build_docs_strict(session: Session) -> None:
    """Build Sphinx documentation with warnings as errors."""
    install_poetry_and_deps(session)
    session.run("sphinx-build", "-n", "-W", "docs/source", "docs/build")


@nox.session(name="gen_master_index", tags=["ci", "docs"])
def gen_master_index(session: Session) -> None:
    """Generate the top-level documentation index file."""
    session.run("python", "scripts/generate_master_index.py")


# ─────────────────────────────────────────────────────────────────────────────
# 5. Extended Linting (YAML, Markdown, Mixed)
# ─────────────────────────────────────────────────────────────────────────────


@nox.session(name="lint_all", python=LATEST, tags=["ci", "extended-linting"])
def lint_all(session: Session) -> None:
    """Run linting on YAML and Markdown using prettier, yamllint, markdownlint."""
    session.install("yamllint")
    session.install("prettier")
    session.install("markdownlint-cli")

    yaml_files = discover_files(".", [".yaml", ".yml"], EXCLUDE_PATHS)
    if yaml_files:
        session.run("npx", "prettier", "--write", *yaml_files, external=True)
        session.run("yamllint", "-f", "parsable", *yaml_files)

    md_files = discover_files(".", [".md"], EXCLUDE_PATHS)
    if md_files:
        session.run("markdownlint", "--fix", *md_files, external=True)


@nox.session(name="lint_rst", python=LATEST, tags=["ci", "docs"])
def lint_rst(session: Session) -> None:
    """Run rst linter using sphinx-lint on reStructuredText documentation."""
    install_poetry_and_deps(session)
    session.install("sphinx-lint")
    rst_dirs = ["docs/source/rst/"]
    session.run("sphinx-lint", *rst_dirs)


# ─────────────────────────────────────────────────────────────────────────────
# 6. Session Discovery Utilities
# ─────────────────────────────────────────────────────────────────────────────


@nox.session(name="lint_docs", python=LATEST, tags=["ci", "docs"])
def lint_docs(session: Session) -> None:
    """Lint reStructuredText, catch spelling mistakes, and verify Sphinx directives."""
    install_poetry_and_deps(session, with_dev=True, no_root=False)

    # 1) .rst syntax & directive linting
    session.run("sphinx-lint", "docs/source")

    # 2) catch typos
    session.run("codespell", "docs/source")


@nox.session(name="list-security-sessions", python=False, tags=["ci", "util"])
def list_security_sessions(session: Session) -> None:
    """Print a list of all sessions tagged as 'security'."""
    from nox._decorators import Func

    security_sessions = [
        name
        for name, obj in globals().items()
        if isinstance(obj, Func) and "security" in getattr(obj, "tags", [])
    ]
    session.log("Security sessions: " + ", ".join(security_sessions))
    session.run("echo", json.dumps(security_sessions))


@nox.session(name="lint_all_combined", python=LATEST, tags=["ci", "extended-linting"])
def lint_all_combined(session: Session) -> None:
    """Run all linting: Python, YAML, Markdown, and reStructuredText."""
    install_poetry_and_deps(session)

    # 1. Python linting (Ruff)
    session.install("ruff")
    session.log("🔍 Running Ruff (Python linter)...")
    session.run("ruff", "check", *LINT_TARGETS)

    # 2. YAML linting
    session.install("yamllint")
    session.install("prettier")  # Needed for YAML reformatting
    yaml_files = discover_files(".", [".yaml", ".yml"], EXCLUDE_PATHS)
    if yaml_files:
        session.log("🔍 Running Prettier + Yamllint on YAML files...")
        session.run("npx", "prettier", "--write", *yaml_files, external=True)
        session.run("yamllint", "-f", "parsable", *yaml_files)

    # 3. Markdown linting
    session.install("markdownlint-cli")
    md_files = discover_files(".", [".md"], EXCLUDE_PATHS)
    if md_files:
        session.log("🔍 Running Markdownlint...")
        session.run("markdownlint", "--fix", *md_files, external=True)

    # 4. RST linting
    session.install("sphinx-lint")
    rst_dirs = ["docs/source/rst/"]
    session.log("🔍 Running sphinx-lint on RST files...")
    session.run("sphinx-lint", *rst_dirs)
