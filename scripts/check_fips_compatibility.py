#!/usr/bin/env python3
##: name = check_fips_compatibility.py
##: description = Scan Python sources for FIPS 140-2/140-3 incompatible cryptography.
##: category = security
##: usage = python scripts/check_fips_compatibility.py [options] [paths...]
##: behavior = Reports non-FIPS crypto as text or JSON; exits non-zero on errors.
##: inputs = Python source files under src/ (and tests/ with --include-tests)
##: outputs = Text or JSON findings on stdout
##: dependencies = none (standard library only)
##: author = LedgerBase Team
##: tags = security, fips, compliance
"""FIPS 140-2/140-3 compatibility checker for LedgerBase.

Scans Python sources for cryptographic usage that is not permitted in FIPS
mode, such as MD5 or SHA-1 used for security, the non-validated ``Crypto``
package, or the ``random`` module for security-sensitive values, and reports
the findings as human-readable text or JSON.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

ERROR = "error"
WARNING = "warning"
INFO = "info"

# Hash algorithms that are not FIPS-approved when used for security.
NON_APPROVED_HASHES = {"md5", "sha1", "md4", "ripemd160"}
# Default and test scan roots.
DEFAULT_PATHS = ("src",)
TEST_PATHS = ("tests",)


@dataclass
class Finding:
    """A single FIPS compatibility finding."""

    file: str
    line: int
    severity: str
    code: str
    message: str
    hint: str


@dataclass
class Report:
    """Aggregated FIPS findings and a scan summary."""

    findings: list[Finding] = field(default_factory=list)
    files_scanned: int = 0

    def add(self, finding: Finding) -> None:
        """Record a finding."""
        self.findings.append(finding)

    def count(self, severity: str) -> int:
        """Return the number of findings at the given severity."""
        return sum(1 for finding in self.findings if finding.severity == severity)

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serialisable representation of the report."""
        return {
            "summary": {
                "errors": self.count(ERROR),
                "warnings": self.count(WARNING),
                "info": self.count(INFO),
                "files_scanned": self.files_scanned,
            },
            "findings": [
                {
                    "file": finding.file,
                    "line": finding.line,
                    "severity": finding.severity,
                    "code": finding.code,
                    "message": finding.message,
                    "hint": finding.hint,
                }
                for finding in self.findings
            ],
        }


def _uses_security_opt_out(call: ast.Call) -> bool:
    """Return True if the call passes ``usedforsecurity=False``."""
    return any(
        keyword.arg == "usedforsecurity"
        and isinstance(keyword.value, ast.Constant)
        and keyword.value.value is False
        for keyword in call.keywords
    )


def _check_hashlib_new(call: ast.Call, path: Path, report: Report) -> None:
    """Flag ``hashlib.new("md5")``-style calls with a non-approved algorithm."""
    if not call.args:
        return
    first = call.args[0]
    if (
        isinstance(first, ast.Constant)
        and isinstance(first.value, str)
        and first.value.lower() in NON_APPROVED_HASHES
        and not _uses_security_opt_out(call)
    ):
        report.add(
            Finding(
                file=str(path),
                line=call.lineno,
                severity=ERROR,
                code="FIPS001",
                message=f"Hash algorithm '{first.value}' is not FIPS-approved.",
                hint="Use a SHA-2/SHA-3 algorithm, or pass usedforsecurity=False "
                "for non-security use.",
            ),
        )


def _check_call(call: ast.Call, path: Path, report: Report) -> None:
    """Inspect a call node for FIPS-incompatible hash usage."""
    if not isinstance(call.func, ast.Attribute):
        return
    name = call.func.attr
    lowered = name.lower()
    if lowered in NON_APPROVED_HASHES and not _uses_security_opt_out(call):
        report.add(
            Finding(
                file=str(path),
                line=call.lineno,
                severity=ERROR,
                code="FIPS001",
                message=f"Hash algorithm '{name}' is not FIPS-approved for "
                "security use.",
                hint="Use sha256/sha384/sha512, or pass usedforsecurity=False "
                "for non-security use.",
            ),
        )
    elif lowered == "new":
        _check_hashlib_new(call, path, report)


