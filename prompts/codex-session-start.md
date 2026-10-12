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

PHASE 1 — CLARIFY AND PLAN (no file edits, no implementer):
1. Invoke the Superpowers brainstorming skill and ask me the questions that change the design.
2. Use explorer/researcher children only where read-only evidence informs the plan.
3. Invoke the Superpowers writing-plans skill and save the plan. Include: success criteria, scope/non-goals, architecture decision, execution graph with read/write classification, child roles with model/effort tiers, ordered tasks with exact files and tests, verification plan, risks, open questions.
4. Summarize the plan and give its path, then STOP and wait for explicit user approval. Do not start PHASE 2 in the same turn.

PHASE 2 — EXECUTE (only after I approve the plan):
Route work by cost tier, execute, verify, and return only the synthesized result and important evidence. If the plan must change materially, stop and ask again.
```
