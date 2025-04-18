from collections import defaultdict
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from validate_file_headers import parse_header_metadata

# === Configuration ===
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = PROJECT_ROOT / "docs" / "source" / "_templates"
RST_ROOT = PROJECT_ROOT / "docs" / "source" / "rst"

CATEGORY_PATHS = {
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

TEMPLATE_MAPPING = {
    ".sh": "script_template.rst.j2",
    ".py": "python_template.rst.j2",
    ".yaml": "config_template.rst.j2",
    ".yml": "config_template.rst.j2",
    ".toml": "config_template.rst.j2",
}

DEFAULT_TEMPLATE = "script_template.rst.j2"

# === Jinja2 Environment ===
env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_PATH)),
    trim_blocks=True,
    lstrip_blocks=True,
    autoescape=select_autoescape(["html", "xml"]),  # Safe defaults
)


def discover_annotated_files():
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
    return [
        p
        for p in PROJECT_ROOT.rglob("*")
        if p.suffix in include_exts
        and p.is_file()
        and not set(p.parts).intersection(exclude_dirs)
    ]


def main():
    print("📁 Regenerating categorized documentation files...")

    index_map = defaultdict(list)
    files = discover_annotated_files()

    for file in files:

        meta = parse_header_metadata(file)
        if not meta or "name" not in meta or "description" not in meta:
            continue

        category = meta.get("category", "misc")
        out_dir = CATEGORY_PATHS.get(category, CATEGORY_PATHS["misc"])
        out_dir.mkdir(parents=True, exist_ok=True)

        extension = file.suffix
        template_name = TEMPLATE_MAPPING.get(extension, DEFAULT_TEMPLATE)
        template = env.get_template(template_name)

        rendered = template.render(**meta, title=Path(meta["name"]).stem)
        rst_filename = f"{Path(meta['name']).stem}.rst"
        rst_path = out_dir / rst_filename
        rst_path.write_text(rendered, encoding="utf-8")

        index_map[out_dir].append(Path(rst_filename).stem)

    # Write index.rst for each category
    for folder, entries in index_map.items():
        index_path = folder / "index.rst"
        title = folder.name.capitalize()
        lines = [
            f"{title} Documentation",
            "=" * (len(title) + 13),
            "",
            ".. toctree::",
            "   :maxdepth: 1",
            "",
        ]
        lines.extend([f"   {entry}" for entry in sorted(entries)])
        content = "\n".join(lines) + "\n"
        index_path.write_text(content, encoding="utf-8")
        print(f"📚 Index written: {index_path}")

    print(
        f"✅ {sum(len(v) for v in index_map.values())} .rst files generated across {len(index_map)} categories."
    )


if __name__ == "__main__":
    main()
