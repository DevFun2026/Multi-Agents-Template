@AGENTS.md

# Claude Code Adapter

This repository uses AGENTS.md as the cross-harness source of truth.

Claude Code-specific behavior:

- Keep the model selected for the main Claude session as the controller and final decision-maker.
- Use project subagents from `.claude/agents/` for bounded work.
- Prefer `haiku` roles for search, exploration, and bounded research.
- Prefer `sonnet` roles for implementation and focused review.
- Keep architecture, difficult conflict resolution, and final decisions in the main session unless explicit escalation is useful.
- Do not spawn agents merely to maximize parallelism.
- Give every subagent a narrow, self-contained task and ask for compact results.
- Use Superpowers as process authority, ECC as specialist/verification capability, and UI UX Pro Max only for UI/UX work.
