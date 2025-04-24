#!/usr/bin/env python
"""A script to verify that the requirements.txt file exists.

Intended for use as a local pre-commit hook.
"""

import sys
from pathlib import Path


def main() -> None:
    """Check if requirements.txt exists in the current directory.

    If the file is missing, print a warning and exit with
    status code 1 to block the commit.
    """
    requirements_file = Path("requirements.txt")

    if not requirements_file.is_file():
        print(f"WARNING: {requirements_file} is missing!")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
