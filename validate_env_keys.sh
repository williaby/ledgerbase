#!/bin/bash

##: name = validate_env_keys.sh
##: description = Validates that required keys exist in the decrypted env files (.env.dev.sops.yaml, .env.prod.sops.yaml).
##: usage = ./validate_env_keys.sh
##: behavior = Greps required keys and exits with error if any are missing in each env file.
##: author = LedgerBase Team
##: last_modified = 2025-04-25
##: changelog = Added AOSS keys and support for both dev and prod envs.

set -e

REQUIRED_VARS=(
  POSTGRES_DB
  SNYK_TOKEN
  POSTGRES_USER
  POSTGRES_PASSWORD
  SEMGREP_APP_TOKEN
  SEMGREP_DEPLOYMENT_ID
  CODECOV_TOKEN
  AIKIDO_API_TOKEN
  GOOGLE_APPLICATION_CREDENTIALS
  GOOGLE_CLOUD_PROJECT
)

FILES_TO_CHECK=(
  .env.prod.sops.yaml
  .env.dev.sops.yaml
)

for FILE in "${FILES_TO_CHECK[@]}"; do
  if [[ -f "$FILE" ]]; then
    echo "🔍 Checking: $FILE"
    DECRYPTED=$(sops -d "$FILE" 2>/dev/null || echo "")
    if [[ -z "$DECRYPTED" ]]; then
      echo "❌ Failed to decrypt $FILE or file empty."
      exit 1
    fi

    MISSING_KEYS=()
    for KEY in "${REQUIRED_VARS[@]}"; do
      if ! echo "$DECRYPTED" | grep -q "^$KEY="; then
        MISSING_KEYS+=("$KEY")
      fi
    done

    if [[ ${#MISSING_KEYS[@]} -gt 0 ]]; then
      echo "❌ Missing required keys in $FILE:"
      for KEY in "${MISSING_KEYS[@]}"; do
        echo "   - $KEY"
      done
      exit 1
    else
      echo "✅ All required keys present in $FILE."
    fi
  else
    echo "⚠️  File not found: $FILE — skipping."
  fi
done
