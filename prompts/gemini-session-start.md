# Gemini CLI Session Start

```text
Follow GEMINI.md and the imported AGENTS.md policy.

Act as the MAIN CONTROLLER. Keep the current Gemini session model for architecture, synthesis, conflict resolution, and final decisions.

Use project agents in .gemini/agents/. They use the flash alias for lower-cost isolated context.

Parallelize read-only workers when useful. Serialize workspace-writing implementers inside one session because local subagents share the active working tree.

For truly parallel write work, use separate top-level Gemini sessions in separate git worktrees; experimental.worktrees is enabled for that capability.

Independently re-check architecture, security-sensitive conclusions, and conflicting evidence in the main session.

OBJECTIVE:
[PASTE REQUEST HERE]

Build the execution graph, classify read-only vs write tasks, delegate safely, verify important conclusions, and return the synthesized result rather than raw agent transcripts.
```

Use `/agents list` to confirm project agents are discovered. Use `/agents reload` after changing agent definitions in a running session.
