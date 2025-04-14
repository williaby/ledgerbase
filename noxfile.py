##: name = noxfile.py
##: description = Nox sessions for testing, linting, CI, and documentation generation in LedgerBase. # noqa: E501
##: category = dev
##: usage = nox -s <session_name> (e.g., nox -s tests)
##: behavior = Defines reusable Nox sessions for CI workflows such as linting, testing, doc building, and security scans. # noqa: E501
##: dependencies = nox, poetry
##: tags = ci, automation, testing, docs
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
    snyk_token = os.environ.get("SNYK_TOKEN")
    if not snyk_token:
        session.error("Missing required SNYK_TOKEN environment variable.")
    session.run("npm", "install", "-g", "snyk", external=True)
    session.run("snyk", "auth", snyk_token, external=True)
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
    snyk_token = os.environ.get("SNYK_TOKEN")
    if not snyk_token:
        session.error("Missing required SNYK_TOKEN environment variable.")
    install_poetry_and_deps(session)
    session.run("npm", "install", "-g", "snyk", external=True)
    session.run("snyk", "auth", snyk_token, external=True)
    session.run(
        "snyk",
        "test",
        "--all-projects",
        "--detection-depth=3",
        "--json-file-output=snyk-results.json",
        external=True,
    )


@nox.session(name="snyk_iac", tags=["ci", "security"])
def snyk_iac(session: Session) -> None:
    """Run Snyk Infrastructure as Code scan with SARIF output."""
    snyk_token = os.environ.get("SNYK_TOKEN")
    if not snyk_token:
        session.error("Missing required SNYK_TOKEN environment variable.")
    session.run("npm", "install", "-g", "snyk", external=True)
    session.run("snyk", "auth", snyk_token, external=True)
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
    """Run Snyk container monitor on built Docker image."""
    snyk_token = os.environ.get("SNYK_TOKEN")
    if not snyk_token:
        session.error("Missing required SNYK_TOKEN environment variable.")
    session.run("docker", "build", "-t", "ledgerbase:latest", ".", external=True)
    session.run("npm", "install", "-g", "snyk", external=True)
    session.run("snyk", "auth", snyk_token, external=True)
    session.run(
        "snyk",
        "container",
        "monitor",
        "ledgerbase:latest",
        "--file=Dockerfile",
        external=True,
    )


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
    """Run rst linter using doc8 on reStructuredText documentation."""
    install_poetry_and_deps(session)
    session.install("doc8")
    rst_dirs = ["docs/source/rst/"]
    session.run("doc8", *rst_dirs)


# ─────────────────────────────────────────────────────────────────────────────
# 6. Session Discovery Utilities
# ─────────────────────────────────────────────────────────────────────────────


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
