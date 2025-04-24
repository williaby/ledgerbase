#!/usr/bin/env python3
"""---
title: "Markdown Header Converter"
name: "convert_headers.py"
description: "Converts old-style metadata headers to YAML front-matter in Markdown"
    " files."
category: script
usage: "python convert_headers.py"
behavior: "Scans Markdown files, converts old metadata to YAML front-matter, removes"
    " original headers"
inputs: "Markdown files in docs/ directory"
outputs: "Updated Markdown files with YAML front-matter"
dependencies: "pathlib, re"
author: "Byron Williams"
last_modified: "2023-11-15"
changelog: "Updated to match annotation_spec.md requirements"
tags: [conversion, front-matter]
---

Scan all Markdown files in docs/, parse old metadata lines (`##:` or `# key = value`),
emit a YAML front-matter block, and remove the original headers.

This script identifies Markdown files with old-style metadata headers and converts them
to the new YAML front-matter format as specified in annotation_spec.md. It preserves
all existing metadata while ensuring the output follows the project's documentation
standards.
"""

import re
import sys
from pathlib import Path


def parse_metadata(lines: list[str]) -> tuple[dict[str, str], list[int]]:
    """Parse old-style metadata lines from a list of text lines.

    Extracts metadata from lines starting with '##:' or '# key = value' format
    and tracks which lines were consumed by the metadata parsing.

    Args:
        lines (list): List of strings representing lines of text to parse.

    Returns:
        tuple: A tuple containing:
            - dict: Extracted metadata as key-value pairs.
            - list: Indices of lines that were consumed by metadata parsing.

    """
    meta = {}
    pattern = re.compile(r"^(?:##:|#)\s*(\w+)\s*=\s*(.*)$")
    consumed = []
    for i, line in enumerate(lines):
        m = pattern.match(line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            meta[key] = val
            consumed.append(i)
        elif consumed and not line.strip():
            # blank line after metadata block
            consumed.append(i)
            break
        elif consumed:
            break
    return meta, consumed

def yaml_block(meta: dict[str, str], path: Path) -> list[str]:
    """Generate a YAML front-matter block from metadata.

    Creates a properly formatted YAML front-matter block with all required fields,
    using fallback values where necessary.

    Args:
        meta (dict): Metadata key-value pairs to include in the YAML block.
        path (Path): Path object for the file being processed, used for fallback title.

    Returns:
        list: List of strings representing lines of the YAML front-matter block.

    """
    # Fallback title
    if "title" not in meta:
        meta["title"] = path.stem.replace("_", " ").title()
    # Ensure required fields exist
    required = [
        "title", "name", "description", "category", "author",
        "last_modified", "changelog",
    ]
    for k in required:
        meta.setdefault(k, '""')
    block = ["---"]
    for k, v in meta.items():
        block.append(f"{k}: {v}")
    block.append("---")
    return block

def process_file(path: Path) -> bool:
    """Process a single Markdown file to convert old metadata to YAML front-matter.

    Reads the file, extracts old-style metadata, removes the original metadata lines,
    and prepends a new YAML front-matter block.

    Args:
        path (Path): Path object for the file to process.

    Returns:
        bool: True if the file was converted, False if no metadata was found.

    """
    text = path.read_text().splitlines()
    meta, consumed = parse_metadata(text)
    if not meta:
        return False
    # Remove old metadata lines
    rest = [ln for i,ln in enumerate(text) if i not in consumed]
    # Prepend YAML block
    new = [*yaml_block(meta, path), "", *rest]
    path.write_text("\n".join(new))
    return True

def main() -> None:
    """Execute the metadata conversion process.

    Scans all Markdown files in the docs/ directory, converts old-style metadata
    to YAML front-matter, and reports the results.

    Returns:
        None

    Raises:
        SystemExit: With exit code 0 if files were converted, 1 if no files needed
            conversion.

    """
    docs = Path("docs")
    converted = [md for md in docs.rglob("*.md") if process_file(md)]
    if converted:
        print(f"Converted front-matter in {len(converted)} file(s):")
        for p in converted:
            print(" -", p)
        sys.exit(0)
    else:
        print("No old metadata found to convert.")
        sys.exit(1)

if __name__ == "__main__":
    main()
