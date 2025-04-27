##: name = conf.py
##: description = Sphinx documentation configuration file for LedgerBase project
##: category = docs
##: usage = Used by Sphinx to generate project documentation
##: behavior = Configures Sphinx documentation settings, extensions, and output formats
##: inputs = Project source code and documentation files
##: outputs = HTML documentation with cross-references, search functionality, and diagrams # noqa: E501
##: dependencies = Sphinx, sphinx_rtd_theme, sphinxcontrib-plantuml, sphinxcontrib-spelling # noqa: E501
##: author = LedgerBase Team
##: last_modified = 2023-11-15
##: changelog = Initial version

import sys
from datetime import UTC, datetime
from pathlib import Path

# -- Path setup -----------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

# -- Project information --------------------------------------------
project = "LedgerBase"
author = "Byron Williams"
copyright_str = f"{datetime.now(tz=UTC).year}, {author}"
release = "0.1.0"

# -- General configuration ------------------------------------------
extensions = [
    "sphinx.ext.autodoc",            # Core autodoc support
    "sphinx.ext.autosummary",        # Generate autodoc summaries
    "sphinx.ext.viewcode",           # Link to highlighted source code
    "sphinx.ext.intersphinx",        # Link to other projects' docs
    "sphinx.ext.napoleon",           # Google/NumPy style docstrings
    "sphinx.ext.todo",               # Support for todo directives
    "sphinxcontrib.plantuml",        # PlantUML diagrams
    "readthedocs_sphinx_search.extension",  # RTD search-as-you-type
    "sphinxcontrib.spelling",        # Spell checking

    # **New additions for Markdown & front-matter**
    "myst_parser",                   # Markdown support + front-matter
    "sphinx_copybutton",             # “Copy” button on code blocks
    "sphinx_autodoc_typehints",      # Inline param/return types
]

# Automatically generate summary pages for modules
autosummary_generate = True

# -- MyST (Markdown) front-matter configuration --------------------
myst_enable_extensions = ["front_matter"]
myst_front_matter_enable = True

# -- Autodoc default options ----------------------------------------
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

# -- Napoleon configuration -----------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True

# -- Intersphinx mapping --------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "requests": ("https://docs.python-requests.org/en/latest/", None),
    # Add other mappings as needed…
}

# -- PlantUML configuration -----------------------------------------
# Ensure 'plantuml' is in your PATH or adjust to its full path
plantuml = "plantuml"
plantuml_output_format = "svg"

# -- Spelling configuration -----------------------------------------
spelling_show_suggestions = True
spelling_ignore_pypi_package_names = True
spelling_word_list_filename = ["spelling_wordlist.txt"]

# -- TODO configuration ---------------------------------------------
todo_include_todos = True

# -- Templates and exclude patterns ---------------------------------
templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "reports/json/*",
    "reports/sarif/*",
]
html_static_path = ["_static"]

# -- HTML output options --------------------------------------------
html_theme = "furo"
html_theme_options = {
    "navigation_depth": 4,
    "collapse_navigation": False,
}
