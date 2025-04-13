#!/usr/bin/env python3
##: name = fix_metadata_noqa.py  # noqa: E265
##: description = Adds `# noqa: E265` to structured metadata lines starting with `##:` in Python files.  # noqa: E265
##: category = dev  # noqa: E265
##: usage = python scripts/fix_metadata_noqa.py path/to/file.py  # noqa: E265
##: behavior = Modifies the file in place by appending `# noqa: E265` to all applicable lines.  # noqa: E265
##: inputs = Python source file with structured metadata comments  # noqa: E265
##: outputs = The same file, updated to comply with flake8 E265 linting rules  # noqa: E265
##: author = Byron Williams  # noqa: E265
import sys
from pathlib import Path


def fix_metadata_noqa(file_path: str) -> str:
    path = Path(file_path)

    if not path.exists() or not path.is_file():
        return f"❌ Error: {file_path} does not exist or is not a file."

    if path.suffix != ".py":
        return f"⚠️ Skipped: {file_path} is not a Python (.py) file."

    lines = path.read_text(encoding="utf-8").splitlines()
    updated_lines = []
    modified = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("##:") and "# noqa: E265" not in stripped:
            updated_line = line.rstrip() + "  # noqa: E265"
            updated_lines.append(updated_line)
            modified = True
        else:
            updated_lines.append(line)

    if modified:
        path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")
        return f"✅ Fixed: {file_path} updated with missing '# noqa: E265'"
    else:
        return f"✅ No changes: {file_path} already compliant."


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/fix_metadata_noqa.py <file.py>")
        sys.exit(1)

    result = fix_metadata_noqa(sys.argv[1])
    print(result)
