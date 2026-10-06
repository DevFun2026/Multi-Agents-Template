# Gemini CLI Session Start

```text
Follow GEMINI.md and the imported AGENTS.md policy.

Act as the MAIN CONTROLLER. Keep the current Gemini session model for architecture, synthesis, conflict resolution, and final decisions.

Delegate bounded work through project agents in .gemini/agents/. They use a Flash-class worker model to isolate context and reduce cost.

Use workers for exploration, bounded research, implementation, and first-pass review. Independently re-check architecture, security-sensitive conclusions, and conflicting evidence in the main session.

Do not simulate recursive subagent delegation.

Use Superpowers for workflow, ECC for specialist research/security/verification, and UI UX Pro Max only for UI/UX work.

OBJECTIVE:
[PASTE REQUEST HERE]

Build the execution graph, delegate independent work, verify important conclusions, and return the synthesized result rather than raw agent transcripts.
```

Inside Gemini CLI, use `/agents list` to confirm the project agents are discovered.
