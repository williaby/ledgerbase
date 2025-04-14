import os
from pathlib import Path

from dotenv import load_dotenv

# Define the fallback priority
ENV_PATHS = [
    Path(".env.prod"),  # preferred for CI/staging
    Path("ledgerbase_secure_env/.env.dev"),  # fallback for local dev
]

# Required variables to validate
REQUIRED_VARS = ["DATABASE_URL", "SNYK_TOKEN", "POSTGRES_USER", "POSTGRES_PASSWORD"]


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
