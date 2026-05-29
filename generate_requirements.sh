#!/bin/bash

##: name = generate_requirements.sh
##: description = Generates requirements.txt and dev-requirements.txt from uv.lock for compatibility tools.
##: usage = ./generate_requirements.sh
##: behavior = Uses uv export to regenerate requirements.txt and dev-requirements.txt without hashes.

set -e

echo "📦 Exporting requirements.txt using uv export..."
uv export --no-hashes --no-emit-project --no-dev --format requirements-txt -o requirements.txt
echo "✅ requirements.txt updated."

echo "📦 Exporting dev-requirements.txt using uv export..."
uv export --no-hashes --no-emit-project --only-group dev --format requirements-txt -o dev-requirements.txt
echo "✅ dev-requirements.txt updated."
