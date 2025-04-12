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
#
# Tag Legend:
#   - ci: included in automated CI pipelines
#   - core: unit testing and source linting
#   - security: vulnerability and license checks
#   - docker: container build and image scans
#   - docs: documentation and generation workflows
#   - extended-linting: combined config format checks
#   - util: internal tooling helpers
import json
import os
from pathlib import Path

import nox
from nox.sessions import Session

# ─────────────────────────────────────────────────────────────────────────────
# Global Config
# ─────────────────────────────────────────────────────────────────────────────

PYTHON_VERSIONS = ["3.9", "3.10", "3.11"]
LATEST = "3.11"
PACKAGE_DIR = "src/ledgerbase"
TESTS_DIR = "tests"
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


def install_poetry_and_deps(session, with_dev=True, no_root=True):
    session.install("poetry")
    command = ["poetry", "install"]
    if no_root:
        command.append("--no-root")
    if with_dev:
        command.extend(["--with", "dev"])
    else:
        command.extend(["--only", "main"])
    session.run(*command)


def discover_files(
    root: str, extensions: list[str], exclude_dirs: set[str]
) -> list[str]:
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        if any(excluded in Path(dirpath).parts for excluded in exclude_dirs):
            continue
        for file in filenames:
            if any(file.endswith(ext) for ext in extensions):
                found.append(str(Path(dirpath) / file))
    return found


# ─────────────────────────────────────────────────────────────────────────────
# Core Dev Sessions (Tests, Lint, Pre-commit)
# ─────────────────────────────────────────────────────────────────────────────


@nox.session(name="tests", python=PYTHON_VERSIONS, tags=["ci", "core"])
def tests(session):
    install_poetry_and_deps(session)
    session.run("pytest")


@nox.session(name="lint", python=PYTHON_VERSIONS, tags=["ci", "core"])
def lint(session):
    install_poetry_and_deps(session)
    session.run("ruff", PACKAGE_DIR)


@nox.session(name="pre-commit", python=PYTHON_VERSIONS, tags=["ci", "core"])
def pre_commit(session):
    install_poetry_and_deps(session)
    session.run("pre-commit", "run", "--all-files")


@nox.session(name="ruff", python=PYTHON_VERSIONS, tags=["ci", "core"])
def ruff_check(session):
    install_poetry_and_deps(session)
    session.install("ruff")
    session.run("ruff", PACKAGE_DIR, "--format", "sarif", "--output", "ruff.sarif")


@nox.session(name="black", python=PYTHON_VERSIONS, tags=["ci", "core"])
def black_check(session):
    install_poetry_and_deps(session)
    session.install("black")
    session.run("black", "--check", PACKAGE_DIR)


@nox.session(name="mypy", python=PYTHON_VERSIONS, tags=["ci", "core"])
def mypy_check(session):
    install_poetry_and_deps(session)
    session.install("mypy")
    session.run("mypy", PACKAGE_DIR)


@nox.session(name="check-lockfile", python=False, tags=["ci", "core"])
def check_lockfile(session):
    session.install("poetry")
    session.run("poetry", "lock", "--check")


# ─────────────────────────────────────────────────────────────────────────────
# Security and Compliance
# ─────────────────────────────────────────────────────────────────────────────


@nox.session(name="bandit", python=LATEST, tags=["ci", "security"])
def bandit_scan(session):
    install_poetry_and_deps(session)
    session.run("bandit", "-r", PACKAGE_DIR, "-f", "json", "-o", "bandit-report.json")


@nox.session(name="pip-audit", python=LATEST, tags=["ci", "security"])
def pip_audit(session):
    install_poetry_and_deps(session)
    session.run("pip-audit")


@nox.session(name="semgrep", python=LATEST, tags=["ci", "security"])
def semgrep(session):
    install_poetry_and_deps(session)
    session.run(
        "semgrep", "--config", "auto", "--json", "--output", "semgrep-results.json"
    )
    session.run("semgrep", "--config", "auto", "--sarif", "--output", "semgrep.sarif")


@nox.session(name="snyk_scan", tags=["ci", "security"])
def snyk_scan(session: Session):
    session.install("poetry")
    session.run("poetry", "install", "--no-root", external=True)
    session.run("npm", "install", "-g", "snyk", external=True)
    snyk_token = os.environ.get("SNYK_TOKEN")
    if not snyk_token:
        session.error("Missing required SNYK_TOKEN environment variable.")
    session.run("snyk", "auth", snyk_token, external=True)
    session.run(
        "snyk",
        "test",
        "--all-projects",
        "--detection-depth=3",
        "--json-file-output=snyk-results.json",
        external=True,
    )


