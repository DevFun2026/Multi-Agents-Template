#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python3 scripts/validate_template.py

bash -n scripts/bootstrap.sh
bash -n scripts/verify-template.sh

if command -v shellcheck >/dev/null 2>&1; then
  shellcheck scripts/bootstrap.sh scripts/verify-template.sh
else
  echo "[warn] shellcheck not installed; CI runs shellcheck separately"
fi

echo "Template verification passed for Codex + Claude Code + Gemini CLI."
