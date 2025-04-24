from pathlib import Path

"""
This script generates the master index file for the LedgerBase documentation.

It consolidates category-specific documentation indices into a single
`index.rst` file, providing a unified entry point for navigating the
documentation site.
"""

RST_ROOT = Path(__file__).resolve().parent.parent / "docs" / "source" / "rst"
MASTER_INDEX = RST_ROOT.parent / "index.rst"

CATEGORY_ORDER = [
    ("usage", "Quick Start & Usage"),
    ("dev", "Developer Docs"),
    ("etl", "ETL Pipelines"),
    ("budget", "Budgeting Modules"),
    ("api", "API Reference"),
    ("docs", "Internal Docs"),
    ("misc", "Uncategorized Files"),
]


def main() -> None:
    """Generate the master index file for the LedgerBase documentation.

    This function creates a master `index.rst` file that consolidates
    all category-specific documentation indices into a single entry point.
    It iterates through the predefined `CATEGORY_ORDER` and includes
    the index files for categories that exist.

    The generated file is written to the `MASTER_INDEX` path.
    """
    lines = [
        "LedgerBase Documentation",
        "=========================",
        "",
        "Welcome to the LedgerBase documentation site. Navigate below by section.",
        "",
    ]

    for category, caption in CATEGORY_ORDER:
        category_index = RST_ROOT / category / "index.rst"
        if category_index.exists():
            lines.extend(
                [
                    ".. toctree::",
                    "   :maxdepth: 2",
                    f"   :caption: {caption}",
                    "",
                    f"   rst/{category}/index",
                    "",
                ],
            )

    MASTER_INDEX.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"✅ Master index written to: {MASTER_INDEX}")


if __name__ == "__main__":
    main()
