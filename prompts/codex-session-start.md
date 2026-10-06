# Codex Session Start

```text
Follow AGENTS.md and .codex/config.toml.

Act as the MAIN CONTROLLER. Keep the current session model for decomposition, architecture, synthesis, conflict resolution, and final decisions.

For EVERY spawned child:
1. set fork_turns: "none" by default (or a deliberately small integer when recent context is truly required);
2. select a model from the CURRENT spawn allowlist;
3. explicitly select reasoning effort.

Do not spawn a child with full inherited history when the purpose is cheaper model routing or context isolation.

Parallelize read-only explorer/research/review tasks when useful. Codex children share the same project directory, so serialize workspace-writing implementers unless separate worktrees/workspaces have deliberately been prepared.

Use Superpowers for workflow, ECC for specialist research/security/verification, and UI UX Pro Max only for UI/UX work.

OBJECTIVE:
[PASTE REQUEST HERE]

Build the execution graph, route work by cost tier, execute, verify, and return only the synthesized result and important evidence.
```
