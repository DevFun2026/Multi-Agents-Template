#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ECC_VERSION="2.2.3"
ECC_REF="0348d7b6d722c8832b306859b78a1d969b427f5b"
UIPRO_VERSION="2.15.0"
SUPERPOWERS_REF="8ca22dba9a94f28898bbce59f2537ff4d87c747d"

usage() {
  cat <<'EOF'
Usage:
  bash scripts/bootstrap.sh
  bash scripts/bootstrap.sh codex|claude|gemini|all
  bash scripts/bootstrap.sh --install codex|claude|gemini

No-argument and positional harness forms are CHECK/INSPECT ONLY.
--install mutates one harness at a time. "--install all" is intentionally unsupported.
EOF
}

ACTION="check"
TARGET="all"

if [[ $# -eq 0 ]]; then
  :
elif [[ "$1" == "--help" || "$1" == "-h" ]]; then
  usage
  exit 0
elif [[ "$1" == "--install" ]]; then
  if [[ $# -ne 2 ]]; then
    usage
    exit 2
  fi
  ACTION="install"
  TARGET="$2"
  if [[ "$TARGET" == "all" ]]; then
    echo "[error] --install all is intentionally unsupported."
    echo "Install one harness at a time so third-party changes can be reviewed."
    exit 2
  fi
elif [[ $# -eq 1 ]]; then
  TARGET="$1"
else
  usage
  exit 2
fi

case "$TARGET" in
  codex|claude|gemini|all) ;;
  *)
    echo "[error] unknown target: $TARGET"
    usage
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
echo "[root] $ROOT_DIR"
echo "[mode] $ACTION"
echo "[target] $TARGET"

if have git; then echo "[ok] git: $(git --version)"; else echo "[missing] git"; fi
if have codex; then echo "[ok] codex: $(codex --version 2>/dev/null || true)"; else echo "[info] codex not found"; fi
if have claude; then echo "[ok] claude command found"; else echo "[info] claude not found"; fi
if have gemini; then echo "[ok] gemini: $(gemini --version 2>/dev/null || true)"; else echo "[info] gemini not found"; fi

NODE_OK=false
if have node; then
  NODE_VERSION="$(node --version)"
  NODE_MAJOR="$(version_major "$NODE_VERSION")"
  echo "[ok] node: $NODE_VERSION"
  if [[ "$NODE_MAJOR" =~ ^[0-9]+$ ]] && (( NODE_MAJOR >= 18 )); then
    NODE_OK=true
  else
    echo "[warn] Node.js 18+ is required by ECC universal tooling"
  fi
else
  echo "[missing] node"
fi

if have npm; then echo "[ok] npm: $(npm --version)"; else echo "[missing] npm"; fi
if have python3; then
  echo "[ok] python3: $(python3 --version 2>&1)"
  if python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)'; then
    echo "[ok] Python version supports the validator (tomli fallback is used below 3.11)"
  else
    echo "[warn] Python 3.9+ is required for template validation"
  fi
else
  echo "[missing] python3"
fi

print_plan() {
  local harness="$1"
  case "$harness" in
    codex)
      echo
      echo "== Codex plan =="
      echo "Superpowers: install interactively from /plugins."
      echo "ECC source pin: $ECC_REF (release $ECC_VERSION)"
      echo "UI UX Pro Max CLI pin: $UIPRO_VERSION"
      ;;
    claude)
      echo
      echo "== Claude Code plan =="
      echo "Superpowers: install interactively from the official Claude plugin marketplace."
      echo "ECC npm pin: ecc-universal@$ECC_VERSION"
      echo "UI UX Pro Max CLI pin: $UIPRO_VERSION"
      ;;
    gemini)
      echo
      echo "== Gemini CLI plan =="
      echo "Superpowers Git pin: $SUPERPOWERS_REF"
      echo "ECC source pin for reviewed manual adapter step: $ECC_REF"
      echo "UI UX Pro Max CLI pin: $UIPRO_VERSION"
      ;;
  esac
}

for harness in codex claude gemini; do
  if wants "$harness"; then
    print_plan "$harness"
  fi
done

if [[ "$ACTION" == "check" ]]; then
  echo
  echo "Check/inspect mode made no installation changes."
  echo "Use --install with exactly one harness when ready."
  exit 0
fi

