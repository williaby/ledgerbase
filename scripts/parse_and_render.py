##: name = parse_and_render.py
##: description = CLI tool to parse header metadata and render .rst documentation using Flask templates for safe autoescaping # noqa: E501
##: category = correctness
##: usage = python parse_and_render.py <input_file> [-o output_dir]
##: behavior = Extracts metadata from annotated source files and renders .rst via Flask's render_template for security # noqa: E501
##: inputs = input_file (str), output-dir (str, optional)
##: outputs = .rst files in designated category directories
##: dependencies = Flask, validate_file_headers, argparse, pathlib
##: author = Byron Williams
##: last_modified = 2025-04-19
##: tags = docs, util, flask
##: changelog = - Replaced direct Jinja2 Environment with Flask app.render_template for safe HTML escaping # noqa: E501

"""CLI tool that parses header metadata from a source file and uses Flask's template engine to render .rst files safely."""  # noqa: E501

import argparse
from pathlib import Path

from validate_file_headers import parse_header_metadata

from flask import Flask, render_template

# Initialize a Flask app to leverage its built-in Jinja2 environment with autoescaping enabled. # noqa: E501
app = Flask(
    __name__,
    template_folder=str(Path("docs/source/_templates")),
)

# === Constants ===
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
    ".py": "python_template.html",
    ".sh": "script_template.html",
    ".yml": "config_template.html",
    ".yaml": "config_template.html",
    ".toml": "config_template.html",
}
DEFAULT_TEMPLATE = "script_template.html"


def main() -> None:
    """Entry point for CLI parsing and rendering logic."""
    parser = argparse.ArgumentParser(
        description="Render .rst from a single annotated file using Flask templates",
    )
    parser.add_argument(
        "input_file",
        type=str,
        help="Path to the annotated source file",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        help=("(Optional) Override output directory. Defaults to mapped location."),
    )
    args = parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ Error: {input_path} does not exist.")
        return

    metadata = parse_header_metadata(input_path)
    if not metadata or "name" not in metadata or "description" not in metadata:
        print(
            "❌ Error: File is missing required header metadata (`name`, `description`).",  # noqa: E501
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

    # Safely render using Flask's render_template within application context
    with app.app_context():
        rendered = render_template(template_name, **metadata)

    output_path = output_dir / f"{metadata['title']}.rst"
    output_path.write_text(rendered, encoding="utf-8")
    print(f"✅ Rendered to: {output_path}")


if __name__ == "__main__":
    main()
