##: name = load_env.py
##: description = Utility for loading and validating environment variables from .env files # noqa: E501

##: category = util
##: usage = Import and use in Python applications or run directly
##: behavior = Loads environment variables from .env files and validates required variables # noqa: E501

##: inputs = .env.prod or ledgerbase_secure_env/.env.dev files
##: outputs = Environment variables loaded into the process
##: dependencies = python-dotenv
##: author = LedgerBase Team
##: last_modified = 2023-11-15
##: changelog = Initial version

import os
from pathlib import Path

from dotenv import load_dotenv

"""Utility for loading and validating environment variables from .env files.

This module provides functionality to load environment variables from .env files
with a fallback mechanism and validate that required variables are present.
It supports loading from multiple file locations with priority order and
raises appropriate exceptions if required files or variables are missing.
"""

# Define the fallback priority
ENV_PATHS = [
    Path(".env.prod"),  # preferred for CI/staging
    Path("ledgerbase_secure_env/.env.dev"),  # fallback for local dev
]

# Required variables to validate
REQUIRED_VARS = [
    "POSTGRES_DB",
    "SNYK_TOKEN",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "SEMGREP_APP_TOKEN",
    "SEMGREP_DEPLOYMENT_ID",
    "CODECOV_TOKEN",
    "AIKIDO_API_TOKEN",
    "GOOGLE_APPLICATION_CREDENTIALS",
]


def load_and_validate_env() -> None:
    """Load environment variables from .env files and validate required keys.

    This function attempts to load environment variables from a list of known paths.
    If none are found, it raises a FileNotFoundError. It also ensures that all
    required variables are set in the environment,
    raising an OSError if any are missing.
    """
    for env_path in ENV_PATHS:
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=True)
            print(f"✅ Loaded environment from {env_path}")
            break
    else:
        msg = "❌ No .env file found in known locations."
        raise FileNotFoundError(msg)

    # Validate required variables
    missing = [key for key in REQUIRED_VARS if not os.getenv(key)]
    if missing:
        msg = f"❌ Missing required environment variables: {', '.join(missing)}"
        raise OSError(msg)

    print("✅ All required environment variables are present.")


# Example usage
if __name__ == "__main__":
    load_and_validate_env()
