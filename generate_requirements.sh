#!/bin/bash

##: name = generate_requirements.sh
##: description = Generates requirements.txt and dev-requirements.txt from poetry.lock for compatibility tools.
##: usage = ./generate_requirements.sh
##: behavior = Uses poetry export to regenerate requirements.txt and dev-requirements.txt without hashes.

set -e

echo "📦 Exporting requirements.txt using poetry-plugin-export..."
poetry export --without-hashes --format=requirements.txt -o requirements.txt
echo "✅ requirements.txt updated."

echo "📦 Exporting dev-requirements.txt using poetry-plugin-export..."
poetry export --only dev --without-hashes --format=requirements.txt -o dev-requirements.txt
echo "✅ dev-requirements.txt updated."
