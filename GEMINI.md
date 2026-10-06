@AGENTS.md

# Gemini CLI Adapter

This repository uses AGENTS.md as the cross-harness source of truth.

Gemini CLI-specific behavior:

- Keep the main Gemini session as controller and final decision-maker.
- Use project subagents from `.gemini/agents/` for bounded work.
- Project workers use the `flash` model alias so current Flash promotion remains available.
- Parallelize read-only workers when useful.
- Serialize workspace-writing implementers inside one Gemini session because subagents share the active working tree.
- `.gemini/settings.json` enables worktree support for separate top-level sessions; it does not make local subagents automatically get their own worktrees.
- For truly parallel write work, start separate top-level Gemini sessions in separate worktrees.
- Gemini subagents are one level deep by design.
- External researcher has web tools but no local file tools.
- Security/UI reviewers have local tools but no dedicated web tools. Their shell can still launch network-capable commands; Gemini 0.62.0 requires a user-tier policy for enforceable curl/wget denial because workspace policies are currently non-functional. See `examples/gemini-user-policies/reviewer-network-deny.toml`.
- Main Gemini must re-evaluate high-risk architecture, security conclusions, and conflicting evidence.
- Gemini may have stronger built-in delegation preferences than project instructions; treat "skip delegation for tiny tasks" as best-effort.
- Use Superpowers as process authority, ECC as specialist/verification capability, and UI UX Pro Max only for UI/UX work.