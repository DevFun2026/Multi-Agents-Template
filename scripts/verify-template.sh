#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python3 scripts/validate_template.py
python3 scripts/test-validator-mutations.py
python3 scripts/test-bootstrap.py

if command -v node >/dev/null 2>&1; then
  node scripts/test-gemini-policy.mjs
elif [[ "${REQUIRE_GEMINI_POLICY_TEST:-}" == "1" ]]; then
  echo "[fail] node is required for the Gemini policy engine test"
  exit 1
else
  echo "[warn] node not installed; skipping Gemini policy engine test (CI runs it)"
fi

bash -n scripts/bootstrap.sh
bash -n scripts/verify-template.sh

if command -v shellcheck >/dev/null 2>&1; then
  shellcheck scripts/bootstrap.sh scripts/verify-template.sh
else
  echo "[warn] shellcheck not installed; CI runs shellcheck separately"
fi

echo "Template verification passed for Codex + Claude Code + Gemini CLI."
