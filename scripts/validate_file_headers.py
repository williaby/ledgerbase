##: name = validate_file_headers.py
##: description = Validates structured file headers against annotation spec
##: category = correctness
##: usage = python scripts/validate_file_headers.py
##: behavior = Scans code files for metadata headers; reports issues
##: inputs = .py, .sh, .yml, .yaml, .toml files in project excluding Gitignore paths
##: outputs = stdout warnings and errors indicating header issues
##: dependencies = pydantic, pathspec
##: author = Byron Williams
##: last_modified = 2025-04-18
##: tags = validation, tooling, compliance
##: changelog = Added YAML-style header support; expanded VALID_KEYS; improved parsing

import shutil
from pathlib import Path
from typing import Any, ClassVar

import pathspec
from pydantic import BaseModel, ValidationError


# === CONFIGURATION ===
class Config:
    """Configuration options for file type inclusion and directory exclusion."""

    INCLUDE_EXTS: ClassVar[set[str]] = {".py", ".sh", ".yml", ".yaml", ".toml"}
    EXCLUDE_DIRS: ClassVar[set[str]] = {
        ".git",
        ".venv",
        "venv",
        ".nox",
        "node_modules",
        "build",
        "dist",
        ".git.bak/",
        "docs/build",
    }
    HEADER_STYLE_LIST_KEYS: ClassVar[set[str]] = {
        "inputs",
        "outputs",
        "dependencies",
        "tags",
    }
    VALID_KEYS: ClassVar[set[str]] = HEADER_STYLE_LIST_KEYS.union(
        {
            "name",
            "description",
            "category",
            "usage",
            "behavior",
            "author",
            "last_modified",
            "changelog",
        },
    )
    KEYVAL_LENGTH: ClassVar[int] = 2  # Named constant for key-value pair length


# === SCHEMA ===
class FileMetadata(BaseModel):
    """Structured metadata model for headers."""

    name: str
    description: str | None = None
    category: str | None = None
    usage: str | None = None
    behavior: str | None = None
    author: str | None = None
    last_modified: str | None = None
    changelog: str | None = None
    dependencies: list[str] | None = None
    tags: list[str] | None = None
    inputs: list[str] | None = None
    outputs: list[str] | None = None


# === UTILITIES ===
def _is_command_available(command: str) -> bool:
    """Check if a command is available in the system PATH.

    Args:
        command: The command to check

    Returns:
        True if the command is available, False otherwise

    """
    return shutil.which(command) is not None


def load_gitignore_spec(path: Path = Path(".gitignore")) -> pathspec.PathSpec:
    """Load `.gitignore` rules into a pathspec matcher."""
    lines = []
    try:
        with path.open(encoding="utf-8") as f:
            lines = f.readlines()
    except (OSError, PermissionError) as e:
        print(f"⚠️  Warning: Could not read .gitignore file: {e}")
    return pathspec.PathSpec.from_lines("gitwildmatch", lines)


def parse_header_metadata(path: Path) -> dict[str, Any]:
    """Parse the structured metadata block from the top of a file.

    Supports both Python-style (`##:`) and shell/YAML-style (`# `) headers.

    Returns:
        A dict of parsed metadata values, strings or lists.

    """
    metadata: dict[str, Any] = {}
    try:
        with path.open(encoding="utf-8") as file:
            for line in file:
                stripped = line.lstrip()
                if stripped.startswith("##:"):
                    content = stripped[3:]
                elif stripped.startswith("# "):
                    content = stripped[2:]
                else:
                    break
                keyval = content.strip().split("=", 1)
                if len(keyval) != Config.KEYVAL_LENGTH:
                    continue
                key, val = keyval
                key = key.strip()
                val = val.strip(" '\"")
                if key not in Config.VALID_KEYS:
                    continue
                if key in Config.HEADER_STYLE_LIST_KEYS:
                    # comma-separated list
                    metadata[key] = [v.strip() for v in val.split(",")]
                else:
                    metadata[key] = val
    except (OSError, PermissionError) as e:
        print(f"⚠️  Warning: Could not read file {path}: {e}")
    return metadata


# === MAIN ===
def main() -> None:
    """Check source files for structured headers and validate against FileMetadata model."""  # noqa: E501
    base_dir = Path()
    gitignore = load_gitignore_spec()

    for file_path in base_dir.rglob("*"):
        try:
            if file_path.is_dir():
                continue
        except PermissionError:
            print(f"⚠️  Warning: Permission denied accessing {file_path}")
            continue
        if file_path.suffix not in Config.INCLUDE_EXTS:
            continue
        if any(part in Config.EXCLUDE_DIRS for part in file_path.parts):
            continue
        if gitignore.match_file(str(file_path)):
            continue

        metadata = parse_header_metadata(file_path)
        if not metadata:
            print(f"⚠️  Warning: {file_path} is missing header metadata.")
            continue

        try:
            FileMetadata.model_validate(metadata)
        except ValidationError as e:
            print(f"❌ Error in {file_path}: {e}")
            continue

        # No longer checking for noqa: E265 on metadata lines


if __name__ == "__main__":
    main()
