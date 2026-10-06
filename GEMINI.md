@AGENTS.md

# Gemini CLI Adapter

This repository uses AGENTS.md as the cross-harness source of truth.

Gemini CLI-specific behavior:

- Keep the main Gemini session as the controller and final decision-maker.
- Use project subagents from `.gemini/agents/` for bounded work.
- The project agents use a Flash-class worker model to protect main-session context and cost.
- For architecture, ambiguous high-risk decisions, difficult conflicts, or security conclusions, the main session must re-evaluate the worker evidence before deciding.
- Gemini subagents are one level deep by design; do not simulate recursive delegation.
- Prefer isolated evidence packets over replaying large context.
- Use Superpowers as process authority, ECC as specialist/verification capability, and UI UX Pro Max only for UI/UX work.
