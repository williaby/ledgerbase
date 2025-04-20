#!/bin/bash

##: name = decrypt_env.sh
##: description = Decrypts .env.dev.sops.yaml and .env.prod.sops.yaml into plaintext files.
##: category = security
##: usage = ./decrypt_env.sh
##: behavior = Decrypts and stores output in ledgerbase_secure_env/.
##: inputs = .env.dev.sops.yaml and .env.prod.sops.yaml encrypted files
##: outputs = Decrypted .env.dev and .env.prod files in ledgerbase_secure_env directory
##: dependencies = sops
##: author = LedgerBase Team
##: last_modified = 2023-11-15
##: changelog = Initial version

set -e

INPUT_DEV=".env.dev.sops.yaml"
INPUT_PROD=".env.prod.sops.yaml"
OUTPUT_DIR="ledgerbase_secure_env"
OUTPUT_DEV="${OUTPUT_DIR}/.env.dev"
OUTPUT_PROD="${OUTPUT_DIR}/.env.prod"

mkdir -p "$OUTPUT_DIR"

if [[ -f "$INPUT_DEV" ]]; then
  echo "🔓 Decrypting $INPUT_DEV to $OUTPUT_DEV ..."
  sops -d "$INPUT_DEV" > "$OUTPUT_DEV"
  echo "✅ Decrypted: $OUTPUT_DEV"
else
  echo "⚠️  $INPUT_DEV not found. Skipping."
fi

if [[ -f "$INPUT_PROD" ]]; then
  echo "🔓 Decrypting $INPUT_PROD to $OUTPUT_PROD ..."
  sops -d "$INPUT_PROD" > "$OUTPUT_PROD"
  echo "✅ Decrypted: $OUTPUT_PROD"
else
  echo "⚠️  $INPUT_PROD not found. Skipping."
fi
