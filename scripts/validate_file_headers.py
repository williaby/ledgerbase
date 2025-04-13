import re
from pathlib import Path
from typing import Dict, List, Optional, Union

import pathspec
from pydantic import BaseModel, ValidationError


# === CONFIGURATION ===
class Config:
    INCLUDE_EXTS = {".py", ".sh", ".yml", ".yaml", ".toml"}
    EXCLUDE_DIRS = {
        ".git",
        ".venv",
        "venv",
        ".nox",
        "node_modules",
        "build",
        "docs/build",
    }
    HEADER_STYLE_LIST_KEYS = {"inputs", "outputs", "dependencies", "tags"}
    VALID_KEYS = HEADER_STYLE_LIST_KEYS.union(
        {
            "name",
            "description",
            "category",
            "usage",
            "behavior",
            "author",
            "last_modified",
        }
    )


# === SCHEMA ===
class FileMetadata(BaseModel):
    name: str
    description: str
    category: Optional[str]
    usage: Optional[str]
    behavior: Optional[str]
    inputs: Optional[List[str]]
    outputs: Optional[List[str]]
    dependencies: Optional[List[str]]
    author: Optional[str]
    last_modified: Optional[str]
    tags: Optional[List[str]]


# === UTILITIES ===
def load_gitignore_spec(path: str = ".gitignore") -> pathspec.PathSpec:
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
        return pathspec.PathSpec.from_lines("gitwildmatch", lines)
    except FileNotFoundError:
        return pathspec.PathSpec.from_lines("gitwildmatch", [])
    except (OSError, UnicodeDecodeError) as e:
        print(f"Warning: Could not read {path}: {e}")
        return pathspec.PathSpec.from_lines("gitwildmatch", [])


def parse_header_metadata(path: Path) -> Dict[str, Union[str, List[str]]]:
    """
    Parses the structured comment metadata block from the top of a file.

    Returns:
        A dictionary of parsed metadata. Values are either strings or lists of strings.
    """
    metadata: Dict[str, Union[str, List[str]]] = {}

    try:
        with path.open(encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()

                # Skip non-comment lines
                if not stripped.startswith("#"):
                    if stripped:  # Stop if line is non-empty and not a comment
                        break
                    continue

                # Match lines like: ##: key = value
                match = re.match(r"#*:?[\s]*([\w_]+)\s*=\s*(.+)", stripped)
                if not match:
                    continue

                key, value = match.groups()
                key = key.strip()
                value = value.strip(" '\"")

                if key not in Config.VALID_KEYS:
                    continue

                if key in Config.HEADER_STYLE_LIST_KEYS:
                    metadata[key] = [v.strip() for v in value.split(",")]
                else:
                    metadata[key] = value

    except (OSError, UnicodeDecodeError) as e:
        print(f"Error reading {path}: {e}")

    return metadata


# === MAIN ===
def main():
    base_dir = Path(".")
    spec = load_gitignore_spec()
    total, valid = 0, 0
    invalid = []

    for file_path in base_dir.rglob("*"):
        rel_path = file_path.relative_to(base_dir)

        if (
            not file_path.is_file()
            or file_path.suffix not in Config.INCLUDE_EXTS
            or spec.match_file(str(rel_path))
            or set(file_path.parts).intersection(Config.EXCLUDE_DIRS)
        ):
            continue

        total += 1
        metadata = parse_header_metadata(file_path)

        if not metadata:
            invalid.append((file_path, "Missing or empty header"))
            continue

        try:
            FileMetadata(**metadata)
            valid += 1
        except ValidationError as ve:
            error_detail = "; ".join(
                [f"{err['loc'][0]}: {err['msg']}" for err in ve.errors()]
            )
            invalid.append((file_path, f"Validation error: {error_detail}"))
            continue

        # Soft check: warn if Python metadata lines are missing # noqa: E265
        if file_path.suffix == ".py":
            with file_path.open(encoding="utf-8") as f:
                for line_num, line in enumerate(f, start=1):
                    if line.strip().startswith("##:") and "# noqa: E265" not in line:
                        print(
                            f"⚠️  Warning: {file_path}:{line_num} missing '# noqa: E265' on metadata line"
                        )
                        break

    print(f"\nScanned {total} eligible files.")
    print(f"✅ {valid} files passed validation.")
    print(f"❌ {len(invalid)} files failed:\n")

    for path, reason in invalid:
        print(f"- {path}: {reason}")


if __name__ == "__main__":
    main()
