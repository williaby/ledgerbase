import sys
from datetime import datetime
from pathlib import Path

# -- Path setup -----------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

# -- Project information --------------------------------------------
project = "LedgerBase"
author = "Byron Williams"
copyright = f"{datetime.now().year}, {author}"
release = "0.1.0"

# -- General configuration ------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output ----------------------------------------
html_theme = "alabaster"
html_static_path = ["_static"]

# -- Autodoc default flags ------------------------------------------
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

# -- Napoleon configuration -----------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True
