
Developer Documentation System Guide
====================================

Overview
--------
This guide explains how to use the automated script documentation system in the LedgerBase repository.
It covers directory structure, metadata annotation, how to generate `.rst` documentation files, and
where everything should be stored.

Correct Filepath to Store This Guide
------------------------------------

Save this file to the following path in your repository:

    docs/wiki/developer_doc_system.rst


Directory Layout
----------------

Your documentation layout follows a structured Sphinx convention:

    docs/
    ├── build/                      # HTML build output (ignored in VCS)
    ├── source/
    │   ├── _static/                # Static assets like images and CSS
    │   ├── _templates/             # Jinja2 templates for .rst generation
    │   ├── conf.py                 # Sphinx configuration file
    │   ├── index.rst               # Main landing page
    │   └── rst/                    # Reusable documentation content
    │       ├── api/                # API reference .rst files
    │       ├── dev/                # Developer documentation
    │       │   └── scripts/        # Auto-generated script documentation
    │       └── usage/              # User-facing usage guides
    └── wiki/                       # Internal usage guides and documentation


Metadata Annotation
-------------------

Each script file (e.g. `.py`, `.sh`, `.yaml`, `.toml`) should begin with structured headers using comment blocks like:

    ##: name = extract_budget.py
    ##: description = Parses transaction files and updates budget database.
    ##: category = etl
    ##: usage = python extract_budget.py --file transactions.csv
    ##: behavior = Inserts normalized entries into the `budget` table.

Supported keys:
    name, description, category, usage, behavior, inputs, outputs,
    dependencies, tags, author, last_modified


Generating Script Docs
-----------------------

1. **Annotate** your script with the supported metadata headers.

2. **Run the generator**:

       poetry run python scripts/generate_file_docs.py

   This will:
   - Parse all eligible files in the project.
   - Generate `.rst` documentation into `docs/source/rst/dev/scripts/`
   - Create an `index.rst` file with a `toctree` for Sphinx

3. **Build the documentation**:

       poetry run sphinx-build docs/source docs/build

4. **View output** by opening `docs/build/index.html` in your browser.


What to Store Where
-------------------

- Header templates:          `docs/source/_templates/file_template.rst.j2`
- Generated .rst files:      `docs/source/rst/dev/scripts/`
- Source scripts:            Anywhere in repo (if annotated and not excluded)
- Internal usage guides:     `docs/wiki/` (this file)


Automation Notes
----------------

- Only files with a valid header (`name` and `description`) will be documented
- Existing `.rst` output is wiped and re-generated each time
- Unannotated or excluded files are silently skipped
