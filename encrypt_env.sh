#!/bin/bash

##: name = encrypt_env.sh
##: description = Encrypts env.dev and env.prod files stored in ledgerbase_secure_env using sops.
##: category = security
##: usage = ./encrypt_env.sh
##: behavior = Encrypts dev and prod env files using GPG into .env.dev.sops.yaml and .env.prod.sops.yaml.
##: inputs = ledgerbase_secure_env/.env.dev and ledgerbase_secure_env/.env.prod files
##: outputs = .env.dev.sops.yaml and .env.prod.sops.yaml encrypted files
##: dependencies = sops, gpg
##: author = LedgerBase Team
##: last_modified = 2023-11-15
##: changelog = Initial version

set -e

KEY_ID="9360A8293F1430EB3E88B99CB2C95364612BFFDF"
SECURE_DIR="ledgerbase_secure_env"

DEV_ENV="${SECURE_DIR}/.env.dev"
PROD_ENV="${SECURE_DIR}/.env.prod"
DEV_OUT=".env.dev.sops.yaml"
PROD_OUT=".env.prod.sops.yaml"

if [[ -f "$DEV_ENV" ]]; then
  echo "🔐 Encrypting $DEV_ENV into $DEV_OUT ..."
  sops --encrypt --pgp "$KEY_ID" "$DEV_ENV" > "$DEV_OUT"
  echo "✅ $DEV_OUT written."
else
  echo "⚠️  $DEV_ENV not found. Skipping dev encryption."
fi

if [[ -f "$PROD_ENV" ]]; then
  echo "🔐 Encrypting $PROD_ENV into $PROD_OUT ..."
  sops --encrypt --pgp "$KEY_ID" "$PROD_ENV" > "$PROD_OUT"
  echo "✅ $PROD_OUT written."
else
  echo "⚠️  $PROD_ENV not found. Skipping prod encryption."
fi
