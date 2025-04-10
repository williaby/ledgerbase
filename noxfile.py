import os
from pathlib import Path

import nox
from nox.sessions import Session
os.chdir(os.path.dirname(__file__))

# Define Python version usage
FULL_MATRIX = ["3.9", "3.10", "3.11", "3.12"]
LATEST = "3.12"

SOURCE_DIR = "src/ledgerbase"
TESTS_DIR = "tests"

# Paths to exclude from linting
EXCLUDE_PATHS = {
    ".nox", ".venv", "__pycache__", "build", "dist", ".git", "migrations", "tests", "scripts"
}


# Helper to find files with given extensions, excluding certain paths
def discover_files(root: str, extensions: list[str], exclude_dirs: set[str]) -> list[str]:
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        if any(excluded in Path(dirpath).parts for excluded in exclude_dirs):
            continue
        for file in filenames:
            if any(file.endswith(ext) for ext in extensions):
                found.append(str(Path(dirpath) / file))
    return found


# Helper to export requirements for the session
def export_dev_requirements(session: Session, temp_path: Path) -> Path:
    requirements = temp_path / "dev-requirements.txt"
    session.run(
        "poetry",
        "export",
        "--with",
        "dev",
        "--format=requirements.txt",
        "--without-hashes",
        "-o",
        str(requirements),
        external=True,
    )
    return requirements


@nox.session(python=LATEST)
def lint(session):
    """
    Run linters: black, isort, flake8.
    Run on latest Python only to reduce matrix overhead.
    """
    requirements = export_dev_requirements(session, Path(session.create_tmp()))
    session.install("-r", str(requirements))
    session.run("black", "--check", ".")
    session.run("isort", "--check-only", ".")
    session.run(
        "flake8",
        ".",
        "--exclude=.nox,.venv,__pycache__,build,dist,.git,migrations,tests",
        external=True,
    )


@nox.session(python=LATEST)
def typecheck(session):
    """
    Run static type checks using mypy.
    """
    requirements = export_dev_requirements(session, Path(session.create_tmp()))
    session.install("-r", str(requirements))
    session.run("mypy", SOURCE_DIR)


@nox.session(python=LATEST)
def security(session):
    """
    Run security tooling: Bandit, Safety, pip-audit.
    - Bandit outputs SARIF-compatible JSON.
    - B101 is skipped (asserts allowed for dev assertions).
    - pip-audit uses success codes 0/1 (1 = issues found).
    - Safety results are exported to safety_output.txt for CI workflows.
    """
    requirements = export_dev_requirements(session, Path(session.create_tmp()))
    session.install("-r", str(requirements))
    session.run(
        "bandit",
        "-r",
        SOURCE_DIR,
        "-x",
        TESTS_DIR,
        "-f",
        "json",
        "-o",
        "bandit-results.json",
        "--skip",
        "B101",
    )
    session.log("Bandit JSON results written to bandit-results.json")

    with open("safety_output.txt", "w") as f:
        session.run("safety", "check", "--full-report", stdout=f)
    session.log("Safety output written to safety_output.txt")

    session.run("pip-audit", success_codes=[0, 1])


@nox.session(python=LATEST)
def secrets(session):
    """
    Scan for secrets using TruffleHog.
    Exclude common noisy paths to reduce false positives.
    """
    requirements = export_dev_requirements(session, Path(session.create_tmp()))
    session.install("-r", str(requirements))
    session.install("trufflehog")
    session.run(
        "trufflehog",
        "filesystem",
        "--no-update",
        "--regex",
        "--entropy=True",
        "--exclude",
        ".git,.venv,.tox,__pycache__",
        ".",
    )


@nox.session(python=FULL_MATRIX)
def tests(session):
    """
    Run tests using pytest across full Python version matrix.
    Fail explicitly if requirements.txt is missing.
    """
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        session.error(
            "requirements.txt is missing. Please add it before running tests."
        )
    session.install("-r", str(requirements_file))
    session.install("pytest")
    session.run("pytest", TESTS_DIR)


@nox.session(python=LATEST)
def sbom(session):
    """
    Generate SBOMs using cyclonedx-bom.
    - sarif: for GitHub Security tab
    - json: for compliance archival
    """
    session.install("cyclonedx-bom")
    session.run(
        "cyclonedx-py", "--output-format", "sarif", "--output-file", "sbom.sarif"
    )
    session.run("cyclonedx-py", "--output-format", "json", "--output-file", "sbom.json")


@nox.session(python=LATEST)
def license(session):
    """
    Generate a license report and filter disallowed licenses.
    Produces:
    - license-report.json (full)
    - disallowed.txt (if any non-allowed licenses found)
    """
    session.install("pip-licenses")
    session.run(
        "pip-licenses",
        "--format=json",
        "--output-file=license-report.json",
        "--with-authors",
        "--with-urls",
    )

    # Create filtered list of disallowed licenses
    allowed = {"MIT", "BSD", "Apache-2.0", "ISC"}
    import json

    with open("license-report.json") as f:
        licenses = json.load(f)

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


