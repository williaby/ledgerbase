from pathlib import Path

SCRIPT_DIR: Path = Path(__file__).resolve().parent.parent
OUTPUT_FILE: Path = SCRIPT_DIR / "docs" / "scripts.md"
SCRIPTS_PATH: list[Path] = list(SCRIPT_DIR.glob("*.sh"))

KEYVAL_LENGTH: int = 2  # Named constant for the expected key-value pair length


def parse_script_metadata(script_path: Path) -> dict[str, str]:
    """Parse metadata from a shell script.

    Args:
    ----
        script_path (Path): Path to the shell script.

    Returns:
    -------
        Dict[str, str]: A dictionary containing script metadata.

    """
    metadata: dict[str, str] = {"name": script_path.name}
    with script_path.open(encoding="utf-8") as f:
        for line in f:
            if line.startswith("##:"):
                keyval = line[3:].strip().split("=", 1)
                if len(keyval) == KEYVAL_LENGTH:
                    key, val = keyval
                    metadata[key.strip()] = val.strip(" '\"")
    return metadata


def write_docs(scripts: list[dict[str, str]]) -> None:
    """Write documentation for shell scripts to a markdown file.

    Args:
    ----
        scripts (List[Dict[str, str]]): List of metadata dictionaries for scripts.

    """
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", encoding="utf-8") as doc:
        doc.write("# Shell Script Reference\n\n")
        doc.write("> **Auto-generated from script headers**\n\n")
        for meta in scripts:
            doc.write(f"## `{meta['name']}`\n\n")
            doc.write(
                f"### **Purpose**\n"
                f"{meta.get('description', 'No description provided.')}\n\n",
            )
            doc.write(
                f"### **Usage**\n"
                f"```bash\n{meta.get('usage', './' + meta['name'])}\n```\n\n",
            )
            doc.write(
                f"### **Behavior**\n"
                f"{meta.get('behavior', 'No behavior documented.')}\n\n---\n\n",
            )


if __name__ == "__main__":
    all_scripts: list[dict[str, str]] = [
        parse_script_metadata(script) for script in SCRIPTS_PATH if script.is_file()
    ]
    write_docs(all_scripts)