ensure_uipro() {
  if ! $NODE_OK || ! have npm; then
    echo "[skip] UI UX Pro Max: Node.js 18+/npm not ready"
    return 1
  fi

  echo "[install] pinning ui-ux-pro-max-cli@$UIPRO_VERSION"
  npm install -g "ui-ux-pro-max-cli@$UIPRO_VERSION"
}

install_uipro_for() {
  local harness="$1"
  if ensure_uipro; then
    echo "[install] UI UX Pro Max for $harness"
    echo "[note] ui-ux-pro-max-cli $UIPRO_VERSION has no --dry-run; init writes to the current project."
    uipro init --ai "$harness"
  fi
}

if [[ "$TARGET" == "codex" ]]; then
  echo
  echo "== Install Codex integrations =="
  echo "[manual] Superpowers: Start Codex, run /plugins, search Superpowers, select Install Plugin."

  if have codex; then
    echo "[install] ECC native Codex marketplace pinned to $ECC_REF"
    set +e
    marketplace_output="$(codex plugin marketplace add affaan-m/ECC --ref "$ECC_REF" 2>&1)"
    marketplace_rc=$?
    set -e
    printf '%s\n' "$marketplace_output"

    if [[ "$marketplace_rc" -eq 0 ]]; then
      codex plugin add ecc@ecc
      codex plugin list --json
    elif grep -qi 'already added from a different source' <<<"$marketplace_output"; then
      echo "[warn] Existing ECC marketplace was added from a different source/ref."
      echo "       Leaving it unchanged instead of silently using an unpinned source."
      echo "       Remove/update the existing affaan-m/ECC marketplace in Codex, then rerun this command."
    else
      echo "[error] Failed to add the pinned ECC marketplace."
      exit "$marketplace_rc"
    fi
  else
    echo "[skip] ECC for Codex: codex command not found"
  fi

  install_uipro_for codex
fi

if [[ "$TARGET" == "claude" ]]; then
  echo
  echo "== Install Claude Code integrations =="
  echo "[manual] Superpowers inside Claude Code: /plugin install superpowers@claude-plugins-official"

  if $NODE_OK && have npm; then
    echo "[preview] ECC for Claude Code"
    npx "ecc-universal@$ECC_VERSION" install --guided --harness claude --claude-scope local --claude-hooks standard --profile core --yes --dry-run
    echo "[install] ECC for Claude Code"
    npx "ecc-universal@$ECC_VERSION" install --guided --harness claude --claude-scope local --claude-hooks standard --profile core --yes
  else
    echo "[skip] ECC for Claude: Node.js 18+/npm not ready"
  fi

  install_uipro_for claude
fi

if [[ "$TARGET" == "gemini" ]]; then
  echo
  echo "== Install Gemini CLI integrations =="

  if have gemini; then
    extension_list="$(gemini extensions list 2>&1 || true)"
    if grep -qi 'superpowers' <<<"$extension_list"; then
      echo "[ok] Superpowers extension already installed; leaving its current ref unchanged."
      echo "     To force the template pin, uninstall it first and rerun this command."
    else
      echo "[install] Superpowers pinned to $SUPERPOWERS_REF"
      gemini extensions install https://github.com/obra/superpowers --ref "$SUPERPOWERS_REF" --consent
    fi
  else
    echo "[skip] Superpowers for Gemini: gemini command not found"
  fi

  echo
  echo "[manual-review] ECC Gemini adapter is not auto-applied because it writes project-local .gemini files."
  echo "Run the reviewed ECC checkout from THIS project root (do not cd into the ECC checkout):"
  echo "  tmp_dir=\"\$(mktemp -d)\""
  echo "  git clone https://github.com/affaan-m/ECC.git \"\$tmp_dir/ECC\""
  echo "  git -C \"\$tmp_dir/ECC\" checkout $ECC_REF"
  echo "  \"\$tmp_dir/ECC/install.sh\" --profile minimal --target gemini --dry-run"
  echo "Inspect the dry-run output. If acceptable, run the same command without --dry-run, still from this project root."
  echo "Then review the resulting .gemini diff before committing it."

  install_uipro_for gemini
fi

echo
echo "Bootstrap complete for $TARGET."
echo "Validate repository structure with:"
echo "  python3 -m pip install -r requirements-dev.txt"
echo "  bash scripts/verify-template.sh"