@nox.session(name="pip-audit", python=LATEST)
def pip_audit(session: nox.Session) -> None:
    """Run pip-audit for dependency vulnerability scanning."""
    session.install("pip-audit")
    retries = 3
    for attempt in range(1, retries + 1):
        try:
            session.log(f"Attempt {attempt} of pip-audit...")
            session.run("pip-audit", "--output", "audit_results.txt", external=True)
            break
        except nox.command.CommandFailed:
            if attempt == retries:
                session.error("pip-audit failed after 3 attempts.")
            session.log("Retrying pip-audit after failure...")
            session.sleep(10)


@nox.session(python=LATEST)
def semgrep(session):
    """
    Run Semgrep with both JSON and SARIF output formats.
    - JSON: used for direct PR feedback
    - SARIF: uploaded to GitHub Security dashboard
    """
    requirements = export_dev_requirements(session, Path(session.create_tmp()))
    session.install("-r", str(requirements))
    session.install("semgrep")

    session.run(
        "semgrep",
        "--config=auto",
        "--json",
        "--output=semgrep-results.json",
        external=True,
    )

    session.run(
        "semgrep",
        "--config=auto",
        "--sarif",
        "--output=semgrep.sarif",
        external=True,
    )

    session.log("Semgrep analysis completed.")


@nox.session(name="snyk_scan")
def snyk_scan(session: nox.Session) -> None:
    """Run Snyk scan and output JSON results."""
    session.install("poetry")  # Optional: to ensure dependencies are present
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


@nox.session(name="trivy", reuse_venv=True)
def trivy(session):
    """
    Runs a Trivy vulnerability scan on the Docker image built from the repository.
    Outputs results to a SARIF file for GitHub Security integration.
    """
    image_name = "ledgerbase:latest"
    sarif_output = "trivy-results.sarif"

    # Ensure Docker is installed
    session.run("docker", "--version", external=True)

    # Build Docker image
    session.log("Building Docker image for scanning...")
    session.run("docker", "build", "-t", image_name, ".", external=True)

    # Run Trivy scan
    session.log("Running Trivy vulnerability scan...")
    session.run(
        "trivy",
        "image",
        "--format",
        "sarif",
        "--output",
        sarif_output,
        "--exit-code",
        "0",  # Let GitHub Actions handle alerting
        "--ignore-unfixed",
        "--severity",
        "HIGH,CRITICAL",
        image_name,
        external=True,
    )

    session.log(f"Trivy scan completed. Output written to {sarif_output}")


@nox.session(python=LATEST)
def lint_yaml(session):
    """
    Lint YAML files using yamllint.
    """
    requirements = export_dev_requirements(Path(session.create_tmp()))
    session.install("-r", str(requirements))
    session.run("yamllint", ".")


@nox.session(python=LATEST)
def lint_markdown(session):
    """
    Lint Markdown files using markdownlint-cli.
    """
    requirements = export_dev_requirements(session, Path(session.create_tmp()))
    session.install("-r", str(requirements))
    session.run("markdownlint", ".", external=True)


@nox.session(name="lint_all", python=LATEST)
def lint_all(session: Session) -> None:
    """
    Run full lint suite: flake8, prettier (for YAML), markdownlint.
    Discovered files are written to scripts/lint-*.txt.
    """
    tmp = Path(session.create_tmp())
    requirements = export_dev_requirements(session, tmp)
    session.install("-r", str(requirements))
    session.install("yamllint")
    session.install("prettier")

    # Run flake8
    session.log("Running flake8...")
    session.run("flake8", ".", "--exclude=" + ",".join(EXCLUDE_PATHS))

    # YAML formatting + linting
    yaml_files = discover_files(".", [".yaml", ".yml"], EXCLUDE_PATHS)
    yaml_list = Path("scripts/lint-yaml.txt")
    yaml_list.parent.mkdir(parents=True, exist_ok=True)
    yaml_list.write_text("\n".join(yaml_files))

    if yaml_files:
        session.log(
            f"Formatting {len(yaml_files)} YAML files with Prettier (via npx)...")
        session.run("npx", "prettier", "--write", *yaml_files, external=True)

        session.log(f"Running yamllint on {len(yaml_files)} YAML files...")
        session.run("yamllint", "-f", "parsable", *yaml_files)
    else:
        session.log("No YAML files found for yamllint.")

    # Markdown formatting + linting
    md_files = discover_files(".", [".md"], EXCLUDE_PATHS)
    md_list = Path("scripts/lint-md.txt")
    md_list.write_text("\n".join(md_files))

    if md_files:
        session.log(f"Formatting {len(md_files)} Markdown files with markdownlint --fix...")
        session.run("markdownlint", "--fix", *md_files, external=True)
    else:
        session.log("No Markdown files found for markdownlint.")
