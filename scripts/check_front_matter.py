#!/usr/bin/env python3
"""---
title: "Front Matter Validator"
name: "check_front_matter.py"
description: "Validates YAML front-matter in all supported files."
category: script
usage: "python check_front_matter.py"
behavior: "Checks all files for valid front-matter; exits with code 1 on error"
inputs: "Files with extensions: md, py, sh, yml, yaml, toml"
outputs: "Validation error messages to stdout"
dependencies: "yaml"
author: "Byron Williams"
last_modified: "2023-11-15"
changelog: "Updated to match annotation_spec.md requirements"
tags: [validation, front-matter]
---

Validate YAML front-matter in all supported files.

This script scans all supported file types in the current directory and its
subdirectories, extracts YAML front-matter, and validates that it contains
all required fields with proper formatting.

Required fields are defined in the REQUIRED constant and the date format
for 'last_modified' field is validated against YYYY-MM-DD pattern.
"""

import re
import sys
from pathlib import Path

import yaml

# Constants
FRONT_MATTER_PARTS = 3  # Number of parts when splitting by '---' markers
REQUIRED = [
    "title", "name", "description", "category", "usage", "behavior",
    "inputs", "outputs", "dependencies", "author", "last_modified", "changelog",
]
DATE_RX = re.compile(r"^\d{4}-\d{2}-\d{2}$")

def extract_front_matter(text: str) -> str | None:
    """Extract YAML front-matter from text content.

    Looks for content enclosed between '---' markers at the beginning of the text.

    Args:
        text (str): The text content to extract front-matter from.

    Returns:
        str or None: The extracted front-matter content if found, None otherwise.

    """
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= FRONT_MATTER_PARTS:
            return parts[1]
    return None

def validate_meta(meta: dict, path: Path) -> list[str]:
    """Validate metadata against required fields and format rules.

    Checks if all required fields are present in the metadata and validates
    the format of the 'last_modified' field against YYYY-MM-DD pattern.

    Args:
        meta (dict): The metadata dictionary to validate.
        path (Path): The path to the file being validated, used for error messages.

    Returns:
        list: A list of error messages, empty if validation passed.

    """
    errs = [f"Missing '{key}' in {path}" for key in REQUIRED if key not in meta]
    lm = meta.get("last_modified","")
    if lm and not DATE_RX.match(str(lm)):
        errs.append(f"Bad date format in {path}: last_modified='{lm}'")
    return errs

def main() -> None:
    """Execute the front-matter validation process.

    Scans all supported file types in the current directory and its subdirectories,
    extracts and validates YAML front-matter, and reports any validation errors.

    Supported file extensions: md, py, sh, yml, yaml, toml

    Returns:
        None

    Raises:
        SystemExit: With exit code 1 if validation errors are found, 0 otherwise.

    """
    failures = []
    for ext in ("md","py","sh","yml","yaml","toml"):
        for path in Path("../src").rglob(f"*.{ext}"):
            text = path.read_text()
            fm = extract_front_matter(text)
            if not fm:
                failures.append(f"No front-matter in {path}")
                continue
            try:
                meta = yaml.safe_load(fm)
            except yaml.YAMLError as e:
                failures.append(f"YAML parse error in {path}: {e}")
                continue
            failures += validate_meta(meta, path)
    if failures:
        print("Front-matter validation errors:")
        for e in failures:
            print(" -", e)
        sys.exit(1)
    print("All front-matter blocks valid.")
    sys.exit(0)

if __name__ == "__main__":
    main()