def _imported_modules(node: ast.Import | ast.ImportFrom) -> list[str]:
    """Return the top-level module names referenced by an import node."""
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    return [node.module] if node.module else []


def _check_import(
    node: ast.Import | ast.ImportFrom,
    path: Path,
    report: Report,
) -> None:
    """Flag imports of non-FIPS-validated or risky modules."""
    for module in _imported_modules(node):
        root = module.split(".")[0]
        if root == "Crypto":
            report.add(
                Finding(
                    file=str(path),
                    line=node.lineno,
                    severity=WARNING,
                    code="FIPS010",
                    message="The 'Crypto' (pycryptodome) package is not "
                    "FIPS-validated.",
                    hint="Prefer the 'cryptography' package backed by a "
                    "FIPS-validated OpenSSL.",
                ),
            )
        elif root == "random":
            report.add(
                Finding(
                    file=str(path),
                    line=node.lineno,
                    severity=WARNING,
                    code="FIPS011",
                    message="The 'random' module is not suitable for "
                    "security-sensitive values.",
                    hint="Use the 'secrets' module or os.urandom for "
                    "security-sensitive randomness.",
                ),
            )


def scan_file(path: Path, report: Report) -> None:
    """Scan a single Python file and append any findings to the report."""
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as exc:
        report.add(
            Finding(
                file=str(path),
                line=0,
                severity=WARNING,
                code="FIPS000",
                message=f"Could not read file: {exc}",
                hint="Ensure the file is readable.",
            ),
        )
        return
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        report.add(
            Finding(
                file=str(path),
                line=exc.lineno or 0,
                severity=WARNING,
                code="FIPS000",
                message=f"Could not parse file: {exc.msg}",
                hint="Fix the syntax error so the file can be analysed.",
            ),
        )
        return
    report.files_scanned += 1
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            _check_call(node, path, report)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            _check_import(node, path, report)


def iter_python_files(bases: Iterable[Path]) -> Iterator[Path]:
    """Yield Python files under the given files or directories."""
    for base in bases:
        if base.is_file() and base.suffix == ".py":
            yield base
        elif base.is_dir():
            yield from sorted(base.rglob("*.py"))


def render_text(report: Report, *, fix_hints: bool) -> str:
    """Render findings and a summary as human-readable text."""
    lines: list[str] = []
    for finding in report.findings:
        lines.append(
            f"{finding.severity.upper()} {finding.code} "
            f"{finding.file}:{finding.line} {finding.message}",
        )
        if fix_hints and finding.hint:
            lines.append(f"    hint: {finding.hint}")
    lines.append(
        f"FIPS summary: {report.count(ERROR)} errors, "
        f"{report.count(WARNING)} warnings, {report.count(INFO)} info "
        f"({report.files_scanned} files scanned)",
    )
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Check Python sources for FIPS 140-2/140-3 compatibility.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument(
        "--fix-hints",
        action="store_true",
        help="Include remediation hints in text output.",
    )
    parser.add_argument(
        "--include-tests",
        action="store_true",
        help="Also scan the tests directory.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as failures.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Optional explicit files or directories to scan.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run the FIPS compatibility check and return a process exit code."""
    args = parse_args(argv)
    if args.paths:
        bases = [Path(item) for item in args.paths]
    else:
        roots = list(DEFAULT_PATHS)
        if args.include_tests:
            roots += list(TEST_PATHS)
        bases = [Path(item) for item in roots]

    report = Report()
    for file_path in iter_python_files(bases):
        scan_file(file_path, report)

    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(render_text(report, fix_hints=args.fix_hints))

    if report.count(ERROR) or (args.strict and report.count(WARNING)):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
