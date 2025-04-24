#!/usr/bin/env python3
"""Run license report via Nox for pre-commit compatibility."""

import subprocess  # nosec: B404
import sys
from pathlib import Path


def main() -> None:
    """Run license report via Nox and handle any errors.

    This function executes the license report using Nox through Poetry,
    and properly handles any subprocess execution errors.

    Validates executable paths before execution for security.
    """
    # Define the paths to validate
    poetry_path = "/home/byron/.local/bin/poetry"
    nox_path = "/home/byron/.local/bin/nox"

    # Validate executable paths exist
    if not Path(poetry_path).is_file():
        print(f"❌ Poetry executable not found at {poetry_path}")
        sys.exit(1)

    if not Path(nox_path).is_file():
        print(f"❌ Nox executable not found at {nox_path}")
        sys.exit(1)

    try:
        subprocess.run(  # nosec: B603
            [
                poetry_path,
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
