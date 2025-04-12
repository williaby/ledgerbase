#!/bin/bash

##: name = validate_env_keys.sh
##: description = Validates that required keys exist in the decrypted .env file.
##: usage = ./validate_env_keys.sh
##: behavior = Greps required keys and exits with error if any are missing.

set -e

REQUIRED_KEYS=("DATABASE_URL" "SNYK_TOKEN" "POSTGRES_USER" "POSTGRES_PASSWORD")
MISSING_KEYS=()

DECRYPTED=$(sops -d .env.prod.sops.yaml 2>/dev/null || echo "")

if [[ -z "$DECRYPTED" ]]; then
  echo "❌ Failed to decrypt .env.prod.sops.yaml or file missing."
  exit 1
fi

for KEY in "${REQUIRED_KEYS[@]}"; do
  if ! echo "$DECRYPTED" | grep -q "^$KEY="; then
    MISSING_KEYS+=("$KEY")
  fi
done

if [[ ${#MISSING_KEYS[@]} -gt 0 ]]; then
  echo "❌ Missing required keys in .env.prod.sops.yaml:"
  for KEY in "${MISSING_KEYS[@]}"; do
    echo "   - $KEY"
  done
  exit 1
fi

echo "✅ All required keys present in .env.prod.sops.yaml."
