#!/bin/bash

# encrypt_env.sh - Encrypt ledgerbase_secure_env/.env.prod into .env.prod.sops.yaml

set -e

ENV_FILE="ledgerbase_secure_env/.env.prod"
ENCRYPTED_FILE=".env.prod.sops.yaml"
KEY_ID="9360A8293F1430EB3E88B99CB2C95364612BFFDF"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "❌ $ENV_FILE not found."
  exit 1
fi

echo "🔐 Encrypting $ENV_FILE with GPG key: $KEY_ID ..."
sops --encrypt --pgp "$KEY_ID" "$ENV_FILE" > "$ENCRYPTED_FILE"
echo "✅ Encrypted file saved to $ENCRYPTED_FILE"
