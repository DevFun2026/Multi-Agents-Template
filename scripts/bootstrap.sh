#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-check}"

if [[ "$MODE" != "check" && "$MODE" != "--install" ]]; then
  echo "Usage: $0 [--install]"
  exit 2
fi

have() {
  command -v "$1" >/dev/null 2>&1
}

version_major() {
  local value="$1"
  value="${value#v}"
  printf '%s' "${value%%.*}"
}

echo "== Multi-Agents Template bootstrap =="

if have git; then
  echo "[ok] git: $(git --version)"
else
  echo "[missing] git"
fi

if have codex; then
  echo "[ok] codex is available"
else
  echo "[missing] codex"
fi

NODE_OK=false
if have node; then
  NODE_VERSION="$(node --version)"
  NODE_MAJOR="$(version_major "$NODE_VERSION")"
  echo "[ok] node: $NODE_VERSION"
  if [[ "$NODE_MAJOR" =~ ^[0-9]+$ ]] && (( NODE_MAJOR >= 18 )); then
    NODE_OK=true
  else
    echo "[warn] ECC universal tooling requires Node.js 18+"
  fi
else
  echo "[missing] node (Node.js 18+ recommended)"
fi

if have npm; then
  echo "[ok] npm: $(npm --version)"
else
  echo "[missing] npm"
fi

if have python3; then
  echo "[ok] python3: $(python3 --version 2>&1)"
else
  echo "[warn] python3 missing; UI UX Pro Max search tooling requires Python 3"
fi

echo
echo "Superpowers:"
echo "  Install from inside Codex using /plugins, search for 'Superpowers', then Install Plugin."

if [[ "$MODE" == "--install" ]]; then
  echo
  echo "== Installing supported components =="

  if ! have codex; then
    echo "[skip] ECC native plugin: codex command not found"
  else
    echo "[install] ECC native Codex plugin"
    codex plugin marketplace add affaan-m/ECC
    codex plugin add ecc@ecc
    codex plugin list --json
  fi

  if ! $NODE_OK || ! have npm; then
    echo "[skip] UI UX Pro Max: Node.js 18+/npm not ready"
  else
    if ! have uipro; then
      echo "[install] ui-ux-pro-max-cli"
      npm install -g ui-ux-pro-max-cli
    fi
    echo "[install] UI UX Pro Max for Codex"
    uipro init --ai codex
  fi

  echo
  echo "Installation phase complete."
  echo "Superpowers remains an interactive Codex plugin install via /plugins."
else
  echo
  echo "Check-only mode made no installation changes."
  echo "Run '$0 --install' to install ECC and UI UX Pro Max using their supported CLIs."
fi

echo
echo "Validate repository structure with:"
echo "  ./scripts/verify-template.sh"
