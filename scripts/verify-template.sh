#!/usr/bin/env bash
set -euo pipefail

required=(
  "README.md"
  "AGENTS.md"
  "CLAUDE.md"
  "GEMINI.md"

  ".codex/config.toml"
  ".codex/agents/explorer.toml"
  ".codex/agents/researcher.toml"
  ".codex/agents/implementer.toml"
  ".codex/agents/reviewer.toml"
  ".codex/agents/security-reviewer.toml"
  ".codex/agents/uiux-reviewer.toml"

  ".claude/agents/explorer.md"
  ".claude/agents/researcher.md"
  ".claude/agents/implementer.md"
  ".claude/agents/reviewer.md"
  ".claude/agents/security-reviewer.md"
  ".claude/agents/uiux-reviewer.md"

  ".gemini/settings.json"
  ".gemini/agents/explorer.md"
  ".gemini/agents/researcher.md"
  ".gemini/agents/implementer.md"
  ".gemini/agents/reviewer.md"
  ".gemini/agents/security-reviewer.md"
  ".gemini/agents/uiux-reviewer.md"

  "prompts/session-start.md"
  "prompts/codex-session-start.md"
  "prompts/claude-session-start.md"
  "prompts/gemini-session-start.md"

  "docs/HARNESSES.md"
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
  echo "[fail] Codex config must enable multi_agent"
  failed=1
fi

if ! grep -Eq '^[[:space:]]*max_depth[[:space:]]*=[[:space:]]*1' .codex/config.toml; then
  echo "[fail] Codex max_depth should remain 1"
  failed=1
fi

if ! grep -Fq '@AGENTS.md' CLAUDE.md; then
  echo "[fail] CLAUDE.md must import AGENTS.md"
  failed=1
fi

if ! grep -Fq '@AGENTS.md' GEMINI.md; then
  echo "[fail] GEMINI.md must import AGENTS.md"
  failed=1
fi

if ! grep -Eq '"enableAgents"[[:space:]]*:[[:space:]]*true' .gemini/settings.json; then
  echo "[fail] Gemini settings must enable agents"
  failed=1
fi

for file in .claude/agents/*.md; do
  if ! grep -Eq '^model:[[:space:]]+(haiku|sonnet|opus|inherit)[[:space:]]*$' "$file"; then
    echo "[fail] Claude agent missing valid model tier: $file"
    failed=1
  fi
done

for file in .gemini/agents/*.md; do
  if ! grep -Eq '^model:[[:space:]]+[^[:space:]]+' "$file"; then
    echo "[fail] Gemini agent missing explicit worker model: $file"
    failed=1
  fi
done

bash -n scripts/bootstrap.sh
bash -n scripts/verify-template.sh

if [[ "$failed" -ne 0 ]]; then
  echo "Template verification failed."
  exit 1
fi

echo "Template verification passed for Codex + Claude Code + Gemini CLI."
