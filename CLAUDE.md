@AGENTS.md

# Claude Code Adapter

This repository uses AGENTS.md as the cross-harness source of truth.

Claude Code-specific behavior:

- Keep the model selected for the main Claude session as controller and final decision-maker.
- Use project subagents from `.claude/agents/`.
- Explorer and external researcher use Haiku-class workers.
- Implementer and reviewers use Sonnet-class workers.
- The implementer uses `isolation: worktree`; project settings use `worktree.baseRef = "head"`, so it branches from the current committed HEAD. Uncommitted changes are not copied.
- `.claude/settings.json` caps spawn depth at one, and every project agent disallows the `Agent` tool.
- Implementers must report their worktree path and base/head refs; reviewers inspect that worktree directly and can run local tests/checks.
- External researcher has web tools but no local file tools.
- Security/UI reviewers have local tools but no dedicated web tools. Bash can still run network-capable binaries; project permissions deny common curl/wget commands, but this is not a complete network sandbox.
- Do not spawn agents merely to maximize parallelism.
- Use Superpowers as process authority, ECC as specialist/verification capability, and UI UX Pro Max only for UI/UX work.