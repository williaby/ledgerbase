from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = SCRIPT_DIR / "docs" / "scripts.md"
SCRIPTS_PATH = SCRIPT_DIR.glob("*.sh")


def parse_script_metadata(script_path):
    metadata = {"name": script_path.name}
    with open(script_path) as f:
        for line in f:
            if line.startswith("##:"):
                keyval = line[3:].strip().split("=", 1)
                if len(keyval) == 2:
                    key, val = keyval
                    metadata[key.strip()] = val.strip(" '\"")
    return metadata


def write_docs(scripts):
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w") as doc:
        doc.write("# Shell Script Reference\n\n")
        doc.write("> **Auto-generated from script headers**\n\n")
        for meta in scripts:
            doc.write(f"## `{meta['name']}`\n\n")
            doc.write(
                f"### **Purpose**\n{meta.get('description', 'No description provided.')}\n\n"
            )
            doc.write(
                f"### **Usage**\n```bash\n{meta.get('usage', './' + meta['name'])}\n```\n\n"
            )
            doc.write(
                f"### **Behavior**\n{meta.get('behavior', 'No behavior documented.')}\n\n---\n\n"
            )


if __name__ == "__main__":
    all_scripts = [
        parse_script_metadata(script) for script in SCRIPTS_PATH if script.is_file()
    ]
    write_docs(all_scripts)
