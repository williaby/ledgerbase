#!/bin/bash

# generate_requirements.sh - Export Poetry dependencies to requirements.txt

set -e

echo "📦 Exporting requirements.txt using poetry-plugin-export..."
poetry export --without-hashes --format=requirements.txt -o requirements.txt
echo "✅ requirements.txt updated."
