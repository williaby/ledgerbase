# name = SECURITY.md
# description = Security policy and practices for the LedgerBase project
# category = security
# usage = Reference for users and contributors to understand security policies and procedures
# behavior = Outlines supported versions, vulnerability reporting, security practices, and policy enforcement
# inputs = none
# outputs = none
# dependencies = none
# author = LedgerBase Team
# last_modified = 2023-11-15
# changelog = Initial version

# Security Policy

This document outlines the security practices and processes for the LedgerBase project, aligned with the [OSSF Scorecard](https://github.com/ossf/scorecard) and [OpenSSF Best Practices Badge](https://openssf.org/best-practices-badge/) requirements.

## Supported Versions

We follow [Semantic Versioning](https://semver.org/) and maintain security support for the following release series:

| Version    | Supported      |
|------------|----------------|
| `>= 1.0.0` | ✅ Active      |
| `< 1.0.0`  | ❌ End-of-life |

Releases outside the supported range will not receive security updates. Users should upgrade to a supported version by following the [Upgrade Guide](docs/UPGRADE.md) in the repository.

## Reporting a Vulnerability

If you discover a security vulnerability in LedgerBase, please report it via one of the following channels:

1. **GitHub Security Advisory**: Open a confidential advisory in the [Security tab](https://github.com/williaby/ledgerbase/security/advisories).

2. **Encrypted Email**: Send an email to `security@williaby.io`, encrypted with the project PGP key .

-----BEGIN PGP PUBLIC KEY BLOCK-----
(Key ID: `9360A8293F1430EB3E88B99CB2C95364612BFFDF`)
-----END PGP PUBLIC KEY BLOCK-----


Please include in your report:
- Affected version(s)
- Detailed description and steps to reproduce
- Impact assessment
- Proof-of-concept or logs, if available

## CVE & Advisory Workflow

Once a vulnerability is verified:
1. Maintainers will request a CVE ID via GitHub’s integrated CVE assignment.
2. A fix will be developed, merged, and a Security Advisory published, including the CVE.
3. Release notes will reference the advisory and CVE for tracking.

### Acknowledgment & Response

- We will acknowledge receipt within **72 hours**.
- For critical issues, we aim to provide a mitigation or fix within **90 days** of acknowledgment.

## Security Contact

- **GitHub Team**: [@williaby/security](https://github.com/orgs/williaby/teams/security)
- **Email**: `security@williaby.io`

## Security Practices

We enforce comprehensive security measures across code, dependencies, infrastructure, and runtime environments:

- **Dependency Management**:
  - Dependencies are pinned in `pyproject.toml` and periodically reviewed.
  - Automated alerts and pull requests via Dependabot and `pip-audit`.

- **Static Analysis & SAST**:
  - **CodeQL**, **Semgrep**, **Ruff**, **Bandit**, and **Safety** scans run on every pull request.

- **Container Security & SBOM**:
  - **Trivy** scans container images in CI.
  - SBOMs generated with **CycloneDX (cyclonedx-py)** for each release.

- **Vulnerability Scanning & Testing**:
  - **Snyk** and **Codecov** integrated for continuous monitoring and coverage metrics.

- **Secrets Detection**:
  - `ggshield` (GitGuardian) and pre-commit hooks detect accidental commits of secrets.

- **Infrastructure Hardening**:
  - GitHub Actions workflows use `step-security/harden-runner@v2.11.1`, pinned to the specific SHA, to ensure runner environments are secured and up-to-date.

- **CI/CD Enforcement**:
  - All PRs must pass security checks (CodeQL, Semgrep, Trivy, Snyk, Safety, Bandit) in GitHub Actions before merging.

## Policy Enforcement

- Pull requests introducing security issues or failing automated checks will be blocked.
- Contributors must follow this policy; non-compliance may delay or reject contributions.

## Acknowledgements

We appreciate the work of security researchers, contributors, and the OpenSSF community for guidance and best practices.

---

_Last updated: November 15, 2023_
