#!/usr/bin/env bash
set -euo pipefail

required=(
  "README.md"
  "AGENTS.md"
  ".codex/config.toml"
  ".codex/agents/explorer.toml"
  ".codex/agents/researcher.toml"
  ".codex/agents/implementer.toml"
  ".codex/agents/reviewer.toml"
  ".codex/agents/security-reviewer.toml"
  ".codex/agents/uiux-reviewer.toml"
  "prompts/session-start.md"
  "docs/ORCHESTRATION.md"
  "docs/SESSION-EXAMPLES.md"
  "docs/UPSTREAMS.md"
  "scripts/bootstrap.sh"
)

failed=0

for file in "${required[@]}"; do
  if [[ -f "$file" ]]; then
    echo "[ok] $file"
  else
    echo "[missing] $file"
    failed=1
  fi
done

if ! grep -Eq '^[[:space:]]*multi_agent[[:space:]]*=[[:space:]]*true' .codex/config.toml; then
  echo "[fail] .codex/config.toml must enable multi_agent"
  failed=1
fi

if ! grep -Eq '^[[:space:]]*max_depth[[:space:]]*=[[:space:]]*1' .codex/config.toml; then
  echo "[fail] max_depth should remain 1 for controller-owned orchestration"
  failed=1
fi

bash -n scripts/bootstrap.sh
bash -n scripts/verify-template.sh

if [[ "$failed" -ne 0 ]]; then
  echo "Template verification failed."
  exit 1
fi

echo "Template verification passed."