@nox.session(name="trivy", reuse_venv=True, tags=["ci", "security", "docker"])
def trivy(session):
    image_name = "ledgerbase:latest"
    sarif_output = "trivy-results.sarif"
    session.run("docker", "--version", external=True)
    session.run("docker", "build", "-t", image_name, ".", external=True)
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
        image_name,
        external=True,
    )


@nox.session(name="sbom", python=LATEST, tags=["ci", "security"])
def sbom(session):
    session.install("cyclonedx-bom")
    session.run(
        "cyclonedx-py", "--output-format", "sarif", "--output-file", "sbom.sarif"
    )
    session.run("cyclonedx-py", "--output-format", "json", "--output-file", "sbom.json")


@nox.session(name="license", python=LATEST, tags=["ci", "security"])
def license(session):
    session.install("pip-licenses")
    session.run(
        "pip-licenses",
        "--format=json",
        "--output-file=license-report.json",
        "--with-authors",
        "--with-urls",
    )
    with open("license-report.json") as f:
        licenses = json.load(f)
    allowed = {"MIT", "BSD", "Apache-2.0", "ISC"}
    disallowed = [
        f"{pkg['Name']} ({pkg['License']})"
        for pkg in licenses
        if pkg["License"] not in allowed
    ]
    if disallowed:
        with open("disallowed.txt", "w") as out:
            out.write("\n".join(disallowed))
        session.log(f"Found {len(disallowed)} disallowed licenses.")
    else:
        session.log("No disallowed licenses found.")


@nox.session(name="safety", python="3.12", tags=["ci", "security"])
def safety(session):
    session.install("safety", "safety-sarif", "jq")
    session.run(
        "safety", "check", "--full-report", "--json", "-o", "safety_output.json"
    )
    session.run("safety-sarif", "safety_output.json", "-o", "safety.sarif")


# ─────────────────────────────────────────────────────────────────────────────
# Docker & Artifacts
# ─────────────────────────────────────────────────────────────────────────────


@nox.session(name="docker-build", python=False, tags=["ci", "docker"])
def docker_build(session):
    session.run("docker", "build", "-f", "Dockerfile", "-t", "ledgerbase:dev", ".")


@nox.session(name="gen_script_docs", tags=["ci", "docs"])
def gen_script_docs(session):
    session.run("python", "scripts/generate_script_docs.py")


# ─────────────────────────────────────────────────────────────────────────────
# Extended Linting (YAML, Markdown, Mixed)
# ─────────────────────────────────────────────────────────────────────────────


@nox.session(name="lint_all", python=LATEST, tags=["ci", "extended-linting"])
def lint_all(session: Session) -> None:
    session.install("yamllint")
    session.install("prettier")
    session.install("markdownlint-cli")

    yaml_files = discover_files(".", [".yaml", ".yml"], EXCLUDE_PATHS)
    yaml_list = Path("scripts/lint-yaml.txt")
    yaml_list.parent.mkdir(parents=True, exist_ok=True)
    yaml_list.write_text("\n".join(yaml_files))
    if yaml_files:
        session.run("npx", "prettier", "--write", *yaml_files, external=True)
        session.run("yamllint", "-f", "parsable", *yaml_files)

    md_files = discover_files(".", [".md"], EXCLUDE_PATHS)
    md_list = Path("scripts/lint-md.txt")
    md_list.write_text("\n".join(md_files))
    if md_files:
        session.run("markdownlint", "--fix", *md_files, external=True)


# ─────────────────────────────────────────────────────────────────────────────
# Session Discovery Utilities
# ─────────────────────────────────────────────────────────────────────────────


@nox.session(name="list-security-sessions", python=False, tags=["ci", "util"])
def list_security_sessions(session):
    from nox._decorators import Func

    security_sessions = [
        name
        for name, obj in globals().items()
        if isinstance(obj, Func) and "security" in getattr(obj, "tags", [])
    ]
    session.log("Security sessions: " + ", ".join(security_sessions))
    session.run("echo", json.dumps(security_sessions))
