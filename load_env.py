import os
from pathlib import Path

from dotenv import load_dotenv

"""
Utility for loading and validating environment variables from .env files,
writing out the Google service-account JSON to disk for ADC, and
configuring pip to use Google Artifact Registry via the keyring plugin.
Requires:
  - python-dotenv
  - keyring
  - keyrings.google-artifactregistry-auth>=0.6.0
  - packaging
"""

# Enforce plugin version
try:
    import keyrings.google_artifactregistry_auth as gar_auth
    from packaging.version import parse as parse_version

    version = gar_auth.__version__
    required_version = "0.6.0"
    if parse_version(version) < parse_version(required_version):
        message = (
            "keyrings.google-artifactregistry-auth>="
            f"{required_version} is required (found {version})"
        )
        raise RuntimeError(message)
except ImportError as err:
    message = (
        "Please install keyring and "
        "keyrings.google-artifactregistry-auth>=0.6.0"
    )
    raise ImportError(message) from err

# Files to search for environment definitions
ENV_PATHS = [
    Path(".env.dev"),  # local dev env file
    Path(".env.prod"), # CI / staging env file
]

# Environment variables required for operation
REQUIRED_VARS = [
    "POSTGRES_DB",
    "SNYK_TOKEN",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "SEMGREP_APP_TOKEN",
    "SEMGREP_DEPLOYMENT_ID",
    "CODECOV_TOKEN",
    "AIKIDO_API_TOKEN",
    "GOOGLE_CLOUD_PROJECT",
]

def load_and_validate_env() -> None:
    """Load environment, validate required variables, and configure credentials."""
    # 1. Load from the first existing .env
    for env_path in ENV_PATHS:
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=True)
            print(f"✅ Loaded environment from {env_path}")
            break
    else:
        message = "No .env file found in known locations."
        raise FileNotFoundError(message)

    # 2. Validate presence of all required variables
    missing_vars = [key for key in REQUIRED_VARS if not os.getenv(key)]
    if missing_vars:
        missing_list = ", ".join(missing_vars)
        message = (
            "Missing required environment variables: "
            f"{missing_list}"
        )
        raise OSError(message)

    # 3. Locate or write the GCP JSON for ADC
    creds_dir = Path("ledgerbase_secure_env")
    creds_dir.mkdir(exist_ok=True)
    local_cred = creds_dir / "service-account.json"

    if local_cred.exists():
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(local_cred)
        print(f"🔐 Using existing credentials from {local_cred}")
    elif os.getenv("GCP_SA_JSON"):
        content = os.getenv("GCP_SA_JSON")
        local_cred.write_text(content)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(local_cred)
        print(f"🔐 Wrote credentials to {local_cred} from GCP_SA_JSON secret")
    else:
        message = (
            "No local service-account.json found and "
            "GCP_SA_JSON is unset."
        )
        raise FileNotFoundError(message)

    # 4. Ensure project is set
    os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("GOOGLE_CLOUD_PROJECT")

    # 5. Configure pip to use Artifact Registry (keyring will handle auth)
    os.environ["PIP_INDEX_URL"] = (
        "https://us-python.pkg.dev/cloud-aoss/"
        "cloud-aoss-python/simple"
    )
    os.environ["PIP_EXTRA_INDEX_URL"] = "https://pypi.org/simple"

    print(
        "✅ Environment loaded; credentials configured; "
        "pip configured for Artifact Registry via keyring.",
    )


if __name__ == "__main__":
    load_and_validate_env()
