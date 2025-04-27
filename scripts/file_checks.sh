#!/usr/bin/env bash
# scripts/file_checks.sh

if [ $# -eq 0 ]; then
  echo "Usage: $0 <path/to/file> [more files...]"
  exit 1
fi

LOG="docs/reports/txt/file_checks.log"
mkdir -p "$(dirname "$LOG")"
echo "=== file_checks run at $(date) ===" > "$LOG"
nox -s file_checks -- "$@" 2>&1 | tee -a "$LOG"
