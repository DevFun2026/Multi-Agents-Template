@AGENTS.md

# Claude Code Adapter

This repository uses AGENTS.md as the cross-harness source of truth.

Claude Code-specific behavior:

- Keep the model selected for the main Claude session as controller and final decision-maker.
- Use project subagents from `.claude/agents/`.
- Explorer and external researcher use Haiku-class workers.
- Implementer and reviewers use Sonnet-class workers.
- The implementer uses `isolation: worktree`.
- `.claude/settings.json` caps spawn depth at one, and every project agent disallows the `Agent` tool.
- Reviewers inspect the actual diff and can run local tests/checks.
- External researcher has web tools but no local file tools.
- Security/UI reviewers have local tools but no outbound web tools.
- Do not spawn agents merely to maximize parallelism.
- Use Superpowers as process authority, ECC as specialist/verification capability, and UI UX Pro Max only for UI/UX work.
