from pathlib import Path
from typing import ClassVar

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
            "dependencies",
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
    dependencies: list[str] | None = None
    tags: list[str] | None = None
    inputs: list[str] | None = None
    outputs: list[str] | None = None


# === UTILITIES ===
def load_gitignore_spec(path: Path = Path(".gitignore")) -> pathspec.PathSpec:
    """Load `.gitignore` rules into a pathspec matcher."""
    with path.open(encoding="utf-8") as f:
        lines = f.readlines()
    return pathspec.PathSpec.from_lines("gitwildmatch", lines)


def parse_header_metadata(path: Path) -> dict[str, str | list[str]]:
    """Parse the structured comment metadata block from the top of a file.

    Returns
    -------
    dict
        A dictionary of parsed metadata. Values are either strings or lists of strings.

    """
    metadata: dict[str, str | list[str]] = {}
    with path.open(encoding="utf-8") as file:
        for line in file:
            if not line.strip().startswith("##:"):
                break
            keyval = line[3:].strip().split("=", 1)
            if len(keyval) == Config.KEYVAL_LENGTH:
                key, val = keyval
                key = key.strip()
                val = val.strip(" '\"")
                if key in Config.HEADER_STYLE_LIST_KEYS:
                    metadata[key] = [v.strip() for v in val.split(",")]
                else:
                    metadata[key] = val
    return metadata


# === MAIN ===
def main() -> None:
    """Check source files for structured headers and validate against FileMetadata model."""  # noqa: E501
    base_dir = Path()
    spec = load_gitignore_spec()

    for file_path in base_dir.rglob("*"):
        if file_path.is_dir():
            continue
        if file_path.suffix not in Config.INCLUDE_EXTS:
            continue
        if any(part in Config.EXCLUDE_DIRS for part in file_path.parts):
            continue
        if spec.match_file(str(file_path)):
            continue

        metadata = parse_header_metadata(file_path)
        if not metadata:
            print(f"⚠️  Warning: {file_path} is missing header metadata.")
            continue

        try:
            # Validate metadata keys and values against the FileMetadata model
            FileMetadata.parse_obj(metadata)
        except ValidationError as e:
            print(f"❌ Error in {file_path}: {e}")
            continue

        for line_num, line in enumerate(
            file_path.read_text(encoding="utf-8").splitlines(),
            1,
        ):
            if line.strip().startswith("##:") and "# noqa: E265" not in line:
                print(
                    f"⚠️  Warning: {file_path}:{line_num} missing "
                    f"'# noqa: E265' on metadata line",
                )
                break
