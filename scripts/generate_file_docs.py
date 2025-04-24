##: name = generate_file_docs.py
##: description = Batch generator for .rst documentation files from annotated source files using Flask templates for safe rendering  # noqa: E501
##: category = maintainability
##: usage = python generate_file_docs.py
##: behavior = Discovers annotated source files, extracts header metadata, and renders categorized .rst files with Flask's template engine  # noqa: E501
##: inputs = None; uses project directory structure
##: outputs = .rst files under docs/source/rst/<category> and index.rst files per category  # noqa: E501
##: dependencies = Flask, validate_file_headers, pathlib, collections
##: author = Byron Williams
##: last_modified = 2023-04-19
##: tags = docs, automation, flask
##: changelog = - Replaced direct Jinja2 Environment with Flask app.jinja_env for safe autoescaping # noqa: E501
#             - Added Flask app context to template rendering; updated template extensions to .html # noqa: E501

"""Script to batch-generate categorized .rst documentation files using Flask's rendering for autoescaping."""  # noqa: E501

from collections import defaultdict
from pathlib import Path

from validate_file_headers import load_gitignore_spec, parse_header_metadata

from flask import Flask, render_template

# Initialize Flask app to leverage its Jinja environment with autoescaping
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = PROJECT_ROOT / "docs" / "source" / "_templates"
app = Flask(__name__, template_folder=str(TEMPLATE_PATH))

# === Configuration ===
RST_ROOT = PROJECT_ROOT / "docs" / "source" / "rst"
CATEGORY_PATHS: dict[str, Path] = {
    "etl": RST_ROOT / "etl",
    "budget": RST_ROOT / "budget",
    "api": RST_ROOT / "api",
    "ci": RST_ROOT / "dev",
    "setup": RST_ROOT / "dev",
    "dev": RST_ROOT / "dev",
    "usage": RST_ROOT / "usage",
    "docs": RST_ROOT / "docs",
    "misc": RST_ROOT / "misc",
}
TEMPLATE_MAPPING: dict[str, str] = {
    ".sh": "script_template.html",
    ".py": "python_template.html",
    ".yaml": "config_template.html",
    ".yml": "config_template.html",
    ".toml": "config_template.html",
}
DEFAULT_TEMPLATE = "script_template.html"
TOCTREE_MAXDEPTH = 1  # Avoid magic values


def discover_annotated_files() -> list[Path]:
    """Return a list of annotated source files with supported extensions."""
    include_exts = {".py", ".sh", ".yml", ".yaml", ".toml"}
    exclude_dirs = {
        ".git",
        ".venv",
        "venv",
        ".nox",
        "node_modules",
        "build",
        "docs/build",
    }
    gitignore = load_gitignore_spec(PROJECT_ROOT / ".gitignore")

    return [
        p
        for p in PROJECT_ROOT.rglob("*")
        if (
            p.suffix in include_exts
            and p.is_file()
            and not set(p.parts).intersection(exclude_dirs)
            and not gitignore.match_file(str(p))
        )
    ]


def main() -> None:
    """Generate .rst files for each annotated source file and write category indexes."""
    print("📁 Regenerating categorized documentation files...")

    index_map: dict[Path, list[str]] = defaultdict(list)
    try:
        files = discover_annotated_files()
    except (FileNotFoundError, PermissionError, OSError) as e:
        print(f"❌ Error discovering files: {e}")
        return

    for file in files:
        try:
            meta = parse_header_metadata(file)
            if not meta or "name" not in meta or "description" not in meta:
                continue

            category = meta.get("category", "misc")
            out_dir = CATEGORY_PATHS.get(category, CATEGORY_PATHS["misc"])
            out_dir.mkdir(parents=True, exist_ok=True)

            template_name = TEMPLATE_MAPPING.get(
                file.suffix,
                DEFAULT_TEMPLATE,
            )
            # Safely render within Flask app context
            with app.app_context():
                rendered = render_template(
                    template_name,
                    **meta,
                    title=Path(meta["name"]).stem,
                )

            rst_path = out_dir / f"{Path(meta['name']).stem}.rst"
            rst_path.write_text(rendered, encoding="utf-8")
            index_map[out_dir].append(Path(meta["name"]).stem)
        except (OSError, KeyError, ValueError, TypeError) as e:
            print(f"❌ Error processing {file}: {e}")
            continue

    # Write index.rst for each category
    for folder, entries in index_map.items():
        try:
            index_path = folder / "index.rst"
            title = folder.name.capitalize()
            lines = [
                f"{title} Documentation",
                "=" * (len(title) + 13),
                "",
                ".. toctree::",
                f"   :maxdepth: {TOCTREE_MAXDEPTH}",
                "",
            ]
            lines.extend([f"   {entry}" for entry in sorted(entries)])
            content = "\n".join(lines) + "\n"
            index_path.write_text(content, encoding="utf-8")
            print(f"📚 Index written: {index_path}")
        except (PermissionError, OSError) as e:
            print(f"❌ Error writing index for {folder}: {e}")
            continue

    total = sum(len(v) for v in index_map.values())
    print(f"✅ {total} .rst files generated across {len(index_map)} categories.")


if __name__ == "__main__":
    main()
