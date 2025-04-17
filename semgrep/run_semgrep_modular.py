#!/usr/bin/env python3
##: name = run_semgrep_modular.py
##: description = Parallelized modular Semgrep runner for scoped rule execution.
##: category = ci
##: usage = python run_semgrep_modular.py [--verbose]
##: behavior = Runs targeted Semgrep scans across LedgerBase submodules and emits SARIF reports. # noqa: E501
##: inputs = semgrep/*/semgrep.yml, source code folders under src/, scripts/, .github/, etc # noqa: E501
##: outputs = sarif/*.sarif
##: dependencies = Python 3.8+, Semgrep CLI, pathlib, subprocess, ThreadPoolExecutor
##: author = Byron Williams
##: last_modified = 2025-04-17
##: tags = semgrep, ci, security, automation, sarif


"""run_semgrep_modular.py.

This script is a parallelized modular Semgrep runner designed for scoped rule execution.
It scans specific submodules of the LedgerBase project using Semgrep rules and
generates SARIF reports.

Features:
- Executes targeted Semgrep scans across various submodules.
- Supports parallel execution using ThreadPoolExecutor.
- Outputs SARIF reports for each scan.

Usage:
    python run_semgrep_modular.py [--verbose]

Dependencies:
- Python 3.8+
- Semgrep CLI
- pathlib
- subprocess
- ThreadPoolExecutor
"""


import argparse
import subprocess  # nosec B404
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

TARGETS = [
    {
        "name": "CLI",
        "paths": ["src/ledgerbase/cli"],
        "includes": ["*.py"],
        "config": "semgrep/cli/semgrep.yml",
    },
    {
        "name": "Library",
        "paths": ["src/ledgerbase/services", "src/ledgerbase/models"],
        "includes": ["*.py"],
        "config": "semgrep/lib/semgrep.yml",
    },
    {
        "name": "Scripts",
        "paths": ["scripts", "src/ledgerbase/scripts"],
        "includes": ["*.py", "*.sh"],
        "config": "semgrep/scripts/semgrep.yml",
    },
    {
        "name": "GitHub Workflows",
        "paths": [".github/workflows"],
        "includes": ["*.yml", "*.yaml"],
        "config": "semgrep/github/semgrep.yml",
    },
    {
        "name": "Docs",
        "paths": ["docs"],
        "includes": ["*.md", "*.yml", "*.yaml"],
        "config": "semgrep/docs/semgrep.yml",
    },
    {
        "name": "Tests",
        "paths": ["tests"],
        "includes": ["*.py"],
        "config": "semgrep/tests/semgrep.yml",
    },
    {
        "name": "Configs",
        "paths": ["."],
        "includes": ["*.yaml", "*.yml", "*.toml", "*.json"],
        "config": "semgrep/configs/semgrep.yml",
    },
    {
        "name": "Semgrep Internal",
        "paths": ["semgrep"],
        "includes": ["*.yml"],
        "config": "semgrep/semgrep/semgrep.yml",
    },
    {
        "name": "Other",
        "paths": ["src/ledgerbase"],
        "includes": ["*.py", "*.yml", "*.yaml", "*.json"],
        "config": "semgrep/other/semgrep.yml",
    },
]


def run_semgrep(
    config: str,
    paths: list[str],
    includes: list[str],
    output_path: str,
    *,
    verbose: bool = False,
) -> None:
    """Run a Semgrep scan on the specified paths using the given configuration file.

    The function generates SARIF output and includes specific file patterns if provided.

    Parameters
    ----------
    config: str
        The path to the Semgrep configuration file.
    paths: list[str]
        A list of file or directory paths to scan.
    includes: list[str]
        A list of file glob patterns to include in the scan.
    output_path: str
        The directory path where the SARIF output file will be saved.
    verbose: bool, optional
        If True, prints the executed command and any errors to the standard output.

    Returns
    -------
    None

    Raises
    ------
    Does not explicitly raise any exceptions, but an error might occur if the
    Semgrep command fails or if there are issues with the provided paths/files.

    """
    for path in paths:
        abs_path = str(Path(path).resolve())
        include_args = []
        for inc in includes:
            include_args.extend(["--include", inc])
        output_file = f"{output_path}/semgrep-{Path(config).parent.name}.sarif"
        cmd = [
            "semgrep",
            "scan",
            "--config",
            config,
            "--format",
            "sarif",
            "--output",
            output_file,
            abs_path,
            *include_args,
        ]

        if verbose:
            print(f"Running: {' '.join(cmd)}")

        # Determine working directory relative to this script's location
        script_dir = Path(__file__).resolve().parent

        result = subprocess.run(  # nosec S603
            cmd,  # nosec S603  # noqa: S603
            capture_output=not verbose,
            text=True,
            check=False,
            cwd=str(script_dir),  # Safer and more predictable than Path.cwd()
        )  # nosec S603

        if result.returncode != 0:
            print(f"Error: Semgrep failed for config '{config}' on path '{path}'")
            if not verbose:
                print(result.stderr)


def validate_targets(targets: list[dict]) -> None:
    """Validate the structure of targets in a list of dictionaries.

    Each target is expected to     contain required keys to ensure proper configuration.

    Parameters
    ----------
    targets: list[dict]
        A list of dictionaries representing target configurations. Each dictionary must
        include the required keys: "name", "paths", "includes", and "config".

    Raises
    ------
    ValueError
        If any target configuration is missing one or more required keys.

    """
    for target in targets:
        required = ["name", "paths", "includes", "config"]
        if not all(k in target for k in required):
            err_msg = f"Invalid target configuration: {target}"
            raise ValueError(err_msg)


def main() -> None:
    """Run modular scans with Semgrep based on specified targets and configurations.

    This function sets up the directory for SARIF output files, validates the
    provided scan targets, and performs concurrent execution of scans using
    Semgrep. The results are saved in the specified directory.

    Functions:
        - main: Entry point for running the Semgrep scans.

    Raises
    ------
        OSError: If the SARIF output directory cannot be accessed or created.
        NotADirectoryError: If an existing SARIF output path is not a directory.
        ValueError: If validation of the targets fails.

    Parameters
    ----------
        None

    Returns
    -------
        None

    """
    parser = argparse.ArgumentParser(description="Run Semgrep modular scans")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    try:
        output_dir = Path("sarif")
        if output_dir.exists() and not output_dir.is_dir():
            err_msg = "SARIF output path is not a directory."
            raise NotADirectoryError(err_msg)
        output_dir.mkdir(exist_ok=True)
    except OSError as e:
        print(f"Error: Cannot access output directory: {e}")
        return

    try:
        validate_targets(TARGETS)
    except ValueError as e:
        print(str(e))
        return

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(
                run_semgrep,
                str(target["config"]),
                list(target["paths"]),
                list(target["includes"]),
                output_path=str(output_dir),
                verbose=args.verbose,
            )
            for target in TARGETS
        ]
        for future in futures:
            future.result()


if __name__ == "__main__":
    main()
