#!/usr/bin/env python3
##: name = generate_license_report.py
##: description = Generates license report via Nox and outputs the contents of license-report.json # noqa: E501
##: category = licensing
##: usage = python scripts/generate_license_report.py
##: behavior = Runs license report and displays the generated JSON file
##: inputs = None
##: outputs = license-report.json, stdout
##: dependencies = nox, poetry
##: author = Byron Williams
##: last_modified = 2025-04-20
##: tags = licensing, reporting, compliance
##: changelog = Address Bandit and Ruff issues
"""Run license report via Nox and output the contents of license-report.json."""

import shutil
import subprocess  # nosec B404
import sys
from pathlib import Path

REPORT_PATH = Path("license-report.json")


def _is_command_available(command: str) -> bool:
    """Check if a command is available in the system PATH.

    Args:
        command: The command to check

    Returns:
        True if the command is available, False otherwise

    """
    return shutil.which(command) is not None


def main() -> None:
    """Run license report via Nox and output the contents of license-report.json.

    This function executes the license report using Nox through Poetry,
    and properly handles any command execution errors.

    The function checks if the report was generated successfully and
    outputs its contents to stdout.
    """
    poetry_cmd = "poetry"
    nox_cmd = "nox"

    if not _is_command_available(poetry_cmd):
        print("❌ Poetry command not found in PATH")
        sys.exit(1)

    if not _is_command_available(nox_cmd):
        print("❌ Nox command not found in PATH")
        sys.exit(1)

    cmd_args = [poetry_cmd, "run", nox_cmd, "-s", "license_report"]

    try:
        result = subprocess.run(  # nosec B603
            cmd_args,
            check=False,
            capture_output=False,
            shell=False,
        )
        if result.returncode != 0:
            print("❌ Failed to generate license report.")
            sys.exit(result.returncode)
    except (subprocess.SubprocessError, OSError) as e:
        print(f"❌ Error executing command: {e}")
        sys.exit(1)

    if REPORT_PATH.exists():
        print(f"✅ License report generated at {REPORT_PATH.resolve()}\n")
        print(REPORT_PATH.read_text())
    else:
        print("⚠️ license-report.json not found.")
        sys.exit(1)


if __name__ == "__main__":
    main()
