#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-check}"
TARGET="${2:-all}"

if [[ "$MODE" != "check" && "$MODE" != "--install" ]]; then
  echo "Usage: $0 [--install] [codex|claude|gemini|all]"
  exit 2
fi

case "$TARGET" in
  codex|claude|gemini|all) ;;
  *)
    echo "Unknown target: $TARGET"
    echo "Usage: $0 [--install] [codex|claude|gemini|all]"
    exit 2
    ;;
esac

have() {
  command -v "$1" >/dev/null 2>&1
}

version_major() {
  local value="$1"
  value="${value#v}"
  printf '%s' "${value%%.*}"
}

wants() {
  [[ "$TARGET" == "all" || "$TARGET" == "$1" ]]
}

echo "== Multi-Agents Template bootstrap =="

if have git; then echo "[ok] git: $(git --version)"; else echo "[missing] git"; fi
if have codex; then echo "[ok] codex"; else echo "[info] codex not found"; fi
if have claude; then echo "[ok] claude"; else echo "[info] claude not found"; fi
if have gemini; then echo "[ok] gemini"; else echo "[info] gemini not found"; fi

NODE_OK=false
if have node; then
  NODE_VERSION="$(node --version)"
  NODE_MAJOR="$(version_major "$NODE_VERSION")"
  echo "[ok] node: $NODE_VERSION"
  if [[ "$NODE_MAJOR" =~ ^[0-9]+$ ]] && (( NODE_MAJOR >= 18 )); then
    NODE_OK=true
  else
    echo "[warn] Node.js 18+ is recommended for ECC/UI UX tooling"
  fi
else
  echo "[missing] node"
fi

if have npm; then echo "[ok] npm: $(npm --version)"; else echo "[missing] npm"; fi
if have python3; then echo "[ok] python3: $(python3 --version 2>&1)"; else echo "[warn] python3 missing; UI UX Pro Max requires Python 3"; fi

echo
echo "Project adapters already included:"
echo "  Codex      -> .codex/"
echo "  Claude     -> CLAUDE.md + .claude/agents/"
echo "  Gemini CLI -> GEMINI.md + .gemini/agents/"

if [[ "$MODE" != "--install" ]]; then
  echo
  echo "Check-only mode made no installation changes."
  echo "Install one harness with:"
  echo "  $0 --install codex"
  echo "  $0 --install claude"
  echo "  $0 --install gemini"
  echo
  echo "See docs/UPSTREAMS.md before installing third-party integrations."
  exit 0
fi

ensure_uipro() {
  if ! $NODE_OK || ! have npm; then
    echo "[skip] UI UX Pro Max: Node.js 18+/npm not ready"
    return
  fi

  if ! have uipro; then
    echo "[install] ui-ux-pro-max-cli"
    npm install -g ui-ux-pro-max-cli
  fi
}

if wants codex; then
  echo
  echo "== Codex =="

  echo "[manual] Superpowers:"
  echo "  Start Codex, run /plugins, search Superpowers, select Install Plugin."

  if have codex; then
    echo "[install] ECC native Codex plugin"
    codex plugin marketplace add affaan-m/ECC
    codex plugin add ecc@ecc
    codex plugin list --json
  else
    echo "[skip] ECC for Codex: codex command not found"
  fi

  ensure_uipro
  if have uipro; then
    echo "[install] UI UX Pro Max for Codex"
    uipro init --ai codex
  fi
fi

if wants claude; then
  echo
  echo "== Claude Code =="

  echo "[manual] Superpowers inside Claude Code:"
  echo "  /plugin install superpowers@claude-plugins-official"

  if $NODE_OK && have npm; then
    echo "[install] ECC for Claude Code using official guided installer"
    npx ecc-universal@2.2.3 install --guided --harness claude --claude-scope local --claude-hooks standard --profile core --yes
  else
    echo "[skip] ECC for Claude: Node.js 18+/npm not ready"
  fi

  ensure_uipro
  if have uipro; then
    echo "[install] UI UX Pro Max for Claude Code"
    uipro init --ai claude
  fi
fi

if wants gemini; then
  echo
  echo "== Gemini CLI =="

  if have gemini; then
    echo "[install] Superpowers Gemini extension"
    gemini extensions install https://github.com/obra/superpowers
  else
    echo "[skip] Superpowers for Gemini: gemini command not found"
  fi

  echo "[manual] ECC Gemini adapter:"
  echo "  ECC currently documents a project-local adapter from a reviewed ECC checkout:"
  echo "    git clone https://github.com/affaan-m/ECC.git /tmp/ecc"
  echo "    cd /tmp/ecc"
  echo "    ./install.sh --profile minimal --target gemini"
  echo "  Review the generated .gemini changes before merging because this template already defines project agents."

  ensure_uipro
  if have uipro; then
    echo "[install] UI UX Pro Max for Gemini CLI"
    uipro init --ai gemini
  fi
fi

echo
echo "Bootstrap complete."
echo "Validate repository structure with:"
echo "  ./scripts/verify-template.sh"
