#!/usr/bin/env python
"""---
title: "Validate Assured OSS Credentials"
name: "validate_assuredoss.py"
description: "Validates ADC for Assured OSS and lists available packages."
category: script
usage: "python scripts/validate_assuredoss.py"
behavior: "Checks ADC credentials and enumerates OSS packages"
inputs: "GOOGLE_APPLICATION_CREDENTIALS, GOOGLE_CLOUD_PROJECT"
outputs: "Console output of credential path, project ID, and package list"
dependencies: "google-auth, google-cloud-assuredoss, google-api-core"
author: "Byron Williams"
last_modified: "2025-04-26"
changelog: "Add front-matter metadata and module docstring"
tags: [docs, tools]
---

Module: validate_assuredoss

This script verifies that Google Application Default Credentials (ADC)
are correctly configured for Assured OSS, and lists available OSS packages
for the configured project.

Functions:
    main(): Entry point for credential validation and package listing.
"""

import os

from google.api_core.exceptions import GoogleAPICallError
from google.auth.exceptions import DefaultCredentialsError
from google.cloud.assuredoss import V1Client


def main() -> None:
    """Validate ADC credentials and list Assured OSS packages.

    Reads the `GOOGLE_APPLICATION_CREDENTIALS` and
    `GOOGLE_CLOUD_PROJECT` environment variables, initializes the
    Assured OSS client, and prints the retrieved package list.

    Raises:
        DefaultCredentialsError: If ADC cannot be loaded.
        GoogleAPICallError: If the API call fails.

    """
    try:
        cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        print("🔐 Credentials from:", cred_path)
        print("📦 Project:", project_id)

        client = V1Client()
        response = client.list_packages()
        print("✅ Connected to Assured OSS. Available packages:")
        for pkg in response.packages:
            print(f"  - {pkg.name} ({pkg.version})")

    except DefaultCredentialsError:
        print("❌ Could not load credentials")
        raise
    except GoogleAPICallError:
        print("❌ Failed to list packages")
        raise


if __name__ == "__main__":
    main()
