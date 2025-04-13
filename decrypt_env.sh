#!/bin/bash

##: name = decrypt_env.sh
##: description = Decrypts the LedgerBase environment files using sops.
##: category = dev
##: usage = ./decrypt_env.sh
##: behavior = Decrypts .env.enc and .env.prod.sops.yaml into plaintext .env files for local use.
##: inputs = .env.enc, .env.prod.sops.yaml
##: outputs = .env, ledgerbase_secure_env/.env.prod
##: dependencies = sops, bash
##: tags = secrets, env, sops, decryption
##: author = Byron Williams
##: last_modified = 2025-04-12


set -e
sops -d .env.enc > .env

ENCRYPTED_FILE=".env.prod.sops.yaml"
OUTPUT_FILE="ledgerbase_secure_env/.env.prod"

if [[ ! -f "$ENCRYPTED_FILE" ]]; then
  echo "❌ $ENCRYPTED_FILE not found."
  exit 1
fi

if [[ -f "$OUTPUT_FILE" ]]; then
  echo "⚠️  $OUTPUT_FILE already exists. Overwrite? (y/n)"
  read -r confirm
  if [[ "$confirm" != "y" ]]; then
    echo "❌ Aborted."
    exit 1
  fi
fi

echo "🔓 Decrypting $ENCRYPTED_FILE into $OUTPUT_FILE ..."
sops -d "$ENCRYPTED_FILE" > "$OUTPUT_FILE"
echo "✅ Decryption complete: $OUTPUT_FILE"
