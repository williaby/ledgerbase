#!/bin/bash

##: name = check-system.sh
##: description = Verifies required system dependencies for LedgerBase.
##: usage = ./check-system.sh
##: behavior = Prints version info for uv, Python, and sops; exits if any tool is missing.

set -e
command -v uv && uv --version
command -v python3 && python3 --version
command -v sops && sops --version


echo "🔍 Checking system environment..."

# Section 1: uv setup
echo "📦 uv:"
uv --version || { echo "❌ uv not found"; exit 1; }
uv lock --locked > /dev/null 2>&1 || { echo "❌ uv.lock is not consistent with pyproject.toml"; exit 1; }

echo "✅ uv is installed and the lockfile is consistent."

# Section 2: uv export capability
echo -n "🔌 Checking uv export... "
if ! uv export --no-hashes --format requirements-txt > /dev/null 2>&1; then
  echo "❌ uv export failed"
  exit 1
else
  echo "✅"
fi

# Section 3: GPG key
echo "🔐 Checking GPG secret key..."
if ! gpg --list-secret-keys --keyid-format LONG | grep -q "9360A8293F1430EB3E88B99CB2C95364612BFFDF"; then # pragma: allowlist secret
  echo "❌ GPG key not found"
  exit 1
else
  echo "✅ GPG key is present"
fi

# Section 4: SOPS decryption
echo "🧪 Testing sops decryption..."
if ! sops -d .env.prod.sops.yaml >/dev/null 2>&1; then
  echo "❌ Failed to decrypt .env.prod.sops.yaml"
  exit 1
else
  echo "✅ Decryption successful"
fi

# Section 5: Environment key check
echo "🔍 Checking required keys in .env.prod.sops.yaml..."
REQUIRED_KEYS=("DATABASE_URL" "SNYK_TOKEN" "POSTGRES_USER" "POSTGRES_PASSWORD")
MISSING_KEYS=()
DECRYPTED=$(sops -d .env.prod.sops.yaml)

for KEY in "${REQUIRED_KEYS[@]}"; do
  if ! echo "$DECRYPTED" | grep -q "^$KEY="; then
    MISSING_KEYS+=("$KEY")
  fi
done

if [[ ${#MISSING_KEYS[@]} -gt 0 ]]; then
  echo "❌ Missing keys:"
  printf '   - %s\n' "${MISSING_KEYS[@]}"
  exit 1
else
  echo "✅ All required keys found"
fi

# Section 6: Direnv
echo "🌱 Checking direnv load..."
if [[ -z "$SNYK_TOKEN" ]]; then
  echo "⚠️  $SNYK_TOKEN not in shell — run 'direnv allow' in ledgerbase_secure_env"
else
  echo "✅ direnv loaded environment: SNYK_TOKEN=${#SNYK_TOKEN} characters"
fi

# Section 7: Python environment loader
echo "🐍 Testing load_env.py..."
if uv run python load_env.py | grep -q "All required environment variables are present"; then
  echo "✅ load_env.py is working"
else
  echo "❌ load_env.py failed — check dotenv files"
  exit 1
fi

# Section 8: Pre-commit validation
echo "🧹 Running pre-commit checks..."
pre-commit run --all-files || {
  echo "❌ One or more pre-commit checks failed."
  exit 1
}

echo "🎉 All systems GO — Ledgerbase secure environment verified."
