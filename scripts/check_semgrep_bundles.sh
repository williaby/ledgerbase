#!/usr/bin/env bash
##: name = check_semgrep_bundles.sh
##: description = Script to check the availability of Semgrep bundles in both Pro and Community versions
##: category = security
##: usage = ./scripts/check_semgrep_bundles.sh
##: behavior = Tests each Semgrep bundle with both p/ and r/ prefixes and reports availability
##: inputs = none
##: outputs = Console output showing which bundles are available in Pro vs Community
##: dependencies = Semgrep CLI
##: author = LedgerBase Team
##: last_modified = 2023-11-15
##: changelog = Initial version

set -euo pipefail

# Bundles to check (without prefix)
bundles=(
  python.flask
  python.bandit
  python.cwe-top-25
  python.security-audit
  python.secure-defaults
  r2c-best-practices
  owasp-top-ten
  injection
  xss
  secrets
  gitleaks
  github-actions
  semgrep-misconfigurations
  bash.shellcheck
  ci
)

echo "Checking Semgrep bundle availability (Pro vs Community)..."
for name in "${bundles[@]}"; do
  echo "→ $name"
  for prefix in p r; do
    full="${prefix}/${name}"
    if semgrep scan --config "$full" --dryrun > /dev/null 2>&1; then
      echo "    ✅  $full"
    else
      echo "    ❌  $full"
    fi
  done
  echo
done
