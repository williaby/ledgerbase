#!/usr/bin/env python
"""
A script to verify that the requirements.txt file exists.
Intended for use as a local pre-commit hook.
"""

import os
import sys


def main():
    # Define the path to the requirements file
    requirements_file = "requirements.txt"

    # Check if the requirements.txt file exists in the current directory
    if not os.path.isfile(requirements_file):
        print(f"WARNING: {requirements_file} is missing!")
        # Exit with 1 to indicate failure (this will block the commit).
        # Change to sys.exit(0) if you prefer only to warn without blocking.
        sys.exit(1)
    # File exists; exit successfully.
    sys.exit(0)


if __name__ == "__main__":
    main()
