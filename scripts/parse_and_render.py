import argparse
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from validate_file_headers import parse_header_metadata

# === Constants ===
TEMPLATE_PATH = Path("docs/source/_templates")
CATEGORY_PATHS = {
    "etl": Path("docs/source/rst/etl"),
    "budget": Path("docs/source/rst/budget"),
    "api": Path("docs/source/rst/api"),
    "ci": Path("docs/source/rst/dev"),
    "setup": Path("docs/source/rst/dev"),
    "dev": Path("docs/source/rst/dev"),
    "usage": Path("docs/source/rst/usage"),
    "docs": Path("docs/source/rst/docs"),
    "misc": Path("docs/source/rst/misc"),
}
TEMPLATE_MAPPING = {
    ".py": "python_template.rst.j2",
    ".sh": "script_template.rst.j2",
    ".yml": "config_template.rst.j2",
    ".yaml": "config_template.rst.j2",
    ".toml": "config_template.rst.j2",
}
DEFAULT_TEMPLATE = "script_template.rst.j2"


def main():
    parser = argparse.ArgumentParser(
        description="Render .rst from a single annotated file"
    )
    parser.add_argument(
        "input_file", type=str, help="Path to the annotated source file"
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        help="(Optional) Override output directory. Defaults to category-mapped location.",
    )
    args = parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ Error: {input_path} does not exist.")
        return

    metadata = parse_header_metadata(input_path)
    if not metadata or "name" not in metadata or "description" not in metadata:
        print(
            "❌ Error: File is missing required header metadata (`name`, `description`)."
        )
        return

    category = metadata.get("category", "misc")
    output_dir = (
        Path(args.output_dir)
        if args.output_dir
        else CATEGORY_PATHS.get(category, CATEGORY_PATHS["misc"])
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    metadata["title"] = Path(metadata["name"]).stem
    extension = input_path.suffix
    template_name = TEMPLATE_MAPPING.get(extension, DEFAULT_TEMPLATE)

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_PATH)),
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=select_autoescape(["html", "xml"]),  # Safe for web rendering
    )

    template = env.get_template(template_name)
    rendered = template.render(**metadata)

    output_path = output_dir / f"{metadata['title']}.rst"
    output_path.write_text(rendered, encoding="utf-8")
    print(f"✅ Rendered to: {output_path}")


if __name__ == "__main__":
    main()
