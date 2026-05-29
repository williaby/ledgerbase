#!/usr/bin/env python3
"""Run license report via Nox for pre-commit compatibility."""

import shutil
import subprocess  # nosec: B404
import sys


def main() -> None:
    """Run license report via Nox and handle any errors.

    This function executes the license report using Nox through uv,
    and properly handles any subprocess execution errors.

    Validates executable paths before execution for security.
    """
    uv_path = shutil.which("uv")
    nox_path = shutil.which("nox")

    if uv_path is None:
        print("❌ uv executable not found in PATH")
        sys.exit(1)

    if nox_path is None:
        print("❌ Nox executable not found in PATH")
        sys.exit(1)

    try:
        subprocess.run(  # nosec: B603
            [
                uv_path,
                "run",
                nox_path,
                "-s",
                "license_report",
            ],
            check=True,
            shell=False,
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ License report failed with exit code {e.returncode}")
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()
