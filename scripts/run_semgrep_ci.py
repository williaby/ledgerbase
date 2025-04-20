#!/usr/bin/env python3
"""Run Semgrep CI session via Nox using Poetry-managed virtualenv."""  # D200

import subprocess  # nosec B404
import sys


def main() -> None:
    """Invoke the Nox semgrep_ci session and exit with its return code."""  # D103
    try:
        poetry = "poetry"
        nox = "nox"
        subprocess.run(  # nosec: B603 # noqa: S603
            [poetry, "run", nox, "-s", "semgrep_ci"],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ Semgrep CI failed with exit code {e.returncode}")
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()
