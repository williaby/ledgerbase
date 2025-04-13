import csv
from pathlib import Path

import pathspec

# === CONFIGURATION ===
INCLUDE_EXTS = {".py", ".sh", ".yml", ".yaml", ".toml"}
HARDCODED_EXCLUDE_DIRS = {
    ".git",
    ".git.bak",
    ".venv",
    ".nox",
    "venv",
    "__pycache__",
    "node_modules",
    "build",
    "docs/build",
}
OUTPUT_CSV = Path("scripts/unannotated_files.csv")

# === Map file extension to header style ===
HEADER_STYLE_MAP = {".py": "##:", ".sh": "##:", ".yml": "#", ".yaml": "#", ".toml": "#"}


# === LOAD .gitignore USING PATHSPEC ===
def load_gitignore_spec(path=".gitignore"):
    try:
        with open(path) as f:
            lines = f.readlines()
        return pathspec.PathSpec.from_lines("gitwildmatch", lines)
    except FileNotFoundError:
        print(".gitignore not found. Continuing without it.")
        return pathspec.PathSpec.from_lines("gitwildmatch", [])


# === MAIN FUNCTION ===
def main():
    base_dir = Path(".")
    spec = load_gitignore_spec()
    output_list = []

    for file_path in base_dir.rglob("*"):
        try:
            if not file_path.is_file():
                continue

            rel_path = file_path.relative_to(base_dir)

            # Skip excluded file types and folders
            if (
                file_path.suffix not in INCLUDE_EXTS
                or spec.match_file(str(rel_path))
                or any(part in HARDCODED_EXCLUDE_DIRS for part in file_path.parts)
            ):
                continue

            ext = file_path.suffix
            header_style = HEADER_STYLE_MAP.get(ext, "UNKNOWN")

            output_list.append(
                {
                    "name": file_path.name,
                    "file_type": ext,
                    "header_style": header_style,
                    "path": str(file_path.resolve()),
                }
            )

        except PermissionError:
            print(f"Permission denied: {file_path}")
        except Exception as e:
            print(f"Error accessing {file_path}: {e}")

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["name", "file_type", "header_style", "path"]
        )
        writer.writeheader()
        writer.writerows(output_list)

    print(f"{len(output_list)} files written to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
